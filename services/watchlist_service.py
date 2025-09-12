"""
Watchlist service for managing followed tickers
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

from database.database_manager import DatabaseManager
from database.models import WatchlistTicker

logger = logging.getLogger(__name__)


class WatchlistService:
    """Service for managing watchlist tickers"""
    
    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()
    
    def validate_ticker(self, ticker: str) -> Dict[str, Any]:
        """
        Validate if a ticker exists and get basic information
        
        Args:
            ticker: Stock ticker symbol to validate
            
        Returns:
            Dict with validation result and ticker info
        """
        try:
            # Clean ticker symbol
            ticker = ticker.strip().upper()
            
            if not ticker:
                return {
                    'valid': False,
                    'error': 'Ticker symbol cannot be empty'
                }
            
            # Try to get ticker info from yfinance
            ticker_obj = yf.Ticker(ticker)
            
            # Get basic info
            info = ticker_obj.info
            
            # Check if we got valid info
            if not info or 'symbol' not in info:
                return {
                    'valid': False,
                    'error': f'Ticker "{ticker}" not found'
                }
            
            # Extract relevant information
            company_name = info.get('longName', info.get('shortName', ticker))
            sector = info.get('sector', 'Unknown')
            
            return {
                'valid': True,
                'ticker': ticker,
                'company_name': company_name,
                'sector': sector,
                'info': info
            }
            
        except Exception as e:
            logger.error(f"Error validating ticker {ticker}: {e}")
            return {
                'valid': False,
                'error': f'Error validating ticker: {str(e)}'
            }
    
    def add_ticker_to_watchlist(self, ticker: str, notes: str = None, 
                               target_price: float = None, stop_loss: float = None,
                               priority: int = 3) -> Dict[str, Any]:
        """
        Add a ticker to the watchlist after validation
        
        Args:
            ticker: Stock ticker symbol
            notes: Optional notes about the ticker
            target_price: Optional target price
            stop_loss: Optional stop loss price
            priority: Priority level (1-5, default 3)
            
        Returns:
            Dict with operation result
        """
        try:
            # First validate the ticker
            validation_result = self.validate_ticker(ticker)
            
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            # Check if ticker already exists in watchlist
            if self.db_manager.is_ticker_in_watchlist(ticker):
                return {
                    'success': False,
                    'error': f'Ticker "{ticker}" is already in your watchlist'
                }
            
            # Create watchlist ticker object
            watchlist_ticker = WatchlistTicker(
                ticker=ticker,
                company_name=validation_result['company_name'],
                sector=validation_result['sector'],
                added_date=datetime.now(),
                notes=notes,
                target_price=target_price,
                stop_loss=stop_loss,
                is_active=True,
                priority=priority,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Save to database
            success = self.db_manager.add_watchlist_ticker(watchlist_ticker)
            
            if success:
                return {
                    'success': True,
                    'message': f'Successfully added "{ticker}" to watchlist',
                    'ticker': watchlist_ticker
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to save ticker to database'
                }
                
        except Exception as e:
            logger.error(f"Error adding ticker {ticker} to watchlist: {e}")
            return {
                'success': False,
                'error': f'Error adding ticker: {str(e)}'
            }
    
    def get_watchlist_tickers(self, active_only: bool = True) -> List[WatchlistTicker]:
        """
        Get all tickers from watchlist
        
        Args:
            active_only: If True, only return active tickers
            
        Returns:
            List of WatchlistTicker objects
        """
        try:
            return self.db_manager.get_watchlist_tickers(active_only=active_only)
        except Exception as e:
            logger.error(f"Error getting watchlist tickers: {e}")
            return []
    
    def remove_ticker_from_watchlist(self, ticker: str) -> Dict[str, Any]:
        """
        Remove a ticker from the watchlist
        
        Args:
            ticker: Stock ticker symbol to remove
            
        Returns:
            Dict with operation result
        """
        try:
            success = self.db_manager.remove_watchlist_ticker(ticker)
            
            if success:
                return {
                    'success': True,
                    'message': f'Successfully removed "{ticker}" from watchlist'
                }
            else:
                return {
                    'success': False,
                    'error': f'Ticker "{ticker}" not found in watchlist'
                }
                
        except Exception as e:
            logger.error(f"Error removing ticker {ticker} from watchlist: {e}")
            return {
                'success': False,
                'error': f'Error removing ticker: {str(e)}'
            }
    
    def update_watchlist_ticker(self, ticker: str, **kwargs) -> Dict[str, Any]:
        """
        Update a ticker in the watchlist
        
        Args:
            ticker: Stock ticker symbol
            **kwargs: Fields to update (notes, target_price, stop_loss, priority, is_active)
            
        Returns:
            Dict with operation result
        """
        try:
            # Add updated_at timestamp
            kwargs['updated_at'] = datetime.now()
            
            success = self.db_manager.update_watchlist_ticker(ticker, **kwargs)
            
            if success:
                return {
                    'success': True,
                    'message': f'Successfully updated "{ticker}" in watchlist'
                }
            else:
                return {
                    'success': False,
                    'error': f'Ticker "{ticker}" not found in watchlist'
                }
                
        except Exception as e:
            logger.error(f"Error updating ticker {ticker} in watchlist: {e}")
            return {
                'success': False,
                'error': f'Error updating ticker: {str(e)}'
            }
    
    def get_most_recent_ticker(self) -> Optional[str]:
        """
        Get the most recently added ticker from the watchlist
        
        Returns:
            Most recently added ticker symbol or None if watchlist is empty
        """
        try:
            tickers = self.get_watchlist_tickers(active_only=True)
            
            if not tickers:
                return None
            
            # Sort by added_date descending to get the most recent
            # The database query already orders by added_date DESC, so first item is most recent
            most_recent = tickers[0]
            return most_recent.ticker
            
        except Exception as e:
            logger.error(f"Error getting most recent ticker: {e}")
            return None
    
    def get_watchlist_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for the watchlist
        
        Returns:
            Dict with watchlist summary
        """
        try:
            tickers = self.get_watchlist_tickers(active_only=True)
            
            if not tickers:
                return {
                    'total_tickers': 0,
                    'sectors': {},
                    'priority_distribution': {},
                    'tickers': []
                }
            
            # Count sectors
            sectors = {}
            priority_dist = {}
            
            for ticker in tickers:
                sector = ticker.sector or 'Unknown'
                sectors[sector] = sectors.get(sector, 0) + 1
                
                priority = ticker.priority
                priority_dist[priority] = priority_dist.get(priority, 0) + 1
            
            return {
                'total_tickers': len(tickers),
                'sectors': sectors,
                'priority_distribution': priority_dist,
                'tickers': [ticker.to_dict() for ticker in tickers]
            }
            
        except Exception as e:
            logger.error(f"Error getting watchlist summary: {e}")
            return {
                'total_tickers': 0,
                'sectors': {},
                'priority_distribution': {},
                'tickers': []
            }
