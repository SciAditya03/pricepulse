!pip install fastapi nest-asyncio uvicorn pyngrok

from fastapi import FastAPI
from pydantic import BaseModel
import nest_asyncio
from pyngrok import ngrok, conf
import uvicorn

# Configure ngrok with your authtoken
conf.get_default().auth_token = "2xS3diau9Z9eejAKamJrljVEfBX_DQBG2hdU3EXHu7ArLuLr"

# Initialize FastAPI app
app = FastAPI()

# Define data model
class URLRequest(BaseModel):
    url: str

# Root endpoint
@app.get("/")
def root():
    return {"message": "PricePulse API is up and running!"}

# Track price endpoint
@app.post("/track")
def track_price(data: URLRequest):
    return {
        "message": "Tracking initiated!",
        "product_url": data.url,
        "price": "Scraper integration pending"
    }

# Allow nested loops (required in Colab)
nest_asyncio.apply()

# Create ngrok tunnel
public_url = ngrok.connect(8000)
print("Public URL:", public_url)

# Run the app using uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)

!pip install playwright
!playwright install

import nest_asyncio
nest_asyncio.apply()


import asyncio
import nest_asyncio
import sqlite3
from datetime import datetime
from playwright.async_api import async_playwright

nest_asyncio.apply()

# DB Setup
def init_db():
    conn = sqlite3.connect("prices.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            price TEXT,
            url TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

# Scrape Amazon Product
async def scrape_amazon(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=60000)

        # Try extracting product title and price
        try:
            title = await page.text_content("span#productTitle")
            price = await page.text_content("span.a-price-whole")
        except Exception as e:
            print("Error extracting content:", e)
            title = "Unavailable"
            price = "Unavailable"

        await browser.close()

        # Save to DB
        conn = sqlite3.connect("prices.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO prices (title, price, url, timestamp) VALUES (?, ?, ?, ?)",
                       (title.strip() if title else "N/A",
                        price.strip() if price else "N/A",
                        url,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

        # Print output
        print(f"Title: {title.strip() if title else 'N/A'}")
        print(f"Price: {price.strip() if price else 'N/A'}")

# Main trigger
init_db()
await scrape_amazon("https://www.amazon.in/dp/B0C9J48B3N")