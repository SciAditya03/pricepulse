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
import sqlite3

# Connect to SQLite DB (creates file if it doesn't exist)
conn = sqlite3.connect("price_data.db")
cursor = conn.cursor()

# Create table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        product_name TEXT,
        price TEXT,
        timestamp TEXT
    )
''')

conn.commit()
conn.close()

print("Database and table created successfully.")
import sqlite3
from datetime import datetime

def insert_data(url, product_name, price):
    conn = sqlite3.connect("price_data.db")
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
        INSERT INTO prices (url, product_name, price, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (url, product_name, price, timestamp))

    conn.commit()
    conn.close()
    print("Data inserted successfully.")
    from playwright.sync_api import sync_playwright

def scrape_amazon_product(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)

        try:
            product_name = page.locator("span#productTitle").inner_text().strip()
        except:
            product_name = "N/A"

        try:
            price = page.locator("span.a-price-whole").first.inner_text().strip()
        except:
            price = "N/A"

        browser.close()

        insert_data(url, product_name, price)
        print(f"Scraped: {product_name} - ₹{price}")
        !pip install APScheduler
        from apscheduler.schedulers.background import BackgroundScheduler
import time

scheduler = BackgroundScheduler()

def scheduled_scrape():
    print("Running scheduled scrape...")
    product_url = "https://www.amazon.in/dp/B0C9J48B3N"
    scrape_amazon_product(product_url)

# Schedule job every minute for demo (you can change to 'hours=1' for hourly)
scheduler.add_job(scheduled_scrape, 'interval', minutes=1)
scheduler.start()

print("Scheduler started.")
try:
    while True:
        time.sleep(60)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    print("Scheduler stopped.")
    from fastapi import FastAPI, Request, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import datetime
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class URLRequest(BaseModel):
    url: str
  def get_data_from_db():
    conn = sqlite3.connect('product_prices.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prices ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows
@app.get("/")
def root():
    return {"message": "PricePulse API is up and running!"}

@app.post("/submit")
def submit_url(data: URLRequest):
    # You can trigger scrape here or just store
    return {"message": "URL received", "url": data.url}

@app.get("/history")
def fetch_history():
    rows = get_data_from_db()
    return {"data": [
        {"timestamp": row[0], "url": row[1], "name": row[2], "price": row[3]} for row in rows
    ]}
