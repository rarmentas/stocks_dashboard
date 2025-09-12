"""
Configuration settings for the Stock Dashboard application
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Database settings
DATABASE_PATH = BASE_DIR / "data" / "stock_dashboard.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# API settings
DEFAULT_TICKERS = ['AAPL', 'GOOGL', 'AMZN', 'MSFT', 'TSLA', 'NVDA']
DEFAULT_TIME_PERIODS = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '5y', 'max']

# Chart settings
CHART_TYPES = ['Candlestick', 'Line']
TECHNICAL_INDICATORS = ['SMA 20', 'SMA 50', 'SMA 100', 'SMA 200', 'EMA 20', 'RSI 14', 'MACD', 'Bollinger Bands']

# Interval mapping for different time periods
INTERVAL_MAPPING = {
    '1d': '1m',
    '5d': '5m',
    '1mo': '1h',
    '3mo': '1d',
    '6mo': '1d',
    '1y': '1wk',
    '5y': '1mo',
    'max': '1mo',
}

# Cache settings
CACHE_DURATION_MINUTES = 5  # How long to cache stock data

# UI settings
CHART_HEIGHT = 600
SIDEBAR_WIDTH = 300
