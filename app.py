"""
Main Streamlit application for the Stock Dashboard
Refactored to use modular architecture with SQLite integration
"""

import streamlit as st
import logging
from datetime import datetime

# Import our modular components
from database.database_manager import DatabaseManager
from services.data_service import DataService
from services.technical_indicators_service import TechnicalIndicatorsService
from components.ui_components import (
    SidebarComponent, MetricsComponent, DataTableComponent
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
        
        return db_manager, data_service, indicators_service
    except Exception as e:
        st.error(f"Error initializing services: {e}")
        return None, None, None

# Initialize components
# @st.cache_resource  # Temporarily disabled to allow component updates
def initialize_components():
    """Initialize UI components"""
    return {
        'sidebar': SidebarComponent(),
        'metrics': MetricsComponent(),
        'data_table': DataTableComponent(),
        'chart': ChartComponent(),
        'indicator_summary': IndicatorSummaryComponent(),
        'volume_chart': VolumeChartComponent()
    }

def main():
    """Main application function"""
    # Initialize services and components
    db_manager, data_service, indicators_service = initialize_services()
    components = initialize_components()
    
    if not all([db_manager, data_service, indicators_service]):
        st.error("Failed to initialize services. Please check the logs.")
        return
    
    # Render sidebar and get user inputs
    sidebar_inputs = components['sidebar'].render()
    
    # Main dashboard content
    # st.title('Stock follow up')  # Title removed
    
    # Check if follow button was clicked
    if sidebar_inputs.get('follow_clicked', False):
        st.info("🔔 Follow button clicked! This feature will be implemented soon.")
    
    # Check if update button was clicked or parameters changed
    if sidebar_inputs['update_clicked']:
        ticker = sidebar_inputs['ticker']
        time_period = sidebar_inputs['time_period']
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
                
                # Display main metric (Last Price) above chart
                components['metrics'].render_main_metric(metrics, ticker)
                
                # Create and display chart
                components['chart'].render(
                    chart_type=chart_type,
                    data=data,
                    ticker=ticker,
                    time_period=time_period,
                    indicators=indicators
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

if __name__ == "__main__":
    main()
