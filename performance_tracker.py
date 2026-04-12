"""
Portfolio Performance Tracker
Handles historical data logging and performance chart generation
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Tuple

import pandas as pd
import plotly.graph_objects as go


class PerformanceTracker:
    """Track and visualize portfolio performance over time."""
    
    def __init__(self, history_file: str = "portfolio_history.csv"):
        self.history_file = history_file
        self._ensure_history_file()
    
    def _ensure_history_file(self) -> None:
        """Create history file if it doesn't exist."""
        if not os.path.exists(self.history_file):
            df = pd.DataFrame(columns=[
                "Date", "TotalValue", "TotalInvested", "Profit", "ProfitPercent"
            ])
            df.to_csv(self.history_file, index=False)
    
    def log_daily_value(
        self, 
        total_value: float, 
        total_invested: float
    ) -> None:
        """Log today's portfolio value."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Load existing data
        df = pd.read_csv(self.history_file)
        
        # Check if today already logged
        if today in df["Date"].values:
            # Update existing entry
            df.loc[df["Date"] == today, "TotalValue"] = total_value
            df.loc[df["Date"] == today, "TotalInvested"] = total_invested
            df.loc[df["Date"] == today, "Profit"] = total_value - total_invested
            df.loc[df["Date"] == today, "ProfitPercent"] = (
                ((total_value / total_invested) - 1) * 100
            )
        else:
            # Add new entry
            new_row = {
                "Date": today,
                "TotalValue": total_value,
                "TotalInvested": total_invested,
                "Profit": total_value - total_invested,
                "ProfitPercent": ((total_value / total_invested) - 1) * 100
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        
        # Save
        df.to_csv(self.history_file, index=False)
    
    def get_performance_data(
        self, 
        period: str = "All"
    ) -> Tuple[pd.DataFrame, float, dict]:
        """
        Get performance data for specified period.
        
        Args:
            period: One of ["1D", "5D", "1M", "6M", "YTD", "1Y", "5Y", "All"]
        
        Returns:
            (dataframe, performance_pct, stats_dict)
        """
        df = pd.read_csv(self.history_file)
        
        if df.empty:
            return df, 0.0, {}
        
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")
        
        # Filter by period
        today = datetime.now()
        
        if period == "1D":
            cutoff = today - timedelta(days=1)
        elif period == "5D":
            cutoff = today - timedelta(days=5)
        elif period == "1M":
            cutoff = today - timedelta(days=30)
        elif period == "6M":
            cutoff = today - timedelta(days=180)
        elif period == "YTD":
            cutoff = datetime(today.year, 1, 1)
        elif period == "1Y":
            cutoff = today - timedelta(days=365)
        elif period == "5Y":
            cutoff = today - timedelta(days=365*5)
        else:  # All
            cutoff = df["Date"].min()
        
        df_filtered = df[df["Date"] >= cutoff].copy()
        
        if df_filtered.empty:
            return df_filtered, 0.0, {}
        
        # Calculate performance
        start_value = df_filtered.iloc[0]["TotalValue"]
        end_value = df_filtered.iloc[-1]["TotalValue"]
        performance_pct = ((end_value / start_value) - 1) * 100 if start_value > 0 else 0
        
        # Calculate stats
        stats = {
            "min_value": df_filtered["TotalValue"].min(),
            "max_value": df_filtered["TotalValue"].max(),
            "avg_value": df_filtered["TotalValue"].mean(),
            "start_value": start_value,
            "end_value": end_value,
            "best_day": df_filtered.loc[df_filtered["ProfitPercent"].idxmax(), "Date"].strftime("%Y-%m-%d"),
            "worst_day": df_filtered.loc[df_filtered["ProfitPercent"].idxmin(), "Date"].strftime("%Y-%m-%d"),
            "volatility": df_filtered["ProfitPercent"].std(),
        }
        
        return df_filtered, performance_pct, stats
    
    def create_performance_chart(
        self, 
        period: str = "All",
        dark_mode: bool = True
    ) -> go.Figure:
        """Create performance chart for specified period."""
        df, perf_pct, stats = self.get_performance_data(period)
        
        if df.empty:
            # Return empty chart
            fig = go.Figure()
            fig.add_annotation(
                text="Keine Daten vorhanden. Warte auf erstes Daily-Logging.",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="gray")
            )
            return fig
        
        # Determine colors
        if dark_mode:
            bg_color = "#0A0E27"
            grid_color = "#1E293B"
            text_color = "#F1F5F9"
            line_color = "#10B981" if perf_pct >= 0 else "#EF4444"
            fill_color = "rgba(16, 185, 129, 0.2)" if perf_pct >= 0 else "rgba(239, 68, 68, 0.2)"
        else:
            bg_color = "#FFFFFF"
            grid_color = "#E2E8F0"
            text_color = "#1E293B"
            line_color = "#059669" if perf_pct >= 0 else "#DC2626"
            fill_color = "rgba(5, 150, 105, 0.1)" if perf_pct >= 0 else "rgba(220, 38, 38, 0.1)"
        
        # Create figure
        fig = go.Figure()
        
        # Add baseline (invested amount)
        fig.add_trace(go.Scatter(
            x=df["Date"],
            y=[stats["start_value"]] * len(df),
            mode="lines",
            name="Einstandswert",
            line=dict(color=text_color, width=1, dash="dash"),
            hoverinfo="skip"
        ))
        
        # Add performance line
        fig.add_trace(go.Scatter(
            x=df["Date"],
            y=df["TotalValue"],
            mode="lines",
            name="Portfolio-Wert",
            line=dict(color=line_color, width=3),
            fill="tonexty",
            fillcolor=fill_color,
            hovertemplate=(
                "<b>%{x|%d.%m.%Y}</b><br>" +
                "Wert: %{y:,.2f} EUR<br>" +
                "<extra></extra>"
            )
        ))
        
        # Layout
        fig.update_layout(
            template="plotly_dark" if dark_mode else "plotly_white",
            paper_bgcolor=bg_color,
            plot_bgcolor=bg_color,
            font=dict(color=text_color, family="Inter, sans-serif"),
            height=600,
            margin=dict(l=20, r=20, t=40, b=20),
            hovermode="x unified",
            showlegend=False,
            xaxis=dict(
                showgrid=True,
                gridcolor=grid_color,
                gridwidth=1,
            ),
            yaxis=dict(
                autorange=True,  # Automatisch
                showgrid=True,
                gridcolor=grid_color,
                gridwidth=1,
                tickformat=",.0f",
                ticksuffix=" €",
                rangemode='normal'
            )
        )
        
        return fig
    