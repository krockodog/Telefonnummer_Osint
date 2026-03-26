"""
Web Search Module
Performs web searches using various search engines
"""
import time
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a web search result"""
    title: str
    url: str
    snippet: str
    source: str
    position: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'url': self.url,
            'snippet': self.snippet,
            'source': self.source,
            'position': self.position
        }


@dataclass
class SearchQueryResult:
    """Result of a search query"""
    query: str
    results: List[SearchResult] = field(default_factory=list)
    total_results: int = 0
    search_time: float = 0.0
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'query': self.query,
            'results': [r.to_dict() for r in self.results],
            'total_results': self.total_results,
            'search_time': self.search_time,
            'error': self.error
        }


class WebSearcher:
    """Performs web searches"""
    
    def __init__(self, max_results: int = 10, timeout: int = 10):
        self.max_results = max_results
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_duckduckgo(self, query: str, max_results: Optional[int] = None) -> SearchQueryResult:
        """Search using DuckDuckGo"""
        start_time = time.time()
        max_results = max_results or self.max_results
        
        try:
            with DDGS() as ddgs:
                results = []
                for i, r in enumerate(ddgs.text(query, max_results=max_results)):
                    results.append(SearchResult(
                        title=r.get('title', ''),
                        url=r.get('href', ''),
                        snippet=r.get('body', ''),
                        source='DuckDuckGo',
                        position=i + 1
                    ))
                
                return SearchQueryResult(
                    query=query,
                    results=results,
                    total_results=len(results),
                    search_time=time.time() - start_time
                )
                
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return SearchQueryResult(
                query=query,
                error=str(e),
                search_time=time.time() - start_time
            )
    
    def search_phone_number(self, phone_number: str, formats: Dict[str, str]) -> Dict[str, SearchQueryResult]:
        """Search for a phone number in various formats"""
        results = {}
        
        # Define search queries
        queries = [
            (f'"{formats.get("e164", phone_number)}"', 'Exact E164'),
            (f'"{formats.get("local", phone_number)}" spam OR scam', 'Spam Reports'),
            (f'"{formats.get("local", phone_number)}" telefonnummer', 'German Phone'),
            (f'"{formats.get("international", phone_number)}"', 'International Format'),
        ]
        
        for query, label in queries:
            results[label] = self.search_duckduckgo(query, max_results=5)
            time.sleep(0.5)  # Rate limiting
        
        return results
    
    def search_username(self, username: str) -> Dict[str, SearchQueryResult]:
        """Search for a username across platforms"""
        results = {}
        
        queries = [
            (f'"{username}" profile', 'General Profile'),
            (f'"@{username}" social media', 'Social Media'),
            (f'"{username}" instagram OR facebook OR twitter', 'Platform Search'),
        ]
        
        for query, label in queries:
            results[label] = self.search_duckduckgo(query, max_results=5)
            time.sleep(0.5)
        
        return results
    
    def search_name(self, name: str) -> Dict[str, SearchQueryResult]:
        """Search for a person's name"""
        results = {}
        
        queries = [
            (f'"{name}"', 'Exact Name'),
            (f'"{name}" profile OR kontakt', 'Profile Search'),
            (f'"{name}" social media', 'Social Media'),
        ]
        
        for query, label in queries:
            results[label] = self.search_duckduckgo(query, max_results=5)
            time.sleep(0.5)
        
        return results
    
    def lookup_phone_sources(self, local_number: str) -> List[Dict[str, Any]]:
        """Get lookup URLs for phone number sources"""
        sources = [
            {
                'name': 'Tellows',
                'url': f'https://www.tellows.de/num/{local_number}',
                'type': 'spam_database',
                'description': 'Spam and scam reports'
            },
            {
                'name': 'DasÖrtliche',
                'url': f'https://www.dasoertliche.de/rueckwaertssuche/?ph={local_number}',
                'type': 'reverse_lookup',
                'description': 'German reverse phone lookup'
            },
            {
                'name': 'WerRuftAn',
                'url': f'https://www.wer-ruft-an.de/nummer/{local_number}',
                'type': 'community_reports',
                'description': 'Community phone reports'
            },
            {
                'name': 'TelSearch',
                'url': f'https://www.telsearch.de/?was={local_number}',
                'type': 'directory',
                'description': 'Swiss phone directory'
            },
            {
                'name': 'Klicktel',
                'url': f'https://www.klicktel.de/rueckwaertssuche/{local_number}',
                'type': 'reverse_lookup',
                'description': 'German phone directory'
            },
            {
                'name': 'TelefonABC',
                'url': f'https://www.telefonabc.de/nummer/{local_number}',
                'type': 'community_reports',
                'description': 'Phone number information'
            }
        ]
        
        # Check if sources are reachable
        for source in sources:
            try:
                response = self.session.head(
                    source['url'], 
                    timeout=5, 
                    allow_redirects=True
                )
                source['reachable'] = response.status_code < 400
                source['status_code'] = response.status_code
            except Exception as e:
                source['reachable'] = False
                source['error'] = str(e)
        
        return sources


# Global searcher instance
web_searcher = WebSearcher()
