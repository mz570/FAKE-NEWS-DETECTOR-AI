"""
Real Web Search using SerpApi (100 free searches/month)
"""

import requests
from typing import List, Dict
import time
import streamlit as st

class RealWebSearch:
    def __init__(self, api_key=None):
        """Initialize with SerpApi key"""
        # Try to get API key from various sources
        self.api_key = api_key or st.secrets.get("SERPAPI_KEY", None)
        
        if not self.api_key:
            # Try to read from file
            try:
                with open('serpapi_key.txt', 'r') as f:
                    self.api_key = f.read().strip()
            except:
                pass
        
        self.has_api_key = self.api_key is not None
        self.search_cache = {}
    
    def search_google_news(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search Google News for real articles about the claim
        """
        if not self.has_api_key:
            return self._mock_search(query, num_results)
        
        # Check cache first
        cache_key = f"{query}_{num_results}"
        if cache_key in self.search_cache:
            return self.search_cache[cache_key]
        
        try:
            # Real API call to SerpApi
            params = {
                "q": f"{query} news fact check",
                "api_key": self.api_key,
                "engine": "google_news",
                "gl": "us",
                "hl": "en",
                "num": num_results
            }
            
            response = requests.get("https://serpapi.com/search", params=params)
            data = response.json()
            
            articles = []
            
            # Extract news results
            if "news_results" in data:
                for item in data["news_results"][:num_results]:
                    articles.append({
                        "title": item.get("title", "No title"),
                        "url": item.get("link", ""),
                        "source": item.get("source", {}).get("name", "Unknown"),
                        "date": item.get("date", ""),
                        "snippet": item.get("snippet", "")
                    })
            
            # Cache results
            self.search_cache[cache_key] = articles
            return articles
            
        except Exception as e:
            st.error(f"Search API error: {str(e)}")
            return self._mock_search(query, num_results)
    
    def _mock_search(self, query: str, num_results: int) -> List[Dict]:
        """
        Fallback mock search when no API key (for demo)
        """
        # Analyze query for credibility indicators
        query_lower = query.lower()
        
        fake_indicators = ['miracle', 'secret', 'shocking', 'conspiracy', 
                          'you won\'t believe', 'cure', 'hidden', 'truth']
        true_indicators = ['study', 'research', 'scientists', 'official', 
                          'government', 'report', 'data']
        
        fake_score = sum(1 for i in fake_indicators if i in query_lower)
        true_score = sum(1 for i in true_indicators if i in query_lower)
        
        if fake_score > true_score:
            # Return warning sources
            return [
                {
                    "title": f"⚠️ Fact Check: {query[:60]}...",
                    "url": "https://www.snopes.com/fact-check",
                    "source": "Snopes (Fact Check)",
                    "date": "Recent",
                    "snippet": "This claim has been fact-checked and found to be misleading..."
                },
                {
                    "title": f"False Information Alert: {query[:50]}",
                    "url": "https://www.factcheck.org",
                    "source": "FactCheck.org",
                    "date": "Recent", 
                    "snippet": "No credible evidence supports this claim..."
                }
            ]
        else:
            # Return credible sources
            return [
                {
                    "title": f"Reuters: {query[:60]}",
                    "url": "https://www.reuters.com",
                    "source": "Reuters",
                    "date": "Recent",
                    "snippet": "Official sources confirm the accuracy of this information..."
                },
                {
                    "title": f"BBC News: {query[:50]}",
                    "url": "https://www.bbc.com",
                    "source": "BBC News",
                    "date": "Recent",
                    "snippet": "This has been verified by multiple independent sources..."
                }
            ]
    
    def verify_claim(self, claim: str) -> Dict:
        """
        Verify a claim using real web search
        """
        # Search for the claim
        articles = self.search_google_news(claim, num_results=5)
        
        # Define credible sources
        credible_sources = {
            'reuters.com', 'apnews.com', 'bbc.com', 'npr.org',
            'nytimes.com', 'washingtonpost.com', 'cnn.com',
            'theguardian.com', 'factcheck.org', 'snopes.com',
            'politifact.com', 'abcnews.go.com', 'nbcnews.com'
        }
        
        # Score the results
        score = 0
        credible_count = 0
        
        for article in articles:
            source = article['source'].lower()
            
            # Check if source is credible
            if any(cred in source for cred in credible_sources):
                score += 25
                credible_count += 1
            elif 'factcheck' in source or 'snopes' in source:
                score += 30  # Fact-checking sites get higher score
        
        # Normalize score
        max_score = len(articles) * 25
        if max_score > 0:
            confidence = (score / max_score) * 100
        else:
            confidence = 0
        
        # Determine verdict
        if confidence >= 60:
            verdict = "Likely True"
            explanation = f"Found {credible_count} credible sources supporting this claim."
            color = "green"
        elif confidence >= 30:
            verdict = "Mixed Evidence"
            explanation = "Found both credible and questionable sources. More verification needed."
            color = "orange"
        else:
            verdict = "Likely False / Unverified"
            explanation = "Could not find sufficient credible sources to verify this claim."
            color = "red"
        
        return {
            "claim": claim,
            "verdict": verdict,
            "confidence": confidence,
            "color": color,
            "articles_found": len(articles),
            "credible_sources": credible_count,
            "articles": articles,
            "explanation": explanation,
            "has_api_key": self.has_api_key
        }

# Initialize search
def init_web_search():
    """Initialize web search with API key"""
    # You can set your key here directly (temporary)
    # Get free key from https://serpapi.com/
    YOUR_API_KEY = "2735a594231069a3c483d695d016790955652a3c5bbc49ad35564ff84575c82a"  # <-- PASTE YOUR API KEY HERE
    
    if YOUR_API_KEY:
        return RealWebSearch(api_key=YOUR_API_KEY)
    else:
        # Try to read from file
        try:
            with open('serpapi_key.txt', 'r') as f:
                key = f.read().strip()
                if key:
                    return RealWebSearch(api_key=key)
        except:
            pass
        
        # No API key - will use mock mode
        st.warning("⚠️ No SerpApi key found. Using mock search mode. Get free key at serpapi.com")
        return RealWebSearch(api_key=None)