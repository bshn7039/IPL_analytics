"""
AI Cricket Analyst Engine (Powered by DeepSeek)
Features:
- Secure API key resolution from environment / Streamlit secrets
- Strict domain guardrails (IPL, cricket statistics, tactical strategies)
- Ultra-optimized token usage via smart dynamic database context injection
- Compact conversational memory management
"""
import os
import re
import json
import logging
import requests
from dotenv import load_dotenv
from database.db import query

load_dotenv(override=True)
logger = logging.getLogger(__name__)

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-chat"

def get_deepseek_api_key():
    """Resolves API key securely without exposing it in source control."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "DEEPSEEK_API_KEY" in st.secrets:
            return st.secrets["DEEPSEEK_API_KEY"]
    except Exception:
        pass
    return os.getenv("DEEPSEEK_API_KEY", "")

def get_dynamic_cricket_context(user_query):
    """
    Extracts relevant entities (team, player, season) from user query
    and pulls a hyper-compact 2-3 line SQL snippet to optimize token usage.
    """
    context_bits = []
    q_lower = user_query.lower()

    # Detect teams
    teams = ["MI", "CSK", "RCB", "KKR", "RR", "SRH", "DC", "PBKS", "GT", "LSG"]
    team_aliases = {
        "mumbai": "MI", "chennai": "CSK", "bangalore": "RCB", "bengaluru": "RCB",
        "kolkata": "KKR", "rajasthan": "RR", "hyderabad": "SRH", "delhi": "DC",
        "punjab": "PBKS", "gujarat": "GT", "lucknow": "LSG"
    }

    matched_team = None
    for t in teams:
        if re.search(rf"\b{t.lower()}\b", q_lower):
            matched_team = t
            break
    if not matched_team:
        for alias, t in team_aliases.items():
            if alias in q_lower:
                matched_team = t
                break

    # Detect season
    season_match = re.search(r"\b(2019|2020|2021|2022|2023|2024|2025|2026)\b", q_lower)
    matched_season = int(season_match.group(1)) if season_match else None

    # Fetch targeted snippet if team or season found
    if matched_team:
        season_filter = f"AND m.season = {matched_season}" if matched_season else ""
        sql = f"""
        SELECT 
            COUNT(DISTINCT m.match_id) as games,
            SUM(CASE WHEN m.winner = '{matched_team}' THEN 1 ELSE 0 END) as wins,
            ROUND(AVG(b.runs), 1) as avg_score
        FROM matches m
        LEFT JOIN batting b ON m.match_id = b.match_id AND b.team = '{matched_team}'
        WHERE (m.team1 = '{matched_team}' OR m.team2 = '{matched_team}') {season_filter}
        """
        res = query(sql)
        if not res.empty and res["games"].iloc[0] > 0:
            row = res.iloc[0]
            context_bits.append(f"Database Record for {matched_team} (Season {matched_season or 'All'}): {row['games']} matches, {row['wins']} wins, avg score {row['avg_score']}.")

    # Check top players if mentioned
    top_players = ["kohli", "rohit", "bumrah", "dhoni", "russell", "narine", "cummins", "head", "klaasen"]
    for p in top_players:
        if p in q_lower:
            p_sql = f"""
            SELECT player, team, SUM(runs) as total_runs, MAX(runs) as high_score 
            FROM batting 
            WHERE player LIKE '%{p}%' 
            GROUP BY player LIMIT 1
            """
            p_res = query(p_sql)
            if not p_res.empty:
                r = p_res.iloc[0]
                context_bits.append(f"Player Stat for {r['player']} ({r['team']}): {r['total_runs']} career runs, highest score {r['high_score']}.")
            break

    if context_bits:
        return "Relevant Database Facts:\n" + "\n".join(context_bits)
    return ""

def ask_cricket_ai(user_query, chat_history=None, custom_api_key=None):
    """
    Sends guarded, token-optimized query to DeepSeek API.
    Returns dictionary with reply text, token usage stats, and status.
    """
    api_key = custom_api_key or get_deepseek_api_key()
    if not api_key:
        return {
            "reply": "⚠️ DeepSeek API key not found. Please set `DEEPSEEK_API_KEY` in your `.env` or Streamlit secrets.",
            "usage": None,
            "success": False
        }

    # Strict token-optimized system prompt
    system_prompt = (
        "You are 'CricAI', an elite sports performance and statistics analyst for the IPL Analytics Hub. "
        "Strict Domain Rules: "
        "1. ONLY answer questions directly concerning the Indian Premier League (IPL), cricket statistics, players, teams, matches, venues, rules, and strategy. "
        "2. If a user asks about any non-cricket subject (e.g. cooking, coding, history, general knowledge), politely decline in one sentence and redirect them to IPL analytics. "
        "3. Keep answers concise, highly factual, analytically sharp, and formatted with bullet points or bold numbers. "
        "4. Always cite specific figures when available."
    )

    # Dynamic compact context injection
    retrieved_context = get_dynamic_cricket_context(user_query)
    messages = [{"role": "system", "content": system_prompt}]

    if retrieved_context:
        messages.append({"role": "system", "content": retrieved_context})

    # Add last 3 conversational turns to save tokens
    if chat_history:
        for msg in chat_history[-3:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": user_query})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "max_tokens": 600,
        "temperature": 0.4,
        "stream": False
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            data = response.json()
            reply_text = data["choices"][0]["message"]["content"].strip()
            usage = data.get("usage", {})
            return {
                "reply": reply_text,
                "usage": usage,
                "success": True
            }
        else:
            err_msg = f"API Error ({response.status_code}): {response.text}"
            logger.error(err_msg)
            return {
                "reply": f"⚠️ Could not complete request ({response.status_code}). Please verify your DeepSeek key quota.",
                "usage": None,
                "success": False
            }
    except Exception as e:
        logger.error(f"DeepSeek Request Exception: {e}")
        return {
            "reply": f"⚠️ Connection error: {str(e)}",
            "usage": None,
            "success": False
        }
