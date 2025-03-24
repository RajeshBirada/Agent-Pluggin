from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import asyncio

from app.services.stock_service import get_stock_data, analyze_fluctuations
from app.services.news_service import get_news_for_stock, extract_key_news_points
from app.services.correlation_service import correlate_news_with_price_changes, generate_comprehensive_report

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
        
        # Step 2: Analyze stock price fluctuations
        fluctuation_analysis = await analyze_fluctuations(stock_data)
        
        # Step 3: Get news articles for the stock
        news_articles = await get_news_for_stock(stock_data['name'], request.ticker, days=7)
        
        # Step 4: Extract key points from news
        news_summary = await extract_key_news_points(news_articles)
        
        # Step 5: Analyze correlation between news and price changes
        correlation_analysis = await correlate_news_with_price_changes(stock_data, news_articles)
        
        # Step 6: Generate comprehensive report
        comprehensive_report = await generate_comprehensive_report(
            request.ticker,
            stock_data,
            fluctuation_analysis,
            news_summary,
            correlation_analysis
        )
        
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
    Analyze correlation between news and stock price changes
    """
    try:
        # Get stock data
        stock_data = await get_stock_data(ticker, period)
        if not stock_data:
            raise HTTPException(status_code=404, detail=f"Stock data not found for ticker {ticker}")
        
        # Get news articles
        news_articles = await get_news_for_stock(stock_data['name'], ticker, days=7)
        
        # Analyze correlation
        correlation_analysis = await correlate_news_with_price_changes(stock_data, news_articles)
        
        return {
            "ticker": ticker,
            "company_name": stock_data['name'],
            "correlation_analysis": correlation_analysis
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 