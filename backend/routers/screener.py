"""
backend/routers/screener.py
---------------------------
GET /api/screen

Accepts filter parameters as query strings and returns a list of
matching stocks with their fundamental data.

Example request:
    GET /api/screen?sector=Technology&min_market_cap=10000000000&max_pe=30&limit=50

Example response:
    [
      {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "sector": "Technology",
        "market_cap": 2800000000000,
        "pe_ratio": 28.4,
        "pb_ratio": 45.2,
        "roe": 1.47,
        "debt_equity": 1.73,
        "dividend_yield": 0.005,
        "beta": 1.24,
        "avg_volume": 58000000
      },
      ...
    ]
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from data.fetcher import YFinanceFetcher
from data.cache import screener_cache

logger = logging.getLogger(__name__)
router = APIRouter()

# ---------------------------------------------------------------------------
# A curated default universe of S&P 500 stocks to screen against.
# In a future version this can be replaced with a dynamic list from Polygon.
# ---------------------------------------------------------------------------

DEFAULT_UNIVERSE = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
    "UNH",  "JNJ",  "JPM",   "V",    "PG",   "MA",   "HD",   "CVX",
    "MRK",  "ABBV", "PEP",   "KO",   "AVGO", "COST", "MCD",  "WMT",
    "BAC",  "CRM",  "ACN",   "LLY",  "TMO",  "CSCO", "ABT",  "DHR",
    "TXN",  "NEE",  "PM",    "RTX",  "UPS",  "AMGN", "QCOM", "IBM",
    "INTU", "SPGI", "AMD",   "INTC", "GS",   "CAT",  "MS",   "BLK",
    "SCHW", "AXP",
]

# ---------------------------------------------------------------------------
# Response model
# ---------------------------------------------------------------------------

class StockSummary(BaseModel):
    ticker:         str
    name:           Optional[str]   = None
    sector:         Optional[str]   = None
    industry:       Optional[str]   = None
    market_cap:     Optional[float] = None
    pe_ratio:       Optional[float] = None
    pb_ratio:       Optional[float] = None
    roe:            Optional[float] = None
    debt_equity:    Optional[float] = None
    dividend_yield: Optional[float] = None
    beta:           Optional[float] = None
    avg_volume:     Optional[float] = None
    ev_ebitda:      Optional[float] = None
    revenue_growth: Optional[float] = None


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.get("/screen", response_model=list[StockSummary])
def screen_stocks(
    # --- Universe ---
    tickers: Optional[str] = Query(
        default=None,
        description="Comma-separated tickers to screen. Defaults to built-in universe."
    ),

    # --- Fundamental filters ---
    sector: Optional[str] = Query(default=None, description="e.g. Technology"),
    industry: Optional[str] = Query(default=None, description="e.g. Semiconductors"),

    min_market_cap: Optional[float] = Query(default=None, description="Minimum market cap in USD"),
    max_market_cap: Optional[float] = Query(default=None, description="Maximum market cap in USD"),

    min_pe: Optional[float] = Query(default=None, description="Minimum P/E ratio"),
    max_pe: Optional[float] = Query(default=None, description="Maximum P/E ratio"),

    min_pb: Optional[float] = Query(default=None, description="Minimum P/B ratio"),
    max_pb: Optional[float] = Query(default=None, description="Maximum P/B ratio"),

    min_roe: Optional[float] = Query(default=None, description="Minimum ROE (e.g. 0.15 = 15%)"),
    
    max_debt_equity: Optional[float] = Query(default=None, description="Maximum debt/equity ratio"),

    min_dividend_yield: Optional[float] = Query(default=None, description="Minimum dividend yield"),

    min_beta: Optional[float] = Query(default=None, description="Minimum beta"),
    max_beta: Optional[float] = Query(default=None, description="Maximum beta"),

    # --- Result controls ---
    limit: int = Query(default=50, ge=1, le=200, description="Max results to return"),
    sort_by: str = Query(default="market_cap", description="Field to sort results by"),
    ascending: bool = Query(default=False, description="Sort ascending"),
):
    # Build cache key fromm all query params
    cache_key = (
        f"screen:{tickers}:{sector}:{industry}:{min_market_cap}:{max_market_cap}:"
        f"{min_pe}:{max_pe}:{min_pb}:{max_pb}:{min_roe}:{max_debt_equity}:"
        f"{min_dividend_yield}:{min_beta}:{max_beta}:{limit}:{sort_by}:{ascending}"
    )

    cached = screener_cache.get(cache_key)
    if cached is not None:
        logger.info("Cache hit for %s", cache_key)
        return cached

    # Resolve universe
    universe = (
        [t.strip().upper() for t in tickers.split(",")]
        if tickers
        else DEFAULT_UNIVERSE
    )

    # Fetch fundamentals
    try:
        fetcher = YFinanceFetcher()
        df = fetcher.get_fundamentals_bulk(universe)
    except Exception as e:
        logger.error("Fetcher error: %s", e)
        raise HTTPException(status_code=502, detail="Failed to fetch market data")

    if df.empty:
        return []

    # --- Apply filters ---
    if sector:
        df = df[df["sector"].str.lower() == sector.lower()]
    if industry:
        df = df[df["industry"].str.lower() == industry.lower()]
    if min_market_cap is not None:
        df = df[df["market_cap"] >= min_market_cap]
    if max_market_cap is not None:
        df = df[df["market_cap"] <= max_market_cap]
    if min_pe is not None:
        df = df[df["pe_ratio"] >= min_pe]
    if max_pe is not None:
        df = df[df["pe_ratio"] <= max_pe]
    if min_pb is not None:
        df = df[df["pb_ratio"] >= min_pb]
    if max_pb is not None:
        df = df[df["pb_ratio"] <= max_pb]
    if min_roe is not None:
        df = df[df["roe"] >= min_roe]
    if max_debt_equity is not None:
        df = df[df["debt_equity"] <= max_debt_equity]
    if min_dividend_yield is not None:
        df = df[df["dividend_yield"] >= min_dividend_yield]
    if min_beta is not None:
        df = df[df["beta"] >= min_beta]
    if max_beta is not None:
        df = df[df["beta"] <= max_beta]

    # --- Sort ---
    if sort_by in df.columns:
        df = df.sort_values(sort_by, ascending=ascending, na_position="last")

    # --- Limit & serialize ---
    df = df.head(limit).reset_index() # brings 'ticker' back as a column
    results = df.to_dict(orient="records")

    # Clean NaN -> None so Pydantic/JSON don't choke
    import math
    cleaned = [
        {k: (None if isinstance(v, float) and math.isnan(v) else v)
        for k, v in row.items()}
        for row in results
    ]

    screener_cache.set(cache_key, cleaned)
    return cleaned