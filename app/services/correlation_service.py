from typing import Dict, List, Any
from app.utils.llm import query_llm

async def correlate_news_with_price_changes(
    stock_data: Dict[str, Any], 
    news_articles: List[Dict[str, Any]]
) -> str:
    """
    Analyze correlation between news articles and stock price changes
    
    Args:
        stock_data: Stock price data
        news_articles: List of news articles
        
    Returns:
        Analysis of correlation between news and stock price changes
    """
    if not stock_data or not news_articles:
        return "Insufficient data to perform correlation analysis."
    
    # Organize price changes by date
    price_changes_by_date = {}
    for change in stock_data.get('daily_changes', []):
        price_changes_by_date[change['date']] = change
    
    # Organize news by date
    news_by_date = {}
    for article in news_articles:
        date = article['published_at']
        if date not in news_by_date:
            news_by_date[date] = []
        news_by_date[date].append(article)
    
    # Prepare data for correlation analysis
    correlation_data = []
    for date, articles in news_by_date.items():
        if date in price_changes_by_date:
            correlation_data.append({
                'date': date,
                'price_change': price_changes_by_date[date],
                'news': articles[:3]  # Limit to top 3 articles
            })
    
    if not correlation_data:
        return "No matching dates found between news articles and price data."
    
    # Prepare input for LLM analysis
    prompt = f"""
    I need to analyze the correlation between news articles and stock price changes for {stock_data['name']} ({stock_data['symbol']}).
    
    Here is the data:
    
    """
    
    for item in correlation_data:
        date = item['date']
        price_change = item['price_change']
        news = item['news']
        
        prompt += f"\nDATE: {date}\n"
        prompt += f"PRICE CHANGE: {price_change['percent_change']:.2f}% (Closed at ${price_change['close']:.2f})\n"
        prompt += "NEWS ARTICLES:\n"
        
        for i, article in enumerate(news):
            prompt += f"{i+1}. {article['title']}\n"
            if article['description']:
                prompt += f"   {article['description'][:200]}{'...' if len(article['description']) > 200 else ''}\n"
    
    prompt += """
    Based on this data, please:
    1. Analyze whether there appears to be a correlation between news events and stock price movements
    2. Identify specific news events that likely influenced significant price changes
    3. Provide a brief summary of how news sentiment appears to affect this stock
    4. Rate the strength of the correlation on a scale of 1-10
    
    Format your response as a concise analysis that could be presented to an investor.
    """
    
    # Query the LLM
    correlation_analysis = await query_llm(prompt)
    
    return correlation_analysis

async def generate_comprehensive_report(
    ticker: str,
    stock_data: Dict[str, Any],
    fluctuation_analysis: str,
    news_summary: str,
    correlation_analysis: str
) -> str:
    """
    Generate a comprehensive report combining all analyses
    
    Args:
        ticker: Stock ticker symbol
        stock_data: Stock data dictionary
        fluctuation_analysis: Analysis of stock price fluctuations
        news_summary: Summary of news articles
        correlation_analysis: Analysis of correlation between news and price changes
        
    Returns:
        Comprehensive report
    """
    prompt = f"""
    Please create a comprehensive research report for {stock_data['name']} ({ticker}) based on the following data:
    
    STOCK PRICE FLUCTUATION ANALYSIS:
    {fluctuation_analysis}
    
    NEWS SUMMARY:
    {news_summary}
    
    CORRELATION ANALYSIS:
    {correlation_analysis}
    
    Based on this information, please:
    1. Create an executive summary of the key findings
    2. Identify the most important news events that affected the stock price
    3. Provide insights on how this stock reacts to news
    4. Suggest potential trading strategies based on news-price correlation
    
    Format your response as a professional investment research report with clear sections and actionable insights.
    """
    
    # Query the LLM
    comprehensive_report = await query_llm(prompt)
    
    return comprehensive_report 