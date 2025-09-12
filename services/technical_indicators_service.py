"""
Technical indicators service for calculating and managing technical analysis indicators
"""

import pandas as pd
import ta
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from database.database_manager import DatabaseManager
from database.models import TechnicalIndicators

logger = logging.getLogger(__name__)


class TechnicalIndicatorsService:
    """Service for calculating and managing technical indicators"""
    
    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()
    
    def calculate_indicators(self, data: pd.DataFrame, ticker: str, 
                           indicators: List[str] = None) -> pd.DataFrame:
        """
        Calculate technical indicators for the given data
        
        Args:
            data: DataFrame with OHLCV data
            ticker: Stock ticker symbol
            indicators: List of indicators to calculate
            
        Returns:
            DataFrame with original data plus technical indicators
        """
        if data.empty:
            return data
        
        try:
            # Default indicators if none specified
            if indicators is None:
                indicators = ['SMA_20', 'EMA_20', 'RSI_14', 'MACD', 'BB']
            
            # Calculate indicators
            for indicator in indicators:
                if indicator == 'SMA_20':
                    data['SMA_20'] = ta.trend.sma_indicator(data['Close'], window=20)
                elif indicator == 'EMA_20':
                    data['EMA_20'] = ta.trend.ema_indicator(data['Close'], window=20)
                elif indicator == 'RSI_14':
                    data['RSI_14'] = ta.momentum.rsi(data['Close'], window=14)
                elif indicator == 'MACD':
                    macd_data = ta.trend.MACD(data['Close'])
                    data['MACD'] = macd_data.macd()
                    data['MACD_Signal'] = macd_data.macd_signal()
                elif indicator == 'BB':
                    bb_data = ta.volatility.BollingerBands(data['Close'])
                    data['BB_Upper'] = bb_data.bollinger_hband()
                    data['BB_Middle'] = bb_data.bollinger_mavg()
                    data['BB_Lower'] = bb_data.bollinger_lband()
                elif indicator == 'SMA_50':
                    data['SMA_50'] = ta.trend.sma_indicator(data['Close'], window=50)
                elif indicator == 'SMA_100':
                    data['SMA_100'] = ta.trend.sma_indicator(data['Close'], window=100)
                elif indicator == 'SMA_200':
                    data['SMA_200'] = ta.trend.sma_indicator(data['Close'], window=200)
                elif indicator == 'RSI_21':
                    data['RSI_21'] = ta.momentum.rsi(data['Close'], window=21)
            
            # Save indicators to database
            self._save_indicators_to_cache(data, ticker)
            
            return data
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return data
    
    def _save_indicators_to_cache(self, data: pd.DataFrame, ticker: str):
        """Save technical indicators to database cache"""
        try:
            indicators_list = []
            
            for _, row in data.iterrows():
                indicators = TechnicalIndicators(
                    ticker=ticker,
                    datetime=row['Datetime'],
                    sma_20=float(row.get('SMA_20', 0)) if pd.notna(row.get('SMA_20')) else None,
                    sma_50=float(row.get('SMA_50', 0)) if pd.notna(row.get('SMA_50')) else None,
                    sma_100=float(row.get('SMA_100', 0)) if pd.notna(row.get('SMA_100')) else None,
                    sma_200=float(row.get('SMA_200', 0)) if pd.notna(row.get('SMA_200')) else None,
                    ema_20=float(row.get('EMA_20', 0)) if pd.notna(row.get('EMA_20')) else None,
                    rsi_14=float(row.get('RSI_14', 0)) if pd.notna(row.get('RSI_14')) else None,
                    macd=float(row.get('MACD', 0)) if pd.notna(row.get('MACD')) else None,
                    macd_signal=float(row.get('MACD_Signal', 0)) if pd.notna(row.get('MACD_Signal')) else None,
                    bb_upper=float(row.get('BB_Upper', 0)) if pd.notna(row.get('BB_Upper')) else None,
                    bb_middle=float(row.get('BB_Middle', 0)) if pd.notna(row.get('BB_Middle')) else None,
                    bb_lower=float(row.get('BB_Lower', 0)) if pd.notna(row.get('BB_Lower')) else None
                )
                indicators_list.append(indicators)
            
            self.db_manager.save_technical_indicators(indicators_list)
            logger.info(f"Cached {len(indicators_list)} technical indicator records for {ticker}")
            
        except Exception as e:
            logger.error(f"Error saving indicators to cache: {e}")
    
    def get_cached_indicators(self, ticker: str, limit: Optional[int] = None) -> pd.DataFrame:
        """Get cached technical indicators from database"""
        try:
            return self.db_manager.get_technical_indicators(ticker, limit)
        except Exception as e:
            logger.error(f"Error getting cached indicators: {e}")
            return pd.DataFrame()
    
    def get_indicator_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Get summary of current indicator values"""
        if data.empty:
            return {}
        
        try:
            latest = data.iloc[-1]
            summary = {}
            
            # SMA/EMA
            if 'SMA_20' in data.columns and pd.notna(latest['SMA_20']):
                summary['sma_20'] = float(latest['SMA_20'])
            if 'SMA_50' in data.columns and pd.notna(latest['SMA_50']):
                summary['sma_50'] = float(latest['SMA_50'])
            if 'SMA_100' in data.columns and pd.notna(latest['SMA_100']):
                summary['sma_100'] = float(latest['SMA_100'])
            if 'SMA_200' in data.columns and pd.notna(latest['SMA_200']):
                summary['sma_200'] = float(latest['SMA_200'])
            if 'EMA_20' in data.columns and pd.notna(latest['EMA_20']):
                summary['ema_20'] = float(latest['EMA_20'])
            
            # RSI
            if 'RSI_14' in data.columns and pd.notna(latest['RSI_14']):
                rsi = float(latest['RSI_14'])
                summary['rsi_14'] = rsi
                summary['rsi_signal'] = self._get_rsi_signal(rsi)
            
            # MACD
            if 'MACD' in data.columns and pd.notna(latest['MACD']):
                macd = float(latest['MACD'])
                macd_signal = float(latest.get('MACD_Signal', 0)) if pd.notna(latest.get('MACD_Signal')) else 0
                summary['macd'] = macd
                summary['macd_signal'] = macd_signal
                summary['macd_histogram'] = macd - macd_signal
            
            # Bollinger Bands
            if 'BB_Upper' in data.columns and pd.notna(latest['BB_Upper']):
                bb_upper = float(latest['BB_Upper'])
                bb_middle = float(latest.get('BB_Middle', 0)) if pd.notna(latest.get('BB_Middle')) else 0
                bb_lower = float(latest.get('BB_Lower', 0)) if pd.notna(latest.get('BB_Lower')) else 0
                current_price = float(latest['Close'])
                
                summary['bb_upper'] = bb_upper
                summary['bb_middle'] = bb_middle
                summary['bb_lower'] = bb_lower
                summary['bb_position'] = self._get_bb_position(current_price, bb_upper, bb_lower)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting indicator summary: {e}")
            return {}
    
    def _get_rsi_signal(self, rsi: float) -> str:
        """Get RSI signal interpretation"""
        if rsi > 70:
            return "Overbought"
        elif rsi < 30:
            return "Oversold"
        else:
            return "Neutral"
    
    def _get_bb_position(self, price: float, upper: float, lower: float) -> str:
        """Get Bollinger Bands position"""
        if price > upper:
            return "Above Upper Band"
        elif price < lower:
            return "Below Lower Band"
        else:
            return "Within Bands"
    
    def get_trading_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate trading signals based on technical indicators"""
        if data.empty or len(data) < 2:
            return {}
        
        try:
            signals = {}
            latest = data.iloc[-1]
            previous = data.iloc[-2]
            
            # RSI signals
            if 'RSI_14' in data.columns:
                current_rsi = float(latest['RSI_14']) if pd.notna(latest['RSI_14']) else 50
                prev_rsi = float(previous['RSI_14']) if pd.notna(previous['RSI_14']) else 50
                
                if current_rsi < 30 and prev_rsi >= 30:
                    signals['rsi'] = "Buy Signal (Oversold)"
                elif current_rsi > 70 and prev_rsi <= 70:
                    signals['rsi'] = "Sell Signal (Overbought)"
                else:
                    signals['rsi'] = "Hold"
            
            # MACD signals
            if 'MACD' in data.columns and 'MACD_Signal' in data.columns:
                current_macd = float(latest['MACD']) if pd.notna(latest['MACD']) else 0
                current_signal = float(latest['MACD_Signal']) if pd.notna(latest['MACD_Signal']) else 0
                prev_macd = float(previous['MACD']) if pd.notna(previous['MACD']) else 0
                prev_signal = float(previous['MACD_Signal']) if pd.notna(previous['MACD_Signal']) else 0
                
                if current_macd > current_signal and prev_macd <= prev_signal:
                    signals['macd'] = "Buy Signal (MACD Cross Above)"
                elif current_macd < current_signal and prev_macd >= prev_signal:
                    signals['macd'] = "Sell Signal (MACD Cross Below)"
                else:
                    signals['macd'] = "Hold"
            
            # Moving Average signals
            if 'SMA_20' in data.columns and 'EMA_20' in data.columns:
                current_price = float(latest['Close'])
                sma_20 = float(latest['SMA_20']) if pd.notna(latest['SMA_20']) else current_price
                ema_20 = float(latest['EMA_20']) if pd.notna(latest['EMA_20']) else current_price
                
                if current_price > sma_20 and current_price > ema_20:
                    signals['ma'] = "Bullish (Price Above MAs)"
                elif current_price < sma_20 and current_price < ema_20:
                    signals['ma'] = "Bearish (Price Below MAs)"
                else:
                    signals['ma'] = "Neutral"
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating trading signals: {e}")
            return {}
