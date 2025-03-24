import httpx
import asyncio
import json
from typing import Dict, Any

async def fetch_stock_research(ticker: str, period: str = "1wk") -> Dict[str, Any]:
    """
    Fetch stock research from the API
    
    Args:
        ticker: Stock ticker symbol
        period: Time period for analysis
        
    Returns:
        Dictionary containing research results
    """
    url = "http://localhost:8000/api/stock-research/research"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json={"ticker": ticker, "period": period}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return {"status": "error", "error": response.text}

async def display_research_results(research_results: Dict[str, Any]) -> None:
    """
    Display the research results in a readable format
    
    Args:
        research_results: Dictionary containing research results
    """
    if research_results.get("status") == "error":
        print(f"Error: {research_results.get('error')}")
        return
    
    print("\n" + "="*80)
    print(f"STOCK RESEARCH RESULTS FOR {research_results.get('ticker', 'Unknown')}")
    print("="*80)
    
    # Stock Data Summary
    stock_data = research_results.get("stock_data", {})
    if stock_data:
        print(f"\nStock: {stock_data.get('name')} ({research_results.get('ticker')})")
        print(f"Current Price: ${stock_data.get('current_price', 'N/A')}")
        print(f"Sector: {stock_data.get('sector', 'Unknown')}")
        print(f"Industry: {stock_data.get('industry', 'Unknown')}")
    
    # Fluctuation Analysis
    print("\n" + "-"*80)
    print("PRICE FLUCTUATION ANALYSIS")
    print("-"*80)
    print(research_results.get("fluctuation_analysis", "No analysis available"))
    
    # News Summary
    print("\n" + "-"*80)
    print("NEWS SUMMARY")
    print("-"*80)
    print(research_results.get("news_summary", "No news summary available"))
    
    # Correlation Analysis
    print("\n" + "-"*80)
    print("CORRELATION ANALYSIS")
    print("-"*80)
    print(research_results.get("correlation_analysis", "No correlation analysis available"))
    
    # Comprehensive Report
    print("\n" + "-"*80)
    print("COMPREHENSIVE REPORT")
    print("-"*80)
    print(research_results.get("comprehensive_report", "No comprehensive report available"))
    
    print("\n" + "="*80 + "\n")

async def main():
    """
    Main function to run the client
    """
    print("Stock Research Client")
    print("---------------------")
    
    # Get user input
    ticker = input("Enter stock ticker symbol: ").strip().upper()
    
    if not ticker:
        print("Invalid ticker symbol")
        return
    
    # Fetch research
    print(f"\nFetching research for {ticker}...")
    research_results = await fetch_stock_research(ticker)
    
    # Display results
    await display_research_results(research_results)
    
    # Save results to file
    filename = f"{ticker}_research.json"
    with open(filename, "w") as f:
        json.dump(research_results, f, indent=2)
    
    print(f"Research results saved to {filename}")

if __name__ == "__main__":
    asyncio.run(main()) 