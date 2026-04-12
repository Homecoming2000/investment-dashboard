"""
Investment Dashboard - Hauptseite
Metriken, Portfolio-Tabelle mit Logos, Top/Worst Performers
"""

import os
import time
from typing import Optional
import pandas as pd
import streamlit as st
import yfinance as yf
from performance_tracker import PerformanceTracker
from styles import get_custom_css, show_demo_banner
from logo_mapping import get_logo_url

st.set_page_config(
    page_title="Investment Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Demo-Modus: Liest die Umgebungsvariable DEMO_MODE.
# Wenn aktiv, werden Beispieldaten geladen statt echter Portfolio-Daten.
# Damit können persönliche Finanzdaten lokal bleiben, während das
# öffentliche Repository gefahrlos mit Beispieldaten läuft.
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# Fail-Safe: Wenn die produktive Portfolio.csv nicht existiert (z.B. bei
# Cloud-Deployment oder nach frischem Clone), automatisch in den
# Demo-Modus wechseln. Verhindert Abstürze und stellt sicher, dass das
# Dashboard immer in einem sicheren Zustand startet.
if not DEMO_MODE and not os.path.exists("Portfolio.csv"):
    DEMO_MODE = True

SESSION_TIMEOUT = 8 * 60
REFRESH_INTERVAL = 60
PORTFOLIO_FILE = "Portfolio.demo.csv" if DEMO_MODE else "Portfolio.csv"

def check_password() -> bool:
    """Validate password. Im Demo-Modus deaktiviert."""
    # Im Demo-Modus kein Passwortschutz, damit jeder das Dashboard ansehen kann
    if DEMO_MODE:
        return True

    def password_entered() -> None:
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Passwort eingeben", type="password",
                      on_change=password_entered, key="password")
        return False

    if not st.session_state["password_correct"]:
        st.text_input("Passwort eingeben", type="password",
                      on_change=password_entered, key="password")
        st.error("Falsches Passwort")
        return False
    return True

def check_session_timeout() -> None:
    """Auto logout."""
    current_time = time.time()
    if "last_activity" not in st.session_state:
        st.session_state["last_activity"] = current_time
    if current_time - st.session_state["last_activity"] > SESSION_TIMEOUT:
        st.session_state["password_correct"] = False
        st.warning("Automatischer Logout.")
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

def auto_refresh() -> None:
    if "last_refresh" not in st.session_state:
        st.session_state["last_refresh"] = time.time()
    if time.time() - st.session_state["last_refresh"] > REFRESH_INTERVAL:
        st.session_state["last_refresh"] = time.time()
        st.rerun()

def main() -> None:
    if not check_password():
        st.stop()
    check_session_timeout()
    auto_refresh()

    st.title("📊 Mein Investment Dashboard")

    

    with st.sidebar:
        st.header("⚙️ Einstellungen")
        dark_mode = st.toggle("🌓 Dark Mode", value=True)

    st.markdown(get_custom_css(dark_mode), unsafe_allow_html=True)

    df = load_portfolio(PORTFOLIO_FILE)
    if "BuyPrice" in df.columns:
        df["BuyPrice"] = pd.to_numeric(df["BuyPrice"], errors='coerce')
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors='coerce')
    df["Price"] = df["Ticker"].apply(get_price).fillna(0)
    df["Value"] = df["Quantity"] * df["Price"]

    if "BuyPrice" in df.columns:
        df["InvestedValue"] = df["Quantity"] * df["BuyPrice"]
        df["Profit"] = df["Value"] - df["InvestedValue"]
        df["Profit%"] = ((df["Price"] / df["BuyPrice"]) - 1) * 100
        
        total_invested = df["InvestedValue"].sum()
        total_value = df["Value"].sum()
        total_profit = total_value - total_invested
        total_profit_pct = (total_profit / total_invested) * 100
        
        history_file = "portfolio_history.demo.csv" if DEMO_MODE else "portfolio_history.csv"
        tracker = PerformanceTracker(history_file=history_file)
        tracker.log_daily_value(total_value, total_invested)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Investiert")
            st.metric(label="", value=f"{total_invested:,.2f} EUR", label_visibility="collapsed")
        with col2:
            st.subheader("Aktueller Wert")
            st.metric(label="", value=f"{total_value:,.2f} EUR", label_visibility="collapsed")
        with col3:
            st.subheader("Gewinn/Verlust")
            st.metric(label="", value=f"{total_profit:,.2f} EUR", delta=f"{total_profit_pct:+.2f}%", label_visibility="collapsed")
            
        st.markdown("---")
        st.subheader("Portfolio-Übersicht")
        
        df["Logo"] = df["Ticker"].apply(get_logo_url)
        display_columns = ["Logo", "Ticker", "Quantity", "Type", "Name", 
                          "BuyPrice", "Price", "Value", "Profit", "Profit%"]
        
        st.dataframe(
            df[display_columns].round(2),
            column_config={
                "Logo": st.column_config.ImageColumn("", width="small"),
                "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                "Quantity": st.column_config.NumberColumn("Qty", format="%.2f"),
                "Type": st.column_config.TextColumn("Type", width="small"),
                "Name": st.column_config.TextColumn("Name", width="medium"),
                "BuyPrice": st.column_config.NumberColumn("Buy €", format="%.2f"),
                "Price": st.column_config.NumberColumn("Preis €", format="%.2f"),
                "Value": st.column_config.NumberColumn("Wert €", format="%.2f"),
                "Profit": st.column_config.NumberColumn("Profit €", format="%.2f"),
                "Profit%": st.column_config.NumberColumn("Profit %", format="%.2f"),
            },
            use_container_width=True,
            hide_index=True
        )
        
        st.write(f"**Gesamtportfolio-Wert:** {df['Value'].sum():,.2f} EUR")
        st.markdown("---")
        
        st.subheader("Portfolio Performance Highlights")
        performers_df = df[df["BuyPrice"] > 0].copy()
        performers_df = performers_df.sort_values("Profit%", ascending=False)
        
        col_top, col_worst = st.columns(2)
        
        with col_top:
            st.markdown("### 📈 Top 5 Gewinner")
            top_5 = performers_df.head(5)
            for idx, row in top_5.iterrows():
                profit_color = "#10B981" if row["Profit"] >= 0 else "#EF4444"
                st.markdown(f"""<div style="background: rgba(16, 185, 129, 0.1);border-left: 4px solid {profit_color};padding: 12px;margin: 8px 0;border-radius: 8px;"><div style="display: flex; justify-content: space-between; align-items: center;"><div><strong style="font-size: 1.1rem;">{row['Ticker']}</strong><span style="color: #64748B; margin-left: 8px;">{row['Name'][:30]}</span></div><div style="text-align: right;"><div style="color: {profit_color}; font-weight: bold; font-size: 1.2rem;">{'+' if row['Profit%'] >= 0 else ''}{row['Profit%']:.2f}%</div><div style="color: {profit_color}; font-size: 0.9rem;">{'+' if row['Profit'] >= 0 else ''}{row['Profit']:,.2f} EUR</div></div></div></div>""", unsafe_allow_html=True)
        
        with col_worst:
            st.markdown("### 📉 Top 5 Verlierer")
            worst_5 = performers_df.tail(5)
            for idx, row in worst_5.iterrows():
                profit_color = "#10B981" if row["Profit"] >= 0 else "#EF4444"
                st.markdown(f"""<div style="background: rgba(239, 68, 68, 0.1);border-left: 4px solid {profit_color};padding: 12px;margin: 8px 0;border-radius: 8px;"><div style="display: flex; justify-content: space-between; align-items: center;"><div><strong style="font-size: 1.1rem;">{row['Ticker']}</strong><span style="color: #64748B; margin-left: 8px;">{row['Name'][:30]}</span></div><div style="text-align: right;"><div style="color: {profit_color}; font-weight: bold; font-size: 1.2rem;">{'+' if row['Profit%'] >= 0 else ''}{row['Profit%']:.2f}%</div><div style="color: {profit_color}; font-size: 0.9rem;">{'+' if row['Profit'] >= 0 else ''}{row['Profit']:,.2f} EUR</div></div></div></div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
