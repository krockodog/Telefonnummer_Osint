"""
OSINT Phone Intelligence Platform - Configuration
"""
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Import crypto utilities
from src.crypto_utils import decrypt_key

load_dotenv()

@dataclass
class Config:
    """Application configuration"""
    
    # Flask Settings
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV: str = os.getenv('FLASK_ENV', 'production')
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Server Settings
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', 5000))
    
    # Security
    RATE_LIMIT: str = os.getenv('RATE_LIMIT', '100 per hour')
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB max file size
    
    # CORS Settings - Allow all origins for local development
    CORS_ORIGINS: List[str] = field(default_factory=lambda: ["*"])
    
    # Cache Settings
    CACHE_TYPE: str = os.getenv('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT: int = int(os.getenv('CACHE_TIMEOUT', 3600))
    
    # Database
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///osint.db')
    
    # AI Service API Keys (decrypted from environment)
    # Keys can be stored as plain text or encrypted with ENC: prefix
    KIMI_API_KEY: Optional[str] = field(init=False)
    PERPLEXITY_API_KEY: Optional[str] = field(init=False)
    GEMINI_API_KEY: Optional[str] = field(init=False)
    
    # Legacy API Keys (optional)
    OPENAI_API_KEY: Optional[str] = field(init=False)
    GOOGLE_CSE_API_KEY: Optional[str] = field(init=False)
    GOOGLE_CSE_CX: Optional[str] = field(init=False)
    
    # OSINT Settings
    OSINT_SETTINGS: Dict = field(default_factory=lambda: {
        'phone_validation': True,
        'social_media_search': True,
        'web_search_enabled': True,
        'max_search_results': 10,
        'timeout': 10,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Social Media Platforms
    SOCIAL_PLATFORMS: List[str] = field(default_factory=lambda: [
        'facebook', 'instagram', 'twitter', 'linkedin', 
        'tiktok', 'telegram', 'whatsapp'
    ])
    
    # Data Sources
    PHONE_LOOKUP_SOURCES: List[Dict] = field(default_factory=lambda: [
        {'name': 'Tellows', 'url': 'https://www.tellows.de/num/{number}'},
        {'name': 'DasOertliche', 'url': 'https://www.dasoertliche.de/rueckwaertssuche/?ph={number}'},
        {'name': 'WerRuftAn', 'url': 'https://www.wer-ruft-an.de/nummer/{number}'},
        {'name': 'TelSearch', 'url': 'https://www.telsearch.de/?was={number}'},
    ])
    
    # Compliance
    DATA_RETENTION_DAYS: int = int(os.getenv('DATA_RETENTION_DAYS', 7))
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    def __post_init__(self):
        """Decrypt API keys after initialization"""
        # Decrypt AI service API keys
        self.KIMI_API_KEY = self._get_decrypted('KIMI_API_KEY')
        self.PERPLEXITY_API_KEY = self._get_decrypted('PERPLEXITY_API_KEY')
        self.GEMINI_API_KEY = self._get_decrypted('GEMINI_API_KEY')
        
        # Legacy API keys (also support encryption)
        self.OPENAI_API_KEY = self._get_decrypted('OPENAI_API_KEY')
        self.GOOGLE_CSE_API_KEY = self._get_decrypted('GOOGLE_CSE_API_KEY')
        self.GOOGLE_CSE_CX = os.getenv('GOOGLE_CSE_CX')  # Usually not sensitive
    
    def _get_decrypted(self, key_name: str) -> Optional[str]:
        """Get and decrypt an environment variable"""
        value = os.getenv(key_name)
        if value:
            # decrypt_key handles both encrypted (ENC:) and plain text values
            return decrypt_key(value)
        return None
    
    @classmethod
    def from_env(cls):
        """Create config from environment variables"""
        return cls()
    
    def get_available_ai_services(self) -> List[str]:
        """Get list of configured AI services"""
        services = []
        if self.KIMI_API_KEY:
            services.append('kimi')
        if self.PERPLEXITY_API_KEY:
            services.append('perplexity')
        if self.GEMINI_API_KEY:
            services.append('gemini')
        return services

# Global config instance
config = Config.from_env()
