"""
Database models for stock data storage
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import pandas as pd


@dataclass
class StockData:
    """Stock data model"""
    ticker: str
    datetime: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    period: str
    interval: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database insertion"""
        return {
            'ticker': self.ticker,
            'datetime': self.datetime,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'period': self.period,
            'interval': self.interval
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StockData':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class TechnicalIndicators:
    """Technical indicators model"""
    ticker: str
    datetime: datetime
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_100: Optional[float] = None
    sma_200: Optional[float] = None
    ema_20: Optional[float] = None
    rsi_14: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database insertion"""
        return {
            'ticker': self.ticker,
            'datetime': self.datetime,
            'sma_20': self.sma_20,
            'sma_50': self.sma_50,
            'sma_100': self.sma_100,
            'sma_200': self.sma_200,
            'ema_20': self.ema_20,
            'rsi_14': self.rsi_14,
            'macd': self.macd,
            'macd_signal': self.macd_signal,
            'bb_upper': self.bb_upper,
            'bb_middle': self.bb_middle,
            'bb_lower': self.bb_lower
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TechnicalIndicators':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class WatchlistTicker:
    """Watchlist ticker model for tracking followed stocks"""
    ticker: str
    company_name: str
    sector: Optional[str] = None
    added_date: Optional[datetime] = None
    notes: Optional[str] = None
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    is_active: bool = True
    priority: int = 3  # Default priority (1-5 scale)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database insertion"""
        return {
            'ticker': self.ticker,
            'company_name': self.company_name,
            'sector': self.sector,
            'added_date': self.added_date,
            'notes': self.notes,
            'target_price': self.target_price,
            'stop_loss': self.stop_loss,
            'is_active': self.is_active,
            'priority': self.priority,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'WatchlistTicker':
        """Create from dictionary"""
        return cls(**data)