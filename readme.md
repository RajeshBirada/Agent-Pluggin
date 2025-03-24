RajeshBirada

# Stock Research FastAPI Application with Multi-Step LLM Tool Calling

A FastAPI application that performs multi-step research to analyze stock price movements and correlate them with news events using Google's Gemini LLM. This implementation follows the iterative pattern demonstrated in Session3.ipynb, with explicit LLM query→response→tool call→result cycles.

## Features

- Fetch stock data including price, volume, and daily changes
- Analyze stock price fluctuations
- Retrieve relevant news articles about a stock
- Correlate news events with stock price movements
- Generate comprehensive research reports
- Uses Google's Gemini LLM in a step-by-step agent workflow

## Multi-Step LLM Tool Calling

This application demonstrates a clear iteration-based approach to LLM tool calling similar to the one in Session3.ipynb:

1. **Initial Query** → The process starts with a query about a stock
2. **LLM Response** → The LLM determines the next function to call (e.g., `analyze_price_data`)
3. **Function Call** → The system executes the function with the provided parameters
4. **Function Result** → The result is returned to the LLM
5. **Next Iteration** → The LLM receives the result and determines the next step
6. **Final Analysis** → After multiple iterations, the LLM provides the comprehensive analysis

This creates a chain of:
```
Query → LLM Response → Function Call → Function Result → Query → LLM Response → Function Call → Function Result → ... → Final Analysis
```

Each iteration is tracked and displayed during processing, mimicking the approach shown in Session3.ipynb.

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

- `POST /api/stock-research/research`: Perform comprehensive research on a stock using multi-step LLM tool calling
- `GET /api/stock-research/stock-data/{ticker}`: Get stock data for a ticker
- `GET /api/stock-research/news/{ticker}`: Get news articles for a stock
- `GET /api/stock-research/correlation/{ticker}`: Analyze correlation between news and stock price changes using the agent-based approach

## How It Works

This application uses a multi-step approach without any agentic framework:

1. **Data Collection**: Fetch stock data using yfinance and news using NewsAPI
2. **Agent Initialization**: Set up the StockAnalysisAgent with system prompt and initial query
3. **First Iteration**: LLM analyzes the query and calls `analyze_price_data`
4. **Second Iteration**: LLM processes the result and calls `analyze_news_sentiment`
5. **Third Iteration**: LLM examines both results and calls `correlate_news_and_price`
6. **Fourth Iteration**: LLM reviews correlation data and calls `generate_investment_insight`
7. **Final Iteration**: LLM produces the FINAL_ANALYSIS based on all previous results

The StockAnalysisAgent class orchestrates this workflow by:
- Tracking each iteration's request and response
- Executing function calls based on LLM decisions
- Providing context from previous iterations to the LLM
- Detecting when the process has reached completion

## Example Code

```python
# Example of using the StockAnalysisAgent
async def analyze_stock_correlation(ticker, stock_data, news_articles):
    # Set up the agent
    agent = StockAnalysisAgent(max_iterations=4)
    
    # Define the system prompt
    system_prompt = """You are a financial analyst agent. Respond with EXACTLY ONE of these formats:
1. FUNCTION_CALL: analyze_price_data|{stock_data}
2. FUNCTION_CALL: analyze_news_sentiment|{news_data}
3. FUNCTION_CALL: correlate_news_and_price|{combined_data}
4. FUNCTION_CALL: generate_investment_insight|{correlation_data}
5. FINAL_ANALYSIS: [Your comprehensive analysis of the stock]"""
    
    agent.set_system_prompt(system_prompt)
    
    # Set the initial query
    initial_query = f"I need to analyze the correlation between news events and stock price movements for {ticker}."
    agent.set_initial_query(initial_query)
    
    # Define function map and run until completion
    function_map = {
        "analyze_price_data": analyze_price_data,
        "analyze_news_sentiment": analyze_news_sentiment,
        "correlate_news_and_price": correlate_news_and_price,
        "generate_investment_insight": generate_investment_insight
    }
    
    # Run the agent until it reaches a FINAL_ANALYSIS
    result = await agent.run_until_completion(
        function_map=function_map,
        completion_marker="FINAL_ANALYSIS"
    )
    
    return result
```

## License

This project is licensed under the MIT License.
