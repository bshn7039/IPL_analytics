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
import os
import streamlit as st

def apply_custom_styles():
    """Injects world-class sports telemetry broadcast CSS into any Streamlit page."""
    
    # ── INJECT APEX LOGO IF AVAILABLE ──
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.svg")
    if os.path.exists(logo_path):
        try:
            st.logo(logo_path, size="large")
        except Exception:
            pass

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

        /* ── SIDEBAR BROADCAST CONTAINER & SCROLLBAR ── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #060E20 0%, #080D1A 60%, #050914 100%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
            box-shadow: 4px 0 28px rgba(0, 0, 0, 0.6) !important;
        }
        [data-testid="stSidebar"] ::-webkit-scrollbar {
            width: 4px !important;
        }
        [data-testid="stSidebar"] ::-webkit-scrollbar-track {
            background: transparent !important;
        }
        [data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.12) !important;
            border-radius: 4px !important;
        }
        [data-testid="stSidebar"] ::-webkit-scrollbar-thumb:hover {
            background: rgba(6, 182, 212, 0.4) !important;
        }

        [data-testid="stSidebarContent"] {
            padding: 0.8rem 0.9rem !important;
            background: transparent !important;
        }

        /* ── SIDEBAR HEADER & LOGO ── */
        [data-testid="stSidebarHeader"] {
            padding: 0.4rem 0.2rem 0.8rem 0.2rem !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
            margin-bottom: 0.8rem !important;
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
        }
        [data-testid="stSidebarLogo"] {
            display: flex !important;
            align-items: center !important;
        }
        [data-testid="stSidebarLogo"] img {
            height: 32px !important;
            width: auto !important;
            max-width: 210px !important;
            filter: drop-shadow(0 0 10px rgba(6, 182, 212, 0.25));
        }

        /* Sidebar Collapse / Toggle Button */
        [data-testid="stSidebarCollapseButton"] button {
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 8px !important;
            color: #94A3B8 !important;
            transition: all 0.2s ease !important;
        }
        [data-testid="stSidebarCollapseButton"] button:hover {
            background: rgba(6, 182, 212, 0.15) !important;
            border-color: rgba(6, 182, 212, 0.4) !important;
            color: #4CD7F6 !important;
            box-shadow: 0 0 12px rgba(6, 182, 212, 0.25) !important;
        }

        /* ── SIDEBAR NAVIGATION MODULES ── */
        [data-testid="stSidebarNav"] {
            padding: 0.2rem 0 !important;
        }
        [data-testid="stSidebarNav"]::before {
            content: "TELEMETRY MODULES";
            display: block;
            font-family: 'Space Mono', monospace;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            color: #64748B;
            padding: 0.2rem 0.6rem 0.55rem 0.6rem;
            text-transform: uppercase;
        }
        [data-testid="stSidebarNavItems"] ul,
        [data-testid="stSidebarNav"] ul {
            list-style: none !important;
            padding: 0 !important;
            margin: 0 !important;
            display: flex !important;
            flex-direction: column !important;
            gap: 0.35rem !important;
        }

        /* Nav Links Common Styles */
        [data-testid="stSidebarNavLink"],
        [data-testid="stSidebarNav"] li a {
            display: flex !important;
            align-items: center !important;
            gap: 0.65rem !important;
            padding: 0.55rem 0.85rem !important;
            border-radius: 9px !important;
            font-family: 'Outfit', sans-serif !important;
            font-size: 0.88rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.01em !important;
            color: #94A3B8 !important;
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.04) !important;
            border-left: 3px solid transparent !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            text-decoration: none !important;
            position: relative !important;
        }

        /* Nav Links Hover State */
        [data-testid="stSidebarNavLink"]:hover,
        [data-testid="stSidebarNav"] li a:hover {
            background: rgba(255, 255, 255, 0.05) !important;
            border-color: rgba(255, 255, 255, 0.1) !important;
            border-left: 3px solid rgba(6, 182, 212, 0.6) !important;
            color: #FFFFFF !important;
            transform: translateX(3px) !important;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3) !important;
        }

        /* Active Nav Link State */
        [data-testid="stSidebarNavLink"][aria-current="page"],
        [data-testid="stSidebarNav"] li a[aria-current="page"] {
            background: linear-gradient(90deg, rgba(6, 182, 212, 0.16) 0%, rgba(13, 27, 46, 0.85) 100%) !important;
            border: 1px solid rgba(6, 182, 212, 0.35) !important;
            border-left: 4px solid #06B6D4 !important;
            color: #4CD7F6 !important;
            font-weight: 700 !important;
            box-shadow: 0 0 18px rgba(6, 182, 212, 0.2), inset 0 0 10px rgba(6, 182, 212, 0.06) !important;
        }

        /* Active Pulse Dot Indicator */
        [data-testid="stSidebarNavLink"][aria-current="page"]::after,
        [data-testid="stSidebarNav"] li a[aria-current="page"]::after {
            content: "" !important;
            display: inline-block !important;
            width: 6px !important;
            height: 6px !important;
            border-radius: 50% !important;
            background: #06B6D4 !important;
            box-shadow: 0 0 8px #06B6D4, 0 0 12px #06B6D4 !important;
            margin-left: auto !important;
            flex-shrink: 0 !important;
        }

        /* Entrypoint (app.py) title replacement */
        [data-testid="stSidebarNav"] li:first-child [data-testid="stSidebarNavLink"] span,
        [data-testid="stSidebarNav"] li:first-child a span {
            display: none !important;
        }
        [data-testid="stSidebarNav"] li:first-child [data-testid="stSidebarNavLink"]::before,
        [data-testid="stSidebarNav"] li:first-child a::before {
            content: "🏠 Overview Command Deck" !important;
            display: inline-flex !important;
            align-items: center !important;
            font-family: 'Outfit', sans-serif !important;
            font-size: 0.88rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.01em !important;
        }
        [data-testid="stSidebarNav"] li:first-child [data-testid="stSidebarNavLink"][aria-current="page"]::before,
        [data-testid="stSidebarNav"] li:first-child a[aria-current="page"]::before {
            color: #4CD7F6 !important;
            font-weight: 700 !important;
        }
        [data-testid="stSidebarNav"] li:first-child [data-testid="stSidebarNavLink"]:not([aria-current="page"])::before,
        [data-testid="stSidebarNav"] li:first-child a:not([aria-current="page"])::before {
            color: #94A3B8 !important;
        }
        [data-testid="stSidebarNav"] li:first-child [data-testid="stSidebarNavLink"]:not([aria-current="page"]):hover::before,
        [data-testid="stSidebarNav"] li:first-child a:not([aria-current="page"]):hover::before {
            color: #FFFFFF !important;
        }

        /* ── SIDEBAR WIDGETS & CARDS ── */
        .sidebar-card {
            background: linear-gradient(160deg, #0C1527 0%, #070D1A 100%) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            padding: 0.9rem !important;
            margin-top: 0.85rem !important;
            box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.5) !important;
            position: relative !important;
            overflow: hidden !important;
        }
        .sidebar-card:hover {
            border-color: rgba(6, 182, 212, 0.3) !important;
        }
        .sidebar-card-title {
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            font-family: 'Space Mono', monospace !important;
            font-size: 0.68rem !important;
            font-weight: 700 !important;
            color: #64748B !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
            margin-bottom: 0.6rem !important;
            padding-bottom: 0.4rem !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
        }
        .sidebar-stat-row {
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            font-family: 'Space Mono', monospace !important;
            font-size: 0.72rem !important;
            padding: 0.28rem 0 !important;
            color: #94A3B8 !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03) !important;
        }
        .sidebar-stat-row:last-child {
            border-bottom: none !important;
        }
        .sidebar-stat-row strong {
            color: #FFFFFF !important;
            font-variant-numeric: tabular-nums !important;
        }
        .sidebar-badge {
            display: inline-flex !important;
            align-items: center !important;
            gap: 4px !important;
            padding: 2px 7px !important;
            border-radius: 12px !important;
            font-family: 'Space Mono', monospace !important;
            font-size: 0.65rem !important;
            font-weight: 700 !important;
        }
        .sidebar-badge-green {
            background: rgba(16, 185, 129, 0.14) !important;
            color: #34D399 !important;
            border: 1px solid rgba(16, 185, 129, 0.3) !important;
        }
        .sidebar-badge-cyan {
            background: rgba(6, 182, 212, 0.14) !important;
            color: #67E8F9 !important;
            border: 1px solid rgba(6, 182, 212, 0.3) !important;
        }
        .sidebar-badge-amber {
            background: rgba(245, 158, 11, 0.14) !important;
            color: #FBBF24 !important;
            border: 1px solid rgba(245, 158, 11, 0.3) !important;
        }
        .sidebar-badge-purple {
            background: rgba(168, 85, 247, 0.14) !important;
            color: #C084FC !important;
            border: 1px solid rgba(168, 85, 247, 0.3) !important;
        }
        .sidebar-footer-strip {
            margin-top: 0.9rem !important;
            padding-top: 0.7rem !important;
            border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            font-family: 'Space Mono', monospace !important;
            font-size: 0.68rem !important;
            color: #64748B !important;
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

        /* ── LUXURY GLASS KPI METRIC TILES ── */
        .kpi-tile {
            background: linear-gradient(160deg, #131B2E 0%, #0D1424 100%);
            border-radius: 14px;
            padding: 1.25rem 1.4rem;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.05);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .kpi-tile:hover {
            transform: translateY(-3px);
            border-color: rgba(6, 182, 212, 0.4);
            box-shadow: 0 16px 32px -8px rgba(6, 182, 212, 0.2);
        }
        .kpi-tile::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 100%; height: 2px;
            background: linear-gradient(90deg, transparent, rgba(6, 182, 212, 0.8), transparent);
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        .kpi-tile:hover::before {
            opacity: 1;
        }

        .metric-label {
            font-family: 'Space Mono', monospace;
            font-size: 0.72rem;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.35rem;
            font-weight: 700;
        }
        .metric-value {
            font-family: 'Outfit', sans-serif;
            font-size: 2.2rem;
            font-weight: 800;
            color: #FFFFFF;
            letter-spacing: -0.02em;
            line-height: 1.1;
            font-variant-numeric: tabular-nums;
        }
        .metric-sub {
            font-size: 0.78rem;
            color: #94A3B8;
            margin-top: 0.45rem;
            font-weight: 500;
        }

        /* ── BROADCAST STATUS CHIPS ── */
        .telemetry-chip {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.72rem;
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            background: rgba(255, 255, 255, 0.05);
            color: #94A3B8;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .telemetry-chip-amber {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.72rem;
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            background: rgba(245, 158, 11, 0.14);
            color: #FBBF24;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        .telemetry-chip-red {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.72rem;
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            background: rgba(239, 68, 68, 0.14);
            color: #F87171;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }
        .telemetry-chip-purple {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.72rem;
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            background: rgba(168, 85, 247, 0.14);
            color: #C084FC;
            border: 1px solid rgba(168, 85, 247, 0.3);
        }
        .telemetry-chip-green {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.72rem;
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            background: rgba(16, 185, 129, 0.14);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        .telemetry-chip-cyan {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.72rem;
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            background: rgba(6, 182, 212, 0.14);
            color: #67E8F9;
            border: 1px solid rgba(6, 182, 212, 0.3);
        }
        .telemetry-chip-blue {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.72rem;
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            background: rgba(59, 130, 246, 0.14);
            color: #60A5FA;
            border: 1px solid rgba(59, 130, 246, 0.3);
        }

        /* ── PLAYER PROFILE HERO CARDS (Module 04) ── */
        .player-profile-card {
            background: linear-gradient(160deg, #131B2E 0%, #0D1424 100%);
            border-radius: 14px;
            padding: 1.3rem 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.05);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            margin-bottom: 0.8rem;
        }
        .player-profile-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 16px 32px -8px rgba(0, 0, 0, 0.6);
            border-color: rgba(255, 255, 255, 0.15);
        }
        .player-franchise-label {
            font-size: 0.75rem;
            font-family: 'Space Mono', monospace;
            color: #94A3B8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .player-profile-name {
            margin: 0.25rem 0 0.55rem !important;
            color: #FFFFFF !important;
            font-weight: 800 !important;
            font-size: 1.85rem !important;
            letter-spacing: -0.02em !important;
            line-height: 1.15 !important;
        }
        .player-chip-row {
            display: flex;
            gap: 0.4rem;
            flex-wrap: wrap;
            margin-bottom: 0.85rem;
        }
        .player-stat-box {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 10px;
            padding: 0.8rem 1.1rem;
            transition: border-color 0.2s ease;
        }
        .player-stat-box:hover {
            border-color: rgba(255, 255, 255, 0.12);
        }
        .player-stat-box-title {
            font-size: 0.7rem;
            font-family: 'Space Mono', monospace;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            font-weight: 700;
        }
        .player-stat-box-value {
            color: #FFFFFF;
            font-size: 0.98rem;
            font-weight: 700;
            margin-top: 0.25rem;
            font-variant-numeric: tabular-nums;
        }

        /* ── CHART HEADERS & CONTAINERS ── */
        .chart-wrapper {
            background: linear-gradient(160deg, #131B2E 0%, #0D1424 100%);
            border-radius: 14px;
            padding: 1.2rem 1.4rem;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
            margin-bottom: 1.2rem;
        }
        .chart-header, .chart-title {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-family: 'Outfit', sans-serif;
            font-size: 1.05rem;
            font-weight: 700;
            color: #FFFFFF;
            margin-bottom: 0.8rem;
        }

        /* ── FRANCHISE & H2H DUEL CARDS (Module 03) ── */
        .franchise-card {
            background: linear-gradient(160deg, #131B2E 0%, #0D1424 100%);
            border-radius: 14px;
            padding: 1.4rem 1.2rem;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
            margin-bottom: 1rem;
        }
        .split-card {
            background: linear-gradient(160deg, #131B2E 0%, #0D1424 100%);
            border-radius: 14px;
            padding: 1.4rem 1.2rem;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
            margin-bottom: 1rem;
        }
        .verdict-card {
            background: linear-gradient(160deg, #131B2E 0%, #0D1424 100%);
            border-radius: 14px;
            padding: 1.25rem 1.4rem;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
            margin-bottom: 1rem;
        }

        /* ── KPI & ANALYTICS CARDS (Shared Across Modules) ── */
        .kpi-card, .analytics-card {
            background: linear-gradient(160deg, #131B2E 0%, #0D1424 100%);
            border-radius: 14px;
            padding: 1.25rem 1.4rem;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
            margin-bottom: 1rem;
        }
        .kpi-label, .analytics-title {
            font-family: 'Space Mono', monospace;
            font-size: 0.72rem;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.35rem;
            font-weight: 700;
        }
        .kpi-value, .analytics-val {
            font-family: 'Outfit', sans-serif;
            font-size: 2.1rem;
            font-weight: 800;
            color: #FFFFFF;
            letter-spacing: -0.02em;
            line-height: 1.1;
            font-variant-numeric: tabular-nums;
        }
        .kpi-sub, .analytics-sub {
            font-size: 0.78rem;
            color: #94A3B8;
            margin-top: 0.45rem;
            font-weight: 500;
        }

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

def render_sidebar_system_status():
    """Renders the standard broadcast telemetry database status card in the sidebar for analytical pages."""
    try:
        from database.db import get_db_stats
        db_stats = get_db_stats()
        st.sidebar.markdown(f"""
        <div class="sidebar-card">
            <div class="sidebar-card-title">
                <span style="display:flex; align-items:center; gap:5px;">
                    <span style="width:6px; height:6px; border-radius:50%; background:#10B981; box-shadow:0 0 8px #10B981;"></span>
                    SQLITE TELEMETRY
                </span>
                <span class="sidebar-badge sidebar-badge-green">ONLINE</span>
            </div>
            <div class="sidebar-stat-row">
                <span>Total Matches:</span>
                <strong>{db_stats['matches']}</strong>
            </div>
            <div class="sidebar-stat-row">
                <span>Batting Records:</span>
                <strong>{db_stats['batting']:,}</strong>
            </div>
            <div class="sidebar-stat-row">
                <span>Bowling Spells:</span>
                <strong>{db_stats['bowling']:,}</strong>
            </div>
            <div class="sidebar-stat-row">
                <span>Players Indexed:</span>
                <strong>{db_stats['players']}</strong>
            </div>
            <div class="sidebar-footer-strip">
                <span>BROADCAST FEED v4.2</span>
                <strong style="color:#4CD7F6;">SYNCED</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        pass
