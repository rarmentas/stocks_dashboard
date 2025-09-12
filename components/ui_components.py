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
    
    def __init__(self, watchlist_service=None):
        # Don't initialize instance variables that will be set in render()
        self.watchlist_service = watchlist_service
    
    def render(self) -> Dict[str, Any]:
        """Render the sidebar and return user inputs"""
        st.sidebar.header('Chart Parameters')
        
        # Dynamic ticker selection - dropdown with watchlist + free text input
        # Initialize ticker in session state if not exists
        if 'current_ticker' not in st.session_state:
            # Try to get the most recent ticker from watchlist, fallback to AAPL
            default_ticker = 'AAPL'
            if self.watchlist_service:
                try:
                    most_recent = self.watchlist_service.get_most_recent_ticker()
                    if most_recent:
                        default_ticker = most_recent
                except Exception as e:
                    # If there's an error getting the most recent ticker, use AAPL
                    pass
            st.session_state.current_ticker = default_ticker
        
        # Get watchlist tickers for dropdown
        watchlist_tickers = []
        if self.watchlist_service:
            try:
                watchlist_data = self.watchlist_service.get_watchlist_tickers(active_only=True)
                watchlist_tickers = [ticker.ticker for ticker in watchlist_data]
            except Exception as e:
                # If there's an error getting watchlist, continue with empty list
                pass
        
        # Create options list with watchlist tickers + "Enter new ticker..." option
        # Add visual indicators for watchlist tickers
        options = []
        for ticker in watchlist_tickers:
            options.append(f"📋 {ticker}")  # Add watchlist icon
        options.append("➕ Enter new ticker...")  # Add new ticker icon
        
        # Find the current index for the selectbox
        current_ticker = st.session_state.current_ticker
        if current_ticker in watchlist_tickers:
            current_index = watchlist_tickers.index(current_ticker)
        else:
            current_index = len(options) - 1  # "Enter new ticker..." option
        
        # Create the selectbox
        selected_option = st.sidebar.selectbox(
            'Ticker Symbol',
            options=options,
            index=current_index,
            key='ticker_selectbox',
            help='Select from your watchlist or choose "Enter new ticker..." to add a new one'
        )
        
        # Handle the selection
        if selected_option == "➕ Enter new ticker...":
            # Show text input for new ticker
            self.ticker = st.sidebar.text_input(
                'Enter New Ticker Symbol',
                value='',
                key='new_ticker_input',
                help='Enter a valid stock ticker symbol (e.g., AAPL, GOOGL, MSFT)',
                placeholder='e.g., AAPL, GOOGL, MSFT'
            ).upper()
            
            # If user entered something, use that; otherwise keep the last known ticker
            if not self.ticker:
                self.ticker = current_ticker
        else:
            # User selected a ticker from watchlist (remove the icon prefix)
            self.ticker = selected_option.replace("📋 ", "")
        
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
            default=['SMA 20', 'SMA 50', 'SMA 100', 'SMA 200'],
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
    
    def render_main_metric(self, metrics: Dict[str, Any], ticker: str):
        """Render only the main price metric (above chart)"""
        if not metrics:
            st.warning("No metrics available")
            return
        
        # Custom HTML for main price metric without label - small square at left
        delta_color = "#e74c3c" if metrics['change'] < 0 else "#00d4aa"
        st.markdown(f"""
        <div style="display: flex; align-items: flex-start;">
            <div class="custom-metric-container-small">
                <div class="custom-metric-value-small">{metrics['last_close']:.2f} USD</div>
                <div class="custom-metric-delta-small" style="color: {delta_color}">
                    {metrics['change']:+.2f} ({metrics['pct_change']:+.2f}%)
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_additional_metrics(self, metrics: Dict[str, Any]):
        """Render additional metrics (below chart)"""
        if not metrics:
            return
        
        # Additional metrics in columns with custom HTML
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="custom-metric-container">
                <div class="custom-metric-label">High</div>
                <div class="custom-metric-value">{metrics['high']:.2f} USD</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="custom-metric-container">
                <div class="custom-metric-label">Low</div>
                <div class="custom-metric-value">{metrics['low']:.2f} USD</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="custom-metric-container">
                <div class="custom-metric-label">Volume</div>
                <div class="custom-metric-value">{metrics['volume']:,}</div>
            </div>
            """, unsafe_allow_html=True)
    
    def render(self, metrics: Dict[str, Any], ticker: str):
        """Render the metrics section (legacy method for backward compatibility)"""
        self.render_main_metric(metrics, ticker)
        self.render_additional_metrics(metrics)


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
            'SMA_20', 'SMA_50', 'SMA_100', 'SMA_200', 'EMA_20', 'RSI_14', 'MACD', 'MACD_Signal',
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


class WatchlistComponent:
    """Component for displaying and managing watchlist"""
    
    def __init__(self):
        pass
    
    def render_watchlist_summary(self, watchlist_summary: Dict[str, Any]):
        """Render watchlist summary with statistics"""
        if not watchlist_summary or watchlist_summary['total_tickers'] == 0:
            st.info("📋 Your watchlist is empty. Add tickers using the Follow button!")
            return
        
        st.subheader('📋 Watchlist Summary')
        
        # Create columns for summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Tickers",
                value=watchlist_summary['total_tickers']
            )
        
        with col2:
            st.metric(
                label="Sectors",
                value=len(watchlist_summary['sectors'])
            )
        
        with col3:
            high_priority = sum(1 for p in watchlist_summary['priority_distribution'].items() if p[0] <= 2)
            st.metric(
                label="High Priority",
                value=high_priority
            )
        
        with col4:
            avg_priority = sum(p * count for p, count in watchlist_summary['priority_distribution'].items()) / watchlist_summary['total_tickers']
            st.metric(
                label="Avg Priority",
                value=f"{avg_priority:.1f}"
            )
    
    def render_watchlist_table(self, watchlist_tickers: List[Any], data_service=None):
        """Render watchlist table with real-time prices"""
        if not watchlist_tickers:
            return
        
        st.subheader('📊 Watchlist Tickers')
        
        # Get real-time prices for all tickers
        ticker_symbols = [ticker.ticker for ticker in watchlist_tickers]
        real_time_data = {}
        
        if data_service:
            real_time_data = data_service.get_real_time_prices(ticker_symbols)
        
        # Create display data
        display_data = []
        for ticker in watchlist_tickers:
            ticker_data = real_time_data.get(ticker.ticker, {})
            
            # Priority emoji
            priority_emoji = {
                1: '🔴',  # High
                2: '🟠',  # Medium-High
                3: '🟡',  # Medium
                4: '🟢',  # Low
                5: '⚪'   # Very Low
            }.get(ticker.priority, '🟡')
            
            display_data.append({
                'Ticker': ticker.ticker,
                'Company': ticker.company_name,
                'Sector': ticker.sector or 'Unknown',
                'Priority': f"{priority_emoji} {ticker.priority}",
                'Current Price': f"${ticker_data.get('price', 0):.2f}" if ticker_data.get('price', 0) > 0 else 'N/A',
                'Change': f"{ticker_data.get('pct_change', 0):+.2f}%" if ticker_data.get('pct_change') is not None else 'N/A',
                'Target': f"${ticker.target_price:.2f}" if ticker.target_price else 'N/A',
                'Stop Loss': f"${ticker.stop_loss:.2f}" if ticker.stop_loss else 'N/A',
                'Added': ticker.added_date.strftime('%Y-%m-%d') if ticker.added_date and hasattr(ticker.added_date, 'strftime') else 'N/A',
                'Notes': ticker.notes or ''
            })
        
        # Create DataFrame and display
        df = pd.DataFrame(display_data)
        
        # Style the DataFrame
        def style_change(val):
            if isinstance(val, str) and val != 'N/A':
                if val.startswith('+'):
                    return 'color: green'
                elif val.startswith('-'):
                    return 'color: red'
            return ''
        
        styled_df = df.style.applymap(style_change, subset=['Change'])
        st.dataframe(styled_df, use_container_width=True, height=400)
    
    def render_watchlist_management(self, watchlist_service, ticker_to_remove: str = None):
        """Render watchlist management interface"""
        st.subheader('⚙️ Manage Watchlist')
        
        # Remove ticker section
        if ticker_to_remove:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"Remove **{ticker_to_remove}** from watchlist?")
            with col2:
                if st.button('Confirm Remove', type='secondary'):
                    result = watchlist_service.remove_ticker_from_watchlist(ticker_to_remove)
                    if result['success']:
                        st.success(result['message'])
                        st.rerun()
                    else:
                        st.error(result['error'])
        
        # Bulk actions
        st.write("**Bulk Actions:**")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button('Clear All Watchlist', type='secondary'):
                st.warning("This will remove all tickers from your watchlist. Are you sure?")
                # Note: This would need additional confirmation logic
        
        with col2:
            if st.button('Export Watchlist', type='secondary'):
                st.info("Export functionality will be implemented soon")