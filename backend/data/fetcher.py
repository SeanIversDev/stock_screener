"""
data/fetcher.py
---------------
All outbound API calls live here.
Supports Polygon.io (price/market data) and yfinance (fundamentals).

Usage:
    from data.fetcher import PolygonFetcher, YFinanceFetcher

    poly = PolygonFetcher()
    bars = poly.get_daily_bars("AAPL", from_date="2024-01-01", to_date="2024-12-31")

    yf = YFinanceFetcher()
    profile = yf.get_fundamentals("AAPL")
    bulk = yf.get_fundamentals_bulk(["AAPL", "MSFT", "GOOGL])
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Base client (shared retry / error-handling logic)
# -------------------------------------------------------------------

class BaseClient:
    """Thin HTTP client with retry logic and rate-limit back-off."""

    def __init__(self, base_url: str, api_key: str, max_retries: int = 3):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.max_retries = max_retries
        self._client = httpx.Client(timeout=15.0)

    def _get(self, path: str, params: dict | None = None) -> dict:
        """GET with exponential back-off on 429 / 5xx."""
        url = f"{self.base_url}{path}"
        params = params or {}

        for attempt in range(self.max_retries):
            try:
                response = self._client.get(url, params=params)

                if response.status_code == 429:
                    wait = 2 ** attempt # exponential back-off
                    logger.warning("Rate limited. Retrying in %ss...", wait)
                    time.sleep(wait)
                    continue

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                logger.error("HTTP error %s for %s: %s", e.response.status_code, url, e)
                if attempt == self.max_retries - 1:
                    raise
            except httpx.RequestError as e:
                logger.error("Request failed for %s: %s", url, e)
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(1)

        raise RuntimeError(f"All {self.max_retries} attempts failed for {url}")

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

# --------------------------------------------------------------------
# Polygon.io - price & market data
# --------------------------------------------------------------------

class PolygonFetcher(BaseClient):
    """
    Wraps key Polygon.io endpoints.
    Docs: https://polygon.io/docs

    Set POLYGON_API_KEY in your .env file.
    """

    BASE_URL = "https://api.polygon.io"

    def __init__(self):
        key = os.getenv("POLYGON_API_KEY")
        if not key:
            raise EnvironmentError("POLYGON_API_KEY not set in environment.")
        super().__init__(self.BASE_URL, api_key=key)

    # -- Tickers ------------------------------------------------------

    def get_tickers(
        self,
        market: str = "stocks",
        exchange: str = "XNAS", # XNAS = Nasdaq, XNYS = NYSE
        active: bool = True,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        List tradable tickers. Returns a DataFrame with at minimum:
            ticker, name, market, primary_exchange, currency_name
        """
        
        params = {
            "market": market,
            "exchange": exchange,
            "active": str(active).lower(),
            "limit": limit,
            "apiKey": self.api_key,
        }
        data = self._get("/v3/reference/tickers", params)
        results = data.get("results", [])
        return pd.DataFrame(results)

    # -- OHLCV bars ---------------------------------------------------

    def get_daily_bars(
        self,
        ticker: str,
        from_date: str | None = None,
        to_date: str | None = None,
        adjusted: bool = True,
        limit: int = 365,
    ) -> pd.DataFrame:
        """
        Daily OHLCV bars for a single ticker.

        Args:
            ticker: e.g. "AAPL"
            from_date: "YYYY-MM-DD" (defaults to 1 year ago)
            to_date: "YYYY-MM-DD" (defaults to today)
            adjusted: split/dividend-adjusted prices
            limit: max bars returned

        Returns DataFrame with columns:
            date, open, high, low, close, volume, vwap
        """
        to_date = to_date or datetime.today().strftime("%Y-%m-%d")
        from_date = from_date or (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")

        params = {
            "adjusted": str(adjusted).lower(),
            "sort": "asc",
            "limit": limit,
            "apiKey": self.api_key,
        }
        data = self._get(f"/v2/aggs/ticker/{ticker}/range/1/day/{from_date}/{to_date}", params)
        
        results = data.get("results", [])
        if not results:
            logger.warning("No bars returned for %s", ticker)
            return pd.DataFrame()

        df = pd.DataFrame(results)
        # print(df.columns.tolist())
        # print(df.head(2))
        rename_map = {
            "t": "timestamp", "o": "open", "h": "high",
            "l": "low", "c": "close", "v": "volume",
            "vw": "vwap", "n": "trades"}
        df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)
        df["date"] = pd.to_datetime(df["timestamp"], unit="ms").dt.date
        df.set_index("date", inplace=True)
        return df[['open', 'high', 'low', 'close', 'volume', 'vwap']]

    # -- Snapshot (latest quote) --------------------------------------------------

    def get_snapshot(self, tickers: list[str]) -> pd.DataFrame:
        """
        Latest quote + day stats for a list of tickers.
        Returns a flat DataFrame with one row per ticker.
        """
        params = {
            "tickers": ",".join(tickers),
            "apiKey": self.api_key,
        }
        data = self._get("/v2/snapshot/locale/us/markets/stocks/tickers", params)

        rows = []
        for item in data.get("tickers", []):
            day = item.get("day", {})
            prev = item.get("prevDay", {})
            rows.append({
                "ticker":       item.get("ticker"),
                "price":        item.get("lastTrade", {}).get("p"),
                "change_pct":   item.get("todaysChangePercent"),
                "volume":       day.get("v"),
                "open":         day.get("o"),
                "high":         day.get("h"),
                "low":          day.get("l"),
                "close":        day.get("c"),
                "prev_close":   prev.get("c"),
            })
        return pd.DataFrame(rows)


# -------------------------------------------------------------------
# yfinance - fundamentals (no API key required)
# -------------------------------------------------------------------

class YFinanceFetcher:
    """
    Wraps yfinance for fundamental data.
    No API key required - uses Yahoo Finance under the hood.
    Not suitable for high-frequency production use, but solid for
    development and personal screeners.
    """

    # Fields pulled from yfinance .info for each ticker
    FIELDS = {
        "longName":           "name",
        "sector":             "sector",
        "industry":           "industry",
        "marketCap":          "market_cap",
        "trailingPE":         "pe_ratio",
        "forwardPE":          "pe_forward",
        "priceToBook":        "pb_ratio",
        "returnOnEquity":     "roe",
        "returnOnAssets":     "roa",
        "debtToEquity":       "debt_equity",
        "currentRatio":       "current_ratio",
        "revenueGrowth":      "revenue_growth",
        "earningsGrowth":     "earnings_growth",
        "dividendYield":      "dividend_yield",
        "beta":               "beta",
        "fiftyTwoWeekHigh":   "week52_high",
        "fiftyTwoWeekLow":    "week52_low",
        "averageVolume":      "avg_volume",
        "enterpriseToEbitda": "ev_ebitda",
        "freeCashflow":       "free_cashflow",
    }

    def get_fundamentals(self, ticker: str) -> dict:
        """
        Fetch fundamental data for a single ticker.
        Returns a flat dict with normalized field names.
        """
        try:
            info = yf.Ticker(ticker).info
        except Exception as e:
            logger.error("yfinance error for %s: %s", ticker, e)
            return {"ticker": ticker}

        result = {"ticker": ticker}
        for yf_key, our_key in self.FIELDS.items():
            result[our_key] = info.get(yf_key)
        return result
    
    def get_fundamentals_bulk(self, tickers: list[str]) -> pd.DataFrame:
        """
        Fetch fundamentals for a list of tickers.
        Returns a DataFrame with one row per ticker.

        Note: makes one HTTP call per ticker - keep lists under ~100
        to avoid long waits. Use cache.py to avoid repeat fetches.
        """
        rows = []
        for ticker in tickers:
            logger.info("Fetching fundamentals for %s", ticker)
            rows.append(self.get_fundamentals(ticker))
        return pd.DataFrame(rows).set_index("ticker")



# --------------------------------------------------------------------
# Quick smoke test - run this file directly to verify your keys work
# --------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("\n=== Polygon: AAPL last 5 daily bars ===")
    with PolygonFetcher() as poly:
        bars = poly.get_daily_bars("AAPL", limit=5)
        print(bars.tail())

    print("\n=== yfinance: fundamentals for AAPL, MSFT, GOOGL ===")
    yff = YFinanceFetcher()
    df = yff.get_fundamentals_bulk(["AAPL", "MSFT", "GOOGL"])
    print(df[["name", "sector", "pe_ratio", "pb_ratio", "market_cap"]].to_string())