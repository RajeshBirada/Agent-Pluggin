from typing import Dict, List, Any, Union
import json

def analyze_price_data(ticker_data: str) -> Dict[str, Any]:
    """
    Analyze stock price data
    
    Args:
        ticker_data: JSON string containing stock data
        
    Returns:
        Dictionary with analysis results
    """
    # Parse the input data if it's a string
    if isinstance(ticker_data, str):
        ticker_data = json.loads(ticker_data)
    
    daily_changes = ticker_data.get('daily_changes', [])
    
    if not daily_changes:
        return {
            "status": "error",
            "message": "No daily price changes found in data"
        }
    
    # Calculate statistics
    total_change = 0
    up_days = 0
    down_days = 0
    
    for change in daily_changes:
        percent_change = change.get('percent_change', 0)
        total_change += percent_change
        
        if percent_change > 0:
            up_days += 1
        elif percent_change < 0:
            down_days += 1
    
    avg_change = total_change / len(daily_changes) if daily_changes else 0
    
    # Find max gain and loss days
    max_gain = max(daily_changes, key=lambda x: x.get('percent_change', 0)) if daily_changes else {}
    max_loss = min(daily_changes, key=lambda x: x.get('percent_change', 0)) if daily_changes else {}
    
    # Prepare the result
    result = {
        "ticker": ticker_data.get('symbol', 'Unknown'),
        "company_name": ticker_data.get('name', 'Unknown'),
        "current_price": ticker_data.get('current_price', 0),
        "analysis_period": f"{daily_changes[0]['date']} to {daily_changes[-1]['date']}" if daily_changes else "Unknown",
        "average_daily_change": avg_change,
        "up_days": up_days,
        "down_days": down_days,
        "max_gain": {
            "date": max_gain.get('date', ''),
            "percent": max_gain.get('percent_change', 0),
            "price": max_gain.get('close', 0)
        },
        "max_loss": {
            "date": max_loss.get('date', ''),
            "percent": max_loss.get('percent_change', 0),
            "price": max_loss.get('close', 0)
        }
    }
    
    return result

def analyze_news_sentiment(news_data: str) -> Dict[str, Any]:
    """
    Organize and partially analyze news data
    
    Args:
        news_data: JSON string containing news articles
        
    Returns:
        Dictionary with news analysis
    """
    # Parse the input data if it's a string
    if isinstance(news_data, str):
        news_data = json.loads(news_data)
    
    # Organize articles by date
    articles_by_date = {}
    for article in news_data:
        date = article.get('published_at', '')
        if date:
            if date not in articles_by_date:
                articles_by_date[date] = []
            articles_by_date[date].append(article)
    
    # Count articles by source
    sources = {}
    for article in news_data:
        source = article.get('source', '')
        if source:
            sources[source] = sources.get(source, 0) + 1
    
    # Prepare the result
    result = {
        "total_articles": len(news_data),
        "days_with_news": len(articles_by_date),
        "articles_by_date": {date: len(articles) for date, articles in articles_by_date.items()},
        "top_sources": sorted([{"source": s, "count": c} for s, c in sources.items()], 
                             key=lambda x: x["count"], reverse=True)[:5],
        "date_range": [min(articles_by_date.keys()), max(articles_by_date.keys())] if articles_by_date else []
    }
    
    return result

def correlate_news_and_price(data: str) -> Dict[str, Any]:
    """
    Process combined stock and news data to find correlations
    
    Args:
        data: JSON string containing combined price and news data by date
        
    Returns:
        Dictionary with correlation analysis
    """
    # Parse the input data if it's a string
    if isinstance(data, str):
        data = json.loads(data)
    
    # Analyze days with news vs. days without news
    days_with_news = []
    days_without_news = []
    
    for date, day_data in data.items():
        price_change = day_data.get("price_change_percent", 0)
        news = day_data.get("news_articles", [])
        
        if news:
            days_with_news.append({"date": date, "price_change": price_change, "news_count": len(news)})
        else:
            days_without_news.append({"date": date, "price_change": price_change})
    
    # Calculate average price change with and without news
    avg_with_news = sum(day["price_change"] for day in days_with_news) / len(days_with_news) if days_with_news else 0
    avg_without_news = sum(day["price_change"] for day in days_without_news) / len(days_without_news) if days_without_news else 0
    
    # Identify days with significant price movements
    significant_days = []
    threshold = 2.0  # Consider a 2% move significant
    
    for date, day_data in data.items():
        price_change = day_data.get("price_change_percent", 0)
        if abs(price_change) >= threshold:
            significant_days.append({
                "date": date,
                "price_change": price_change,
                "news_count": len(day_data.get("news_articles", [])),
                "news_titles": [article.get("title", "") for article in day_data.get("news_articles", [])][:3]
            })
    
    # Prepare the result
    result = {
        "days_with_news": len(days_with_news),
        "days_without_news": len(days_without_news),
        "avg_price_change_with_news": avg_with_news,
        "avg_price_change_without_news": avg_without_news,
        "difference": avg_with_news - avg_without_news,
        "has_correlation": abs(avg_with_news - avg_without_news) > 0.5,
        "correlation_strength": abs(avg_with_news - avg_without_news) / max(abs(avg_with_news), abs(avg_without_news)) if max(abs(avg_with_news), abs(avg_without_news)) > 0 else 0,
        "significant_price_days": significant_days
    }
    
    return result

def generate_investment_insight(correlation_data: str) -> Dict[str, Any]:
    """
    Generate investment insights based on correlation analysis
    
    Args:
        correlation_data: JSON string containing correlation analysis
        
    Returns:
        Dictionary with investment insights
    """
    # Parse the input data if it's a string
    if isinstance(correlation_data, str):
        correlation_data = json.loads(correlation_data)
    
    # Extract key information
    has_correlation = correlation_data.get("has_correlation", False)
    correlation_strength = correlation_data.get("correlation_strength", 0)
    avg_with_news = correlation_data.get("avg_price_change_with_news", 0)
    significant_days = correlation_data.get("significant_price_days", [])
    
    # Generate insights
    if correlation_strength > 0.7:
        correlation_level = "Strong"
    elif correlation_strength > 0.4:
        correlation_level = "Moderate"
    else:
        correlation_level = "Weak"
    
    # Determine if news tends to drive price up or down
    news_impact = "positive" if avg_with_news > 0 else "negative"
    
    # Generate strategy recommendations
    if has_correlation and correlation_strength > 0.4:
        if news_impact == "positive":
            strategy = "Consider buying on significant news days, particularly positive news."
        else:
            strategy = "Consider selling or hedging on significant news days, as news tends to drive prices down."
    else:
        strategy = "No clear news-based strategy recommended due to weak correlation."
    
    # Identify key news events that moved the market
    key_events = []
    for day in sorted(significant_days, key=lambda x: abs(x.get("price_change", 0)), reverse=True)[:3]:
        if day.get("news_count", 0) > 0:
            key_events.append({
                "date": day.get("date", ""),
                "price_change": day.get("price_change", 0),
                "likely_cause": day.get("news_titles", ["No title available"])[0]
            })
    
    # Prepare the result
    result = {
        "correlation_detected": has_correlation,
        "correlation_level": correlation_level,
        "correlation_strength": correlation_strength,
        "news_impact": news_impact,
        "recommended_strategy": strategy,
        "key_market_moving_events": key_events
    }
    
    return result 