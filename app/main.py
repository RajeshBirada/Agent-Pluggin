from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import stock_research

app = FastAPI(
    title="Stock Research API",
    description="API for multi-step research linking stock news with price changes",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(stock_research.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Stock Research API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 