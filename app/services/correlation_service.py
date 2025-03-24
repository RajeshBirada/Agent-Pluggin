from typing import Dict, List, Any
import json
from app.utils.llm import query_llm

async def correlate_news_with_price_changes(
    stock_data: Dict[str, Any], 
    news_articles: List[Dict[str, Any]]
) -> str:
    """
    Analyze correlation between news articles and stock price changes using
    an iterative approach with Gemini LLM
    
    Args:
        stock_data: Stock price data
        news_articles: List of news articles
        
    Returns:
        Analysis of correlation between news and stock price changes
    """
    if not stock_data or not news_articles:
        return "Insufficient data to perform correlation analysis."
    
    # Step 1: Organize the data
    price_changes_by_date = {}
    for change in stock_data.get('daily_changes', []):
        price_changes_by_date[change['date']] = change
    
    news_by_date = {}
    for article in news_articles:
        date = article['published_at']
        if date not in news_by_date:
            news_by_date[date] = []
        news_by_date[date].append(article)
    
    # Step 2: Prepare correlation data
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
    
    # Step 3: Start multi-step analysis with the LLM
    system_prompt = f"""You are a financial analyst performing a step-by-step analysis.
Respond with EXACTLY ONE of these formats:
1. ANALYZE_DATA: Analyze the provided stock data and news for correlation
2. IDENTIFY_KEY_EVENTS: Identify key news events that influenced stock price changes
3. RATE_CORRELATION: Rate the correlation strength on a scale of 1-10 and explain
4. FINAL_ANALYSIS: Provide the final comprehensive correlation analysis

ONLY respond with one of the above commands, followed by the information you need to proceed.
Do not add any explanations before or after the command."""
    
    # Initial data preparation for the LLM
    initial_data = {
        "stock_name": stock_data['name'],
        "symbol": stock_data['symbol'],
        "dates_with_matching_news": len(correlation_data),
        "period": f"{correlation_data[0]['date']} to {correlation_data[-1]['date']}",
        "average_price_change": sum(item['price_change']['percent_change'] for item in correlation_data) / len(correlation_data)
    }
    
    # Step 4: First LLM query - Analyze the data
    current_query = f"""I need to analyze the correlation between news articles and stock price changes for {stock_data['name']} ({stock_data['symbol']}).
Here is the initial data: {json.dumps(initial_data, indent=2)}"""
    
    prompt = f"{system_prompt}\n\nQuery: {current_query}"
    first_response = await query_llm(prompt)
    
    # Step 5: Process first response and send detailed data
    data_by_date = {}
    for item in correlation_data:
        date = item['date']
        price_change = item['price_change']
        news = item['news']
        
        data_by_date[date] = {
            "price_change_percent": price_change['percent_change'],
            "close_price": price_change['close'],
            "volume": price_change['volume'],
            "news_articles": [
                {
                    "title": article['title'],
                    "source": article['source'],
                    "description": article['description'][:200] if article['description'] else ""
                } for article in news[:3]
            ]
        }
    
    # Step 6: Second LLM query - Identify key events
    current_query += f"\n\nFirst analysis step complete. Here is the detailed data by date: {json.dumps(data_by_date, indent=2)}"
    
    prompt = f"{system_prompt}\n\nQuery: {current_query}"
    second_response = await query_llm(prompt)
    
    # Step 7: Third LLM query - Rate correlation
    current_query += f"\n\nSecond analysis step complete. Key events identified. Now rate the correlation."
    
    prompt = f"{system_prompt}\n\nQuery: {current_query}"
    third_response = await query_llm(prompt)
    
    # Step 8: Final LLM query - Comprehensive analysis
    current_query += f"\n\nThird analysis step complete. Correlation rated. Now provide final comprehensive analysis."
    
    prompt = f"""You are a financial analyst providing a final report on news-price correlation.
Based on all the previous analysis steps:
1. Summarize whether there appears to be a correlation between news events and stock price movements for {stock_data['name']} ({stock_data['symbol']})
2. Identify the most significant news events that influenced price changes
3. Explain how news sentiment appears to affect this stock
4. Provide actionable insights for investors

Format your response as a concise analysis that could be presented to an investor."""
    
    final_analysis = await query_llm(prompt)
    
    return final_analysis

async def generate_comprehensive_report(
    ticker: str,
    stock_data: Dict[str, Any],
    fluctuation_analysis: str,
    news_summary: str,
    correlation_analysis: str
) -> str:
    """
    Generate a comprehensive report combining all analyses using an iterative approach
    
    Args:
        ticker: Stock ticker symbol
        stock_data: Stock data dictionary
        fluctuation_analysis: Analysis of stock price fluctuations
        news_summary: Summary of news articles
        correlation_analysis: Analysis of correlation between news and price changes
        
    Returns:
        Comprehensive report
    """
    # Step 1: System prompt definition
    system_prompt = """You are an investment research analyst creating a professional report.
Respond with EXACTLY ONE of these formats:
1. SUMMARIZE_FINDINGS: Create an executive summary of the key findings
2. IDENTIFY_KEY_EVENTS: Identify the most important news events that affected the stock price
3. ANALYZE_STOCK_BEHAVIOR: Provide insights on how this stock reacts to news
4. SUGGEST_STRATEGIES: Suggest potential trading strategies based on news-price correlation
5. FINAL_REPORT: Generate the complete professional investment research report

ONLY respond with one of the above commands, followed by your analysis."""
    
    # Step 2: First LLM query - Summarize findings
    current_query = f"""I need to create a comprehensive research report for {stock_data['name']} ({ticker}).
Here is the stock fluctuation analysis:
{fluctuation_analysis[:500]}... (truncated)

Here is the news summary:
{news_summary[:500]}... (truncated)

Here is the correlation analysis:
{correlation_analysis[:500]}... (truncated)"""
    
    prompt = f"{system_prompt}\n\nQuery: {current_query}"
    summary_response = await query_llm(prompt)
    
    # Step 3: Second LLM query - Identify key events
    current_query += "\n\nStep 1 complete. Now identify key events."
    prompt = f"{system_prompt}\n\nQuery: {current_query}"
    key_events_response = await query_llm(prompt)
    
    # Step 4: Third LLM query - Analyze stock behavior
    current_query += "\n\nStep 2 complete. Now analyze stock behavior."
    prompt = f"{system_prompt}\n\nQuery: {current_query}"
    behavior_response = await query_llm(prompt)
    
    # Step 5: Fourth LLM query - Suggest strategies
    current_query += "\n\nStep 3 complete. Now suggest trading strategies."
    prompt = f"{system_prompt}\n\nQuery: {current_query}"
    strategies_response = await query_llm(prompt)
    
    # Step 6: Final LLM query - Complete report
    prompt = f"""You are an investment research analyst creating a final professional report.
Based on all the previous analysis steps, create a comprehensive research report for {stock_data['name']} ({ticker}) with the following sections:
1. Executive Summary
2. Stock Price Analysis
3. News Events Overview
4. News-Price Correlation Analysis
5. Key News Events Impact
6. Stock Behavior Patterns
7. Trading Strategies
8. Conclusion

Use all the information provided in the stock fluctuation analysis, news summary, and correlation analysis:

STOCK PRICE FLUCTUATION ANALYSIS:
{fluctuation_analysis}

NEWS SUMMARY:
{news_summary}

CORRELATION ANALYSIS:
{correlation_analysis}

Format your response as a professional investment research report with clear sections and actionable insights."""
    
    comprehensive_report = await query_llm(prompt)
    
    return comprehensive_report 