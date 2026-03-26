"""
AI Services Module
Integration with Kimi, Perplexity, and Gemini APIs for enhanced OSINT analysis
"""
import os
import json
import logging
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """AI service providers"""
    KIMI = "kimi"
    PERPLEXITY = "perplexity"
    GEMINI = "gemini"


@dataclass
class AIAnalysisResult:
    """Result from AI analysis"""
    provider: str
    query: str
    response: str
    sources: List[Dict[str, str]] = field(default_factory=list)
    confidence: float = 0.0
    tokens_used: Optional[int] = None
    processing_time: float = 0.0
    error: Optional[str] = None
    success: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'provider': self.provider,
            'query': self.query,
            'response': self.response,
            'sources': self.sources,
            'confidence': self.confidence,
            'tokens_used': self.tokens_used,
            'processing_time': self.processing_time,
            'error': self.error,
            'success': self.success
        }


class KimiService:
    """Kimi AI (Moonshot AI) integration"""
    
    API_BASE_URL = "https://api.moonshot.cn/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        # Import config here to avoid circular imports
        from config import config
        self.api_key = api_key or config.KIMI_API_KEY
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            })
    
    def is_available(self) -> bool:
        """Check if API key is configured"""
        return bool(self.api_key)
    
    def analyze_phone(self, phone_number: str, context: Dict[str, Any]) -> AIAnalysisResult:
        """Analyze phone number with Kimi"""
        import time
        start_time = time.time()
        
        if not self.is_available():
            return AIAnalysisResult(
                provider="kimi",
                query=phone_number,
                error="Kimi API key not configured",
                processing_time=time.time() - start_time
            )
        
        try:
            # Build prompt with context
            prompt = self._build_phone_prompt(phone_number, context)
            
            response = self.session.post(
                f"{self.API_BASE_URL}/chat/completions",
                json={
                    "model": "moonshot-v1-128k",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an OSINT expert analyzing phone numbers. Provide concise, factual analysis."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000
                },
                timeout=60
            )
            
            response.raise_for_status()
            data = response.json()
            
            content = data['choices'][0]['message']['content']
            tokens = data.get('usage', {}).get('total_tokens')
            
            return AIAnalysisResult(
                provider="kimi",
                query=phone_number,
                response=content,
                confidence=0.85,
                tokens_used=tokens,
                processing_time=time.time() - start_time,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Kimi analysis error: {e}")
            return AIAnalysisResult(
                provider="kimi",
                query=phone_number,
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    def analyze_social_profile(self, username: str, platform: str) -> AIAnalysisResult:
        """Analyze social media profile"""
        import time
        start_time = time.time()
        
        if not self.is_available():
            return AIAnalysisResult(
                provider="kimi",
                query=f"{username}@{platform}",
                error="Kimi API key not configured",
                processing_time=time.time() - start_time
            )
        
        try:
            prompt = f"""Analyze this social media profile for OSINT purposes:
            
Platform: {platform}
Username: {username}

Provide:
1. Potential real name indicators
2. Associated interests/topics
3. Risk assessment (low/medium/high)
4. OSINT investigation suggestions

Be concise and factual."""

            response = self.session.post(
                f"{self.API_BASE_URL}/chat/completions",
                json={
                    "model": "moonshot-v1-32k",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an OSINT expert analyzing social media profiles."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1500
                },
                timeout=60
            )
            
            response.raise_for_status()
            data = response.json()
            
            return AIAnalysisResult(
                provider="kimi",
                query=f"{username}@{platform}",
                response=data['choices'][0]['message']['content'],
                confidence=0.80,
                tokens_used=data.get('usage', {}).get('total_tokens'),
                processing_time=time.time() - start_time,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Kimi social analysis error: {e}")
            return AIAnalysisResult(
                provider="kimi",
                query=f"{username}@{platform}",
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    def _build_phone_prompt(self, phone_number: str, context: Dict[str, Any]) -> str:
        """Build analysis prompt for phone number"""
        phone_info = context.get('phone_analysis', {})
        risk_info = context.get('risk_analysis', {})
        
        prompt = f"""Analyze this phone number for OSINT investigation:

Phone Number: {phone_number}

Technical Information:
- Carrier: {phone_info.get('carrier_name', 'Unknown')}
- Location: {phone_info.get('location', 'Unknown')}
- Country: {phone_info.get('country_name', 'Unknown')}
- Type: {phone_info.get('number_type', 'Unknown')}

Risk Assessment: {risk_info.get('level', 'Unknown')} ({risk_info.get('score', 0)}/100)

Provide:
1. Summary of findings
2. Potential risks and red flags
3. Investigation recommendations
4. Additional search suggestions

Be concise and factual."""
        
        return prompt


class PerplexityService:
    """Perplexity AI integration with web search"""
    
    API_BASE_URL = "https://api.perplexity.ai"
    
    def __init__(self, api_key: Optional[str] = None):
        # Import config here to avoid circular imports
        from config import config
        self.api_key = api_key or config.PERPLEXITY_API_KEY
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            })
    
    def is_available(self) -> bool:
        """Check if API key is configured"""
        return bool(self.api_key)
    
    def search_and_analyze(self, query: str, search_type: str = "phone") -> AIAnalysisResult:
        """Search and analyze with Perplexity's web search"""
        import time
        start_time = time.time()
        
        if not self.is_available():
            return AIAnalysisResult(
                provider="perplexity",
                query=query,
                error="Perplexity API key not configured",
                processing_time=time.time() - start_time
            )
        
        try:
            # Build search query
            if search_type == "phone":
                search_query = f"phone number {query} spam scam reports reputation"
            elif search_type == "username":
                search_query = f"@{query} social media profile information"
            else:
                search_query = query
            
            response = self.session.post(
                f"{self.API_BASE_URL}/chat/completions",
                json={
                    "model": "llama-3.1-sonar-large-128k-online",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an OSINT researcher. Search the web and provide factual information with citations."
                        },
                        {
                            "role": "user",
                            "content": search_query
                        }
                    ],
                    "temperature": 0.2,
                    "max_tokens": 2000,
                    "return_citations": True,
                    "return_images": False
                },
                timeout=60
            )
            
            response.raise_for_status()
            data = response.json()
            
            content = data['choices'][0]['message']['content']
            citations = data.get('citations', [])
            
            # Format sources
            sources = []
            for i, citation in enumerate(citations[:5], 1):
                sources.append({
                    'title': f'Source {i}',
                    'url': citation if isinstance(citation, str) else citation.get('url', ''),
                    'snippet': ''
                })
            
            return AIAnalysisResult(
                provider="perplexity",
                query=query,
                response=content,
                sources=sources,
                confidence=0.90,
                tokens_used=data.get('usage', {}).get('total_tokens'),
                processing_time=time.time() - start_time,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Perplexity search error: {e}")
            return AIAnalysisResult(
                provider="perplexity",
                query=query,
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    def deep_research(self, query: str) -> AIAnalysisResult:
        """Perform deep research on a topic"""
        import time
        start_time = time.time()
        
        if not self.is_available():
            return AIAnalysisResult(
                provider="perplexity",
                query=query,
                error="Perplexity API key not configured",
                processing_time=time.time() - start_time
            )
        
        try:
            response = self.session.post(
                f"{self.API_BASE_URL}/chat/completions",
                json={
                    "model": "llama-3.1-sonar-large-128k-online",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert OSINT researcher. Provide comprehensive analysis with citations."
                        },
                        {
                            "role": "user",
                            "content": f"Deep OSINT research: {query}\n\nProvide comprehensive findings with sources."
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 4000,
                    "return_citations": True
                },
                timeout=90
            )
            
            response.raise_for_status()
            data = response.json()
            
            citations = data.get('citations', [])
            sources = [{'title': f'Source {i+1}', 'url': c if isinstance(c, str) else c.get('url', '')} 
                      for i, c in enumerate(citations[:10])]
            
            return AIAnalysisResult(
                provider="perplexity",
                query=query,
                response=data['choices'][0]['message']['content'],
                sources=sources,
                confidence=0.92,
                tokens_used=data.get('usage', {}).get('total_tokens'),
                processing_time=time.time() - start_time,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Perplexity research error: {e}")
            return AIAnalysisResult(
                provider="perplexity",
                query=query,
                error=str(e),
                processing_time=time.time() - start_time
            )


class GeminiService:
    """Google Gemini AI integration"""
    
    API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    
    def __init__(self, api_key: Optional[str] = None):
        # Import config here to avoid circular imports
        from config import config
        self.api_key = api_key or config.GEMINI_API_KEY
    
    def is_available(self) -> bool:
        """Check if API key is configured"""
        return bool(self.api_key)
    
    def analyze_phone(self, phone_number: str, context: Dict[str, Any]) -> AIAnalysisResult:
        """Analyze phone number with Gemini"""
        import time
        start_time = time.time()
        
        if not self.is_available():
            return AIAnalysisResult(
                provider="gemini",
                query=phone_number,
                error="Gemini API key not configured",
                processing_time=time.time() - start_time
            )
        
        try:
            prompt = self._build_phone_prompt(phone_number, context)
            
            response = requests.post(
                f"{self.API_BASE_URL}/models/gemini-1.5-flash:generateContent",
                params={"key": self.api_key},
                json={
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": prompt}]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 2000,
                        "topP": 0.8,
                        "topK": 40
                    }
                },
                timeout=60
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract text from response
            candidates = data.get('candidates', [])
            if candidates:
                content = candidates[0].get('content', {})
                parts = content.get('parts', [])
                text = ' '.join(part.get('text', '') for part in parts)
            else:
                text = "No response generated"
            
            # Get token usage if available
            usage = data.get('usageMetadata', {})
            tokens = usage.get('totalTokenCount')
            
            return AIAnalysisResult(
                provider="gemini",
                query=phone_number,
                response=text,
                confidence=0.82,
                tokens_used=tokens,
                processing_time=time.time() - start_time,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Gemini analysis error: {e}")
            return AIAnalysisResult(
                provider="gemini",
                query=phone_number,
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    def generate_investigation_report(self, investigation_data: Dict[str, Any]) -> AIAnalysisResult:
        """Generate comprehensive investigation report"""
        import time
        start_time = time.time()
        
        if not self.is_available():
            return AIAnalysisResult(
                provider="gemini",
                query="investigation_report",
                error="Gemini API key not configured",
                processing_time=time.time() - start_time
            )
        
        try:
            # Build comprehensive prompt
            query = investigation_data.get('query', 'Unknown')
            phone_analysis = investigation_data.get('phone_analysis', {})
            risk_analysis = investigation_data.get('risk_analysis', {})
            
            prompt = f"""Generate a comprehensive OSINT investigation report:

TARGET: {query}

PHONE ANALYSIS:
- Valid: {phone_analysis.get('valid', False)}
- Carrier: {phone_analysis.get('carrier_name', 'Unknown')}
- Location: {phone_analysis.get('location', 'Unknown')}
- Country: {phone_analysis.get('country_name', 'Unknown')}
- Type: {phone_analysis.get('number_type', 'Unknown')}

RISK ASSESSMENT:
- Level: {risk_analysis.get('level', 'Unknown')}
- Score: {risk_analysis.get('score', 0)}/100

Provide:
1. Executive Summary
2. Technical Analysis
3. Risk Assessment Details
4. Recommendations
5. Next Steps for Investigation

Format as a professional report."""

            response = requests.post(
                f"{self.API_BASE_URL}/models/gemini-1.5-pro:generateContent",
                params={"key": self.api_key},
                json={
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": prompt}]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.2,
                        "maxOutputTokens": 4000,
                        "topP": 0.8
                    }
                },
                timeout=90
            )
            
            response.raise_for_status()
            data = response.json()
            
            candidates = data.get('candidates', [])
            if candidates:
                content = candidates[0].get('content', {})
                parts = content.get('parts', [])
                text = ' '.join(part.get('text', '') for part in parts)
            else:
                text = "No report generated"
            
            usage = data.get('usageMetadata', {})
            
            return AIAnalysisResult(
                provider="gemini",
                query="investigation_report",
                response=text,
                confidence=0.85,
                tokens_used=usage.get('totalTokenCount'),
                processing_time=time.time() - start_time,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Gemini report error: {e}")
            return AIAnalysisResult(
                provider="gemini",
                query="investigation_report",
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    def _build_phone_prompt(self, phone_number: str, context: Dict[str, Any]) -> str:
        """Build analysis prompt for phone number"""
        phone_info = context.get('phone_analysis', {})
        risk_info = context.get('risk_analysis', {})
        social_info = context.get('social_media', {})
        
        prompt = f"""Analyze this phone number for OSINT investigation:

Phone Number: {phone_number}

Technical Information:
- Carrier: {phone_info.get('carrier_name', 'Unknown')}
- Location: {phone_info.get('location', 'Unknown')}
- Country: {phone_info.get('country_name', 'Unknown')}
- Type: {phone_info.get('number_type', 'Unknown')}
- Formats: E.164: {phone_info.get('e164_format', 'N/A')}

Risk Assessment: {risk_info.get('level', 'Unknown')} ({risk_info.get('score', 0)}/100)

Social Media Profiles Found: {social_info.get('total_found', 0)}

Provide:
1. Summary of findings
2. Risk analysis
3. Investigation recommendations
4. Potential associations

Be concise and factual."""
        
        return prompt


class AIServiceManager:
    """Manager for all AI services"""
    
    def __init__(self):
        self.kimi = KimiService()
        self.perplexity = PerplexityService()
        self.gemini = GeminiService()
    
    def get_available_services(self) -> List[str]:
        """Get list of available AI services"""
        available = []
        if self.kimi.is_available():
            available.append("kimi")
        if self.perplexity.is_available():
            available.append("perplexity")
        if self.gemini.is_available():
            available.append("gemini")
        return available
    
    def analyze_phone_all(self, phone_number: str, context: Dict[str, Any]) -> Dict[str, AIAnalysisResult]:
        """Analyze phone number with all available AI services"""
        results = {}
        
        if self.kimi.is_available():
            results['kimi'] = self.kimi.analyze_phone(phone_number, context)
        
        if self.perplexity.is_available():
            results['perplexity'] = self.perplexity.search_and_analyze(phone_number, "phone")
        
        if self.gemini.is_available():
            results['gemini'] = self.gemini.analyze_phone(phone_number, context)
        
        return results
    
    def generate_comprehensive_report(self, investigation_data: Dict[str, Any]) -> Dict[str, AIAnalysisResult]:
        """Generate comprehensive report using all available services"""
        results = {}
        query = investigation_data.get('query', 'Unknown')
        
        # Perplexity for web research
        if self.perplexity.is_available():
            results['perplexity_research'] = self.perplexity.deep_research(
                f"OSINT investigation phone number {query}"
            )
        
        # Gemini for comprehensive report
        if self.gemini.is_available():
            results['gemini_report'] = self.gemini.generate_investigation_report(investigation_data)
        
        # Kimi for additional analysis
        if self.kimi.is_available():
            results['kimi_analysis'] = self.kimi.analyze_phone(query, investigation_data)
        
        return results


# Global AI service manager
ai_service_manager = AIServiceManager()
