"""
UI Styling & Animation Injector — Apex Sports Broadcast Theme
Inspired by Stitch generated telemetry & command deck specifications:
- Midnight slate canvas (#090D16 & #0F172A)
- Glassmorphic telemetry panels with subtle 1px border glows
- Precision typography (Plus Jakarta Sans & Space Mono / tabular numbers)
- Glow badges, radar borders, responsive card layout
- Clean sidebar navigation styling with glowing active indicators
"""
import streamlit as st

def apply_custom_styles():
    """Injects high-end sports analytics dark theme CSS into any Streamlit page."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=Space+Mono:wght@400;700&display=swap');

        /* Global Canvas Styling */
        html, body, [class*="css"], .stApp {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: #090D16 !important;
            color: #DAE2FD !important;
        }

        /* Hide Deploy and Dev clutter */
        .stDeployButton, 
        [data-testid="stDeployButton"],
        button[title="Deploy this app"],
        #MainMenu,
        footer {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
        }

        /* ── SIDEBAR NAVIGATION ── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0B1326 0%, #060E20 100%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        }

        [data-testid="stSidebarNav"] {
            padding-top: 1.4rem !important;
        }
        [data-testid="stSidebarNav"] ul {
            gap: 0.6rem !important;
        }
        [data-testid="stSidebarNav"] li a {
            font-size: 1.05rem !important;
            font-weight: 700 !important;
            padding: 0.75rem 1.1rem !important;
            border-radius: 12px !important;
            color: #94A3B8 !important;
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
            display: flex !important;
            align-items: center !important;
        }
        [data-testid="stSidebarNav"] li a:hover {
            background: linear-gradient(90deg, rgba(6, 182, 212, 0.15), rgba(79, 70, 229, 0.15)) !important;
            border-color: rgba(6, 182, 212, 0.4) !important;
            color: #4CD7F6 !important;
            transform: translateX(4px) !important;
            box-shadow: 0 4px 18px rgba(6, 182, 212, 0.15) !important;
        }
        [data-testid="stSidebarNav"] li a span {
            font-size: 1.05rem !important;
            font-weight: 700 !important;
        }

        /* Rename main entry tab to '🏠 HomeScreen' */
        [data-testid="stSidebarNav"] li:first-child a span {
            display: none !important;
        }
        [data-testid="stSidebarNav"] li:first-child a::after {
            content: "🏠 HomeScreen" !important;
            font-size: 1.05rem !important;
            font-weight: 800 !important;
            color: #4CD7F6 !important;
            letter-spacing: 0.01em !important;
        }

        /* ── ANIMATIONS ── */
        @keyframes fadeInScale {
            0% { opacity: 0; transform: translateY(12px) scale(0.99); }
            100% { opacity: 1; transform: translateY(0) scale(1); }
        }
        @keyframes pulseGlow {
            0%, 100% { box-shadow: 0 0 16px rgba(6, 182, 212, 0.25); }
            50% { box-shadow: 0 0 28px rgba(6, 182, 212, 0.55); }
        }
        @keyframes borderShimmer {
            0% { border-color: rgba(6, 182, 212, 0.3); }
            50% { border-color: rgba(245, 158, 11, 0.5); }
            100% { border-color: rgba(6, 182, 212, 0.3); }
        }

        /* ── HERO BANNER: STITCH APEX STYLE ── */
        .hero-banner {
            padding: 1.8rem 2.2rem;
            border-radius: 18px;
            margin-bottom: 1.6rem;
            background: linear-gradient(135deg, #0D1527 0%, #171F33 55%, #0B1222 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.12);
            animation: fadeInScale 0.5s ease-out;
            position: relative;
            overflow: hidden;
        }
        .hero-banner::after {
            content: '';
            position: absolute;
            top: 0; right: 0; width: 320px; height: 100%;
            background: radial-gradient(circle at right, rgba(6, 182, 212, 0.12) 0%, transparent 70%);
            pointer-events: none;
        }

        /* ── TELEMETRY KPI CARDS (GLASSMORPHIC) ── */
        .analytics-card {
            background: linear-gradient(160deg, #131B2E 0%, #0D1424 100%);
            border-radius: 14px;
            padding: 1.25rem 1.1rem;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.08);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            animation: fadeInScale 0.6s ease-out;
            position: relative;
            height: 100%;
        }
        .analytics-card:hover {
            transform: translateY(-4px);
            border-color: rgba(6, 182, 212, 0.4);
            box-shadow: 0 16px 32px -8px rgba(6, 182, 212, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.2);
        }
        .analytics-title {
            font-size: 0.76rem;
            color: #94A3B8;
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.06em;
            margin-bottom: 0.35rem;
            font-family: 'Space Mono', monospace;
        }
        .analytics-val {
            font-size: 1.95rem;
            font-weight: 800;
            color: #FFFFFF;
            line-height: 1.15;
            letter-spacing: -0.02em;
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-variant-numeric: tabular-nums;
        }
        .analytics-sub {
            font-size: 0.8rem;
            color: #64748B;
            margin-top: 0.45rem;
            font-weight: 500;
        }

        /* ── FORM PILLS (W/L) ── */
        .badge-w, .badge-l {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 26px;
            height: 26px;
            border-radius: 7px;
            font-size: 0.78rem;
            font-weight: 800;
            margin-right: 5px;
            font-family: 'Space Mono', monospace;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
        }
        .badge-w {
            background: linear-gradient(135deg, #059669, #10B981);
            color: #FFFFFF;
            border: 1px solid rgba(16, 185, 129, 0.4);
        }
        .badge-l {
            background: linear-gradient(135deg, #DC2626, #EF4444);
            color: #FFFFFF;
            border: 1px solid rgba(239, 68, 68, 0.4);
        }

        /* ── INSIGHT / TELEMETRY BOX ── */
        .insight-box {
            background: linear-gradient(145deg, #0F172A, #141E33);
            border-radius: 14px;
            padding: 1.4rem 1.6rem;
            border: 1px solid rgba(16, 185, 129, 0.25);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.35);
            margin-top: 1.4rem;
            position: relative;
        }

        /* ── LIVE TELEMETRY CHIPS ── */
        .telemetry-chip {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            background: rgba(6, 182, 212, 0.12);
            color: #4CD7F6;
            border: 1px solid rgba(6, 182, 212, 0.3);
        }

        /* Selectboxes & Inputs styling */
        div[data-baseweb="select"] > div {
            background-color: #131B2E !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 10px !important;
            color: #FFFFFF !important;
        }
        div[data-baseweb="select"] > div:hover {
            border-color: #06B6D4 !important;
        }

        /* Plotly Container polish */
        .js-plotly-plot {
            border-radius: 14px !important;
            overflow: hidden !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            background: #0E1626 !important;
            padding: 6px;
        }

        /* Tables */
        table {
            background: #111827 !important;
            border-radius: 10px !important;
            overflow: hidden !important;
        }
    </style>
    """, unsafe_allow_html=True)
