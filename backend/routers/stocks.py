"""
backend/routers/stocks.py
-------------------------
GET /api/stocks/{ticker}        - company profile + fundamentals
GET /api/stocks/{ticker}/bars   - OHLCV price history for charts
"""

from ast import NodeTransformer
import logging
import math
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from data.fetcher import PolygonFetcher, YFinanceFetcher
from data.cache import fundamentals_cache, bars_cache

logger = logging.getLogger(__name__)
router = APIRouter()


# -------------------------------------------------------------------
# Response models
# -------------------------------------------------------------------

class StockDetail(BaseModel):
    ticker: str
    name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    employees: Optional[int] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    roe: Optional[float] = None
    debt_equity: Optional[float] = None
    dividend_yield: Optional[float] = None
    beta: Optional[float] = None
    ev_ebitda: Optional[float] = None
    week52_high: Optional[float] = None
    week52_low: Optional[float] = None
    avg_volume: Optional[float] = None
    free_cashflow: Optional[float] = None


class Bar(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float


# -------------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------------

@router.get("/stocks/{ticker}", response_model=StockDetail)
def get_stock_detail(ticker: str):
    ticker = ticker.upper()
    cache_key = f"detail:{ticker}"

    cached = fundamentals_cache.get(cache_key)
    if cached:
        return cached

    try:
        yff = YFinanceFetcher()
        data = yff.get_fundamentals(ticker)

        # Clean NaN -> None
        cleaned = {
            k: (None if isinstance(v, float) and math.isnan(v) else v)
            for k, v in data.items()
        }

        # Fetch extended fields
        import yfinance as yf
        info = yf.Ticker(ticker).info
        cleaned["description"] = info.get("longBusinessSummary")
        cleaned["website"] = info.get("website")
        cleaned["employees"] = info.get("fullTimeEmployees")

    except Exception as e:
        logger.error("Error fetching detail for %s: %s", ticker, e)
        raise HTTPException(status_code=502, detail="Failed to fetch stock data.")

    fundamentals_cache.set(cache_key, cleaned)
    return cleaned


@router.get("/stocks/{ticker}/bars", response_model=list[Bar])
def get_stock_bars(
    ticker: str,
    period: str = Query(default="6m", description="1m, 3m, 6m, 1y, 2y"),
):
    ticker = ticker.upper()
    cache_key = f"bars:{ticker}:{period}"

    cached = bars_cache.get(cache_key)
    if cached:
        return cached
    # Resolve period to date range
    from datetime import datetime, timedelta
    today = datetime.today()
    period_map = {
        "1m": 30,
        "3m": 90,
        "6m": 180,
        "1y": 365,
        "2y": 730,
    }
    days = period_map.get(period, 180)
    from_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")

    try:
        with PolygonFetcher() as poly:
            df = poly.get_daily_bars(ticker, from_date=from_date, to_date=to_date, limit=days)
    except Exception as e:
        logger.error("Error fetching bars for %s: %s", ticker, e)
        raise HTTPException(status_code=502, detail="Failed to fetch price data.")
    
    if df.empty:
        return []

    bars = [
        {
            "date": str(date),
            "open": row["open"],
            "high": row["high"],
            "low": row["low"],
            "close": row["close"],
            "volume": row["volume"],
        }
        for date, row in df.iterrows()
    ]

    bars_cache.set(cache_key, bars)
    return bars