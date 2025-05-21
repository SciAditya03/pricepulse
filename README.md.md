PricePulse Tracker -- AI-Powered Price Monitoring

Overview

PricePulse Tracker is an AI-powered price tracking tool that helps users
monitor Amazon product prices, visualize historical trends, and compare
similar products across multiple e-commerce platforms like Flipkart and
Meesho using LLM-based product matching .

The system includes:

\- Automated Scraper (Playwright) for fetching Amazon product details
every 30 minutes .

\- FastAPI Backend for managing product tracking requests.

\- React Frontend for user-friendly interaction and price visualization.

\- AI-Powered Search to find similar products across multiple platforms.

\- Database for storing historical price data.

\-\--

Tech Stack

\- Scraping: Playwright (for dynamic content handling)

\- Backend: FastAPI (efficient API routing)

\- Frontend: React (UI with Chart.js for visualization)

\- Database: SQLite/PostgreSQL (for storing price trends)

\- Scheduler: APScheduler (automates periodic scraping)

\- AI Matching: LLMs + Serper API (Google-powered product comparison)

\-\--

Project Structure

\`\`\`

pricepulse-tracker/

├── backend/

│ ├── main.py FastAPI entry point

│ ├── scraper.py Scrapes product details using Playwright

│ ├── scheduler.py Automates scraping every 30 minutes

│ ├── database.py Stores product prices for historical analysis

├── frontend/

│ ├── public/

│ ├── src/

│ │ ├── App.jsx Main UI for tracking products

│ │ ├── components/ Reusable UI components

│ │ ├── styles/ Frontend styling (Tailwind CSS)

├── requirements.txt Dependencies for backend

├── README.md Documentation

└── .gitignore Ignored files in version control

\`\`\`

\-\--

Installation & Setup

1\. Backend Setup (FastAPI)

\`\`\`bash

Clone repository

git clone \<repository-url\>

cd pricepulse-tracker/backend

Install dependencies

pip install -r requirements.txt

Start API server

uvicorn main:app \--reload

\`\`\`

API Endpoint Example:

\- \`/track-price?url=\<Amazon-Product-URL\>\` → Returns real-time
price.

\-\--

2\. Scraper Setup (Playwright)

\`\`\`bash

Install Playwright and dependencies

pip install playwright

playwright install

Run scraper

python scraper.py

\`\`\`

This will fetch the latest product price and store it in the database.

\-\--

3\. Frontend Setup (React)

\`bash

cd pricepulse-tracker/frontend

Install dependencies

npm install

Start frontend server

npm start

\`\`\`

User can enter an Amazon product URL , view price trends, and see
alternative platform comparisons.

Features

✅ Real-Time Price Tracking -- Automatically records Amazon prices every
30 minutes.

✅ Historical Price Visualization -- Uses Chart.js to display price
trends.

✅ Multi-Platform AI Comparison -- Finds similar products across
Flipkart, Meesho, etc.

✅ Scalable Backend with FastAPI -- High-performance API handling.

✅ Scheduled Scraping & Data Logging -- Ensures consistency in price
records.

\-\--

Future Enhancements

🚀 Enhance AI Matching → Improve product identification across
platforms.

🚀 Deploy API on Cloud → Host backend on AWS/GCP for scalability.

🚀 Optimized Web Scraping → Improve efficiency and handle captchas
dynamically.

🚀 User Authentication → Secure user activity with login/signup.

References & Tools

📌 Playwright Guide -- \[YouTube: Playwright
Tutorial\](https://www.youtube.com/)

📌 FastAPI Crash Course -- \[FastAPI
Documentation\](https://fastapi.tiangolo.com/)

📌 React Form Handling -- \[React.js Form Guide\](https://reactjs.org/)

📌 Serper API for Google Search -- \[Serper.dev\](https://serper.dev/)
