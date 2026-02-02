"""
UI Components and Styling
Reusable UI components and styling for the Streamlit interface
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any


class UIComponents:
    """Reusable UI components and styling"""
    
    @staticmethod
    def load_custom_css():
        """Load custom CSS styling"""
        st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            
            .main-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem;
                border-radius: 15px;
                color: white;
                text-align: center;
                margin: 1rem 0;
                font-family: 'Inter', sans-serif;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            }
            
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1.5rem;
                border-radius: 12px;
                color: white;
                text-align: center;
                margin: 0.5rem 0;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                transition: transform 0.2s ease;
            }
            
            .metric-card:hover {
                transform: translateY(-2px);
            }
            
            .speedup-card {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                padding: 1.5rem;
                border-radius: 12px;
                color: white;
                text-align: center;
                margin: 0.5rem 0;
                box-shadow: 0 4px 20px rgba(245,87,108,0.2);
            }
            
            .ai-card {
                background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                padding: 1.5rem;
                border-radius: 12px;
                color: white;
                text-align: center;
                margin: 0.5rem 0;
                box-shadow: 0 4px 20px rgba(17,153,142,0.2);
            }
            
            .timer-display {
                font-family: 'Inter', sans-serif;
                font-size: 2.2rem;
                font-weight: 700;
                color: #FFD93D;
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }
            
            .status-badge {
                background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
                padding: 0.4rem 1rem;
                border-radius: 20px;
                color: white;
                font-weight: 600;
                font-size: 0.9rem;
                display: inline-block;
                margin: 0.2rem;
            }
            
            .recommendation-card {
                background: rgba(255,255,255,0.05);
                border-left: 4px solid #4ECDC4;
                padding: 1rem;
                border-radius: 8px;
                margin: 0.5rem 0;
                backdrop-filter: blur(10px);
            }
            
            .performance-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                margin: 1rem 0;
            }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def create_header(title: str, subtitle: str = ""):
        """Create main application header"""
        header_html = f"""
        <div class="main-header">
            <h1>{title}</h1>
            {f'<p>{subtitle}</p>' if subtitle else ''}
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)
    
    @staticmethod
    def create_metric_card(title: str, value: str, subtitle: str = "", card_type: str = "metric"):
        """Create a metric display card"""
        card_class = f"{card_type}-card"
        card_html = f"""
        <div class="{card_class}">
            <h3>{title}</h3>
            <h1>{value}</h1>
            {f'<p>{subtitle}</p>' if subtitle else ''}
        </div>
        """
        return card_html
    
    @staticmethod
    def create_timer_display(time_value: float, label: str = ""):
        """Create animated timer display"""
        timer_html = f"""
        <div style="text-align: center; margin: 1rem 0;">
            <div class="timer-display">{time_value:.1f}s</div>
            {f'<p style="color: #666; margin-top: 0.5rem;">{label}</p>' if label else ''}
        </div>
        """
        return timer_html
    
    @staticmethod
    def create_status_badge(text: str, status_type: str = "info"):
        """Create status badge"""
        colors = {
            'success': '#4CAF50',
            'warning': '#FF9800',
            'error': '#F44336',
            'info': '#2196F3'
        }
        color = colors.get(status_type, colors['info'])
        
        badge_html = f"""
        <span style="
            background: {color};
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.85rem;
            font-weight: 600;
            display: inline-block;
            margin: 0.2rem;
        ">{text}</span>
        """
        return badge_html
    
    @staticmethod
    def create_recommendation_card(recommendation: Dict[str, str]):
        """Create AI recommendation card"""
        icons = {
            'success': '✅',
            'warning': '⚠️',
            'error': '🚨',
            'info': '💡',
            'optimization': '⚡'
        }
        
        icon = icons.get(recommendation.get('type', 'info'), '💡')
        
        card_html = f"""
        <div class="recommendation-card">
            <h4>{icon} {recommendation.get('title', 'Recommendation')}</h4>
            <p>{recommendation.get('message', '')}</p>
        </div>
        """
        return card_html
    
    @staticmethod
    def create_speedup_gauge(speedup: float, max_value: float = 10.0):
        """Create speedup gauge visualization"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=speedup,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Speedup Factor", 'font': {'size': 20}},
            delta={'reference': 1},
            gauge={
                'axis': {'range': [None, max_value]},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [0, 2], 'color': "lightgray"},
                    {'range': [2, 5], 'color': "#FFD93D"},
                    {'range': [5, max_value], 'color': "#4CAF50"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_value * 0.8
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            font={'color': "darkblue", 'family': "Inter"},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        return fig
    
    @staticmethod
    def create_performance_chart(metrics_history: List[Dict[str, Any]]):
        """Create performance monitoring chart"""
        if not metrics_history:
            return None
        
        df = pd.DataFrame(metrics_history)
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('CPU Usage %', 'Memory Usage %', 'System Load', 'Performance Trend'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # CPU Usage
        fig.add_trace(
            go.Scatter(
                x=df.index, 
                y=df['cpu_percent'], 
                name='CPU %', 
                line=dict(color='#FF6B6B', width=2)
            ),
            row=1, col=1
        )
        
        # Memory Usage
        fig.add_trace(
            go.Scatter(
                x=df.index, 
                y=df['memory_percent'], 
                name='Memory %', 
                line=dict(color='#4ECDC4', width=2)
            ),
            row=1, col=2
        )
        
        # System Load
        if 'cpu_percent' in df.columns and 'memory_percent' in df.columns:
            system_load = df['cpu_percent'] + df['memory_percent']
            fig.add_trace(
                go.Scatter(
                    x=df.index, 
                    y=system_load, 
                    name='System Load', 
                    line=dict(color='#FFD93D', width=2),
                    fill='tonexty'
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            height=500, 
            showlegend=True,
            title_text="Real-Time System Performance",
            font={'family': "Inter"},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        return fig
    
    @staticmethod
    def create_processing_comparison_chart(sequential_time: float, parallel_time: float, workers: int):
        """Create before/after comparison chart"""
        categories = ['Sequential', 'Parallel']
        times = [sequential_time, parallel_time]
        colors = ['#FF6B6B', '#4CAF50']
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=times,
                marker_color=colors,
                text=[f'{t:.1f}s' for t in times],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title=f"Processing Time Comparison ({workers} workers)",
            yaxis_title="Time (seconds)",
            font={'family': "Inter"},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=400
        )
        
        return fig