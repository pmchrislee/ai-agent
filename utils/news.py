"""
News service for fetching real news headlines.

This module provides functionality to fetch current news headlines
from various news sources.
"""

import logging
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class NewsService:
    """Service for fetching news headlines from various sources."""

    def __init__(self):
        """Initialize the news service."""
        import os
        # Using NewsAPI (free tier available at newsapi.org)
        # Fallback to RSS feeds if API key not available
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2/top-headlines"
        self.search_url = "https://newsapi.org/v2/everything"
        # Local news RSS feeds by region
        self.local_rss_feeds = {
            "new york": [
                "https://www.ny1.com/nyc/all-boroughs/rss.xml",
                "https://www.nydailynews.com/arc/outboundfeeds/rss/",
                "https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/nyregion/rss.xml",
            ],
            "ny": [
                "https://www.ny1.com/nyc/all-boroughs/rss.xml",
                "https://www.nydailynews.com/arc/outboundfeeds/rss/",
                "https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/nyregion/rss.xml",
            ],
        }
        # General/national RSS feeds as fallback
        self.rss_feeds = [
            "https://feeds.bbci.co.uk/news/rss.xml",
            "https://rss.cnn.com/rss/edition.rss",
            "https://feeds.npr.org/1001/rss.xml",
        ]

    async def get_headlines(self, country: str = "us", category: Optional[str] = None, 
                           limit: int = 5, location: Optional[str] = None,
                           city: Optional[str] = None, state: Optional[str] = None) -> List[Dict]:
        """
        Get current news headlines, optionally filtered by location.

        Args:
            country: Country code (default: "us")
            category: News category (optional: business, entertainment, general, health, science, sports, technology)
            limit: Maximum number of headlines to return
            location: Location string (e.g., "New York, NY" or "Queens, NY")
            city: City name (optional, used if location not provided)
            state: State name or abbreviation (optional, used if location not provided)

        Returns:
            list: List of news articles with keys:
                - title: Article title
                - description: Article description
                - url: Article URL
                - source: News source name
                - published_at: Publication timestamp
        """
        # Determine if we should fetch local news
        local_query = None
        if location:
            local_query = location
        elif city:
            local_query = f"{city}"
            if state:
                local_query += f", {state}"
        
        # Try NewsAPI first if available
        if self.api_key:
            try:
                if local_query:
                    # Try to get local news using search
                    articles = await self._fetch_local_news_from_newsapi(local_query, limit)
                    if articles:
                        return articles
                    # Fall back to regular headlines if local search fails
                    logger.info(f"Local news search failed, falling back to national headlines")
                
                return await self._fetch_from_newsapi(country, category, limit)
            except Exception as e:
                logger.warning(f"NewsAPI failed: {e}, falling back to RSS")
        
        # Fallback to RSS feeds (prefer local if available)
        try:
            if local_query:
                articles = await self._fetch_from_local_rss(local_query, limit)
                if articles:
                    return articles
            
            return await self._fetch_from_rss(limit)
        except Exception as e:
            logger.error(f"RSS fetch failed: {e}")
            return self._get_fallback_news()

    async def _fetch_from_newsapi(self, country: str, category: Optional[str], 
                                  limit: int) -> List[Dict]:
        """Fetch news from NewsAPI."""
        params = {
            "country": country,
            "apiKey": self.api_key,
            "pageSize": limit
        }
        if category:
            params["category"] = category

        timeout = aiohttp.ClientTimeout(total=5, connect=3)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(self.base_url, params=params, timeout=timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get("articles", [])
                    return [
                        {
                            "title": article.get("title", ""),
                            "description": article.get("description", ""),
                            "url": article.get("url", ""),
                            "source": article.get("source", {}).get("name", "Unknown"),
                            "published_at": article.get("publishedAt", "")
                        }
                        for article in articles[:limit]
                        if article.get("title") and article.get("title") != "[Removed]"
                    ]
                else:
                    raise Exception(f"NewsAPI returned status {response.status}")

    async def _fetch_local_news_from_newsapi(self, location: str, limit: int) -> List[Dict]:
        """Fetch local news from NewsAPI using search."""
        # Extract city and state from location string
        location_parts = location.lower().split(',')
        city = location_parts[0].strip()
        state = location_parts[1].strip() if len(location_parts) > 1 else None
        
        # Build search query
        query_parts = [city]
        if state:
            # Map common state abbreviations
            state_map = {
                "ny": "New York",
                "ca": "California",
                "tx": "Texas",
                "fl": "Florida",
            }
            state_name = state_map.get(state.lower(), state)
            query_parts.append(state_name)
        
        query = " AND ".join(query_parts)
        
        params = {
            "q": query,
            "apiKey": self.api_key,
            "pageSize": limit,
            "sortBy": "publishedAt",
            "language": "en"
        }
        
        timeout = aiohttp.ClientTimeout(total=5, connect=3)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(self.search_url, params=params, timeout=timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get("articles", [])
                    if articles:
                        return [
                            {
                                "title": article.get("title", ""),
                                "description": article.get("description", ""),
                                "url": article.get("url", ""),
                                "source": article.get("source", {}).get("name", "Unknown"),
                                "published_at": article.get("publishedAt", "")
                            }
                            for article in articles[:limit]
                            if article.get("title") and article.get("title") != "[Removed]"
                        ]
                # If search fails, return empty list to trigger fallback
                return []

    async def _fetch_from_local_rss(self, location: str, limit: int) -> List[Dict]:
        """Fetch local news from location-specific RSS feeds."""
        location_lower = location.lower()
        
        # Find matching local RSS feeds
        feeds_to_try = []
        for key, feeds in self.local_rss_feeds.items():
            if key in location_lower:
                feeds_to_try.extend(feeds)
        
        if not feeds_to_try:
            return []
        
        # Try each local RSS feed
        return await self._fetch_from_rss(limit, feeds_to_try)

    async def _fetch_from_rss(self, limit: int, feeds: Optional[List[str]] = None) -> List[Dict]:
        """Fetch news from RSS feeds using direct RSS parsing."""
        import ssl
        import feedparser
        import urllib.request
        
        # Create SSL context that doesn't verify certificates (for free RSS feeds)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Use provided feeds or default to general feeds
        feeds_to_try = feeds if feeds else self.rss_feeds
        
        # Try each RSS feed until one works
        for rss_url in feeds_to_try:
            try:
                # Fetch RSS feed with SSL context
                req = urllib.request.Request(rss_url)
                with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                    feed_data = response.read()
                
                # Parse RSS feed
                feed = feedparser.parse(feed_data)
                
                if feed.bozo and feed.bozo_exception:
                    logger.warning(f"RSS feed parse error for {rss_url}: {feed.bozo_exception}")
                    continue
                
                if not feed.entries:
                    logger.warning(f"No entries found in RSS feed: {rss_url}")
                    continue
                
                articles = []
                for entry in feed.entries[:limit]:
                    # Extract description/summary
                    description = ""
                    if hasattr(entry, 'summary'):
                        description = entry.summary
                    elif hasattr(entry, 'description'):
                        description = entry.description
                    
                    # Clean HTML from description
                    import re
                    description = re.sub(r'<[^>]+>', '', description)
                    description = description.strip()[:200]  # Limit length
                    
                    articles.append({
                        "title": entry.get("title", "No title"),
                        "description": description,
                        "url": entry.get("link", ""),
                        "source": feed.feed.get("title", "News"),
                        "published_at": entry.get("published", entry.get("updated", ""))
                    })
                
                if articles:
                    logger.info(f"Successfully fetched {len(articles)} articles from {rss_url}")
                    return articles
                    
            except Exception as e:
                logger.warning(f"Error fetching RSS from {rss_url}: {e}")
                continue
        
        # If all feeds failed, raise exception
        raise Exception("All RSS feeds failed")

    def _get_fallback_news(self) -> List[Dict]:
        """Return fallback news when all sources fail."""
        return [
            {
                "title": "News service temporarily unavailable",
                "description": "We're having trouble fetching the latest news. Please try again later.",
                "url": "",
                "source": "System",
                "published_at": datetime.utcnow().isoformat()
            }
        ]

    def format_news_response(self, articles: List[Dict]) -> str:
        """
        Format news articles into a user-friendly response.

        Args:
            articles: List of news article dictionaries

        Returns:
            str: Formatted news response
        """
        if not articles:
            return "I couldn't fetch any news at the moment. Please try again later."

        response = "Here are the latest news headlines:\n\n"
        
        for i, article in enumerate(articles, 1):
            title = article.get("title", "No title")
            source = article.get("source", "Unknown source")
            description = article.get("description", "")
            url = article.get("url", "")
            
            response += f"{i}. {title}\n"
            if description:
                # Truncate description if too long
                desc = description[:150] + "..." if len(description) > 150 else description
                response += f"   {desc}\n"
            response += f"   Source: {source}\n"
            if url:
                response += f"   {url}\n"
            response += "\n"

        return response.strip()


# Global news service instance
_news_service: Optional[NewsService] = None


def get_news_service() -> NewsService:
    """Get or create the global news service instance."""
    global _news_service
    if _news_service is None:
        _news_service = NewsService()
    return _news_service

