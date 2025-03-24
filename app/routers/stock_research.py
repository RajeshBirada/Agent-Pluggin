from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json
import asyncio

from app.services.stock_service import get_stock_data, analyze_fluctuations
from app.services.news_service import get_news_for_stock, extract_key_news_points
from app.services.correlation_service import correlate_news_with_price_changes, generate_comprehensive_report
from app.services.stock_functions import (
    analyze_price_data, 
    analyze_news_sentiment, 
    correlate_news_and_price, 
    generate_investment_insight
)
from app.utils.llm import StockAnalysisAgent, query_llm

router = APIRouter(
    prefix="/api/stock-research",
    tags=["Stock Research"],
)

class ResearchRequest(BaseModel):
    ticker: str
    period: str = "1wk"

class ResearchResponse(BaseModel):
    ticker: str
    stock_data: Optional[Dict[str, Any]] = None
    fluctuation_analysis: Optional[str] = None
    news_summary: Optional[str] = None
    correlation_analysis: Optional[str] = None
    comprehensive_report: Optional[str] = None
    status: str = "success"
    error: Optional[str] = None

@router.post("/research", response_model=ResearchResponse)
async def research_stock(request: ResearchRequest):
    """
    Perform multi-step research on a stock, analyzing price movements and related news
    """
    try:
        # Step 1: Get stock data
        stock_data = await get_stock_data(request.ticker, request.period)
        if not stock_data:
            raise HTTPException(status_code=404, detail=f"Stock data not found for ticker {request.ticker}")
        
        # Step 2: Get news articles for the stock
        news_articles = await get_news_for_stock(stock_data['name'], request.ticker, days=7)
        
        # Step 3: Set up the agent for correlation analysis
        agent = StockAnalysisAgent(max_iterations=4)
        
        # Define the system prompt
        system_prompt = """You are a financial analyst agent. Respond with EXACTLY ONE of these formats:
1. FUNCTION_CALL: analyze_price_data|{stock_data}
2. FUNCTION_CALL: analyze_news_sentiment|{news_data}
3. FUNCTION_CALL: correlate_news_and_price|{combined_data}
4. FUNCTION_CALL: generate_investment_insight|{correlation_data}
5. FINAL_ANALYSIS: [Your comprehensive analysis of the stock]

DO NOT include multiple responses. Give ONE response at a time."""
        
        agent.set_system_prompt(system_prompt)
        
        # Set the initial query
        initial_query = f"""I need to analyze the correlation between news events and stock price movements for {stock_data['name']} ({request.ticker}) over the past week.
I should analyze the stock price data first, then the news sentiment, then correlate them, and finally generate investment insights."""
        
        agent.set_initial_query(initial_query)
        
        # Define function map
        function_map = {
            "analyze_price_data": lambda params: analyze_price_data(params if isinstance(params, str) else json.dumps(stock_data)),
            "analyze_news_sentiment": lambda params: analyze_news_sentiment(params if isinstance(params, str) else json.dumps(news_articles)),
            "correlate_news_and_price": correlate_news_and_price,
            "generate_investment_insight": generate_investment_insight
        }
        
        # Run the agent until completion
        correlation_analysis = await agent.run_until_completion(
            function_map=function_map,
            completion_marker="FINAL_ANALYSIS"
        )
        
        # Generate the comprehensive report
        system_prompt = """You are an investment research report writer creating a final report.
Based on all the previous analysis steps, create a comprehensive research report with these sections:
1. Executive Summary
2. Stock Price Analysis
3. News Summary
4. News-Price Correlation Analysis
5. Investment Strategy Recommendations
6. Conclusion"""
        
        # Prepare input for the report
        fluctuation_analysis = await analyze_fluctuations(stock_data)
        news_summary = await extract_key_news_points(news_articles)
        
        final_prompt = f"""Create a comprehensive research report for {stock_data['name']} ({request.ticker}) with the following information:

STOCK PRICE FLUCTUATION ANALYSIS:
{fluctuation_analysis}

NEWS SUMMARY:
{news_summary}

CORRELATION ANALYSIS:
{correlation_analysis}

Format your response as a professional investment research report with clear sections and actionable insights."""
        
        comprehensive_report = await query_llm(final_prompt)
        
        # Return the complete analysis
        return ResearchResponse(
            ticker=request.ticker,
            stock_data=stock_data,
            fluctuation_analysis=fluctuation_analysis,
            news_summary=news_summary,
            correlation_analysis=correlation_analysis,
            comprehensive_report=comprehensive_report
        )
    
    except Exception as e:
        return ResearchResponse(
            ticker=request.ticker,
            status="error",
            error=str(e)
        )

@router.get("/stock-data/{ticker}")
async def get_stock_data_endpoint(
    ticker: str, 
    period: str = Query("1wk", description="Time period for stock data (e.g., 1d, 1wk, 1mo)")
):
    """
    Get stock data for a given ticker
    """
    try:
        stock_data = await get_stock_data(ticker, period)
        if not stock_data:
            raise HTTPException(status_code=404, detail=f"Stock data not found for ticker {ticker}")
        
        return {"ticker": ticker, "stock_data": stock_data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/news/{ticker}")
async def get_news_endpoint(
    ticker: str,
    days: int = Query(7, description="Number of days to look back for news")
):
    """
    Get news articles for a stock
    """
    try:
        # First get the stock data to get the company name
        stock_data = await get_stock_data(ticker)
        if not stock_data:
            raise HTTPException(status_code=404, detail=f"Stock data not found for ticker {ticker}")
        
        news_articles = await get_news_for_stock(stock_data['name'], ticker, days)
        news_summary = await extract_key_news_points(news_articles)
        
        return {
            "ticker": ticker,
            "company_name": stock_data['name'],
            "news_articles": news_articles,
            "news_summary": news_summary
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/correlation/{ticker}")
async def get_correlation_endpoint(
    ticker: str,
    period: str = Query("1wk", description="Time period for stock data (e.g., 1d, 1wk, 1mo)")
):
    """
    Analyze correlation between news and stock price changes using agent-based approach
    """
    try:
        # Get stock data
        stock_data = await get_stock_data(ticker, period)
        if not stock_data:
            raise HTTPException(status_code=404, detail=f"Stock data not found for ticker {ticker}")
        
        # Get news articles
        news_articles = await get_news_for_stock(stock_data['name'], ticker, days=7)
        
        # Set up the agent for correlation analysis
        agent = StockAnalysisAgent(max_iterations=4)
        
        # Define the system prompt
        system_prompt = """You are a financial analyst agent. Respond with EXACTLY ONE of these formats:
1. FUNCTION_CALL: analyze_price_data|{stock_data}
2. FUNCTION_CALL: analyze_news_sentiment|{news_data}
3. FUNCTION_CALL: correlate_news_and_price|{combined_data}
4. FUNCTION_CALL: generate_investment_insight|{correlation_data}
5. FINAL_ANALYSIS: [Your comprehensive analysis of the stock]

DO NOT include multiple responses. Give ONE response at a time."""
        
        agent.set_system_prompt(system_prompt)
        
        # Set the initial query
        initial_query = f"""I need to analyze the correlation between news events and stock price movements for {stock_data['name']} ({ticker})."""
        
        agent.set_initial_query(initial_query)
        
        # Define function map
        function_map = {
            "analyze_price_data": lambda params: analyze_price_data(params if isinstance(params, str) else json.dumps(stock_data)),
            "analyze_news_sentiment": lambda params: analyze_news_sentiment(params if isinstance(params, str) else json.dumps(news_articles)),
            "correlate_news_and_price": correlate_news_and_price,
            "generate_investment_insight": generate_investment_insight
        }
        
        # Run the agent until completion
        correlation_analysis = await agent.run_until_completion(
            function_map=function_map, 
            completion_marker="FINAL_ANALYSIS"
        )
        
        return {
            "ticker": ticker,
            "company_name": stock_data['name'],
            "correlation_analysis": correlation_analysis
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 