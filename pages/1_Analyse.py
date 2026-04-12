"""
Portfolio-Analyse
Performance Charts, Asset-Verteilung, Sektor-Analyse, Geografische Verteilung
Alle Pie Charts mit Hover-Details
"""

import time
from typing import Optional
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf
import os
from performance_tracker import PerformanceTracker
from styles import get_custom_css, show_demo_banner
from logo_mapping import get_region

st.set_page_config(
    page_title="Portfolio-Analyse",
    page_icon="📊",
    layout="wide"
)

# Demo-Modus: Liest die Umgebungsvariable DEMO_MODE.
# Wenn aktiv, werden Beispieldaten geladen statt echter Portfolio-Daten.
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# Fail-Safe: Siehe app.py – fällt automatisch auf Demo-Daten zurück,
# wenn die produktive Portfolio.csv nicht verfügbar ist.
if not DEMO_MODE and not os.path.exists("Portfolio.csv"):
    DEMO_MODE = True

SESSION_TIMEOUT = 8 * 60
PORTFOLIO_FILE = "Portfolio.demo.csv" if DEMO_MODE else "Portfolio.csv"

def check_session_timeout() -> None:
    current_time = time.time()
    if "last_activity" not in st.session_state:
        st.session_state["last_activity"] = current_time
    if current_time - st.session_state["last_activity"] > SESSION_TIMEOUT:
        if "password_correct" in st.session_state:
            st.session_state["password_correct"] = False
        st.warning("Session abgelaufen.")
        st.stop()
    st.session_state["last_activity"] = current_time

@st.cache_data(ttl=3600)
def load_portfolio(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path, sep=None, engine="python")

@st.cache_data(ttl=1800)
def get_exchange_rate(from_currency: str, to_currency: str = "EUR") -> Optional[float]:
    try:
        ticker = f"{from_currency}{to_currency}=X"
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            return float(data["Close"].iloc[-1])
    except:
        return None
    return None

@st.cache_data(ttl=300)
def get_price(ticker: str) -> Optional[float]:
    if ticker in ["GOLD-750", "VRENELI-20FR", "NL-10G-WILLEM3", "SOVEREIGN-VICTORIA"]:
        try:
            gold = yf.Ticker("GLD")
            data = gold.history(period="5d")
            if not data.empty:
                gld_price = float(data["Close"].iloc[-1])
                price_usd_oz = gld_price * 10
                eur_usd_rate = get_exchange_rate("EUR", "USD")
                if eur_usd_rate:
                    price_eur_oz = price_usd_oz / eur_usd_rate
                    price_eur_g = price_eur_oz / 31.1035
                    if ticker == "GOLD-750":
                        return price_eur_g * 0.75
                    elif ticker == "VRENELI-20FR":
                        return price_eur_g * 5.81
                    elif ticker == "NL-10G-WILLEM3":
                        return price_eur_g * 6.05
                    elif ticker == "SOVEREIGN-VICTORIA":
                        return price_eur_g * 7.32
            return None
        except:
            return None
    
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="5d")
        if data.empty:
            return None
        price = float(data["Close"].dropna().iloc[-1])
        if ticker.endswith(".L"):
            price /= 100
        currency = None
        try:
            currency = stock.fast_info.get("currency", None)
        except:
            pass
        if currency is None:
            if ticker.endswith((".DE", ".PA", ".AS")):
                currency = "EUR"
            elif ticker.endswith(".L"):
                currency = "GBP"
            elif ticker.endswith(".ST"):
                currency = "SEK"
            elif ticker.endswith(".CO"):
                currency = "DKK"
            else:
                currency = "USD"
        if currency != "EUR":
            if currency == "USD":
                rate = get_exchange_rate("EUR", "USD")
                if rate:
                    price = price / rate
            else:
                rate = get_exchange_rate(currency, "EUR")
                if rate:
                    price *= rate
        return price
    except:
        return None

def main() -> None:
    check_session_timeout()
    
    st.title("📊 Portfolio-Analyse")

    if DEMO_MODE:
        show_demo_banner(compact=True)
    
    with st.sidebar:
        st.header("⚙️ Einstellungen")
        dark_mode = st.toggle("🌓 Dark Mode", value=True)
    
    st.markdown(get_custom_css(dark_mode), unsafe_allow_html=True)
    chart_template = "plotly_dark" if dark_mode else "plotly_white"
    
    df = load_portfolio(PORTFOLIO_FILE)
    if "BuyPrice" in df.columns:
        df["BuyPrice"] = pd.to_numeric(df["BuyPrice"], errors='coerce')
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors='coerce')
    df["Price"] = df["Ticker"].apply(get_price).fillna(0)
    df["Value"] = df["Quantity"] * df["Price"]
    
    # Portfolio% HIER berechnen - VOR den Pie Charts!
    df["Portfolio%"] = (df["Value"] / df["Value"].sum()) * 100
    
    if "BuyPrice" in df.columns:
        df["InvestedValue"] = df["Quantity"] * df["BuyPrice"]
        df["Profit"] = df["Value"] - df["InvestedValue"]
        df["Profit%"] = ((df["Price"] / df["BuyPrice"]) - 1) * 100
        
        st.subheader("📈 Portfolio Performance")
        
        history_file = "portfolio_history.demo.csv" if DEMO_MODE else "portfolio_history.csv"
        tracker = PerformanceTracker(history_file=history_file)
        
        if "selected_period" not in st.session_state:
            st.session_state["selected_period"] = "All"
        
        history_df = pd.read_csv(history_file) if os.path.exists(history_file) else pd.DataFrame()
        data_days = len(history_df) if not history_df.empty else 0
        
        period_requirements = {"1D": 2, "5D": 5, "1M": 30, "6M": 180, "YTD": 30, "5Y": 365*5, "All": 1}
        
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
        col_btn5, col_btn6, col_btn7 = st.columns([1,1,1])
        
        periods = ["1D", "5D", "1M", "6M", "YTD", "5Y", "All"]
        button_cols = [col_btn1, col_btn2, col_btn3, col_btn4, col_btn5, col_btn6, col_btn7]
        
        for col, period in zip(button_cols, periods):
            with col:
                is_disabled = data_days < period_requirements[period]
                is_selected = st.session_state["selected_period"] == period
                button_type = "primary" if is_selected and not is_disabled else "secondary"
                if st.button(period, use_container_width=True, disabled=is_disabled, type=button_type, key=f"btn_{period}"):
                    st.session_state["selected_period"] = period
                    st.rerun()
        
        selected_period = st.session_state["selected_period"]
        perf_fig = tracker.create_performance_chart(period=selected_period, dark_mode=dark_mode)
        st.plotly_chart(perf_fig, use_container_width=True)
        
        _, perf_pct, stats = tracker.get_performance_data(selected_period)
        
        if stats:
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("Min", f"{stats['min_value']:,.0f} €")
            with col_stat2:
                st.metric("Durchschnitt", f"{stats['avg_value']:,.0f} €")
            with col_stat3:
                st.metric("Max", f"{stats['max_value']:,.0f} €")
        
        st.markdown("---")
        st.subheader("Portfolio-Verteilung")
        
        col_pie1, col_pie2, col_pie3 = st.columns(3)
        
        # ========================================
        # PIE 1: ASSET-KLASSE MIT HOVER
        # ========================================
        with col_pie1:
            st.markdown("### Asset-Klasse")
            
            # Gruppiere mit Ticker-Details
            type_data = df.groupby("Type").agg({
                "Value": "sum",
                "Ticker": lambda x: list(x),
                "Portfolio%": lambda x: list(x)
            }).reset_index()
            
            # Hover-Text generieren
            hover_text = []
            for _, row in type_data.iterrows():
                tickers = row["Ticker"]
                percentages = row["Portfolio%"]
                text = f"<b>{row['Type']}</b><br>"
                text += "<br>".join([f"{t}: {p:.1f}%" for t, p in zip(tickers, percentages)])
                hover_text.append(text)
            
            fig1 = px.pie(type_data, values="Value", names="Type", hole=0.4, 
                         color_discrete_sequence=px.colors.sequential.RdBu, 
                         template=chart_template, custom_data=[hover_text])
            fig1.update_layout(height=500, showlegend=True, 
                              legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05, font=dict(size=10)))
            if not dark_mode:
                fig1.update_layout(paper_bgcolor='white', plot_bgcolor='white', font=dict(color='#262730'))
            fig1.update_traces(textposition='inside', textinfo='percent', textfont_size=12,
                              hovertemplate="%{customdata[0]}<extra></extra>")
            st.plotly_chart(fig1, use_container_width=True)
        
        # ========================================
        # PIE 2: SEKTOR MIT HOVER
        # ========================================
        with col_pie2:
            st.markdown("### Sektor")
            if "Sector" in df.columns:
                # Gruppiere mit Ticker-Details
                sector_data = df.groupby("Sector").agg({
                    "Value": "sum",
                    "Ticker": lambda x: list(x),
                    "Portfolio%": lambda x: list(x)
                }).reset_index()
                
                # Hover-Text generieren
                hover_text = []
                for _, row in sector_data.iterrows():
                    tickers = row["Ticker"]
                    percentages = row["Portfolio%"]
                    text = f"<b>{row['Sector']}</b><br>"
                    text += "<br>".join([f"{t}: {p:.1f}%" for t, p in zip(tickers, percentages)])
                    hover_text.append(text)
                
                fig2 = px.pie(sector_data, values="Value", names="Sector", hole=0.4, 
                             template=chart_template, custom_data=[hover_text])
                fig2.update_layout(height=500, showlegend=True, 
                                  legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05, font=dict(size=10)))
                if not dark_mode:
                    fig2.update_layout(paper_bgcolor='white', plot_bgcolor='white', font=dict(color='#262730'))
                fig2.update_traces(textposition='inside', textinfo='percent', textfont_size=12,
                                  hovertemplate="%{customdata[0]}<extra></extra>")
                st.plotly_chart(fig2, use_container_width=True)
        
        # ========================================
        # PIE 3: GEOGRAFISCH MIT HOVER
        # ========================================
        with col_pie3:
            st.markdown("### Geografisch")
            df["Region"] = df["Ticker"].apply(get_region)
            
            region_data = df.groupby("Region").agg({
                "Value": "sum",
                "Ticker": lambda x: list(x),
                "Portfolio%": lambda x: list(x)
            }).reset_index()
            
            hover_text = []
            for _, row in region_data.iterrows():
                tickers = row["Ticker"]
                percentages = row["Portfolio%"]
                text = f"<b>{row['Region']}</b><br>"
                text += "<br>".join([f"{t}: {p:.1f}%" for t, p in zip(tickers, percentages)])
                hover_text.append(text)
            
            fig3 = px.pie(region_data, values="Value", names="Region", hole=0.4, 
                         template=chart_template, custom_data=[hover_text])
            fig3.update_layout(height=500, showlegend=True, 
                              legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05, font=dict(size=10)))
            if not dark_mode:
                fig3.update_layout(paper_bgcolor='white', plot_bgcolor='white', font=dict(color='#262730'))
            fig3.update_traces(textposition='inside', textinfo='percent', textfont_size=12, 
                             hovertemplate="%{customdata[0]}<extra></extra>")
            st.plotly_chart(fig3, use_container_width=True)

if __name__ == "__main__":
    main()