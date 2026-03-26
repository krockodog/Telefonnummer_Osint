"""
Risk Analysis Module
Analyzes the risk level associated with phone numbers
"""
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(Enum):
    """Risk level enumeration"""
    UNKNOWN = 'unknown'
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


@dataclass
class RiskFactor:
    """Individual risk factor"""
    name: str
    score: int  # 0-100
    description: str
    category: str


@dataclass
class RiskAnalysis:
    """Complete risk analysis result"""
    score: int  # 0-100 overall score
    level: str
    factors: List[RiskFactor] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'score': self.score,
            'level': self.level,
            'factors': [
                {
                    'name': f.name,
                    'score': f.score,
                    'description': f.description,
                    'category': f.category
                } for f in self.factors
            ],
            'recommendations': self.recommendations
        }


class RiskAnalyzer:
    """Analyzes risk for phone numbers"""
    
    # Spam-related keywords
    SPAM_KEYWORDS = [
        'spam', 'scam', 'betrug', 'abzocke', 'werbung',
        'telemarketing', 'unwanted', 'nuisance', 'fraud',
        'phishing', 'fake', 'unseriös', 'ping-anruf'
    ]
    
    # Premium rate prefixes (Germany)
    PREMIUM_PREFIXES = ['0190', '0180', '0900', '0137', '0138']
    
    # Suspicious patterns
    SUSPICIOUS_PATTERNS = [
        r'(\d)\1{4,}',  # Repeated digits
        r'123456|654321',  # Sequential patterns
        r'000000|111111|222222',  # All same digits
    ]
    
    def __init__(self):
        pass
    
    def analyze(self, 
                phone_info: Dict[str, Any],
                search_results: Dict[str, Any],
                social_results: Dict[str, Any]) -> RiskAnalysis:
        """Perform comprehensive risk analysis"""
        
        factors = []
        total_score = 0
        
        # Factor 1: Number type
        number_type_factor = self._analyze_number_type(phone_info)
        factors.append(number_type_factor)
        total_score += number_type_factor.score * 0.15
        
        # Factor 2: Search results sentiment
        search_factor = self._analyze_search_results(search_results)
        factors.append(search_factor)
        total_score += search_factor.score * 0.35
        
        # Factor 3: Number pattern
        pattern_factor = self._analyze_number_pattern(phone_info)
        factors.append(pattern_factor)
        total_score += pattern_factor.score * 0.20
        
        # Factor 4: Social media presence
        social_factor = self._analyze_social_presence(social_results)
        factors.append(social_factor)
        total_score += social_factor.score * 0.15
        
        # Factor 5: Carrier reputation
        carrier_factor = self._analyze_carrier(phone_info)
        factors.append(carrier_factor)
        total_score += carrier_factor.score * 0.15
        
        # Calculate final score
        final_score = min(100, max(0, int(total_score)))
        level = self._score_to_level(final_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(final_score, factors)
        
        return RiskAnalysis(
            score=final_score,
            level=level,
            factors=factors,
            recommendations=recommendations
        )
    
    def _analyze_number_type(self, phone_info: Dict[str, Any]) -> RiskFactor:
        """Analyze based on number type"""
        number_type = phone_info.get('number_type', '').lower()
        
        if 'premium' in number_type:
            return RiskFactor(
                name='Number Type',
                score=80,
                description='Premium rate number - high cost risk',
                category='number'
            )
        elif 'voip' in number_type:
            return RiskFactor(
                name='Number Type',
                score=50,
                description='VoIP number - harder to trace',
                category='number'
            )
        elif 'mobile' in number_type:
            return RiskFactor(
                name='Number Type',
                score=20,
                description='Mobile number - standard risk',
                category='number'
            )
        else:
            return RiskFactor(
                name='Number Type',
                score=30,
                description='Fixed line number - lower risk',
                category='number'
            )
    
    def _analyze_search_results(self, search_results: Dict[str, Any]) -> RiskFactor:
        """Analyze search results for risk indicators"""
        if not search_results or 'error' in search_results:
            return RiskFactor(
                name='Search Results',
                score=50,
                description='No search data available',
                category='reputation'
            )
        
        # Check for spam keywords in results
        spam_mentions = 0
        all_text = str(search_results).lower()
        
        for keyword in self.SPAM_KEYWORDS:
            spam_mentions += all_text.count(keyword)
        
        if spam_mentions > 5:
            score = 90
            desc = f'Multiple spam reports found ({spam_mentions} mentions)'
        elif spam_mentions > 2:
            score = 70
            desc = f'Some spam reports found ({spam_mentions} mentions)'
        elif spam_mentions > 0:
            score = 50
            desc = f'Few spam mentions ({spam_mentions})'
        else:
            score = 10
            desc = 'No negative reports found'
        
        return RiskFactor(
            name='Search Results',
            score=score,
            description=desc,
            category='reputation'
        )
    
    def _analyze_number_pattern(self, phone_info: Dict[str, Any]) -> RiskFactor:
        """Analyze number for suspicious patterns"""
        number = phone_info.get('e164_format', '')
        
        # Check for premium prefixes
        for prefix in self.PREMIUM_PREFIXES:
            if prefix in number:
                return RiskFactor(
                    name='Number Pattern',
                    score=85,
                    description=f'Premium rate prefix detected ({prefix})',
                    category='pattern'
                )
        
        # Check for suspicious patterns
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, number):
                return RiskFactor(
                    name='Number Pattern',
                    score=60,
                    description='Suspicious number pattern detected',
                    category='pattern'
                )
        
        return RiskFactor(
            name='Number Pattern',
            score=10,
            description='Normal number pattern',
            category='pattern'
        )
    
    def _analyze_social_presence(self, social_results: Dict[str, Any]) -> RiskFactor:
        """Analyze social media presence"""
        if not social_results:
            return RiskFactor(
                name='Social Presence',
                score=50,
                description='No social media data',
                category='social'
            )
        
        profiles = social_results.get('profiles', [])
        found_count = sum(1 for p in profiles if p.get('found', False))
        
        if found_count > 3:
            return RiskFactor(
                name='Social Presence',
                score=20,
                description=f'Active on {found_count} platforms - legitimate presence',
                category='social'
            )
        elif found_count > 0:
            return RiskFactor(
                name='Social Presence',
                score=40,
                description=f'Limited social presence ({found_count} platforms)',
                category='social'
            )
        else:
            return RiskFactor(
                name='Social Presence',
                score=60,
                description='No social media presence found',
                category='social'
            )
    
    def _analyze_carrier(self, phone_info: Dict[str, Any]) -> RiskFactor:
        """Analyze carrier reputation"""
        carrier = phone_info.get('carrier_name', '').lower()
        
        # Major carriers are generally safer
        major_carriers = ['telekom', 'vodafone', 'o2', 'e-plus', 'congstar']
        
        if any(c in carrier for c in major_carriers):
            return RiskFactor(
                name='Carrier',
                score=10,
                description=f'Reputable carrier: {carrier}',
                category='carrier'
            )
        elif carrier:
            return RiskFactor(
                name='Carrier',
                score=40,
                description=f'Lesser known carrier: {carrier}',
                category='carrier'
            )
        else:
            return RiskFactor(
                name='Carrier',
                score=50,
                description='Carrier information unavailable',
                category='carrier'
            )
    
    def _score_to_level(self, score: int) -> str:
        """Convert score to risk level"""
        if score >= 80:
            return RiskLevel.CRITICAL.value
        elif score >= 60:
            return RiskLevel.HIGH.value
        elif score >= 40:
            return RiskLevel.MEDIUM.value
        elif score >= 20:
            return RiskLevel.LOW.value
        else:
            return RiskLevel.UNKNOWN.value
    
    def _generate_recommendations(self, score: int, factors: List[RiskFactor]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if score >= 80:
            recommendations.append('⚠️ HIGH RISK: Do not answer calls from this number')
            recommendations.append('Block this number immediately')
            recommendations.append('Report to authorities if harassed')
        elif score >= 60:
            recommendations.append('⚡ ELEVATED RISK: Exercise caution')
            recommendations.append('Verify identity before sharing information')
            recommendations.append('Consider blocking if unwanted calls persist')
        elif score >= 40:
            recommendations.append('ℹ️ MODERATE RISK: Be cautious')
            recommendations.append('Research further before trusting')
        else:
            recommendations.append('✅ LOW RISK: Appears legitimate')
            recommendations.append('Standard precautions recommended')
        
        # Add specific recommendations based on factors
        for factor in factors:
            if factor.name == 'Number Type' and factor.score > 60:
                recommendations.append(f'Note: {factor.description}')
        
        return recommendations


# Global analyzer instance
risk_analyzer = RiskAnalyzer()
