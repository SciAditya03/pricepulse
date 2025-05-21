#python 2.7.15
# backend/main.py

from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define a model to receive URL input
class URLRequest(BaseModel):
    url: str

@app.get("/")
async def root():
    return {"message": "PricePulse API is up and running!"}

@app.post("/track")
async def track_price(data: URLRequest):
    # Placeholder for actual scraping logic
    return {
        "message": "Tracking initiated!",
        "product_url": data.url,
        "price": "Scraper integration pending"
    }