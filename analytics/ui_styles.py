"""
UI Styling & Animation Injector
Provides shared CSS rules, keyframe animations, typography upgrades,
sidebar tab enhancements, and hides the Streamlit deploy button.
"""
import streamlit as st

def apply_custom_styles():
    """Injects high-end sports analytics dark theme CSS into any Streamlit page."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* 1. HIDE THE STREAMLIT DEPLOY BUTTON COMPLETELY */
        .stDeployButton, 
        [data-testid="stDeployButton"],
        button[title="Deploy this app"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
        }

        /* 2. SIDEBAR TABS: BIGGER, BOLDER, AND RENAMED FIRST TAB TO 'HomeScreen' */
        [data-testid="stSidebarNav"] {
            padding-top: 1.2rem !important;
        }
        [data-testid="stSidebarNav"] ul {
            gap: 0.65rem !important;
        }
        [data-testid="stSidebarNav"] li a {
            font-size: 1.15rem !important;
            font-weight: 700 !important;
            padding: 0.75rem 1rem !important;
            border-radius: 12px !important;
            color: #F1F5F9 !important;
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.07) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            display: flex !important;
            align-items: center !important;
        }
        [data-testid="stSidebarNav"] li a:hover {
            background: linear-gradient(90deg, rgba(59, 130, 246, 0.22), rgba(168, 85, 247, 0.22)) !important;
            border-color: rgba(59, 130, 246, 0.5) !important;
            transform: translateX(6px) scale(1.02) !important;
            box-shadow: 0 4px 18px rgba(59, 130, 246, 0.22) !important;
            color: #38BDF8 !important;
        }
        [data-testid="stSidebarNav"] li a span {
            font-size: 1.12rem !important;
            font-weight: 700 !important;
        }

        /* Rename the main entry tab from 'app' to '🏠 HomeScreen' */
        [data-testid="stSidebarNav"] li:first-child a span {
            display: none !important;
        }
        [data-testid="stSidebarNav"] li:first-child a::after {
            content: "🏠 HomeScreen" !important;
            font-size: 1.15rem !important;
            font-weight: 800 !important;
            color: #38BDF8 !important;
            letter-spacing: 0.01em !important;
        }

        /* 3. KEYFRAME ANIMATIONS */
        @keyframes fadeInScale {
            0% { opacity: 0; transform: translateY(12px) scale(0.98); }
            100% { opacity: 1; transform: translateY(0) scale(1); }
        }
        @keyframes pulseGlow {
            0%, 100% { box-shadow: 0 0 15px rgba(59, 130, 246, 0.25); }
            50% { box-shadow: 0 0 25px rgba(59, 130, 246, 0.5); }
        }
        @keyframes shimmerBorder {
            0% { border-color: rgba(59, 130, 246, 0.2); }
            50% { border-color: rgba(245, 158, 11, 0.5); }
            100% { border-color: rgba(59, 130, 246, 0.2); }
        }

        /* Hero banner card with animated glow */
        .hero-banner {
            padding: 1.6rem 2.2rem;
            border-radius: 16px;
            margin-bottom: 1.5rem;
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 60%, #0F172A 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
            animation: fadeInScale 0.6s ease-out;
        }

        /* Modern Animated Glassmorphic KPI Cards */
        .analytics-card {
            background: linear-gradient(145deg, #161F30, #0E1626);
            border-radius: 14px;
            padding: 1.2rem 1rem;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
            text-align: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            animation: fadeInScale 0.5s ease-out;
            position: relative;
            overflow: hidden;
        }
        .analytics-card:hover {
            transform: translateY(-4px) scale(1.02);
            border-color: rgba(59, 130, 246, 0.55);
            box-shadow: 0 12px 24px rgba(59, 130, 246, 0.18);
        }
        .analytics-title {
            color: #94A3B8;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin-bottom: 0.35rem;
        }
        .analytics-val {
            font-size: 1.85rem;
            font-weight: 800;
            color: #F8FAFC;
            line-height: 1.1;
        }
        .analytics-sub {
            font-size: 0.76rem;
            color: #64748B;
            margin-top: 0.35rem;
            font-weight: 500;
        }

        /* Pill Badge Animations */
        .badge-w {
            background: linear-gradient(135deg, #059669, #10B981);
            color: #FFFFFF;
            font-weight: 800;
            padding: 0.35rem 0.7rem;
            border-radius: 8px;
            margin-right: 0.35rem;
            display: inline-block;
            font-size: 0.85rem;
            box-shadow: 0 2px 8px rgba(16, 185, 129, 0.35);
        }
        .badge-l {
            background: linear-gradient(135deg, #DC2626, #EF4444);
            color: #FFFFFF;
            font-weight: 800;
            padding: 0.35rem 0.7rem;
            border-radius: 8px;
            margin-right: 0.35rem;
            display: inline-block;
            font-size: 0.85rem;
            box-shadow: 0 2px 8px rgba(239, 68, 68, 0.35);
        }

        /* Shimmer insight panel */
        .insight-box {
            background: linear-gradient(145deg, #0D1829, #111E33);
            border-radius: 14px;
            padding: 1.4rem 1.6rem;
            border-left: 5px solid #10B981;
            border: 1px solid rgba(16, 185, 129, 0.25);
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            animation: fadeInScale 0.7s ease-out;
        }
    </style>
    """, unsafe_allow_html=True)
