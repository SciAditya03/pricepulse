# Complete Backend Integration for Price Tracker
# Save this as: backend.py

import asyncio
import sqlite3
import nest_asyncio
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from playwright.async_api import async_playwright
from apscheduler.schedulers.background import BackgroundScheduler
import uvicorn
import re
import json

# Apply nest_asyncio for Jupyter/Colab compatibility
nest_asyncio.apply()

# Initialize FastAPI app
app = FastAPI(title="PriceTracker API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class URLRequest(BaseModel):
    url: str

class ProductResponse(BaseModel):
    title: str
    currentPrice: float
    image: str
    asin: str
    priceChange: float
    priceChangePercent: float
    platforms: dict

# Database setup
def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect("price_tracker.db")
    cursor = conn.cursor()
    
    # Main products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asin TEXT UNIQUE,
            title TEXT,
            url TEXT,
            image_url TEXT,
            created_at TEXT,
            last_updated TEXT
        )
    """)
    
    # Price history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asin TEXT,
            price REAL,
            platform TEXT DEFAULT 'amazon',
            timestamp TEXT,
            FOREIGN KEY (asin) REFERENCES products (asin)
        )
    """)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

# Amazon scraper class
class AmazonScraper:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
    
    def extract_asin(self, url):
        """Extract ASIN from Amazon URL"""
        patterns = [
            r'/dp/([A-Z0-9]{10})',
            r'/gp/product/([A-Z0-9]{10})',
            r'asin=([A-Z0-9]{10})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    async def scrape_product(self, url):
        """Scrape product details from Amazon"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            context = await browser.new_context(
                user_agent=self.user_agents[0],
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                await page.wait_for_timeout(2000)  # Wait for dynamic content
                
                # Extract product details
                product_data = await self.extract_product_data(page, url)
                
                await browser.close()
                return product_data
                
            except Exception as e:
                await browser.close()
                raise Exception(f"Scraping failed: {str(e)}")
    
    async def extract_product_data(self, page, url):
        """Extract product data from the page"""
        try:
            # Title
            title_selectors = [
                "span#productTitle",
                "h1.a-size-large.a-spacing-none",
                "h1#title"
            ]
            title = await self.get_text_by_selectors(page, title_selectors)
            
            # Price
            price_selectors = [
                "span.a-price-whole",
                "span.a-price.a-text-price.a-size-medium.apexPriceToPay",
                "span.a-price-range",
                ".a-price .a-offscreen"
            ]
            price_text = await self.get_text_by_selectors(page, price_selectors)
            price = self.parse_price(price_text)
            
            # Image
            image_selectors = [
                "img#landingImage",
                "img.a-dynamic-image",
                "img#main-image"
            ]
            image_url = await self.get_attribute_by_selectors(page, image_selectors, 'src')
            
            # ASIN
            asin = self.extract_asin(url)
            
            return {
                'title': title or "Product Title Not Found",
                'price': price,
                'image_url': image_url or "https://via.placeholder.com/200x200/f0f0f0/666?text=No+Image",
                'asin': asin,
                'url': url
            }
            
        except Exception as e:
            print(f"Error extracting product data: {e}")
            return None
    
    async def get_text_by_selectors(self, page, selectors):
        """Try multiple selectors to get text content"""
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    return await element.inner_text()
            except:
                continue
        return None
    
    async def get_attribute_by_selectors(self, page, selectors, attribute):
        """Try multiple selectors to get attribute value"""
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    return await element.get_attribute(attribute)
            except:
                continue
        return None
    
    def parse_price(self, price_text):
        """Parse price from text"""
        if not price_text:
            return 0.0
        
        # Remove currency symbols and extract number
        price_clean = re.sub(r'[^\d.,]', '', price_text.replace(',', ''))
        try:
            return float(price_clean)
        except:
            return 0.0

# Database operations
class DatabaseManager:
    @staticmethod
    def save_product(product_data):
        """Save or update product in database"""
        conn = sqlite3.connect("price_tracker.db")
        cursor = conn.cursor()
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO products 
                (asin, title, url, image_url, created_at, last_updated)
                VALUES (?, ?, ?, ?, 
                    COALESCE((SELECT created_at FROM products WHERE asin = ?), ?), ?)
            """, (
                product_data['asin'], product_data['title'], product_data['url'],
                product_data['image_url'], product_data['asin'], now, now
            ))
            
            # Save price history
            cursor.execute("""
                INSERT INTO price_history (asin, price, platform, timestamp)
                VALUES (?, ?, 'amazon', ?)
            """, (product_data['asin'], product_data['price'], now))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_product_with_history(asin):
        """Get product details with price history"""
        conn = sqlite3.connect("price_tracker.db")
        cursor = conn.cursor()
        
        try:
            # Get product details
            cursor.execute("SELECT * FROM products WHERE asin = ?", (asin,))
            product = cursor.fetchone()
            
            if not product:
                return None
            
            # Get price history (last 30 days)
            cursor.execute("""
                SELECT price, timestamp FROM price_history 
                WHERE asin = ? AND timestamp >= date('now', '-30 days')
                ORDER BY timestamp
            """, (asin,))
            
            price_history = cursor.fetchall()
            
            return {
                'product': product,
                'price_history': price_history
            }
        finally:
            conn.close()
    
    @staticmethod
    def get_price_statistics(asin):
        """Get price statistics for a product"""
        conn = sqlite3.connect("price_tracker.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    MIN(price) as min_price,
                    MAX(price) as max_price,
                    AVG(price) as avg_price,
                    COUNT(*) as data_points
                FROM price_history 
                WHERE asin = ?
            """, (asin,))
            
            return cursor.fetchone()
        finally:
            conn.close()

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "PriceTracker API is running!",
        "version": "1.0.0",
        "endpoints": ["/track", "/product/{asin}", "/history/{asin}"]
    }

@app.post("/track")
async def track_product(request: URLRequest):
    """Track a new product or update existing one"""
    try:
        # Validate Amazon URL
        if not ("amazon." in request.url and ("/dp/" in request.url or "/gp/product/" in request.url)):
            raise HTTPException(status_code=400, detail="Invalid Amazon URL")
        
        # Initialize scraper and scrape product
        scraper = AmazonScraper()
        product_data = await scraper.scrape_product(request.url)
        
        if not product_data:
            raise HTTPException(status_code=500, detail="Failed to scrape product data")
        
        # Save to database
        if not DatabaseManager.save_product(product_data):
            raise HTTPException(status_code=500, detail="Failed to save product data")
        
        # Get price history for response
        history_data = DatabaseManager.get_product_with_history(product_data['asin'])
        price_history = history_data['price_history'] if history_data else []
        
        # Calculate price change (if we have previous data)
        price_change = 0.0
        price_change_percent = 0.0
        
        if len(price_history) > 1:
            current_price = price_history[-1][0]
            previous_price = price_history[-2][0]
            price_change = current_price - previous_price
            price_change_percent = (price_change / previous_price) * 100 if previous_price > 0 else 0
        
        return {
            "success": True,
            "message": "Product tracked successfully",
            "product": {
                "title": product_data['title'],
                "currentPrice": product_data['price'],
                "image": product_data['image_url'],
                "asin": product_data['asin'],
                "priceChange": round(price_change, 2),
                "priceChangePercent": round(price_change_percent, 2),
                "platforms": {
                    "amazon": product_data['price'],
                    "ebay": product_data['price'] * 1.1,  # Mock data
                    "walmart": product_data['price'] * 1.05  # Mock data
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/history/{asin}")
async def get_price_history(asin: str):
    """Get price history for a product"""
    try:
        history_data = DatabaseManager.get_product_with_history(asin)
        
        if not history_data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Format price history
        price_history = []
        for price, timestamp in history_data['price_history']:
            price_history.append({
                "date": timestamp.split(' ')[0],  # Extract date part
                "price": price,
                "platform": "amazon"
            })
        
        # Get statistics
        stats = DatabaseManager.get_price_statistics(asin)
        
        return {
            "success": True,
            "asin": asin,
            "price_history": price_history,
            "statistics": {
                "lowest": stats[0] if stats else 0,
                "highest": stats[1] if stats else 0,
                "average": round(stats[2], 2) if stats else 0,
                "data_points": stats[3] if stats else 0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Scheduler for periodic updates
def setup_scheduler():
    """Setup background scheduler for price updates"""
    scheduler = BackgroundScheduler()
    
    def update_tracked_products():
        """Update all tracked products"""
        print("Running scheduled price update...")
        # This would get all products from DB and update their prices
        # Implementation depends on your requirements
    
    # Run every 6 hours
    scheduler.add_job(
        update_tracked_products, 
        'interval', 
        hours=6,
        id='price_update'
    )
    
    scheduler.start()
    return scheduler

# Startup event
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting PriceTracker API...")
    init_db()
    # setup_scheduler()  # Uncomment if you want scheduled updates
    print("✅ API is ready!")

# For running the server
if __name__ == "__main__":
    # Initialize database
    init_db()
    
    # Run the server
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True
    )
