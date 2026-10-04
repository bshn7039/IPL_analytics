"""
🏏 UI Styling & Animation Injector — IPL Telemetry Pro Broadcast Theme
Directly implements Stitch-generated design system specifications:
- Midnight void chassis (#080D1A / #090D16) & canvas (#0B1326)
- Multi-tier frosted glassmorphic panels (#131B2E / #171F33) with crisp 1px borders
- Precision typography (Outfit for display, Inter for data tables with tabular-nums, Space Mono for telemetry)
- Neon accent tokens: Electric Cyan (#06B6D4), Trophy Amber (#F59E0B), Pitch Green (#10B981),
  Strike Crimson (#EF4444), Neon Purple (#A855F7), Indigo (#818CF8)
- F1/Premier League broadcast command deck controls, buttons, tables, and navigation
"""
import streamlit as st

def apply_custom_styles():
    """Injects world-class sports telemetry broadcast CSS into any Streamlit page."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800;900&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');

        /* ── GLOBAL CANVAS STYLING ── */
        html, body, [class*="css"], .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background-color: #080D1A !important;
            color: #DAE2FD !important;
        }

        /* Top padding tightening */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 3rem !important;
            max-width: 1440px !important;
        }

        /* Hide Deploy and Streamlit Dev clutter */
        .stDeployButton, 
        [data-testid="stDeployButton"],
        button[title="Deploy this app"],
        #MainMenu,
        footer {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
        }

        /* ── HEADINGS HIERARCHY (OUTFIT) ── */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            letter-spacing: -0.02em !important;
            color: #FFFFFF !important;
        }

        /* ── SIDEBAR NAVIGATION ── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #060E20 0%, #0B1326 100%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
            box-shadow: 4px 0 24px rgba(0, 0, 0, 0.5) !important;
        }

        [data-testid="stSidebarNav"] {
            padding-top: 1.2rem !important;
        }
        [data-testid="stSidebarNav"] ul {
            gap: 0.5rem !important;
        }
        [data-testid="stSidebarNav"] li a {
            font-family: 'Outfit', sans-serif !important;
            font-size: 0.98rem !important;
            font-weight: 700 !important;
            padding: 0.7rem 1rem !important;
            border-radius: 10px !important;
            color: #94A3B8 !important;
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.04) !important;
            transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
            display: flex !important;
            align-items: center !important;
        }
        [data-testid="stSidebarNav"] li a:hover {
            background: linear-gradient(90deg, rgba(6, 182, 212, 0.15), rgba(79, 70, 229, 0.12)) !important;
            border-color: rgba(6, 182, 212, 0.4) !important;
            color: #4CD7F6 !important;
            transform: translateX(3px) !important;
            box-shadow: 0 4px 16px rgba(6, 182, 212, 0.18) !important;
        }

        /* Active navigation item styling */
        [data-testid="stSidebarNav"] li a[aria-current="page"] {
            background: linear-gradient(90deg, rgba(6, 182, 212, 0.22), rgba(19, 27, 46, 0.8)) !important;
            border: 1px solid rgba(6, 182, 212, 0.55) !important;
            color: #4CD7F6 !important;
            box-shadow: 0 0 20px rgba(6, 182, 212, 0.25) !important;
        }

        /* Rename main entry tab to '🏠 Overview Command Deck' */
        [data-testid="stSidebarNav"] li:first-child a span {
            display: none !important;
        }
        [data-testid="stSidebarNav"] li:first-child a::after {
            content: "🏠 Overview Command Deck" !important;
            font-size: 0.98rem !important;
            font-weight: 800 !important;
            color: #4CD7F6 !important;
        }

        /* ── ANIMATIONS ── */
        @keyframes fadeInScale {
            0% { opacity: 0; transform: translateY(8px) scale(0.995); }
            100% { opacity: 1; transform: translateY(0) scale(1); }
        }
        @keyframes pulseAmber {
            0%, 100% { box-shadow: 0 0 10px rgba(245, 158, 11, 0.3); }
            50% { box-shadow: 0 0 22px rgba(245, 158, 11, 0.6); }
        }

        /* ── PAGE HEADERS ── */
        .page-header {
            background: linear-gradient(135deg, #090F1E 0%, #131B2E 55%, #0B1220 100%);
            border-radius: 16px;
            padding: 1.6rem 2rem;
            border: 1px solid rgba(255, 255, 255, 0.09);
            box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1);
            margin-bottom: 1.5rem;
            position: relative;
            overflow: hidden;
            animation: fadeInScale 0.4s ease-out;
        }
        .page-header::after {
            content: '';
            position: absolute;
            top: 0; right: 0; width: 340px; height: 100%;
            background: radial-gradient(circle at right, rgba(6, 182, 212, 0.12) 0%, transparent 65%);
            pointer-events: none;
        }
        .section-label {
            font-size: 0.72rem;
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #4CD7F6;
            margin-bottom: 0.45rem;
        }

        /* ── GLASSMORPHIC TELEMETRY CARDS ── */
        .analytics-card, .kpi-card, .franchise-card {
            background: linear-gradient(160deg, #131B2E 0%, #0D1424 100%);
            border-radius: 14px;
            padding: 1.25rem 1.15rem;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.08);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            height: 100%;
        }
        .analytics-card:hover, .kpi-card:hover, .franchise-card:hover {
            transform: translateY(-3px);
            border-color: rgba(6, 182, 212, 0.4);
            box-shadow: 0 16px 32px -8px rgba(6, 182, 212, 0.22), inset 0 1px 0 rgba(255, 255, 255, 0.18);
        }
        .analytics-title, .kpi-label {
            font-size: 0.74rem;
            color: #94A3B8;
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.06em;
            margin-bottom: 0.35rem;
            font-family: 'Space Mono', monospace;
        }
        .analytics-val, .kpi-value {
            font-size: 1.95rem;
            font-weight: 800;
            color: #FFFFFF;
            line-height: 1.15;
            letter-spacing: -0.02em;
            font-family: 'Outfit', sans-serif;
            font-variant-numeric: tabular-nums;
        }
        .analytics-sub, .kpi-sub {
            font-size: 0.78rem;
            color: #64748B;
            margin-top: 0.4rem;
            font-weight: 500;
        }

        /* ── HERO BANNER ── */
        .hero-banner {
            padding: 1.8rem 2.2rem;
            border-radius: 18px;
            margin-bottom: 1.6rem;
            background: linear-gradient(135deg, #0D1527 0%, #171F33 55%, #0B1222 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.12);
            animation: fadeInScale 0.4s ease-out;
            position: relative;
            overflow: hidden;
        }
        .hero-banner::after {
            content: '';
            position: absolute;
            top: 0; right: 0; width: 340px; height: 100%;
            background: radial-gradient(circle at right, rgba(6, 182, 212, 0.14) 0%, transparent 68%);
            pointer-events: none;
        }

        /* ── CHART WRAPPERS ── */
        .chart-wrapper {
            background: linear-gradient(160deg, #0E1626 0%, #0A1020 100%);
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
            padding: 1.1rem 1.25rem 0.6rem;
            margin-bottom: 1.1rem;
        }
        .chart-title {
            font-size: 0.78rem;
            font-family: 'Space Mono', monospace;
            color: #CBD5E1;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 700;
            margin-bottom: 0.65rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            padding-bottom: 0.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        /* ── SPLIT CARDS & VERDICT BOXES ── */
        .split-card, .verdict-card, .insight-box, .simulator-card, .player-profile-card {
            background: linear-gradient(160deg, #131B2E 0%, #0D1424 100%);
            border-radius: 14px;
            padding: 1.35rem 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
            margin-bottom: 1rem;
        }

        /* ── GLOW CLASSES ── */
        .glow-cyan {
            box-shadow: 0 0 20px -3px rgba(6, 182, 212, 0.4) !important;
        }
        .glow-amber {
            box-shadow: 0 0 20px -3px rgba(245, 158, 11, 0.4) !important;
        }
        .glow-crimson {
            box-shadow: 0 0 20px -3px rgba(239, 68, 68, 0.4) !important;
        }
        .glow-emerald {
            box-shadow: 0 0 20px -3px rgba(16, 185, 129, 0.4) !important;
        }
        .glow-purple {
            box-shadow: 0 0 20px -3px rgba(168, 85, 247, 0.4) !important;
        }

        /* ── TELEMETRY PILLS & CHIPS ── */
        .telemetry-chip {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.74rem;
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            background: rgba(6, 182, 212, 0.12);
            color: #4CD7F6;
            border: 1px solid rgba(6, 182, 212, 0.3);
        }
        .telemetry-chip-amber {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.74rem;
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            background: rgba(245, 158, 11, 0.12);
            color: #F59E0B;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        .telemetry-chip-green {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.74rem;
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            background: rgba(16, 185, 129, 0.12);
            color: #10B981;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        .telemetry-chip-red {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.74rem;
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            background: rgba(239, 68, 68, 0.12);
            color: #F87171;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }
        .telemetry-chip-purple {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.74rem;
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            background: rgba(168, 85, 247, 0.12);
            color: #C084FC;
            border: 1px solid rgba(168, 85, 247, 0.3);
        }

        /* Form pills (W/L) */
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

        /* ── SECTION DIVIDERS ── */
        .section-divider {
            border: none;
            border-top: 1px solid rgba(255, 255, 255, 0.07);
            margin: 1.5rem 0;
        }

        /* ── INPUTS, SELECTBOXES, RADIOS ── */
        div[data-baseweb="select"] > div {
            background-color: #131B2E !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 10px !important;
            color: #FFFFFF !important;
            font-family: 'Outfit', sans-serif !important;
        }
        div[data-baseweb="select"] > div:hover {
            border-color: #06B6D4 !important;
            box-shadow: 0 0 12px rgba(6, 182, 212, 0.25) !important;
        }
        div[data-baseweb="input"] {
            background-color: #131B2E !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 10px !important;
            color: #FFFFFF !important;
        }
        div[data-baseweb="input"]:focus-within {
            border-color: #06B6D4 !important;
            box-shadow: 0 0 16px rgba(6, 182, 212, 0.3) !important;
        }

        /* Radio Buttons */
        div[role="radiogroup"] {
            gap: 0.8rem !important;
            background: rgba(19, 27, 46, 0.6) !important;
            padding: 6px 12px !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            width: fit-content !important;
        }

        /* Buttons */
        .stButton > button {
            background: linear-gradient(180deg, #06B6D4 0%, #0891B2 100%) !important;
            color: #080D1A !important;
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            font-size: 0.92rem !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.55rem 1.4rem !important;
            transition: all 0.22s ease !important;
            box-shadow: 0 4px 14px rgba(6, 182, 212, 0.3) !important;
        }
        .stButton > button:hover {
            background: linear-gradient(180deg, #22D3EE 0%, #06B6D4 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(6, 182, 212, 0.5) !important;
            color: #080D1A !important;
        }

        /* Plotly Containers Polish */
        .js-plotly-plot {
            border-radius: 12px !important;
            overflow: hidden !important;
            background: transparent !important;
        }

        /* Dataframe / Tables */
        [data-testid="stDataFrame"], table {
            border-radius: 12px !important;
            overflow: hidden !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            font-variant-numeric: tabular-nums !important;
        }
    </style>
    """, unsafe_allow_html=True)
