RajeshBirada

# Stock Research FastAPI Application

A FastAPI application that performs multi-step research to analyze stock price movements and correlate them with news events using Google's Gemini LLM.

## Features

- Fetch stock data including price, volume, and daily changes
- Analyze stock price fluctuations
- Retrieve relevant news articles about a stock
- Correlate news events with stock price movements
- Generate comprehensive research reports
- Use Google's Gemini LLM for intelligent analysis

## Requirements

- Python 3.8+
- FastAPI
- yfinance
- NewsAPI
- Google Generative AI (Gemini)
- Other dependencies (see requirements.txt)

## Setup

1. Clone the repository:
```
git clone https://github.com/RajeshBirada/Agent-Pluggin.git
cd Agent-Pluggin
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Configure environment variables:
   - Copy the `.env` file and fill in your API keys:
   - `GOOGLE_API_KEY`: Your Google API key for Gemini
   - `NEWSAPI_KEY`: Your NewsAPI key

## Usage

1. Start the FastAPI server:
```
uvicorn app.main:app --reload
```

2. Access the API documentation:
   - Browse to `http://localhost:8000/docs`

3. Run the example client:
```
python -m app.client
```

## API Endpoints

- `POST /api/stock-research/research`: Perform comprehensive research on a stock
- `GET /api/stock-research/stock-data/{ticker}`: Get stock data for a ticker
- `GET /api/stock-research/news/{ticker}`: Get news articles for a stock
- `GET /api/stock-research/correlation/{ticker}`: Analyze correlation between news and stock price changes

## How It Works

This application uses a multi-step approach:

1. Fetch stock data using yfinance
2. Analyze price fluctuations 
3. Retrieve relevant news using NewsAPI
4. Query Google's Gemini LLM to correlate news with price changes
5. Generate a comprehensive research report

The application uses LLM multiple times in the workflow:
- To analyze correlation between news and price movements
- To generate the final comprehensive report

## Example

```python
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/stock-research/research",
            json={"ticker": "AAPL", "period": "1wk"}
        )
        result = response.json()
        print(result["comprehensive_report"])

asyncio.run(main())
```

## License

This project is licensed under the MIT License.
