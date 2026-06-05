# Stock Screener

A full-stack stock screening dashboard built with React and FastAPI. Filter stocks by fundamental metrics, view key financial ratios, and explore interactive candlestick price charts powered by real market data.

![Stock Screener](https://img.shields.io/badge/Status-In%20Development-blue)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![React](https://img.shields.io/badge/React-19-61DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688)

---

## Features

- **Stock Screener** — filter a universe of large-cap stocks by sector, P/E ratio, market cap, beta, ROE, debt/equity, and dividend yield
- **Sortable Table** — click any column header to sort results ascending or descending
- **Stock Detail Page** — click any ticker to view a full profile including company info, key fundamentals, 52-week range, and price history
- **Candlestick Chart** — interactive price chart powered by TradingView's lightweight-charts library with 1m, 3m, 6m, 1y, and 2y period selectors
- **Caching** — in-memory TTL cache on the backend prevents redundant API calls and keeps the UI snappy
- **Loading Skeletons** — smooth loading states throughout the UI

---

## Tech Stack

### Backend
| Tool | Purpose |
|------|---------|
| FastAPI | REST API framework |
| Uvicorn | ASGI server |
| Polygon.io | Real-time and historical price data (OHLCV) |
| yfinance | Fundamental data (P/E, ROE, market cap, etc.) |
| Pydantic | Request/response validation |
| httpx | Async-friendly HTTP client with retry logic |

### Frontend
| Tool | Purpose |
|------|---------|
| React 19 | UI framework |
| Vite | Build tool and dev server |
| TanStack Query | Data fetching, caching, and loading states |
| React Router | Client-side routing |
| lightweight-charts | TradingView candlestick charting library |
| Tailwind CSS | Utility-first styling |
| Axios | HTTP client |

---

## Architecture

```
React (Vite, port 5173)
        │
        │  HTTP (axios + TanStack Query)
        ▼
FastAPI (Uvicorn, port 8000)
        │
        ├── routers/screener.py   GET /api/screen
        ├── routers/stocks.py     GET /api/stocks/{ticker}
        │                         GET /api/stocks/{ticker}/bars
        │
        ├── data/cache.py         In-memory TTL cache
        └── data/fetcher.py
                │
                ├── PolygonFetcher   → Polygon.io API (price bars)
                └── YFinanceFetcher  → Yahoo Finance (fundamentals)
```

The backend follows a clean separation of concerns — routers handle HTTP, fetchers handle I/O, and the cache layer sits between them. Swapping out a data provider means only touching `fetcher.py`.

---

## Project Structure

```
stock_screener/
├── backend/
│   ├── main.py                  # FastAPI app entry point, CORS config
│   ├── routers/
│   │   ├── screener.py          # GET /api/screen
│   │   └── stocks.py            # GET /api/stocks/{ticker}
│   ├── data/
│   │   ├── fetcher.py           # Polygon.io + yfinance API clients
│   │   └── cache.py             # In-memory TTL cache
│   ├── .env                     # API keys (gitignored)
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── api/
    │   │   └── client.js        # Axios client + API call functions
    │   ├── components/
    │   │   ├── ScreenerTable.jsx
    │   │   ├── FilterPanel.jsx
    │   │   └── PriceChart.jsx
    │   ├── pages/
    │   │   └── StockDetail.jsx
    │   ├── App.jsx
    │   └── main.jsx
    ├── tailwind.config.js
    └── package.json
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- A free [Polygon.io](https://polygon.io) API key

### 1. Clone the repository

```bash
git clone https://github.com/SeanIversDev/stock-screener.git
cd stock-screener
```

### 2. Set up the backend

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` folder:

```
POLYGON_API_KEY=your_polygon_key_here
```

Start the backend server:

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.
Auto-generated docs at `http://localhost:8000/docs`.

### 3. Set up the frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/screen` | Screen stocks with optional filters |
| GET | `/api/stocks/{ticker}` | Company profile and fundamentals |
| GET | `/api/stocks/{ticker}/bars` | OHLCV price history |

### Screener query parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `sector` | string | e.g. `Technology` |
| `min_market_cap` | float | Minimum market cap in USD |
| `max_market_cap` | float | Maximum market cap in USD |
| `min_pe` | float | Minimum P/E ratio |
| `max_pe` | float | Maximum P/E ratio |
| `min_roe` | float | Minimum ROE (e.g. `0.15` = 15%) |
| `max_debt_equity` | float | Maximum debt/equity ratio |
| `min_beta` | float | Minimum beta |
| `max_beta` | float | Maximum beta |
| `min_dividend_yield` | float | Minimum dividend yield |
| `limit` | int | Max results (default 50, max 200) |
| `sort_by` | string | Field to sort by (default `market_cap`) |
| `ascending` | bool | Sort direction (default `false`) |

---

## Roadmap

- [ ] Expand universe to full S&P 500
- [ ] Deploy backend to Railway or Render
- [ ] Deploy frontend to Vercel
- [ ] Add technical indicator filters (RSI, moving averages)
- [ ] Stock comparison view (side-by-side fundamentals)
- [ ] Portfolio tracker

---

## Author

**Sean Ivers**
GitHub: [SeanIversDev](https://github.com/SeanIversDev)
