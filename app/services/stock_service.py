import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

async def get_stock_data(ticker: str, period: str = "1wk") -> Optional[Dict[str, Any]]:
    """
    Get stock data for a given ticker
    
    Args:
        ticker: The stock ticker symbol
        period: The period for which to retrieve data (e.g., 1d, 1wk, 1mo)
        
    Returns:
        Dictionary containing stock data or None if data retrieval failed
    """
    try:
        # Get stock info
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Calculate the start and end dates
        end_date = datetime.now()
        
        if period == "1wk":
            start_date = end_date - timedelta(days=7)
        elif period == "1mo":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=7)  # Default to 1 week
        
        # Get historical data
        hist = stock.history(start=start_date, end=end_date)
        
        # Convert to dictionary format for easier handling
        if hist.empty:
            return None
        
        hist_dict = hist.reset_index().to_dict('records')
        
        # Calculate daily changes
        daily_changes = []
        for i in range(1, len(hist_dict)):
            prev_close = hist_dict[i-1]['Close']
            curr_close = hist_dict[i]['Close']
            percent_change = ((curr_close - prev_close) / prev_close) * 100
            
            daily_changes.append({
                'date': hist_dict[i]['Date'].strftime('%Y-%m-%d'),
                'close': curr_close,
                'prev_close': prev_close,
                'change': curr_close - prev_close,
                'percent_change': percent_change,
                'volume': hist_dict[i]['Volume']
            })
        
        # Get basic stock info
        stock_info = {
            'name': info.get('longName', ticker),
            'symbol': ticker,
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            'current_price': info.get('currentPrice', hist_dict[-1]['Close'] if hist_dict else None),
            'daily_changes': daily_changes
        }
        
        return stock_info
    
    except Exception as e:
        print(f"Error fetching stock data for {ticker}: {e}")
        return None

async def analyze_fluctuations(stock_data: Dict[str, Any]) -> str:
    """
    Analyze stock price fluctuations
    
    Args:
        stock_data: The stock data dictionary
        
    Returns:
        String describing the fluctuations
    """
    if not stock_data or 'daily_changes' not in stock_data or not stock_data['daily_changes']:
        return "Insufficient data to analyze fluctuations."
    
    daily_changes = stock_data['daily_changes']
    
    max_gain = max(daily_changes, key=lambda x: x['percent_change'])
    max_loss = min(daily_changes, key=lambda x: x['percent_change'])
    
    avg_change = sum(item['percent_change'] for item in daily_changes) / len(daily_changes)
    
    analysis = f"Stock: {stock_data['name']} ({stock_data['symbol']})\n"
    analysis += f"Sector: {stock_data['sector']}, Industry: {stock_data['industry']}\n"
    analysis += f"Current Price: ${stock_data['current_price']:.2f}\n\n"
    analysis += f"Analysis Period: {daily_changes[0]['date']} to {daily_changes[-1]['date']}\n"
    analysis += f"Average Daily Change: {avg_change:.2f}%\n"
    analysis += f"Biggest Gain: {max_gain['percent_change']:.2f}% on {max_gain['date']}\n"
    analysis += f"Biggest Loss: {max_loss['percent_change']:.2f}% on {max_loss['date']}\n\n"
    
    analysis += "Daily Changes:\n"
    for change in daily_changes:
        direction = "↑" if change['percent_change'] > 0 else "↓"
        analysis += f"{change['date']}: {change['percent_change']:.2f}% {direction} (${change['close']:.2f})\n"
    
    return analysis 