"""
Dividenden-Tracker
Übersicht über Dividendenzahlungen und Erträge
"""

import os
import time
from typing import Optional
import pandas as pd
import streamlit as st
import yfinance as yf
from dividend_tracker import DividendTracker
from styles import get_custom_css, show_demo_banner

st.set_page_config(
    page_title="Dividenden-Tracker",
    page_icon="💰",
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

    st.title("💰 Dividenden-Tracker 2026")

    if DEMO_MODE:
        show_demo_banner(compact=True)

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

    div_tracker = DividendTracker(df)

    if div_tracker.get_dividend_payers().empty:
        st.info("Keine Dividenden-Daten im Portfolio gefunden.")
        st.stop()

    total_annual_div = div_tracker.get_total_annual_dividends()
    total_value = df["Value"].sum()
    div_yield = (total_annual_div / total_value * 100) if total_value > 0 else 0

    tax_rate = 0.26375
    total_annual_div_net = total_annual_div * (1 - tax_rate)
    total_tax = total_annual_div * tax_rate
    div_count = len(div_tracker.get_dividend_payers())

    col_div1, col_div2, col_div3 = st.columns(3)

    with col_div1:
        st.metric(
            "Brutto-Dividenden",
            f"{total_annual_div:,.2f} EUR",
            delta=f"-{total_tax:,.2f} EUR Steuern",
            delta_color="normal",
        )
    with col_div2:
        st.metric(
            "Netto-Dividenden",
            f"{total_annual_div_net:,.2f} EUR",
            delta=f"Yield: {div_yield:.2f}%",
        )
    with col_div3:
        st.metric("Dividenden-Positionen", f"{div_count}")

    st.markdown("---")
    st.markdown("### 📅 Nächste Zahlungen (90 Tage)")

    upcoming = div_tracker.get_upcoming_payments(days_ahead=90)

    if not upcoming.empty:
        for _, payment in upcoming.iterrows():
            payment_date = payment['PaymentDate'].strftime('%d. %B %Y')
            payment_net = payment['Amount'] * (1 - tax_rate)
            st.markdown(f"""<div style="background: rgba(16, 185, 129, 0.1);border-left: 4px solid #10B981;padding: 12px;margin: 8px 0;border-radius: 8px;"><div style="display: flex; justify-content: space-between; align-items: center;"><div><strong style="font-size: 1.1rem;">{payment_date}</strong><div style="margin-top: 4px;"><span style="font-weight: bold;">{payment['Ticker']}</span><span style="color: #64748B; margin-left: 8px;">{payment['Name'][:30]}</span></div></div><div style="text-align: right;"><div style="color: #10B981; font-weight: bold; font-size: 1.2rem;">{payment_net:,.2f} EUR</div><div style="color: #64748B; font-size: 0.85rem;">Brutto: {payment['Amount']:,.2f} EUR | YoC: {payment['YoC']:.2f}%</div></div></div></div>""", unsafe_allow_html=True)
    else:
        st.info("Keine Dividendenzahlungen in den nächsten 90 Tagen.")

    st.markdown("---")
    st.markdown("### 🏆 Top Dividenden-Zahler")

    top_payers = div_tracker.get_top_dividend_payers(n=5)

    if not top_payers.empty:
        for idx, payer in top_payers.iterrows():
            annual_net = payer['AnnualDividend'] * (1 - tax_rate)
            st.markdown(f"""<div style="background: rgba(59, 130, 246, 0.1);padding: 12px;margin: 8px 0;border-radius: 8px;"><div style="display: flex; justify-content: space-between; align-items: center;"><div><strong style="font-size: 1.1rem;">{payer['Ticker']}</strong><span style="color: #64748B; margin-left: 8px;">{payer['Name'][:30]}</span></div><div style="text-align: right;"><div style="font-weight: bold; font-size: 1.1rem;">{annual_net:,.2f} EUR/Jahr</div><div style="color: #64748B; font-size: 0.85rem;">Brutto: {payer['AnnualDividend']:,.2f} EUR | YoC: {payer['YoC']:.2f}%</div></div></div></div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()