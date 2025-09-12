"""
Database manager for SQLite operations
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

from .models import StockData, TechnicalIndicators, WatchlistTicker
from config.settings import DATABASE_PATH, CACHE_DURATION_MINUTES

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database operations for stock data"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_PATH
        self._ensure_database_directory()
        self._create_tables()
    
    def _ensure_database_directory(self):
        """Ensure the database directory exists"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Stock data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    datetime TIMESTAMP NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume INTEGER NOT NULL,
                    period TEXT NOT NULL,
                    interval TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(ticker, datetime, period, interval)
                )
            """)
            
            # Technical indicators table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS technical_indicators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    datetime TIMESTAMP NOT NULL,
                    sma_20 REAL,
                    sma_50 REAL,
                    sma_100 REAL,
                    sma_200 REAL,
                    ema_20 REAL,
                    rsi_14 REAL,
                    macd REAL,
                    macd_signal REAL,
                    bb_upper REAL,
                    bb_middle REAL,
                    bb_lower REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(ticker, datetime)
                )
            """)
            
            # Watchlist table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS watchlist_tickers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL UNIQUE,
                    company_name TEXT NOT NULL,
                    sector TEXT,
                    added_date TIMESTAMP,
                    notes TEXT,
                    target_price REAL,
                    stop_loss REAL,
                    is_active BOOLEAN DEFAULT 1,
                    priority INTEGER DEFAULT 3,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_stock_data_ticker_datetime 
                ON stock_data(ticker, datetime)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_technical_indicators_ticker_datetime 
                ON technical_indicators(ticker, datetime)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_watchlist_ticker 
                ON watchlist_tickers(ticker)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_watchlist_active_priority 
                ON watchlist_tickers(is_active, priority)
            """)
            
            conn.commit()
            
            # Run migrations for existing databases
            self._run_migrations()
    
    def _run_migrations(self):
        """Run database migrations for schema updates"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if new SMA columns exist, if not add them
            cursor.execute("PRAGMA table_info(technical_indicators)")
            columns = [column[1] for column in cursor.fetchall()]
            
            new_columns = ['sma_50', 'sma_100', 'sma_200']
            for column in new_columns:
                if column not in columns:
                    cursor.execute(f"ALTER TABLE technical_indicators ADD COLUMN {column} REAL")
                    logging.info(f"Added column {column} to technical_indicators table")
            
            conn.commit()
    
    def save_stock_data(self, stock_data_list: List[StockData]) -> bool:
        """Save stock data to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for stock_data in stock_data_list:
                    cursor.execute("""
                        INSERT OR REPLACE INTO stock_data 
                        (ticker, datetime, open, high, low, close, volume, period, interval)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        stock_data.ticker,
                        stock_data.datetime,
                        stock_data.open,
                        stock_data.high,
                        stock_data.low,
                        stock_data.close,
                        stock_data.volume,
                        stock_data.period,
                        stock_data.interval
                    ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving stock data: {e}")
            return False
    
    def save_technical_indicators(self, indicators_list: List[TechnicalIndicators]) -> bool:
        """Save technical indicators to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for indicators in indicators_list:
                    cursor.execute("""
                        INSERT OR REPLACE INTO technical_indicators 
                        (ticker, datetime, sma_20, ema_20, rsi_14, macd, macd_signal, bb_upper, bb_middle, bb_lower)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        indicators.ticker,
                        indicators.datetime,
                        indicators.sma_20,
                        indicators.ema_20,
                        indicators.rsi_14,
                        indicators.macd,
                        indicators.macd_signal,
                        indicators.bb_upper,
                        indicators.bb_middle,
                        indicators.bb_lower
                    ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving technical indicators: {e}")
            return False
    
    def get_stock_data(self, ticker: str, period: str, interval: str, 
                      limit: Optional[int] = None) -> pd.DataFrame:
        """Retrieve stock data from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT datetime, open, high, low, close, volume
                    FROM stock_data 
                    WHERE ticker = ? AND period = ? AND interval = ?
                    ORDER BY datetime DESC
                """
                
                if limit:
                    query += f" LIMIT {limit}"
                
                df = pd.read_sql_query(query, conn, params=(ticker, period, interval))
                
                if not df.empty:
                    df['datetime'] = pd.to_datetime(df['datetime'])
                    df = df.sort_values('datetime').reset_index(drop=True)
                
                return df
                
        except Exception as e:
            logger.error(f"Error retrieving stock data: {e}")
            return pd.DataFrame()
    
    def get_technical_indicators(self, ticker: str, limit: Optional[int] = None) -> pd.DataFrame:
        """Retrieve technical indicators from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT datetime, sma_20, ema_20, rsi_14, macd, macd_signal, 
                           bb_upper, bb_middle, bb_lower
                    FROM technical_indicators 
                    WHERE ticker = ?
                    ORDER BY datetime DESC
                """
                
                if limit:
                    query += f" LIMIT {limit}"
                
                df = pd.read_sql_query(query, conn, params=(ticker,))
                
                if not df.empty:
                    df['datetime'] = pd.to_datetime(df['datetime'])
                    df = df.sort_values('datetime').reset_index(drop=True)
                
                return df
                
        except Exception as e:
            logger.error(f"Error retrieving technical indicators: {e}")
            return pd.DataFrame()
    
    def is_data_cached(self, ticker: str, period: str, interval: str) -> bool:
        """Check if data is cached and not expired"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if data exists and is recent
                cutoff_time = datetime.now() - timedelta(minutes=CACHE_DURATION_MINUTES)
                
                cursor.execute("""
                    SELECT COUNT(*) FROM stock_data 
                    WHERE ticker = ? AND period = ? AND interval = ? 
                    AND created_at > ?
                """, (ticker, period, interval, cutoff_time))
                
                count = cursor.fetchone()[0]
                return count > 0
                
        except Exception as e:
            logger.error(f"Error checking cache: {e}")
            return False
    
    def clear_old_data(self, days_to_keep: int = 30):
        """Clear old data to keep database size manageable"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=days_to_keep)
                
                # Clear old stock data
                cursor.execute("""
                    DELETE FROM stock_data WHERE created_at < ?
                """, (cutoff_date,))
                
                # Clear old technical indicators
                cursor.execute("""
                    DELETE FROM technical_indicators WHERE created_at < ?
                """, (cutoff_date,))
                
                conn.commit()
                
                logger.info(f"Cleared data older than {days_to_keep} days")
                
        except Exception as e:
            logger.error(f"Error clearing old data: {e}")
    
    # Watchlist methods
    def add_watchlist_ticker(self, watchlist_ticker: WatchlistTicker) -> bool:
        """Add a ticker to the watchlist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO watchlist_tickers 
                    (ticker, company_name, sector, added_date, notes, target_price, 
                     stop_loss, is_active, priority, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    watchlist_ticker.ticker,
                    watchlist_ticker.company_name,
                    watchlist_ticker.sector,
                    watchlist_ticker.added_date,
                    watchlist_ticker.notes,
                    watchlist_ticker.target_price,
                    watchlist_ticker.stop_loss,
                    watchlist_ticker.is_active,
                    watchlist_ticker.priority,
                    watchlist_ticker.created_at,
                    watchlist_ticker.updated_at
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error adding watchlist ticker: {e}")
            return False
    
    def get_watchlist_tickers(self, active_only: bool = True) -> List[WatchlistTicker]:
        """Get all tickers from watchlist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT ticker, company_name, sector, added_date, notes, 
                           target_price, stop_loss, is_active, priority, 
                           created_at, updated_at
                    FROM watchlist_tickers
                """
                
                if active_only:
                    query += " WHERE is_active = 1"
                
                query += " ORDER BY priority ASC, added_date DESC"
                
                cursor.execute(query)
                rows = cursor.fetchall()
                
                watchlist_tickers = []
                for row in rows:
                    # Convert string dates to datetime objects
                    added_date = None
                    created_at = None
                    updated_at = None
                    
                    if row[3]:  # added_date
                        try:
                            added_date = datetime.fromisoformat(row[3].replace('Z', '+00:00'))
                        except (ValueError, AttributeError):
                            added_date = None
                    
                    if row[9]:  # created_at
                        try:
                            created_at = datetime.fromisoformat(row[9].replace('Z', '+00:00'))
                        except (ValueError, AttributeError):
                            created_at = None
                    
                    if row[10]:  # updated_at
                        try:
                            updated_at = datetime.fromisoformat(row[10].replace('Z', '+00:00'))
                        except (ValueError, AttributeError):
                            updated_at = None
                    
                    ticker = WatchlistTicker(
                        ticker=row[0],
                        company_name=row[1],
                        sector=row[2],
                        added_date=added_date,
                        notes=row[4],
                        target_price=row[5],
                        stop_loss=row[6],
                        is_active=bool(row[7]),
                        priority=row[8],
                        created_at=created_at,
                        updated_at=updated_at
                    )
                    watchlist_tickers.append(ticker)
                
                return watchlist_tickers
                
        except Exception as e:
            logger.error(f"Error getting watchlist tickers: {e}")
            return []
    
    def is_ticker_in_watchlist(self, ticker: str) -> bool:
        """Check if a ticker is already in the watchlist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT COUNT(*) FROM watchlist_tickers 
                    WHERE ticker = ? AND is_active = 1
                """, (ticker,))
                
                count = cursor.fetchone()[0]
                return count > 0
                
        except Exception as e:
            logger.error(f"Error checking if ticker in watchlist: {e}")
            return False
    
    def remove_watchlist_ticker(self, ticker: str) -> bool:
        """Remove a ticker from the watchlist (set is_active to False)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE watchlist_tickers 
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE ticker = ?
                """, (ticker,))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error removing watchlist ticker: {e}")
            return False
    
    def update_watchlist_ticker(self, ticker: str, **kwargs) -> bool:
        """Update a ticker in the watchlist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build dynamic update query
                set_clauses = []
                values = []
                
                for key, value in kwargs.items():
                    if key in ['notes', 'target_price', 'stop_loss', 'priority', 'is_active', 'updated_at']:
                        set_clauses.append(f"{key} = ?")
                        values.append(value)
                
                if not set_clauses:
                    return False
                
                values.append(ticker)
                
                query = f"""
                    UPDATE watchlist_tickers 
                    SET {', '.join(set_clauses)}
                    WHERE ticker = ?
                """
                
                cursor.execute(query, values)
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error updating watchlist ticker: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count records in each table
                cursor.execute("SELECT COUNT(*) FROM stock_data")
                stock_data_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM technical_indicators")
                indicators_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM watchlist_tickers WHERE is_active = 1")
                watchlist_count = cursor.fetchone()[0]
                
                # Get unique tickers
                cursor.execute("SELECT DISTINCT ticker FROM stock_data")
                tickers = [row[0] for row in cursor.fetchall()]
                
                return {
                    'stock_data_records': stock_data_count,
                    'indicators_records': indicators_count,
                    'watchlist_records': watchlist_count,
                    'unique_tickers': len(tickers),
                    'tickers': tickers,
                    'database_size_mb': self.db_path.stat().st_size / (1024 * 1024) if self.db_path.exists() else 0
                }
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def get_company_name(self, ticker: str) -> Optional[str]:
        """Get company name for a ticker from the watchlist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT company_name FROM watchlist_tickers 
                    WHERE ticker = ? AND is_active = 1
                """, (ticker,))
                
                result = cursor.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            logger.error(f"Error getting company name for {ticker}: {e}")
            return None