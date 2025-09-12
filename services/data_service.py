"""
Data service for fetching and processing stock data
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
import logging
from typing import Optional, List, Dict, Any

from database.database_manager import DatabaseManager
from database.models import StockData
from config.settings import INTERVAL_MAPPING, CACHE_DURATION_MINUTES

logger = logging.getLogger(__name__)


class DataService:
    """Service for fetching and processing stock data"""
    
    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()
    
    def fetch_stock_data(self, ticker: str, period: str, interval: str = None, 
                        use_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        Fetch stock data from Yahoo Finance or cache
        
        Args:
            ticker: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, etc.)
            interval: Data interval (1m, 5m, 1h, etc.)
            use_cache: Whether to use cached data if available
            
        Returns:
            DataFrame with stock data or None if error
        """
        try:
            # Use interval mapping if not provided
            if interval is None:
                interval = INTERVAL_MAPPING.get(period, '1d')
            
            # Check cache first
            if use_cache and self.db_manager.is_data_cached(ticker, period, interval):
                logger.info(f"Using cached data for {ticker}")
                cached_data = self.db_manager.get_stock_data(ticker, period, interval)
                if not cached_data.empty:
                    return cached_data
            
            # Fetch fresh data
            logger.info(f"Fetching fresh data for {ticker}")
            data = self._fetch_from_yahoo(ticker, period, interval)
            
            if data is not None and not data.empty:
                # Save to cache
                self._save_to_cache(data, ticker, period, interval)
                return data
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching stock data for {ticker}: {e}")
            return None
    
    def _fetch_from_yahoo(self, ticker: str, period: str, interval: str) -> Optional[pd.DataFrame]:
        """Fetch data from Yahoo Finance API"""
        try:
            end_date = datetime.now()
            if period == '1wk':
                start_date = end_date - timedelta(days=7)
            elif period == 'max':
                start_date = end_date - timedelta(days=365*10)  # 10 years for max
            else:
                # Parse period like '1d', '5d', '1mo', etc.
                if period.endswith('d'):
                    days = int(period[:-1])
                    start_date = end_date - timedelta(days=days)
                elif period.endswith('mo'):
                    months = int(period[:-2])
                    start_date = end_date - timedelta(days=months*30)
                elif period.endswith('y'):
                    years = int(period[:-1])
                    start_date = end_date - timedelta(days=years*365)
                else:
                    start_date = end_date - timedelta(days=1)
            
            data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
            
            if data.empty:
                logger.warning(f"No data found for {ticker}")
                return None
            
            # Flatten columns and process data
            data = self._flatten_columns(data)
            data = self._process_data(data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching from Yahoo Finance: {e}")
            return None
    
    def _flatten_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """Flatten hierarchical column names from yfinance data"""
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            data.columns.name = None
            data.index.name = "Date"
        return data
    
    def _process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Process and format the data"""
        # Handle timezone
        if data.index.tzinfo is None:
            data.index = data.index.tz_localize('UTC')
        data.index = data.index.tz_convert('US/Eastern')
        
        # Reset index and rename
        data.reset_index(inplace=True)
        data.rename(columns={'Date': 'Datetime'}, inplace=True)
        
        return data
    
    def _save_to_cache(self, data: pd.DataFrame, ticker: str, period: str, interval: str):
        """Save data to database cache"""
        try:
            stock_data_list = []
            
            for _, row in data.iterrows():
                stock_data = StockData(
                    ticker=ticker,
                    datetime=row['Datetime'],
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=int(row['Volume']),
                    period=period,
                    interval=interval
                )
                stock_data_list.append(stock_data)
            
            self.db_manager.save_stock_data(stock_data_list)
            logger.info(f"Cached {len(stock_data_list)} records for {ticker}")
            
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")
    
    def get_real_time_prices(self, tickers: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get real-time prices for multiple tickers"""
        real_time_data = {}
        
        for ticker in tickers:
            try:
                data = self.fetch_stock_data(ticker, '1d', '1m', use_cache=False)
                if data is not None and not data.empty:
                    last_price = float(data['Close'].iloc[-1])
                    first_price = float(data['Open'].iloc[0])
                    change = last_price - first_price
                    pct_change = (change / first_price) * 100
                    
                    real_time_data[ticker] = {
                        'price': last_price,
                        'change': change,
                        'pct_change': pct_change
                    }
                    
            except Exception as e:
                logger.error(f"Error getting real-time price for {ticker}: {e}")
                real_time_data[ticker] = {
                    'price': 0.0,
                    'change': 0.0,
                    'pct_change': 0.0
                }
        
        return real_time_data
    
    def calculate_basic_metrics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic metrics from stock data"""
        if data.empty:
            return {}
        
        try:
            last_close = float(data['Close'].iloc[-1])
            prev_close = float(data['Close'].iloc[0])
            change = last_close - prev_close
            pct_change = (change / prev_close) * 100
            high = float(data['High'].max())
            low = float(data['Low'].min())
            volume = int(data['Volume'].sum())
            
            return {
                'last_close': last_close,
                'change': change,
                'pct_change': pct_change,
                'high': high,
                'low': low,
                'volume': volume
            }
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return {}
    
    def get_available_tickers(self) -> List[str]:
        """Get list of available tickers from database"""
        try:
            stats = self.db_manager.get_database_stats()
            return stats.get('tickers', [])
        except Exception as e:
            logger.error(f"Error getting available tickers: {e}")
            return []
