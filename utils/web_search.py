import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time
from googlesearch import search

class WebSearch:
    def __init__(self):
        self.cache = {}
    
    def search_google(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search Google for news/articles related to query"""
        try:
            articles = []
            search_query = f"{query} news fact check"
            
            for url in search(search_query, num_results=num_results):
                articles.append({
                    "title": self._extract_title(url),
                    "url": url,
                    "source": self._extract_domain(url)
                })
            return articles
        except Exception as e:
            return []
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        import re
        match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        return match.group(1) if match else "Unknown"
    
    def _extract_title(self, url: str) -> str:
        """Extract title from URL"""
        # Simple extraction from URL path
        parts = url.split('/')
        last_part = parts[-1].replace('-', ' ').replace('_', ' ')
        return last_part[:100] if last_part else "Article"
    
    def verify_with_web(self, claim: str) -> Dict:
        """Verify a claim using web search"""
        articles = self.search_google(claim, num_results=5)
        
        # Score based on sources
        credible_sources = {
            'reuters.com', 'apnews.com', 'bbc.com', 'npr.org',
            'nytimes.com', 'washingtonpost.com', 'cnn.com',
            'theguardian.com', 'factcheck.org', 'snopes.com'
        }
        
        score = 0
        for article in articles:
            if any(cred in article['source'] for cred in credible_sources):
                score += 20
        
        # Determine verdict
        if score >= 60:
            verdict = "Likely True"
            confidence = score
        elif score >= 30:
            verdict = "Mixed/Unclear"
            confidence = score
        else:
            verdict = "Likely False/Unverified"
            confidence = 100 - score if score > 0 else 50
        
        return {
            "verdict": verdict,
            "confidence": min(confidence, 100),
            "articles_found": len(articles),
            "sources": [a['source'] for a in articles],
            "articles": articles
        }