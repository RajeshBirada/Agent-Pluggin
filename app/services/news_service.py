from newsapi import NewsApiClient
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from app.utils.config import NEWSAPI_KEY

news_api = NewsApiClient(api_key=NEWSAPI_KEY)

async def get_news_for_stock(company_name: str, ticker: str, days: int = 7) -> List[Dict[str, Any]]:
    """
    Get news articles related to a stock
    
    Args:
        company_name: The name of the company
        ticker: The stock ticker symbol
        days: Number of days to look back for news
        
    Returns:
        List of news articles
    """
    try:
        # Calculate the date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days)
        
        # Format dates for the API
        from_date_str = from_date.strftime('%Y-%m-%d')
        to_date_str = to_date.strftime('%Y-%m-%d')
        
        # Search query using both company name and ticker
        query = f"{company_name} OR {ticker}"
        
        # Get news from the News API
        response = news_api.get_everything(
            q=query,
            from_param=from_date_str,
            to=to_date_str,
            language='en',
            sort_by='relevancy',
            page_size=25
        )
        
        # Process and filter the results
        articles = response.get('articles', [])
        processed_articles = []
        
        for article in articles:
            # Extract date in a standardized format
            published_at = datetime.strptime(article['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
            date_str = published_at.strftime("%Y-%m-%d")
            
            processed_articles.append({
                'title': article['title'],
                'description': article['description'],
                'url': article['url'],
                'source': article['source']['name'],
                'published_at': date_str,
                'content': article.get('content', '')
            })
        
        return processed_articles
    
    except Exception as e:
        print(f"Error fetching news for {company_name} ({ticker}): {e}")
        return []

async def extract_key_news_points(news_articles: List[Dict[str, Any]]) -> str:
    """
    Extract key points from news articles
    
    Args:
        news_articles: List of news articles
        
    Returns:
        String summarizing key points from the news
    """
    if not news_articles:
        return "No news articles found for the specified period."
    
    # Group articles by date
    articles_by_date = {}
    for article in news_articles:
        date = article['published_at']
        if date not in articles_by_date:
            articles_by_date[date] = []
        articles_by_date[date].append(article)
    
    # Create a summary
    summary = "News Summary:\n\n"
    
    for date, articles in sorted(articles_by_date.items()):
        summary += f"Date: {date}\n"
        summary += f"Number of articles: {len(articles)}\n"
        
        for i, article in enumerate(articles[:3]):  # Limit to top 3 articles per day
            summary += f"  {i+1}. {article['title']} (Source: {article['source']})\n"
            if article['description']:
                summary += f"     {article['description'][:150]}{'...' if len(article['description']) > 150 else ''}\n"
        
        if len(articles) > 3:
            summary += f"  ... and {len(articles) - 3} more articles\n"
        
        summary += "\n"
    
    return summary 