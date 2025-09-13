"""
Chart components for the stock dashboard
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any, List, Optional

from config.settings import CHART_HEIGHT


class ChartComponent:
    """Component for creating and displaying stock charts"""
    
    def __init__(self):
        self.fig = None
    
    def create_candlestick_chart(self, data: pd.DataFrame, ticker: str, 
                                time_period: str, indicators: List[str] = None, company_name: str = None) -> go.Figure:
        """Create a candlestick chart with technical indicators"""
        self.fig = go.Figure()
        
        # Create continuous index to remove weekend gaps
        continuous_index = list(range(len(data)))
        
        # Add candlestick trace with dark theme colors
        self.fig.add_trace(go.Candlestick(
            x=continuous_index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Price',
            increasing_line_color='#00d4aa',
            decreasing_line_color='#e74c3c',
            increasing_fillcolor='#00d4aa',
            decreasing_fillcolor='#e74c3c'
        ))
        
        # Add technical indicators
        if indicators:
            self._add_technical_indicators(data, indicators, continuous_index)
        
        # Update layout with dark theme
        self._update_layout(ticker, time_period, dark_theme=True, data=data, continuous_index=continuous_index, company_name=company_name)
        
        return self.fig
    
    def create_line_chart(self, data: pd.DataFrame, ticker: str, 
                         time_period: str, indicators: List[str] = None, company_name: str = None) -> go.Figure:
        """Create a line chart with technical indicators"""
        self.fig = go.Figure()
        
        # Create continuous index to remove weekend gaps
        continuous_index = list(range(len(data)))
        
        # Add price line with dark theme color
        self.fig.add_trace(go.Scatter(
            x=continuous_index,
            y=data['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='#00d4aa', width=3)
        ))
        
        # Add technical indicators
        if indicators:
            self._add_technical_indicators(data, indicators, continuous_index)
        
        # Update layout with dark theme
        self._update_layout(ticker, time_period, dark_theme=True, data=data, continuous_index=continuous_index, company_name=company_name)
        
        return self.fig
    
    def _add_technical_indicators(self, data: pd.DataFrame, indicators: List[str], continuous_index: List[int]):
        """Add technical indicators to the chart with dark theme colors"""
        colors = {
            'SMA 20': '#00d4aa',  # Green
            'SMA 50': '#ff7f0e',  # Orange
            'SMA 100': '#2ca02c', # Dark green
            'SMA 200': '#d62728', # Red
            'EMA 20': '#00d4aa',
            'RSI 14': '#e74c3c',
            'MACD': '#9b59b6',
            'Bollinger Bands': '#3498db'
        }
        
        for indicator in indicators:
            if indicator == 'SMA 20' and 'SMA_20' in data.columns:
                self.fig.add_trace(go.Scatter(
                    x=continuous_index,
                    y=data['SMA_20'],
                    mode='lines',
                    name='SMA 20',
                    line=dict(color=colors.get('SMA 20', '#ff7f0e'), width=1),
                    opacity=0.8
                ))
            
            elif indicator == 'SMA 50' and 'SMA_50' in data.columns:
                self.fig.add_trace(go.Scatter(
                    x=continuous_index,
                    y=data['SMA_50'],
                    mode='lines',
                    name='SMA 50',
                    line=dict(color=colors.get('SMA 50', '#ff7f0e'), width=1),
                    opacity=0.8
                ))
            
            elif indicator == 'SMA 100' and 'SMA_100' in data.columns:
                self.fig.add_trace(go.Scatter(
                    x=continuous_index,
                    y=data['SMA_100'],
                    mode='lines',
                    name='SMA 100',
                    line=dict(color=colors.get('SMA 100', '#2ca02c'), width=1),
                    opacity=0.8
                ))
            
            elif indicator == 'SMA 200' and 'SMA_200' in data.columns:
                self.fig.add_trace(go.Scatter(
                    x=continuous_index,
                    y=data['SMA_200'],
                    mode='lines',
                    name='SMA 200',
                    line=dict(color=colors.get('SMA 200', '#d62728'), width=1),
                    opacity=0.8
                ))
            
            elif indicator == 'EMA 20' and 'EMA_20' in data.columns:
                self.fig.add_trace(go.Scatter(
                    x=continuous_index,
                    y=data['EMA_20'],
                    mode='lines',
                    name='EMA 20',
                    line=dict(color=colors.get('EMA 20', '#2ca02c'), width=1),
                    opacity=0.8
                ))
            
            elif indicator == 'RSI 14' and 'RSI_14' in data.columns:
                self.fig.add_trace(go.Scatter(
                    x=continuous_index,
                    y=data['RSI_14'],
                    mode='lines',
                    name='RSI 14',
                    line=dict(color=colors.get('RSI 14', '#d62728'), width=1),
                    yaxis='y2',
                    opacity=0.8
                ))
            
            elif indicator == 'MACD' and 'MACD' in data.columns:
                self.fig.add_trace(go.Scatter(
                    x=continuous_index,
                    y=data['MACD'],
                    mode='lines',
                    name='MACD',
                    line=dict(color=colors.get('MACD', '#9467bd'), width=1),
                    opacity=0.8
                ))
                
                if 'MACD_Signal' in data.columns:
                    self.fig.add_trace(go.Scatter(
                        x=continuous_index,
                        y=data['MACD_Signal'],
                        mode='lines',
                        name='MACD Signal',
                        line=dict(color='#17becf', width=1, dash='dash'),
                        opacity=0.8
                    ))
            
            elif indicator == 'Bollinger Bands' and 'BB_Upper' in data.columns:
                # Upper band
                self.fig.add_trace(go.Scatter(
                    x=continuous_index,
                    y=data['BB_Upper'],
                    mode='lines',
                    name='BB Upper',
                    line=dict(color=colors.get('Bollinger Bands', '#8c564b'), width=1),
                    opacity=0.6,
                    showlegend=False
                ))
                
                # Lower band
                if 'BB_Lower' in data.columns:
                    self.fig.add_trace(go.Scatter(
                        x=continuous_index,
                        y=data['BB_Lower'],
                        mode='lines',
                        name='BB Lower',
                        line=dict(color=colors.get('Bollinger Bands', '#8c564b'), width=1),
                        opacity=0.6,
                        fill='tonexty',
                        fillcolor='rgba(140, 86, 75, 0.1)',
                        showlegend=False
                    ))
                
                # Middle band
                if 'BB_Middle' in data.columns:
                    self.fig.add_trace(go.Scatter(
                        x=continuous_index,
                        y=data['BB_Middle'],
                        mode='lines',
                        name='BB Middle',
                        line=dict(color=colors.get('Bollinger Bands', '#8c564b'), width=1, dash='dot'),
                        opacity=0.6
                    ))
    
    def _update_layout(self, ticker: str, time_period: str, dark_theme: bool = True, data: pd.DataFrame = None, continuous_index: List[int] = None, company_name: str = None):
        """Update chart layout with dark theme"""
        if dark_theme:
            # Dark theme colors
            bg_color = '#0a0a0a'
            grid_color = '#333333'
            text_color = '#ffffff'
            title_color = '#00d4aa'
        else:
            # Light theme colors
            bg_color = '#ffffff'
            grid_color = '#e5e5e5'
            text_color = '#000000'
            title_color = '#1f77b4'
        
        # Generate title with company name (always provided now)
        title_text = f"{company_name} ({ticker})" if company_name else f"{ticker} {time_period.upper()} Chart"
        
        self.fig.update_layout(
            title=dict(
                text=title_text,
                font=dict(color=title_color, size=20)
            ),
            xaxis_title='Time',
            yaxis_title='Price (USD)',
            height=CHART_HEIGHT,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor='rgba(0,0,0,0)',
                font=dict(color=text_color)
            ),
            hovermode='x unified',
            template='plotly_dark' if dark_theme else 'plotly_white',
            plot_bgcolor=bg_color,
            paper_bgcolor=bg_color,
            font=dict(color=text_color),
            xaxis=dict(
                gridcolor=grid_color,
                color=text_color,
                title_font=dict(color=text_color)
            ),
            yaxis=dict(
                gridcolor=grid_color,
                color=text_color,
                title_font=dict(color=text_color)
            )
        )
        
        # Add secondary y-axis for RSI
        self.fig.update_layout(
            yaxis2=dict(
                title='RSI',
                overlaying='y',
                side='right',
                showgrid=False,
                range=[0, 100]
            )
        )
        
        # Update x-axis with continuous index and datetime labels
        if data is not None and continuous_index is not None:
            # Create tick positions and labels for the continuous index
            tick_positions = continuous_index
            tick_labels = [data['Datetime'].iloc[i].strftime('%b %d') for i in continuous_index]
            
            # Show only every nth label to avoid overcrowding
            step = max(1, len(tick_positions) // 10)  # Show about 10 labels max
            tick_positions = tick_positions[::step]
            tick_labels = tick_labels[::step]
            
            self.fig.update_xaxes(
                rangeslider_visible=False,
                tickmode='array',
                tickvals=tick_positions,
                ticktext=tick_labels,
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1D", step="day", stepmode="backward"),
                        dict(count=7, label="1W", step="day", stepmode="backward"),
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(step="all")
                    ]),
                    bgcolor='rgba(42, 42, 42, 0.8)',  # Dark background
                    bordercolor='#333333',  # Dark border
                    borderwidth=1,
                    font=dict(color='#000000', size=12)  # Black text for visibility
                )
            )
        else:
            # Fallback to original behavior
            self.fig.update_xaxes(
                rangeslider_visible=False,
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1D", step="day", stepmode="backward"),
                        dict(count=7, label="1W", step="day", stepmode="backward"),
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(step="all")
                    ]),
                    bgcolor='rgba(42, 42, 42, 0.8)',  # Dark background
                    bordercolor='#333333',  # Dark border
                    borderwidth=1,
                    font=dict(color='#000000', size=12)  # Black text for visibility
                )
            )
    
    def render(self, chart_type: str, data: pd.DataFrame, ticker: str, 
               time_period: str, indicators: List[str] = None, company_name: str = None):
        """Render the chart based on type"""
        if data.empty:
            st.warning("No data available for chart")
            return
        
        try:
            if chart_type == 'Candlestick':
                fig = self.create_candlestick_chart(data, ticker, time_period, indicators, company_name)
            else:
                fig = self.create_line_chart(data, ticker, time_period, indicators, company_name)
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating chart: {e}")


class IndicatorSummaryComponent:
    """Component for displaying technical indicator summaries"""
    
    def render(self, indicator_summary: Dict[str, Any]):
        """Render indicator summary"""
        if not indicator_summary:
            return
        
        st.subheader('Technical Indicator Summary')
        
        # Create columns for different indicators
        cols = st.columns(3)
        
        with cols[0]:
            if 'sma_20' in indicator_summary:
                st.metric(
                    label='SMA 20',
                    value=f"{indicator_summary['sma_20']:.2f}"
                )
            
            if 'sma_50' in indicator_summary:
                st.metric(
                    label='SMA 50',
                    value=f"{indicator_summary['sma_50']:.2f}"
                )
            
            if 'sma_100' in indicator_summary:
                st.metric(
                    label='SMA 100',
                    value=f"{indicator_summary['sma_100']:.2f}"
                )
            
            if 'sma_200' in indicator_summary:
                st.metric(
                    label='SMA 200',
                    value=f"{indicator_summary['sma_200']:.2f}"
                )
            
            if 'ema_20' in indicator_summary:
                st.metric(
                    label='EMA 20',
                    value=f"{indicator_summary['ema_20']:.2f}"
                )
        
        with cols[1]:
            if 'rsi_14' in indicator_summary:
                rsi_value = indicator_summary['rsi_14']
                rsi_signal = indicator_summary.get('rsi_signal', 'Neutral')
                
                # Color based on RSI value
                if rsi_value > 70:
                    delta_color = "inverse"
                elif rsi_value < 30:
                    delta_color = "normal"
                else:
                    delta_color = "off"
                
                st.metric(
                    label='RSI 14',
                    value=f"{rsi_value:.1f}",
                    delta=rsi_signal,
                    delta_color=delta_color
                )
        
        with cols[2]:
            if 'macd' in indicator_summary:
                macd_value = indicator_summary['macd']
                macd_signal = indicator_summary.get('macd_signal', 0)
                histogram = indicator_summary.get('macd_histogram', 0)
                
                st.metric(
                    label='MACD',
                    value=f"{macd_value:.4f}",
                    delta=f"Signal: {macd_signal:.4f}"
                )
                
                st.metric(
                    label='MACD Histogram',
                    value=f"{histogram:.4f}"
                )
        
        # Bollinger Bands
        if 'bb_upper' in indicator_summary:
            st.subheader('Bollinger Bands')
            bb_cols = st.columns(3)
            
            with bb_cols[0]:
                st.metric(
                    label='Upper Band',
                    value=f"{indicator_summary['bb_upper']:.2f}"
                )
            
            with bb_cols[1]:
                st.metric(
                    label='Middle Band',
                    value=f"{indicator_summary['bb_middle']:.2f}"
                )
            
            with bb_cols[2]:
                st.metric(
                    label='Lower Band',
                    value=f"{indicator_summary['bb_lower']:.2f}"
                )
            
            st.info(f"**Position:** {indicator_summary.get('bb_position', 'Unknown')}")


class VolumeChartComponent:
    """Component for displaying volume charts"""
    
    def render(self, data: pd.DataFrame):
        """Render volume chart"""
        if data.empty or 'Volume' not in data.columns:
            return
        
        st.subheader('Volume')
        
        fig = go.Figure()
        
        # Create continuous index to remove weekend gaps
        continuous_index = list(range(len(data)))
        
        # Add volume bars with dark theme colors
        fig.add_trace(go.Bar(
            x=continuous_index,
            y=data['Volume'],
            name='Volume',
            marker_color='#00d4aa',
            opacity=0.7
        ))
        
        # Create tick positions and labels for the continuous index
        tick_positions = continuous_index
        tick_labels = [data['Datetime'].iloc[i].strftime('%b %d') for i in continuous_index]
        
        # Show only every nth label to avoid overcrowding
        step = max(1, len(tick_positions) // 10)  # Show about 10 labels max
        tick_positions = tick_positions[::step]
        tick_labels = tick_labels[::step]
        
        fig.update_layout(
            title=dict(
                text='Trading Volume',
                font=dict(color='#00d4aa', size=16)
            ),
            xaxis_title='Time',
            yaxis_title='Volume',
            height=300,
            showlegend=False,
            template='plotly_dark',
            plot_bgcolor='#0a0a0a',
            paper_bgcolor='#0a0a0a',
            font=dict(color='#ffffff'),
            xaxis=dict(
                gridcolor='#333333',
                color='#ffffff',
                tickmode='array',
                tickvals=tick_positions,
                ticktext=tick_labels
            ),
            yaxis=dict(
                gridcolor='#333333',
                color='#ffffff'
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
