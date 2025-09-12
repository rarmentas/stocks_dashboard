"""
Main Streamlit application for the Stock Dashboard
Refactored to use modular architecture with SQLite integration
"""

import streamlit as st
import logging
import pandas as pd
from datetime import datetime

# Import our modular components
from database.database_manager import DatabaseManager
from services.data_service import DataService
from services.technical_indicators_service import TechnicalIndicatorsService
from services.watchlist_service import WatchlistService
from components.ui_components import (
    SidebarComponent, MetricsComponent, DataTableComponent, WatchlistComponent, TimeFrameCardComponent
)
from components.chart_components import (
    ChartComponent, IndicatorSummaryComponent, VolumeChartComponent
)
from config.settings import DEFAULT_TICKERS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Real-Time Stock Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create sidebar navigation
def create_sidebar_navigation():
    """Create navigation in sidebar"""
    st.sidebar.title("📈 Stock Dashboard")
    
    # Navigation
    page = st.sidebar.selectbox(
        "Navigate to:",
        ["📊 Main Dashboard", "📋 Watchlist Manager"],
        key="page_selector"
    )
    
    return page

# Load custom CSS
def load_css():
    """Load custom CSS for dark theme"""
    try:
        with open('css/styles.css', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("CSS file not found. Using default styling.")
    except Exception as e:
        st.warning(f"Error loading CSS: {e}")

# Load the dark theme
load_css()

# Initialize services
@st.cache_resource
def initialize_services():
    """Initialize database and services"""
    try:
        db_manager = DatabaseManager()
        data_service = DataService(db_manager)
        indicators_service = TechnicalIndicatorsService(db_manager)
        watchlist_service = WatchlistService(db_manager)
        
        return db_manager, data_service, indicators_service, watchlist_service
    except Exception as e:
        st.error(f"Error initializing services: {e}")
        return None, None, None, None

# Initialize components
# @st.cache_resource  # Temporarily disabled to allow component updates
def initialize_components(watchlist_service=None):
    """Initialize UI components"""
    return {
        'sidebar': SidebarComponent(watchlist_service),
        'metrics': MetricsComponent(),
        'data_table': DataTableComponent(),
        'chart': ChartComponent(),
        'indicator_summary': IndicatorSummaryComponent(),
        'volume_chart': VolumeChartComponent(),
        'watchlist': WatchlistComponent(),
        'timeframe_cards': TimeFrameCardComponent()
    }

def render_main_dashboard(db_manager, data_service, indicators_service, watchlist_service, components):
    """Render the main dashboard page"""
    # Render sidebar and get user inputs
    sidebar_inputs = components['sidebar'].render()
    
    # Main dashboard content
    # st.title('Stock follow up')  # Title removed
    
    # Check if follow button was clicked
    if sidebar_inputs.get('follow_clicked', False):
        ticker = sidebar_inputs['ticker']
        
        if not ticker:
            st.error("Please enter a ticker symbol before following")
        else:
            # Show loading spinner for ticker validation
            with st.spinner(f"Validating and adding {ticker} to watchlist..."):
                try:
                    # Add ticker to watchlist with validation
                    result = watchlist_service.add_ticker_to_watchlist(ticker)
                    
                    if result['success']:
                        st.success(f"✅ {result['message']}")
                        # Show ticker info
                        ticker_info = result['ticker']
                        st.info(f"**{ticker_info.company_name}** ({ticker_info.ticker}) - {ticker_info.sector}")
                    else:
                        st.error(f"❌ {result['error']}")
                        
                except Exception as e:
                    logger.error(f"Error adding ticker {ticker} to watchlist: {e}")
                    st.error(f"Error adding ticker: {str(e)}")
    
    # Check if time frame card was clicked
    timeframe_card_clicked = st.session_state.get('timeframe_card_clicked', False)
    selected_timeframe = st.session_state.get('selected_timeframe', None)
    
    # Get current time period (from sidebar or from timeframe card selection)
    current_time_period = selected_timeframe if selected_timeframe else sidebar_inputs['time_period']
    
    # Render time frame cards outside the chart update logic so clicks can be detected
    if 'current_ticker' in st.session_state and st.session_state.current_ticker:
        # Only show time frame cards if we have a ticker
        components['timeframe_cards'].render_timeframe_cards_standalone(current_time_period)
    
    # Check if update button was clicked or parameters changed
    if sidebar_inputs['update_clicked'] or timeframe_card_clicked:
        ticker = sidebar_inputs['ticker']
        # Use selected timeframe from card if clicked, otherwise use sidebar selection
        time_period = selected_timeframe if timeframe_card_clicked else sidebar_inputs['time_period']
        chart_type = sidebar_inputs['chart_type']
        indicators = sidebar_inputs['indicators']
        use_cache = sidebar_inputs['use_cache']
        show_signals = sidebar_inputs['show_signals']
        
        # Processing ticker data
        
        if not ticker:
            st.error("Please enter a ticker symbol")
            return
        
        # Show loading spinner
        with st.spinner(f"Loading data for {ticker}..."):
            try:
                # Fetch stock data
                data = data_service.fetch_stock_data(
                    ticker=ticker,
                    period=time_period,
                    use_cache=use_cache
                )
                
                if data is None or data.empty:
                    st.error(f"No data found for {ticker}. Please check the ticker symbol.")
                    return
                
                # Calculate technical indicators
                if indicators:
                    # Map indicator names to internal names
                    indicator_mapping = {
                        'SMA 20': 'SMA_20',
                        'SMA 50': 'SMA_50',
                        'SMA 100': 'SMA_100',
                        'SMA 200': 'SMA_200',
                        'EMA 20': 'EMA_20',
                        'RSI 14': 'RSI_14',
                        'MACD': 'MACD',
                        'Bollinger Bands': 'BB'
                    }
                    
                    internal_indicators = [
                        indicator_mapping.get(ind, ind) for ind in indicators
                    ]
                    
                    data = indicators_service.calculate_indicators(
                        data=data,
                        ticker=ticker,
                        indicators=internal_indicators
                    )
                
                # Calculate basic metrics
                metrics = data_service.calculate_basic_metrics(data)
                
                # Get company name from database
                company_name = db_manager.get_company_name(ticker)
                
                # Display main metric (Last Price) above chart
                components['metrics'].render_price_card_only(metrics, ticker)
                
                # Create and display chart
                components['chart'].render(
                    chart_type=chart_type,
                    data=data,
                    ticker=ticker,
                    time_period=time_period,
                    indicators=indicators,
                    company_name=company_name
                )
                
                # Display additional metrics (High, Low, Volume) below chart
                components['metrics'].render_additional_metrics(metrics)
                
                # Display volume chart
                components['volume_chart'].render(data)
                
                # Display technical indicator summary
                if indicators:
                    indicator_summary = indicators_service.get_indicator_summary(data)
                    components['indicator_summary'].render(indicator_summary)
                    
                    # Display trading signals if requested
                    if show_signals:
                        signals = indicators_service.get_trading_signals(data)
                        components['data_table'].render_trading_signals(signals)
                
                # Display data tables
                components['data_table'].render_historical_data(data)
                
                if indicators:
                    components['data_table'].render_technical_indicators(data)
                
                # Success message
                st.success(f"✅ Successfully loaded data for {ticker}")
                
            except Exception as e:
                logger.error(f"Error processing data for {ticker}: {e}")
                st.error(f"Error processing data: {e}")
            
            # Reset the button state after processing
            st.session_state.update_clicked = False
            st.session_state.timeframe_card_clicked = False
    
    else:
        # Show welcome message and instructions with custom styling
        st.markdown("""
        <div class="welcome-section">
            <h2>Welcome to the Real-Time Stock Dashboard! 📈</h2>
            <p>This dashboard provides comprehensive stock analysis with:</p>
            <ul>
                <li><strong>Real-time stock data</strong> from Yahoo Finance</li>
                <li><strong>Technical indicators</strong> (SMA, EMA, RSI, MACD, Bollinger Bands)</li>
                <li><strong>Trading signals</strong> based on technical analysis</li>
                <li><strong>Local data caching</strong> for faster access</li>
                <li><strong>Interactive charts</strong> with multiple timeframes</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # How to use section
        st.markdown("""
        <div class="feature-card">
            <h3>How to use:</h3>
            <ol>
                <li>Enter a stock ticker symbol in the sidebar</li>
                <li>Select your desired time period</li>
                <li>Choose chart type and technical indicators</li>
                <li>Click "Update Chart" to load the data</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Features section
        st.markdown("""
        <div class="feature-card">
            <h3>Features:</h3>
            <ul>
                <li>📊 <strong>Multiple Chart Types</strong>: Candlestick and Line charts</li>
                <li>📈 <strong>Technical Analysis</strong>: 20+ technical indicators</li>
                <li>💾 <strong>Smart Caching</strong>: Local SQLite database for faster loading</li>
                <li>🎯 <strong>Trading Signals</strong>: Buy/sell signals based on indicators</li>
                <li>📱 <strong>Responsive Design</strong>: Works on desktop and mobile</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <p style="font-size: 1.2rem; color: var(--accent-color);">
                Start by entering a ticker symbol in the sidebar and clicking "Update Chart"!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display watchlist if it exists
        try:
            watchlist_tickers = watchlist_service.get_watchlist_tickers(active_only=True)
            if watchlist_tickers:
                st.markdown("---")
                watchlist_summary = watchlist_service.get_watchlist_summary()
                components['watchlist'].render_watchlist_summary(watchlist_summary)
                components['watchlist'].render_watchlist_table(watchlist_tickers, data_service)
        except Exception as e:
            logger.error(f"Error displaying watchlist: {e}")
            st.warning("Error loading watchlist data")
        
        # Show some example tickers with custom styling
        st.markdown("""
        <div style="margin: 2rem 0;">
            <h2 style="text-align: center; color: var(--text-primary); margin-bottom: 1.5rem;">
                Popular Tickers
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        example_tickers = [
            ("AAPL", "Apple Inc."),
            ("GOOGL", "Alphabet Inc."),
            ("MSFT", "Microsoft Corp."),
            ("AMZN", "Amazon.com Inc."),
            ("TSLA", "Tesla Inc."),
            ("NVDA", "NVIDIA Corp."),
            ("META", "Meta Platforms Inc."),
            ("NFLX", "Netflix Inc.")
        ]
        
        for i, (ticker, name) in enumerate(example_tickers):
            with [col1, col2, col3, col4][i % 4]:
                st.markdown(f"""
                <div class="ticker-card">
                    <strong>{ticker}</strong>
                    <p>{name}</p>
                </div>
                """, unsafe_allow_html=True)


def render_watchlist_manager(db_manager, data_service, indicators_service, watchlist_service, components):
    """Render the watchlist manager page"""
    st.title("📋 Watchlist Manager")
    
    # Add new ticker section
    st.subheader("➕ Add New Ticker")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_ticker = st.text_input(
            "Ticker Symbol",
            placeholder="Enter ticker symbol (e.g., AAPL, GOOGL)",
            key="new_ticker_input"
        ).upper()
    
    with col2:
        if st.button("Add to Watchlist", type="primary", use_container_width=True):
            if new_ticker:
                with st.spinner(f"Validating and adding {new_ticker}..."):
                    try:
                        result = watchlist_service.add_ticker_to_watchlist(new_ticker)
                        
                        if result['success']:
                            st.success(f"✅ {result['message']}")
                            ticker_info = result['ticker']
                            st.info(f"**{ticker_info.company_name}** ({ticker_info.ticker}) - {ticker_info.sector}")
                            st.rerun()
                        else:
                            st.error(f"❌ {result['error']}")
                            
                    except Exception as e:
                        logger.error(f"Error adding ticker {new_ticker}: {e}")
                        st.error(f"Error adding ticker: {str(e)}")
            else:
                st.error("Please enter a ticker symbol")
    
    st.markdown("---")
    
    # Get current watchlist
    try:
        watchlist_tickers = watchlist_service.get_watchlist_tickers(active_only=True)
        
        if not watchlist_tickers:
            st.info("📋 Your watchlist is empty. Add some tickers above!")
            return
        
        # Watchlist summary
        watchlist_summary = watchlist_service.get_watchlist_summary()
        components['watchlist'].render_watchlist_summary(watchlist_summary)
        
        st.markdown("---")
        
        # Watchlist table with management options
        st.subheader("📊 Your Watchlist")
        
        # Get real-time prices
        ticker_symbols = [ticker.ticker for ticker in watchlist_tickers]
        real_time_data = data_service.get_real_time_prices(ticker_symbols)
        
        # Create display data with management options
        display_data = []
        for i, ticker in enumerate(watchlist_tickers):
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
        
        # Display the table
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
        
        # Management section
        st.markdown("---")
        st.subheader("⚙️ Manage Tickers")
        
        # Create columns for each ticker with management options
        for i, ticker in enumerate(watchlist_tickers):
            with st.expander(f"Manage {ticker.ticker} - {ticker.company_name}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Update priority
                    new_priority = st.selectbox(
                        f"Priority for {ticker.ticker}",
                        options=[1, 2, 3, 4, 5],
                        index=ticker.priority - 1,
                        key=f"priority_{ticker.ticker}_{i}"
                    )
                    
                    if st.button(f"Update Priority", key=f"update_priority_{ticker.ticker}_{i}"):
                        result = watchlist_service.update_watchlist_ticker(
                            ticker.ticker, 
                            priority=new_priority
                        )
                        if result['success']:
                            st.success("Priority updated!")
                            st.rerun()
                        else:
                            st.error(result['error'])
                
                with col2:
                    # Update target price
                    new_target = st.number_input(
                        f"Target Price for {ticker.ticker}",
                        value=float(ticker.target_price) if ticker.target_price else 0.0,
                        step=0.01,
                        key=f"target_{ticker.ticker}_{i}"
                    )
                    
                    if st.button(f"Update Target", key=f"update_target_{ticker.ticker}_{i}"):
                        result = watchlist_service.update_watchlist_ticker(
                            ticker.ticker, 
                            target_price=new_target if new_target > 0 else None
                        )
                        if result['success']:
                            st.success("Target price updated!")
                            st.rerun()
                        else:
                            st.error(result['error'])
                
                with col3:
                    # Remove ticker
                    if st.button(f"Remove {ticker.ticker}", type="secondary", key=f"remove_{ticker.ticker}_{i}"):
                        result = watchlist_service.remove_ticker_from_watchlist(ticker.ticker)
                        if result['success']:
                            st.success(f"Removed {ticker.ticker} from watchlist!")
                            st.rerun()
                        else:
                            st.error(result['error'])
        
        # Bulk actions
        st.markdown("---")
        st.subheader("🔧 Bulk Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Clear All Watchlist", type="secondary"):
                st.warning("⚠️ This will remove ALL tickers from your watchlist!")
                if st.button("Confirm Clear All", type="primary"):
                    for ticker in watchlist_tickers:
                        watchlist_service.remove_ticker_from_watchlist(ticker.ticker)
                    st.success("All tickers removed from watchlist!")
                    st.rerun()
        
        with col2:
            if st.button("Export Watchlist", type="secondary"):
                # Create CSV data
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"watchlist_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col3:
            if st.button("Refresh Prices", type="secondary"):
                st.rerun()
        
    except Exception as e:
        logger.error(f"Error in watchlist manager: {e}")
        st.error(f"Error loading watchlist: {str(e)}")


def main():
    """Main application function"""
    # Initialize services and components
    db_manager, data_service, indicators_service, watchlist_service = initialize_services()
    components = initialize_components(watchlist_service)
    
    if not all([db_manager, data_service, indicators_service, watchlist_service]):
        st.error("Failed to initialize services. Please check the logs.")
        return
    
    # Create navigation
    page = create_sidebar_navigation()
    
    # Route to appropriate page
    if page == "📊 Main Dashboard":
        render_main_dashboard(db_manager, data_service, indicators_service, watchlist_service, components)
    elif page == "📋 Watchlist Manager":
        render_watchlist_manager(db_manager, data_service, indicators_service, watchlist_service, components)

if __name__ == "__main__":
    main()
