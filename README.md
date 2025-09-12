# Real-Time Stock Price Dashboard

> A professional-grade, real-time stock analysis dashboard built with Python and Streamlit, featuring advanced technical indicators, intelligent caching, and a beautiful dark theme.

## 🎯 Project Overview

This dashboard was originally created for personal investment tracking but has evolved into a comprehensive financial analysis tool. It provides real-time stock data visualization, technical analysis, and trading signals through an elegant, responsive interface.

**Key Highlights:**
- **Real-time data** from Yahoo Finance API
- **Advanced technical indicators** (SMA, EMA, RSI, MACD, Bollinger Bands)
- **Intelligent SQLite caching** for optimal performance
- **Professional dark theme** with modern UI/UX
- **Modular architecture** for maintainability and scalability

## 🏗️ Architecture & Design

### Service-Oriented Component Architecture

Since Streamlit doesn't natively support MVC patterns, this project implements a **Service-Oriented Component Architecture** that provides:

- **Separation of Concerns**: Each module has a specific, well-defined responsibility
- **Reusability**: Components and services can be easily reused across the application
- **Testability**: Independent testing of services and components
- **Maintainability**: Changes to one module don't cascade to others
- **Scalability**: Simple to add new features, indicators, and data sources

### Directory Structure

```
Real_Time_Stock_Price_Dashboard/
├── app.py                          # Main Streamlit application entry point
├── config/
│   └── settings.py                 # Centralized configuration and constants
├── database/
│   ├── models.py                   # Data models and schemas
│   └── database_manager.py         # SQLite operations and caching logic
├── services/
│   ├── data_service.py             # Stock data fetching and processing
│   └── technical_indicators_service.py  # Technical analysis calculations
├── components/
│   ├── ui_components.py            # Reusable Streamlit UI components
│   └── chart_components.py         # Plotly chart components and visualizations
├── css/
│   └── styles.css                  # Custom dark theme styling
├── data/                           # SQLite database storage
└── requirements.txt                # Python dependencies
```

### Data Flow Architecture

```
User Input (Sidebar) 
    ↓
UI Components (components/ui_components.py)
    ↓
Main App (app.py)
    ↓
Services Layer (services/)
    ↓
Database Layer (database/)
    ↓
External APIs (Yahoo Finance)
```

### Database Schema

**Stock Data Table:**
```sql
CREATE TABLE stock_data (
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
);
```

**Technical Indicators Table:**
```sql
CREATE TABLE technical_indicators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    datetime TIMESTAMP NOT NULL,
    sma_20 REAL,
    ema_20 REAL,
    rsi_14 REAL,
    macd REAL,
    macd_signal REAL,
    bb_upper REAL,
    bb_middle REAL,
    bb_lower REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, datetime)
);
```

## ✨ Features

### Core Functionality
- **Real-Time Data**: Live stock prices with automatic updates
- **Historical Analysis**: Comprehensive historical data visualization
- **Multiple Chart Types**: Candlestick and line charts with dark theme
- **Technical Indicators**: SMA, EMA, RSI, MACD, and Bollinger Bands
- **Trading Signals**: Automated buy/sell signal generation
- **Multi-Ticker Support**: Monitor multiple stocks simultaneously

### Performance & Caching
- **SQLite Caching**: Intelligent local caching reduces API calls
- **Data Persistence**: Automatic data cleanup and optimization
- **Streamlit Caching**: Optimized expensive operations
- **Efficient Queries**: Optimized database operations

### User Experience
- **Dark Theme**: Professional, eye-friendly interface
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Interactive Charts**: Hover states, zoom, and pan functionality
- **Real-Time Updates**: Live price monitoring in sidebar

## 🎨 Design System

### Color Palette
- **Primary Background**: `#0a0a0a` (Deep black)
- **Secondary Background**: `#1a1a1a` (Dark gray)
- **Card Background**: `#1f1f1f` (Slightly lighter gray)
- **Accent Color**: `#00d4aa` (Teal green)
- **Text Colors**: White and light gray variants
- **Border Colors**: Dark gray tones

### Typography
- **Font Family**: Inter (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700
- **Responsive**: Scales appropriately on all devices

### Interactive Elements
- **Hover Effects**: Smooth transitions and elevation changes
- **Focus States**: Clear visual feedback for accessibility
- **Animations**: Subtle pulse effects for loading states
- **Shadows**: Layered shadow system for depth

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/peterajhgraham/Real_Time_Stock_Price_Dashboard.git
   cd Real_Time_Stock_Price_Dashboard
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   streamlit run app.py
   ```

The dashboard will launch in your browser with the beautiful dark theme!

### Dependencies

```
streamlit>=1.28.0      # Web application framework
yfinance>=0.2.18       # Yahoo Finance API integration
pandas>=2.0.0          # Data manipulation and analysis
plotly>=5.15.0         # Interactive charts and visualizations
ta>=0.10.2             # Technical analysis library
pytz>=2023.3           # Timezone handling
```

## 📖 Usage Guide

### Interface Overview

**Main Controls:**
- **Ticker Input**: Enter stock symbol (e.g., AAPL, GOOGL, MSFT)
- **Time Period**: Select data range (1d, 1wk, 1mo, 1y, etc.)
- **Chart Type**: Choose between candlestick and line charts
- **Technical Indicators**: Select one or more indicators to overlay

**Real-Time Monitoring:**
- Sidebar displays live prices for predefined tickers
- Automatic updates with percentage changes
- Color-coded positive/negative changes

### Example Workflows

**1. Real-Time Analysis:**
```
1. Enter "AAPL" in ticker input
2. Select "1d" for intraday analysis
3. Choose "Candlestick" chart type
4. Enable "SMA 20", "EMA 20", and "RSI 14"
5. Click "Update" to visualize data
```

**2. Historical Trend Analysis:**
```
1. Select longer period (e.g., "1y")
2. Use "Line" chart for smooth trend visualization
3. Enable multiple indicators for comprehensive analysis
4. Review historical data table below chart
```

## 🛠️ Technical Stack

### Backend Technologies
- **Python 3.8+**: Core programming language
- **Streamlit**: Web application framework
- **SQLite**: Local database for caching and persistence
- **yfinance**: Yahoo Finance API integration
- **pandas**: Data manipulation and analysis
- **ta**: Technical analysis calculations

### Frontend Technologies
- **Custom CSS**: Dark theme styling and responsive design
- **Plotly**: Interactive charts and visualizations
- **Inter Font**: Modern typography system
- **Responsive Design**: Mobile-first approach

## 🔧 Customization & Extension

### Adding New Technical Indicators

1. **Extend the Service** (`services/technical_indicators_service.py`):
   ```python
   elif indicator == 'NEW_INDICATOR':
       data['NEW_INDICATOR'] = ta.custom.new_indicator(data['Close'])
   ```

2. **Update UI Options** (`config/settings.py`):
   ```python
   TECHNICAL_INDICATORS = ['SMA 20', 'EMA 20', 'RSI 14', 'NEW INDICATOR']
   ```

3. **Add Chart Rendering** (`components/chart_components.py`):
   ```python
   elif indicator == 'NEW INDICATOR' and 'NEW_INDICATOR' in data.columns:
       self.fig.add_trace(go.Scatter(...))
   ```

### Theme Customization

Modify `css/styles.css` to customize the appearance:
```css
:root {
    --primary-bg: #0a0a0a;        /* Main background color */
    --accent-color: #00d4aa;      /* Accent color (teal) */
    --text-primary: #ffffff;      /* Primary text color */
    /* ... other variables */
}
```

### Stock Symbol Configuration

Edit the `DEFAULT_TICKERS` list in `config/settings.py` to modify monitored stocks.

## 🏆 Architecture Benefits

### Modularity
- Single responsibility principle for each module
- Easy to understand and maintain
- Independent development and testing

### Reusability
- UI components reusable across different pages
- Services accessible by multiple components
- Centralized database operations

### Scalability
- Simple addition of new technical indicators
- Easy integration of new chart types
- Straightforward addition of new data sources

### Performance
- SQLite caching reduces API calls
- Efficient data processing pipelines
- Optimized database queries

### Maintainability
- Clear separation of concerns
- Consistent code organization
- Easy debugging and modification

## 🚧 Known Issues & Limitations

- **Data Fetching Errors**: Invalid ticker symbols will display error messages
- **CSS Loading**: App falls back to default styling if CSS file is missing
- **API Rate Limits**: Yahoo Finance may throttle requests during high usage

## 🔮 Future Enhancements

### Planned Features
- **User Management**: Accounts and personalized preferences
- **Portfolio Tracking**: Watchlists and portfolio management
- **Alerts System**: Price and indicator-based notifications
- **Backtesting**: Historical strategy testing capabilities
- **API Endpoints**: REST API for external integrations
- **Real-time Updates**: WebSocket connections for live data

### Architecture Extensions
- **Message Queue**: Handling real-time updates
- **Redis Cache**: Distributed caching solution
- **Microservices**: Service decomposition
- **Docker**: Containerization for deployment

## 🤝 Contributing

Contributions are welcome! Areas for contribution include:

- **New Technical Indicators**: Additional analysis tools
- **Theme Variants**: Light theme or color variations
- **Mobile Optimization**: Enhanced mobile experience
- **Performance**: Data loading and caching optimizations
- **Documentation**: Improved guides and examples

Please ensure your code follows best practices and is well-documented.

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 📞 Contact

For questions or support: peter_graham@brown.edu

---

**Built with ❤️ for investors who appreciate beautiful, functional dashboards!**