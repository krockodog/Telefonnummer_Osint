"""
OSINT Phone Intelligence Platform - Main Flask Application
Production-ready backend with security features
"""
import os
import sys
import time
import logging
import hashlib
from datetime import datetime
from functools import wraps

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from src.phone_analyzer import phone_analyzer
from src.social_media_search import social_searcher
from src.web_search import web_searcher
from src.risk_analyzer import risk_analyzer
from src.ai_services import ai_service_manager, AIProvider

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# Configuration
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
app.config['JSON_SORT_KEYS'] = False

# Security headers with Talisman (CSP disabled for API)
Talisman(app, 
         force_https=False,
         content_security_policy={},
         content_security_policy_nonce_in=[])

# CORS configuration - allow all origins for local development
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[config.RATE_LIMIT],
    storage_uri='memory://'
)

# Request logging
@app.before_request
def log_request():
    """Log incoming requests"""
    logger.info(f"{request.method} {request.path} from {request.remote_addr}")

# Error handlers
@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded"""
    logger.warning(f"Rate limit exceeded for {request.remote_addr}")
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.',
        'retry_after': e.description
    }), 429

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server error"""
    logger.error(f"Internal error: {e}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

@app.errorhandler(404)
def not_found(e):
    """Handle not found"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404

# Validation helpers
def validate_phone_number(number: str) -> tuple:
    """Validate phone number input"""
    if not number:
        return False, "Phone number is required"
    
    if len(number) < 8 or len(number) > 20:
        return False, "Invalid phone number length"
    
    # Check for valid characters
    allowed_chars = set('0123456789+ -().')
    if not all(c in allowed_chars for c in number):
        return False, "Phone number contains invalid characters"
    
    return True, None

def validate_username(username: str) -> tuple:
    """Validate username input"""
    if not username:
        return False, "Username is required"
    
    if len(username) < 2 or len(username) > 50:
        return False, "Username must be between 2 and 50 characters"
    
    return True, None

def validate_name(name: str) -> tuple:
    """Validate name input"""
    if not name:
        return False, "Name is required"
    
    if len(name) < 2 or len(name) > 100:
        return False, "Name must be between 2 and 100 characters"
    
    return True, None

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

# Phone analysis endpoint
@app.route('/api/analyze/phone', methods=['POST'])
@limiter.limit("30 per hour")
def analyze_phone():
    """Analyze a phone number"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        phone_number = data.get('phone_number', '').strip()
        
        # Validate input
        is_valid, error = validate_phone_number(phone_number)
        if not is_valid:
            return jsonify({'error': error}), 400
        
        logger.info(f"Analyzing phone number: {phone_number}")
        
        # Analyze phone number
        analysis = phone_analyzer.analyze(phone_number)
        
        if not analysis.valid:
            return jsonify({
                'error': 'Invalid phone number',
                'message': analysis.error_message
            }), 400
        
        return jsonify({
            'success': True,
            'data': analysis.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error analyzing phone: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

# Social media search endpoint
@app.route('/api/search/social', methods=['POST'])
@limiter.limit("20 per hour")
def search_social():
    """Search for social media profiles"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        query = data.get('query', '').strip()
        query_type = data.get('type', 'phone')  # phone, username, name
        platforms = data.get('platforms', None)  # Optional list of platforms
        
        # Validate input based on type
        if query_type == 'phone':
            is_valid, error = validate_phone_number(query)
        elif query_type == 'username':
            is_valid, error = validate_username(query)
        elif query_type == 'name':
            is_valid, error = validate_name(query)
        else:
            return jsonify({'error': 'Invalid search type'}), 400
        
        if not is_valid:
            return jsonify({'error': error}), 400
        
        logger.info(f"Social search: {query_type}={query}")
        
        # Perform search
        if query_type == 'phone':
            result = social_searcher.search_by_phone(query, platforms)
        elif query_type == 'username':
            result = social_searcher.search_by_username(query, platforms)
        else:
            result = social_searcher.search_by_name(query, platforms)
        
        return jsonify({
            'success': True,
            'data': result.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error searching social: {e}")
        return jsonify({'error': 'Search failed'}), 500

# Web search endpoint
@app.route('/api/search/web', methods=['POST'])
@limiter.limit("20 per hour")
def search_web():
    """Perform web search"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        query = data.get('query', '').strip()
        search_type = data.get('type', 'general')  # general, phone, username, name
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        logger.info(f"Web search: {search_type}={query}")
        
        # Perform search based on type
        if search_type == 'phone':
            # Get phone formats first
            phone_analysis = phone_analyzer.analyze(query)
            if phone_analysis.valid:
                formats = {
                    'e164': phone_analysis.e164_format,
                    'international': phone_analysis.international_format,
                    'national': phone_analysis.national_format,
                    'local': phone_analysis.local_number
                }
                results = web_searcher.search_phone_number(query, formats)
            else:
                results = {'General': web_searcher.search_duckduckgo(query)}
        elif search_type == 'username':
            results = web_searcher.search_username(query)
        elif search_type == 'name':
            results = web_searcher.search_name(query)
        else:
            results = {'General': web_searcher.search_duckduckgo(query)}
        
        return jsonify({
            'success': True,
            'data': {
                'query': query,
                'type': search_type,
                'results': {k: v.to_dict() for k, v in results.items()}
            }
        })
        
    except Exception as e:
        logger.error(f"Error searching web: {e}")
        return jsonify({'error': 'Search failed'}), 500

# Phone lookup sources endpoint
@app.route('/api/lookup/sources', methods=['POST'])
@limiter.limit("30 per hour")
def lookup_sources():
    """Get phone lookup sources"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        phone_number = data.get('phone_number', '').strip()
        
        is_valid, error = validate_phone_number(phone_number)
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Get phone analysis for local number
        analysis = phone_analyzer.analyze(phone_number)
        local_number = analysis.local_number if analysis.valid else phone_number
        
        # Get lookup sources
        sources = web_searcher.lookup_phone_sources(local_number)
        
        return jsonify({
            'success': True,
            'data': {
                'phone_number': phone_number,
                'local_number': local_number,
                'sources': sources
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting lookup sources: {e}")
        return jsonify({'error': 'Failed to get sources'}), 500

# Full OSINT investigation endpoint
@app.route('/api/investigate', methods=['POST'])
@limiter.limit("10 per hour")
def investigate():
    """Perform full OSINT investigation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        query = data.get('query', '').strip()
        query_type = data.get('type', 'phone')
        include_social = data.get('include_social', True)
        include_web = data.get('include_web', True)
        
        # Validate input
        if query_type == 'phone':
            is_valid, error = validate_phone_number(query)
        elif query_type == 'username':
            is_valid, error = validate_username(query)
        elif query_type == 'name':
            is_valid, error = validate_name(query)
        else:
            return jsonify({'error': 'Invalid query type'}), 400
        
        if not is_valid:
            return jsonify({'error': error}), 400
        
        logger.info(f"Full investigation: {query_type}={query}")
        
        start_time = time.time()
        
        # Initialize results
        investigation = {
            'query': query,
            'type': query_type,
            'timestamp': datetime.utcnow().isoformat(),
            'phone_analysis': None,
            'social_media': None,
            'web_search': None,
            'lookup_sources': None,
            'risk_analysis': None
        }
        
        # Phone analysis (for phone type)
        phone_info = None
        if query_type == 'phone':
            phone_analysis = phone_analyzer.analyze(query)
            investigation['phone_analysis'] = phone_analysis.to_dict()
            phone_info = phone_analysis.to_dict()
        
        # Social media search
        if include_social:
            if query_type == 'phone':
                social_result = social_searcher.search_by_phone(query)
            elif query_type == 'username':
                social_result = social_searcher.search_by_username(query)
            else:
                social_result = social_searcher.search_by_name(query)
            investigation['social_media'] = social_result.to_dict()
        
        # Web search
        if include_web:
            if query_type == 'phone' and phone_info and phone_info.get('valid'):
                formats = {
                    'e164': phone_info.get('e164_format', query),
                    'international': phone_info.get('international_format', query),
                    'national': phone_info.get('national_format', query),
                    'local': phone_info.get('local_number', query)
                }
                web_results = web_searcher.search_phone_number(query, formats)
                investigation['web_search'] = {k: v.to_dict() for k, v in web_results.items()}
            else:
                web_result = web_searcher.search_duckduckgo(query)
                investigation['web_search'] = {'General': web_result.to_dict()}
        
        # Lookup sources (for phone type)
        if query_type == 'phone' and phone_info and phone_info.get('valid'):
            sources = web_searcher.lookup_phone_sources(phone_info.get('local_number', query))
            investigation['lookup_sources'] = sources
        
        # Risk analysis (for phone type)
        if query_type == 'phone':
            risk = risk_analyzer.analyze(
                phone_info or {},
                investigation.get('web_search', {}),
                investigation.get('social_media', {})
            )
            investigation['risk_analysis'] = risk.to_dict()
        
        investigation['search_time'] = round(time.time() - start_time, 2)
        
        return jsonify({
            'success': True,
            'data': investigation
        })
        
    except Exception as e:
        logger.error(f"Error in investigation: {e}")
        return jsonify({'error': 'Investigation failed'}), 500

# Get platforms endpoint
@app.route('/api/platforms', methods=['GET'])
def get_platforms():
    """Get available social media platforms"""
    try:
        platforms = social_searcher.get_all_platforms()
        return jsonify({
            'success': True,
            'data': platforms
        })
    except Exception as e:
        logger.error(f"Error getting platforms: {e}")
        return jsonify({'error': 'Failed to get platforms'}), 500

# AI Services Endpoints

@app.route('/api/ai/status', methods=['GET'])
def ai_status():
    """Get status of AI services"""
    try:
        available = ai_service_manager.get_available_services()
        return jsonify({
            'success': True,
            'data': {
                'available_services': available,
                'kimi': ai_service_manager.kimi.is_available(),
                'perplexity': ai_service_manager.perplexity.is_available(),
                'gemini': ai_service_manager.gemini.is_available()
            }
        })
    except Exception as e:
        logger.error(f"Error getting AI status: {e}")
        return jsonify({'error': 'Failed to get AI status'}), 500

@app.route('/api/ai/analyze', methods=['POST'])
@limiter.limit("15 per hour")
def ai_analyze():
    """Analyze query with AI services"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        query = data.get('query', '').strip()
        query_type = data.get('type', 'phone')
        providers = data.get('providers', None)  # Optional: specific providers
        
        # Validate input
        if query_type == 'phone':
            is_valid, error = validate_phone_number(query)
        elif query_type == 'username':
            is_valid, error = validate_username(query)
        elif query_type == 'name':
            is_valid, error = validate_name(query)
        else:
            return jsonify({'error': 'Invalid query type'}), 400
        
        if not is_valid:
            return jsonify({'error': error}), 400
        
        logger.info(f"AI analysis: {query_type}={query}, providers={providers}")
        
        # Build context for analysis
        context = {}
        
        # Get phone analysis for context if phone type
        if query_type == 'phone':
            phone_analysis = phone_analyzer.analyze(query)
            context['phone_analysis'] = phone_analysis.to_dict() if phone_analysis.valid else {}
            
            # Get risk analysis
            risk = risk_analyzer.analyze(
                context.get('phone_analysis', {}),
                {},
                {}
            )
            context['risk_analysis'] = risk.to_dict()
        
        results = {}
        
        # Analyze with specified or all available providers
        if providers:
            # Use specific providers
            if 'kimi' in providers and ai_service_manager.kimi.is_available():
                results['kimi'] = ai_service_manager.kimi.analyze_phone(query, context).to_dict()
            if 'perplexity' in providers and ai_service_manager.perplexity.is_available():
                results['perplexity'] = ai_service_manager.perplexity.search_and_analyze(query, query_type).to_dict()
            if 'gemini' in providers and ai_service_manager.gemini.is_available():
                results['gemini'] = ai_service_manager.gemini.analyze_phone(query, context).to_dict()
        else:
            # Use all available services
            ai_results = ai_service_manager.analyze_phone_all(query, context)
            results = {k: v.to_dict() for k, v in ai_results.items()}
        
        return jsonify({
            'success': True,
            'data': {
                'query': query,
                'type': query_type,
                'providers': list(results.keys()),
                'results': results
            }
        })
        
    except Exception as e:
        logger.error(f"Error in AI analysis: {e}")
        return jsonify({'error': 'AI analysis failed'}), 500

@app.route('/api/ai/research', methods=['POST'])
@limiter.limit("10 per hour")
def ai_research():
    """Perform deep research with Perplexity"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        if len(query) > 500:
            return jsonify({'error': 'Query too long (max 500 characters)'}), 400
        
        logger.info(f"AI research: {query}")
        
        if not ai_service_manager.perplexity.is_available():
            return jsonify({
                'error': 'Perplexity service not available',
                'message': 'Please configure PERPLEXITY_API_KEY'
            }), 503
        
        result = ai_service_manager.perplexity.deep_research(query)
        
        return jsonify({
            'success': True,
            'data': result.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error in AI research: {e}")
        return jsonify({'error': 'Research failed'}), 500

@app.route('/api/ai/report', methods=['POST'])
@limiter.limit("5 per hour")
def ai_report():
    """Generate comprehensive AI report"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        investigation_data = data.get('investigation_data', {})
        
        if not investigation_data:
            return jsonify({'error': 'Investigation data is required'}), 400
        
        logger.info("Generating AI report")
        
        results = ai_service_manager.generate_comprehensive_report(investigation_data)
        
        return jsonify({
            'success': True,
            'data': {
                'providers': list(results.keys()),
                'reports': {k: v.to_dict() for k, v in results.items()}
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating AI report: {e}")
        return jsonify({'error': 'Report generation failed'}), 500

@app.route('/api/ai/social-profile', methods=['POST'])
@limiter.limit("20 per hour")
def ai_social_profile():
    """Analyze social media profile with AI"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        platform = data.get('platform', '').strip()
        
        if not username:
            return jsonify({'error': 'Username is required'}), 400
        
        if not platform:
            return jsonify({'error': 'Platform is required'}), 400
        
        logger.info(f"AI social profile analysis: {username}@{platform}")
        
        if not ai_service_manager.kimi.is_available():
            return jsonify({
                'error': 'Kimi service not available',
                'message': 'Please configure KIMI_API_KEY'
            }), 503
        
        result = ai_service_manager.kimi.analyze_social_profile(username, platform)
        
        return jsonify({
            'success': True,
            'data': result.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error in AI social profile analysis: {e}")
        return jsonify({'error': 'Social profile analysis failed'}), 500

# Serve static files (for production)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    if path == '':
        path = 'index.html'
    
    static_file = os.path.join(app.static_folder, path)
    if os.path.exists(static_file):
        return send_from_directory(app.static_folder, path)
    
    # Fallback to index.html for SPA routing
    return send_from_directory(app.static_folder, 'index.html')

# Main entry point
if __name__ == '__main__':
    logger.info("Starting OSINT Phone Intelligence Platform")
    logger.info(f"Environment: {config.FLASK_ENV}")
    logger.info(f"Debug: {config.DEBUG}")
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
        threaded=True
    )
