"""
backend/main.py
---------------
FastAPI application entry point.

Run with:
    uvicorn main.app --reload --port 8000

API docs auto-generated at:
    http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import screener
from routers import stocks

app = FastAPI(
    title="Stock Screener API",
    version="0.1.0",
)

# ---------------------------------------------------------------------
# CORS - allow the React dev server (port 5173) to call this API
# ---------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", # Vite dev server
        "http://localhost:3000", # fallback
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------------
# Routers
# ----------------------------------------------------------------------
app.include_router(screener.router, prefix="/api")
app.include_router(stocks.router, prefix="/api")

# ----------------------------------------------------------------------
# Health check
# ----------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}