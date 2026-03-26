"""
Social Media Search Module
Searches for profiles across various social media platforms
"""
import re
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)


@dataclass
class SocialProfile:
    """Represents a social media profile"""
    platform: str
    username: Optional[str] = None
    url: Optional[str] = None
    display_name: Optional[str] = None
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    followers: Optional[int] = None
    following: Optional[int] = None
    posts_count: Optional[int] = None
    location: Optional[str] = None
    verified: bool = False
    confidence: int = 0  # 0-100 confidence score
    found: bool = False
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'platform': self.platform,
            'username': self.username,
            'url': self.url,
            'display_name': self.display_name,
            'profile_picture': self.profile_picture,
            'bio': self.bio,
            'followers': self.followers,
            'following': self.following,
            'posts_count': self.posts_count,
            'location': self.location,
            'verified': self.verified,
            'confidence': self.confidence,
            'found': self.found,
            'error': self.error
        }


@dataclass
class SocialSearchResult:
    """Result of social media search"""
    query: str
    query_type: str  # 'phone', 'username', 'name'
    profiles: List[SocialProfile] = field(default_factory=list)
    total_found: int = 0
    search_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'query': self.query,
            'query_type': self.query_type,
            'profiles': [p.to_dict() for p in self.profiles],
            'total_found': self.total_found,
            'search_time': self.search_time
        }


class SocialMediaSearcher:
    """Searches for social media profiles"""
    
    # Platform configurations
    PLATFORMS = {
        'facebook': {
            'name': 'Facebook',
            'base_url': 'https://facebook.com',
            'search_url': 'https://facebook.com/search/people/?q={query}',
            'profile_url': 'https://facebook.com/{username}',
            'icon': 'facebook',
            'color': '#1877F2'
        },
        'instagram': {
            'name': 'Instagram',
            'base_url': 'https://instagram.com',
            'search_url': 'https://instagram.com/{username}',
            'profile_url': 'https://instagram.com/{username}',
            'icon': 'instagram',
            'color': '#E4405F'
        },
        'twitter': {
            'name': 'Twitter/X',
            'base_url': 'https://twitter.com',
            'search_url': 'https://twitter.com/search?q={query}',
            'profile_url': 'https://twitter.com/{username}',
            'icon': 'twitter',
            'color': '#000000'
        },
        'linkedin': {
            'name': 'LinkedIn',
            'base_url': 'https://linkedin.com',
            'search_url': 'https://linkedin.com/search/results/people/?keywords={query}',
            'profile_url': 'https://linkedin.com/in/{username}',
            'icon': 'linkedin',
            'color': '#0A66C2'
        },
        'tiktok': {
            'name': 'TikTok',
            'base_url': 'https://tiktok.com',
            'search_url': 'https://tiktok.com/search/user?q={query}',
            'profile_url': 'https://tiktok.com/@{username}',
            'icon': 'tiktok',
            'color': '#000000'
        },
        'telegram': {
            'name': 'Telegram',
            'base_url': 'https://t.me',
            'search_url': 'https://t.me/{username}',
            'profile_url': 'https://t.me/{username}',
            'icon': 'telegram',
            'color': '#0088CC'
        },
        'whatsapp': {
            'name': 'WhatsApp',
            'base_url': 'https://wa.me',
            'search_url': 'https://wa.me/{phone}',
            'profile_url': 'https://wa.me/{phone}',
            'icon': 'whatsapp',
            'color': '#25D366'
        },
        'youtube': {
            'name': 'YouTube',
            'base_url': 'https://youtube.com',
            'search_url': 'https://youtube.com/results?search_query={query}',
            'profile_url': 'https://youtube.com/@{username}',
            'icon': 'youtube',
            'color': '#FF0000'
        },
        'pinterest': {
            'name': 'Pinterest',
            'base_url': 'https://pinterest.com',
            'search_url': 'https://pinterest.com/search/users/?q={query}',
            'profile_url': 'https://pinterest.com/{username}',
            'icon': 'pinterest',
            'color': '#BD081C'
        },
        'snapchat': {
            'name': 'Snapchat',
            'base_url': 'https://snapchat.com',
            'search_url': 'https://snapchat.com/add/{username}',
            'profile_url': 'https://snapchat.com/add/{username}',
            'icon': 'snapchat',
            'color': '#FFFC00'
        }
    }
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_by_phone(self, phone_number: str, platforms: Optional[List[str]] = None) -> SocialSearchResult:
        """Search for profiles by phone number"""
        platforms = platforms or list(self.PLATFORMS.keys())
        profiles = []
        
        # Clean phone number
        clean_phone = re.sub(r'[^\d]', '', phone_number)
        if clean_phone.startswith('0'):
            clean_phone = clean_phone[1:]
        
        for platform_key in platforms:
            if platform_key not in self.PLATFORMS:
                continue
                
            platform = self.PLATFORMS[platform_key]
            profile = self._check_phone_platform(platform_key, platform, clean_phone)
            profiles.append(profile)
        
        return SocialSearchResult(
            query=phone_number,
            query_type='phone',
            profiles=profiles,
            total_found=sum(1 for p in profiles if p.found)
        )
    
    def search_by_username(self, username: str, platforms: Optional[List[str]] = None) -> SocialSearchResult:
        """Search for profiles by username"""
        platforms = platforms or list(self.PLATFORMS.keys())
        profiles = []
        
        # Clean username
        clean_username = username.lstrip('@')
        
        for platform_key in platforms:
            if platform_key not in self.PLATFORMS:
                continue
                
            platform = self.PLATFORMS[platform_key]
            profile = self._check_username_platform(platform_key, platform, clean_username)
            profiles.append(profile)
        
        return SocialSearchResult(
            query=username,
            query_type='username',
            profiles=profiles,
            total_found=sum(1 for p in profiles if p.found)
        )
    
    def search_by_name(self, name: str, platforms: Optional[List[str]] = None) -> SocialSearchResult:
        """Search for profiles by name"""
        platforms = platforms or list(self.PLATFORMS.keys())
        profiles = []
        
        for platform_key in platforms:
            if platform_key not in self.PLATFORMS:
                continue
                
            platform = self.PLATFORMS[platform_key]
            profile = self._check_name_platform(platform_key, platform, name)
            profiles.append(profile)
        
        return SocialSearchResult(
            query=name,
            query_type='name',
            profiles=profiles,
            total_found=sum(1 for p in profiles if p.found)
        )
    
    def _check_phone_platform(self, platform_key: str, platform: Dict, phone: str) -> SocialProfile:
        """Check if phone number exists on platform"""
        try:
            if platform_key == 'whatsapp':
                # WhatsApp direct link
                url = platform['profile_url'].format(phone=phone)
                return SocialProfile(
                    platform=platform['name'],
                    url=url,
                    username=phone,
                    confidence=80,
                    found=True
                )
            elif platform_key == 'telegram':
                # Telegram might have user by phone
                url = f"https://t.me/+{phone}"
                return SocialProfile(
                    platform=platform['name'],
                    url=url,
                    username=f"+{phone}",
                    confidence=40,
                    found=True
                )
            else:
                # For other platforms, provide search links
                search_url = platform['search_url'].format(query=quote(phone))
                return SocialProfile(
                    platform=platform['name'],
                    url=search_url,
                    confidence=20,
                    found=False,
                    error="Direct phone lookup not available, search link provided"
                )
                
        except Exception as e:
            logger.error(f"Error checking {platform_key}: {e}")
            return SocialProfile(
                platform=platform['name'],
                found=False,
                error=str(e)
            )
    
    def _check_username_platform(self, platform_key: str, platform: Dict, username: str) -> SocialProfile:
        """Check if username exists on platform"""
        try:
            url = platform['profile_url'].format(username=username)
            
            # Try to access the profile
            try:
                response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
                exists = response.status_code == 200
            except:
                exists = False
            
            return SocialProfile(
                platform=platform['name'],
                username=username,
                url=url,
                confidence=70 if exists else 30,
                found=exists
            )
            
        except Exception as e:
            logger.error(f"Error checking {platform_key}: {e}")
            return SocialProfile(
                platform=platform['name'],
                found=False,
                error=str(e)
            )
    
    def _check_name_platform(self, platform_key: str, platform: Dict, name: str) -> SocialProfile:
        """Check name on platform (returns search link)"""
        try:
            search_url = platform['search_url'].format(query=quote(name))
            
            return SocialProfile(
                platform=platform['name'],
                display_name=name,
                url=search_url,
                confidence=10,
                found=False,
                error="Name search - manual verification required"
            )
            
        except Exception as e:
            logger.error(f"Error checking {platform_key}: {e}")
            return SocialProfile(
                platform=platform['name'],
                found=False,
                error=str(e)
            )
    
    def get_platform_info(self, platform_key: str) -> Optional[Dict]:
        """Get information about a platform"""
        return self.PLATFORMS.get(platform_key)
    
    def get_all_platforms(self) -> Dict[str, Dict]:
        """Get all platform information"""
        return self.PLATFORMS.copy()


# Global searcher instance
social_searcher = SocialMediaSearcher()
