"""
UI components for the stock dashboard
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime

from config.settings import (
    DEFAULT_TICKERS, DEFAULT_TIME_PERIODS, CHART_TYPES, 
    TECHNICAL_INDICATORS, INTERVAL_MAPPING
)


class SidebarComponent:
    """Component for the sidebar interface"""
    
    def __init__(self):
        # Don't initialize instance variables that will be set in render()
        pass
    
    def render(self) -> Dict[str, Any]:
        """Render the sidebar and return user inputs"""
        st.sidebar.header('Chart Parameters')
        
        # Ticker input - let Streamlit manage the state naturally
        # Initialize ticker in session state if not exists
        if 'current_ticker' not in st.session_state:
            st.session_state.current_ticker = 'AAPL'
        
        self.ticker = st.sidebar.text_input(
            'Ticker Symbol', 
            value=st.session_state.current_ticker,
            key='ticker_input_field',
            help='Enter a valid stock ticker symbol (e.g., AAPL, GOOGL, MSFT)'
        ).upper()
        
        # Update session state with current ticker
        st.session_state.current_ticker = self.ticker
        
        # Time period selection
        self.time_period = st.sidebar.selectbox(
            'Time Period',
            options=DEFAULT_TIME_PERIODS,
            index=2,  # Default to '1mo'
            help='Select the time period for the chart'
        )
        
        # Chart type selection
        self.chart_type = st.sidebar.selectbox(
            'Chart Type',
            options=CHART_TYPES,
            help='Choose between candlestick or line chart'
        )
        
        # Technical indicators selection
        self.indicators = st.sidebar.multiselect(
            'Technical Indicators',
            options=TECHNICAL_INDICATORS,
            default=['SMA 20', 'EMA 20', 'RSI 14'],
            help='Select technical indicators to display on the chart'
        )
        
        # Update and Follow buttons in columns
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            # Use session state to track button clicks and current parameters
            if 'update_clicked' not in st.session_state:
                st.session_state.update_clicked = False
            if 'last_ticker' not in st.session_state:
                st.session_state.last_ticker = ''
            if 'last_time_period' not in st.session_state:
                st.session_state.last_time_period = ''
            if 'last_chart_type' not in st.session_state:
                st.session_state.last_chart_type = ''
            if 'last_indicators' not in st.session_state:
                st.session_state.last_indicators = []
            
            # Check if parameters have changed
            params_changed = (
                self.ticker != st.session_state.last_ticker or
                self.time_period != st.session_state.last_time_period or
                self.chart_type != st.session_state.last_chart_type or
                set(self.indicators) != set(st.session_state.last_indicators)
            )
            
            if st.button(
                'Update Chart',
                type='primary',
                use_container_width=True,
                key='update_chart_button'
            ):
                # Update session state with current parameters
                st.session_state.last_ticker = self.ticker
                st.session_state.last_time_period = self.time_period
                st.session_state.last_chart_type = self.chart_type
                st.session_state.last_indicators = self.indicators.copy()
                st.session_state.update_clicked = True
            
            # Trigger update if parameters changed or button was clicked
            self.update_clicked = st.session_state.update_clicked or params_changed
        
        with col2:
            self.follow_clicked = st.button(
                'Follow',
                type='secondary',
                use_container_width=True,
                key='follow_button'
            )
        
        # Additional options
        st.sidebar.subheader('Advanced Options')
        use_cache = st.sidebar.checkbox(
            'Use Cached Data',
            value=True,
            help='Use cached data when available (faster loading)'
        )
        
        show_signals = st.sidebar.checkbox(
            'Show Trading Signals',
            value=False,
            help='Display trading signals based on technical indicators'
        )
        
        # Debug: Print the values being returned
        # st.write(f"DEBUG: Ticker value: '{self.ticker}', Update clicked: {self.update_clicked}")
        
        return {
            'ticker': self.ticker,
            'time_period': self.time_period,
            'chart_type': self.chart_type,
            'indicators': self.indicators,
            'update_clicked': self.update_clicked,
            'follow_clicked': self.follow_clicked,
            'use_cache': use_cache,
            'show_signals': show_signals
        }


class MetricsComponent:
    """Component for displaying stock metrics"""
    
    def render(self, metrics: Dict[str, Any], ticker: str):
        """Render the metrics section"""
        if not metrics:
            st.warning("No metrics available")
            return
        
        # Main price metric
        st.metric(
            label=f"{ticker} Last Price",
            value=f"{metrics['last_close']:.2f} USD",
            delta=f"{metrics['change']:.2f} ({metrics['pct_change']:.2f}%)"
        )
        
        # Additional metrics in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label='High',
                value=f"{metrics['high']:.2f} USD"
            )
        
        with col2:
            st.metric(
                label='Low',
                value=f"{metrics['low']:.2f} USD"
            )
        
        with col3:
            st.metric(
                label='Volume',
                value=f"{metrics['volume']:,}"
            )


class DataTableComponent:
    """Component for displaying data tables"""
    
    def render_historical_data(self, data: pd.DataFrame):
        """Render historical data table"""
        if data.empty:
            st.warning("No historical data available")
            return
        
        st.subheader('Historical Data')
        
        # Select columns to display
        display_columns = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']
        available_columns = [col for col in display_columns if col in data.columns]
        
        if available_columns:
            st.dataframe(
                data[available_columns],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No valid columns found for display")
    
    def render_technical_indicators(self, data: pd.DataFrame):
        """Render technical indicators table"""
        if data.empty:
            st.warning("No technical indicators available")
            return
        
        st.subheader('Technical Indicators')
        
        # Select indicator columns
        indicator_columns = ['Datetime']
        available_indicators = [
            'SMA_20', 'EMA_20', 'RSI_14', 'MACD', 'MACD_Signal',
            'BB_Upper', 'BB_Middle', 'BB_Lower'
        ]
        
        for indicator in available_indicators:
            if indicator in data.columns:
                indicator_columns.append(indicator)
        
        if len(indicator_columns) > 1:
            st.dataframe(
                data[indicator_columns],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No technical indicators found")
    
    def render_trading_signals(self, signals: Dict[str, Any]):
        """Render trading signals"""
        if not signals:
            return
        
        st.subheader('Trading Signals')
        
        for signal_type, signal_value in signals.items():
            if signal_type == 'rsi':
                st.info(f"**RSI Signal:** {signal_value}")
            elif signal_type == 'macd':
                st.info(f"**MACD Signal:** {signal_value}")
            elif signal_type == 'ma':
                st.info(f"**Moving Average Signal:** {signal_value}")


class RealTimePricesComponent:
    """Component for displaying real-time prices in sidebar"""
    
    def render(self, real_time_data: Dict[str, Dict[str, Any]]):
        """Render real-time prices in sidebar"""
        st.sidebar.header('Real-Time Stock Prices')
        
        if not real_time_data:
            st.sidebar.warning("No real-time data available")
            return
        
        for ticker, data in real_time_data.items():
            try:
                st.sidebar.metric(
                    label=ticker,
                    value=f"{data['price']:.2f} USD",
                    delta=f"{data['change']:.2f} ({data['pct_change']:.2f}%)"
                )
            except Exception as e:
                st.sidebar.error(f"Error displaying {ticker}: {e}")


class DatabaseStatsComponent:
    """Component for displaying database statistics"""
    
    def render(self, stats: Dict[str, Any]):
        """Render database statistics"""
        if not stats:
            return
        
        st.sidebar.subheader('Database Statistics')
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            st.sidebar.metric(
                label='Stock Records',
                value=f"{stats.get('stock_data_records', 0):,}"
            )
        
        with col2:
            st.sidebar.metric(
                label='Indicator Records',
                value=f"{stats.get('indicators_records', 0):,}"
            )
        
        st.sidebar.metric(
            label='Database Size',
            value=f"{stats.get('database_size_mb', 0):.1f} MB"
        )
        
        if stats.get('unique_tickers'):
            st.sidebar.write(f"**Cached Tickers:** {', '.join(stats['unique_tickers'][:5])}")
            if len(stats['unique_tickers']) > 5:
                st.sidebar.write(f"... and {len(stats['unique_tickers']) - 5} more")


class AboutComponent:
    """Component for the about section"""
    
    def render(self):
        """Render the about section"""
        st.sidebar.subheader('About')
        st.sidebar.info(
            'This dashboard provides real-time stock data and technical indicators '
            'for various time periods. Data is cached locally for faster access.'
        )
        
        st.sidebar.subheader('Features')
        st.sidebar.markdown("""
        - 📈 Real-time stock data
        - 📊 Technical indicators
        - 💾 Local data caching
        - 🎯 Trading signals
        - 📱 Responsive design
        """)
        
        st.sidebar.subheader('Data Source')
        st.sidebar.markdown("""
        Data provided by [Yahoo Finance](https://finance.yahoo.com/)
        """)
