"""
Custom CSS Styles for Investment Dashboard
Professional, modern design for both Dark and Light modes
"""
  
import streamlit as st


def get_custom_css(dark_mode: bool = True) -> str:

    """
    Get custom CSS based on theme.
    
    Args:
        dark_mode: If True, return dark mode CSS, else light mode
    
    Returns:
        CSS string
    """
    
    if dark_mode:
        return """
        <style>
            /* ========================================
               DARK MODE THEME
               ======================================== */
            
            /* Main App Styling */
            .stApp {
                background: linear-gradient(135deg, #0A0E27 0%, #1a1f3a 100%);
                color: #F1F5F9;
            }
            
            /* Title Styling */
            h1 {
                margin-top: -50px !important;
                padding-top: 10px !important;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
                font-weight: 700 !important;
                background: linear-gradient(135deg, #10B981 0%, #3B82F6 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            h2, h3 {
                font-family: 'Inter', sans-serif !important;
                font-weight: 600 !important;
                color: #F1F5F9 !important;
            }
            
            /* Metrics Styling */
            .stMetric {
                background: rgba(30, 41, 59, 0.5);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                padding: 16px !important;
                border: 1px solid rgba(148, 163, 184, 0.1);
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
            }
            
            .stMetric label {
                font-size: 1.5rem !important;
                font-weight: 600 !important;
                color: #94A3B8 !important;
            }
            
            .stMetric [data-testid="stMetricValue"] {
                font-size: 3.5rem !important;
                font-weight: 700 !important;
                font-variant-numeric: tabular-nums;
                color: #F1F5F9 !important;
            }
            
            .stMetric [data-testid="stMetricDelta"] {
                font-size: 1.2rem !important;
                font-weight: 600 !important;
            }
            
            /* Sidebar Styling */
            [data-testid="stSidebar"] {
                background: rgba(15, 23, 42, 0.95);
                backdrop-filter: blur(10px);
                border-right: 1px solid rgba(148, 163, 184, 0.1);
            }
            
            [data-testid="stSidebar"] h2 {
                color: #F1F5F9 !important;
            }
            
            /* DataFrame Styling */
            div[data-testid="stDataFrame"] {
                background: rgba(30, 41, 59, 0.5);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                padding: 16px;
                border: 1px solid rgba(148, 163, 184, 0.1);
            }
            
            div[data-testid="stDataFrame"] thead tr th {
                background-color: rgba(51, 65, 85, 0.8) !important;
                color: #F1F5F9 !important;
                font-weight: 600 !important;
                border-bottom: 2px solid #10B981 !important;
            }
            
            div[data-testid="stDataFrame"] tbody tr td {
                color: #E2E8F0 !important;
                border-bottom: 1px solid rgba(148, 163, 184, 0.1) !important;
            }
            
            div[data-testid="stDataFrame"] tbody tr:hover {
                background-color: rgba(51, 65, 85, 0.3) !important;
            }
            
            /* Button Styling */
            .stButton button {
                background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.5rem 1.5rem;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.3);
            }
            
            .stButton button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 12px -2px rgba(16, 185, 129, 0.4);
            }
            
            /* Plotly Chart Container - flach, ohne Kasten */
            .js-plotly-plot {
                background: transparent !important;
                padding: 0;
                border: none;
            }
            
            /* Markdown & Text */
            .stMarkdown {
                color: #E2E8F0;
            }
            
            /* Divider */
            hr {
                border-color: rgba(148, 163, 184, 0.2) !important;
                margin: 2rem 0 !important;
            }
        </style>
        """
    
    else:
        return """
        <style>
            /* ========================================
               LIGHT MODE THEME
               ======================================== */
            
            /* Main App Styling */
            .stApp {
                background: linear-gradient(135deg, #F8FAFC 0%, #E0E7FF 100%);
                color: #1E293B;
            }
            
            /* Title Styling */
            h1 {
                margin-top: -50px !important;
                padding-top: 10px !important;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
                font-weight: 700 !important;
                color: #1E293B !important;
                background: linear-gradient(135deg, #059669 0%, #2563EB 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            h2, h3 {
                font-family: 'Inter', sans-serif !important;
                font-weight: 600 !important;
                color: #1E293B !important;
            }
            
            /* Metrics Styling */
            .stMetric {
                background: rgba(255, 255, 255, 0.9);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                padding: 16px !important;
                border: 1px solid rgba(148, 163, 184, 0.2);
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }
            
            .stMetric label {
                font-size: 1.5rem !important;
                font-weight: 600 !important;
                color: #64748B !important;
            }
            
            .stMetric [data-testid="stMetricValue"] {
                font-size: 3.5rem !important;
                font-weight: 700 !important;
                font-variant-numeric: tabular-nums;
                color: #1E293B !important;
            }
            
            .stMetric [data-testid="stMetricDelta"] {
                font-size: 1.2rem !important;
                font-weight: 600 !important;
            }
            
            /* Sidebar Styling */
            [data-testid="stSidebar"] {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-right: 1px solid rgba(148, 163, 184, 0.2);
            }
            
            [data-testid="stSidebar"] h2 {
                color: #1E293B !important;
            }
            
            /* DataFrame Styling */
            div[data-testid="stDataFrame"] {
                background: rgba(255, 255, 255, 0.9);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                padding: 16px;
                border: 1px solid rgba(148, 163, 184, 0.2);
            }
            
            div[data-testid="stDataFrame"] thead tr th {
                background-color: #F1F5F9 !important;
                color: #1E293B !important;
                font-weight: 600 !important;
                border-bottom: 2px solid #059669 !important;
            }
            
            div[data-testid="stDataFrame"] tbody tr td {
                color: #1E293B !important;
                border-bottom: 1px solid rgba(148, 163, 184, 0.1) !important;
            }
            
            div[data-testid="stDataFrame"] tbody tr:hover {
                background-color: rgba(241, 245, 249, 0.5) !important;
            }
            
            /* Button Styling */
            .stButton button {
                background: linear-gradient(135deg, #059669 0%, #047857 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.5rem 1.5rem;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 4px 6px -1px rgba(5, 150, 105, 0.3);
            }
            
            .stButton button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 12px -2px rgba(5, 150, 105, 0.4);
            }
            
            /* Plotly Chart Container - flach, ohne Kasten */
            .js-plotly-plot {
                background: transparent !important;
                padding: 0;
                border: none;
            }
            
            /* Plotly Charts - Text & Hover */
            .js-plotly-plot .plotly text {
                fill: #1E293B !important;
            }
            
            .js-plotly-plot .plotly .legend text {
                fill: #1E293B !important;
            }
            
            g.hovertext path {
                fill: white !important;
                stroke: #1E293B !important;
            }
            
            g.hovertext text {
                fill: #1E293B !important;
            }
            
            /* Markdown & Text */
            .stMarkdown {
                color: #1E293B;
            }
            
            p, span, div, label {
                color: #1E293B;
            }
            
            /* Divider */
            hr {
                border-color: rgba(148, 163, 184, 0.3) !important;
                margin: 2rem 0 !important;
            }
        </style>
        """     
           
def show_demo_banner(compact: bool = False) -> None:
    """
    Zeigt den Demo-Modus-Banner an.

    Diese Funktion wird in allen Seiten des Dashboards wiederverwendet,
    um ein einheitliches Erscheinungsbild sicherzustellen.

    Args:
        compact: Wenn True, kleinere Version für Unterseiten.
                 Wenn False (Standard), großer Banner für die Hauptseite.
    """
    if compact:
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.12), rgba(147, 51, 234, 0.12));
                border-left: 4px solid #3B82F6;
                padding: 12px 18px;
                margin: 8px 0 16px 0;
                border-radius: 8px;
            ">
                <div style="font-size: 1rem; opacity: 0.95;">
                    🎭 <strong>Demo-Modus aktiv</strong> – Beispieldaten statt echter Portfolio-Daten.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(147, 51, 234, 0.15));
                border-left: 6px solid #3B82F6;
                padding: 20px 24px;
                margin: 16px 0 24px 0;
                border-radius: 12px;
            ">
                <div style="font-size: 1.6rem; font-weight: 700; margin-bottom: 8px;">
                    🎭 Demo-Modus aktiv
                </div>
                <div style="font-size: 1.05rem; line-height: 1.5; opacity: 0.9;">
                    Dieses Dashboard läuft mit <strong>fiktiven Beispieldaten</strong>. 
                    Die produktive Version nutzt lokal eine private Portfolio-Datei, 
                    die bewusst nicht Teil des Repositories ist – aus Gründen der Datensicherheit 
                    und zum Schutz persönlicher Finanzdaten.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )   
