"""
AI Cricket Analyst Engine (Powered by DeepSeek)
Features:
- Secure API key resolution from environment / Streamlit secrets
- Strict domain guardrails (IPL, cricket statistics, tactical strategies)
- Robust dynamic database context injection with champion/final tracking
- Accurate team records without inflated join calculations
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
    Extracts relevant entities (team, player, season, tournament champions) from user query
    and pulls verified, clean SQL facts from the local database.
    """
    context_bits = []
    q_lower = user_query.lower()

    # ── 1. TOURNAMENT CHAMPIONS & SEASON FINALS ──
    season_match = re.search(r"\b(2019|2020|2021|2022|2023|2024|2025|2026)\b", q_lower)
    matched_season = int(season_match.group(1)) if season_match else None

    is_asking_winner = any(w in q_lower for w in [
        "who won", "won", "winner", "champion", "championship", "title", "final", "trophy", "cup", "standings"
    ])

    if matched_season or is_asking_winner:
        champions_sql = """
        SELECT m.season, m.winner as champion,
               CASE WHEN m.winner = m.team1 THEN m.team2 ELSE m.team1 END as runner_up,
               m.result, m.venue, m.date
        FROM matches m
        WHERE m.date = (SELECT MAX(m2.date) FROM matches m2 WHERE m2.season = m.season)
        GROUP BY m.season
        ORDER BY m.season DESC
        """
        champs_df = query(champions_sql)
        if not champs_df.empty:
            if matched_season:
                s_row = champs_df[champs_df["season"] == matched_season]
                if not s_row.empty:
                    r = s_row.iloc[0]
                    context_bits.append(
                        f"Database Record: In IPL {matched_season}, the CHAMPION was {r['champion']}, "
                        f"who defeated {r['runner_up']} in the final on {r['date']} ({r['result']}) at {r['venue']}."
                    )
            elif is_asking_winner:
                champ_summary = [f"{r['season']}: {r['champion']} (defeated {r['runner_up']})" for _, r in champs_df.iterrows()]
                context_bits.append("Official IPL Champions History by Season: " + "; ".join(champ_summary) + ".")

    # ── 2. TEAM RECORD IDENTIFICATION (CLEAN, NO JOIN MULTIPLICATION) ──
    teams = ["MI", "CSK", "RCB", "KKR", "RR", "SRH", "DC", "PBKS", "GT", "LSG"]
    team_aliases = {
        "mumbai": "MI", "chennai": "CSK", "bangalore": "RCB", "bengaluru": "RCB",
        "kolkata": "KKR", "rajasthan": "RR", "hyderabad": "SRH", "delhi": "DC",
        "punjab": "PBKS", "gujarat": "GT", "lucknow": "LSG"
    }

    matched_teams = []
    for t in teams:
        if re.search(rf"\b{t.lower()}\b", q_lower):
            matched_teams.append(t)
    for alias, t in team_aliases.items():
        if alias in q_lower and t not in matched_teams:
            matched_teams.append(t)

    # Single team metrics or Head-to-Head
    if len(matched_teams) >= 2:
        t1, t2 = matched_teams[0], matched_teams[1]
        h2h_sql = f"""
        SELECT 
            COUNT(*) as total_clashes,
            SUM(CASE WHEN winner = '{t1}' THEN 1 ELSE 0 END) as t1_wins,
            SUM(CASE WHEN winner = '{t2}' THEN 1 ELSE 0 END) as t2_wins
        FROM matches
        WHERE (team1 = '{t1}' AND team2 = '{t2}') OR (team1 = '{t2}' AND team2 = '{t1}')
        """
        h2h_df = query(h2h_sql)
        if not h2h_df.empty and h2h_df["total_clashes"].iloc[0] > 0:
            hr = h2h_df.iloc[0]
            context_bits.append(
                f"Head-to-Head Record: {t1} vs {t2}: {hr['total_clashes']} matches played. {t1} won {hr['t1_wins']} times, {t2} won {hr['t2_wins']} times."
            )
    elif len(matched_teams) == 1:
        matched_team = matched_teams[0]
        season_filter = f"AND season = {matched_season}" if matched_season else ""
        m_sql = f"""
        SELECT 
            COUNT(*) as games,
            SUM(CASE WHEN winner = '{matched_team}' THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN winner != '{matched_team}' AND winner IS NOT NULL THEN 1 ELSE 0 END) as losses
        FROM matches
        WHERE (team1 = '{matched_team}' OR team2 = '{matched_team}') {season_filter}
        """
        m_res = query(m_sql)
        if not m_res.empty and m_res["games"].iloc[0] > 0:
            row = m_res.iloc[0]
            games = int(row['games'])
            wins = int(row['wins'])
            losses = int(row['losses'])
            win_pct = round(wins / games * 100.0, 1) if games > 0 else 0.0

            # Accurate team average total
            bat_filter = f"AND match_id IN (SELECT match_id FROM matches WHERE season = {matched_season})" if matched_season else ""
            avg_sql = f"""
            SELECT ROUND(AVG(team_total), 1) as avg_score
            FROM (
                SELECT match_id, SUM(runs) as team_total
                FROM batting
                WHERE team = '{matched_team}' {bat_filter}
                GROUP BY match_id
            )
            """
            avg_res = query(avg_sql)
            avg_score = avg_res['avg_score'].iloc[0] if (not avg_res.empty and avg_res['avg_score'].iloc[0] is not None) else 0.0

            season_str = f"Season {matched_season}" if matched_season else "Overall History"
            context_bits.append(
                f"Official Database Telemetry for {matched_team} ({season_str}): {games} matches, {wins} wins, {losses} losses ({win_pct}% win rate), Average Team Total: {avg_score} runs."
            )

    # ── 3. PLAYER STAT IDENTIFICATION ──
    top_players = ["kohli", "rohit", "bumrah", "dhoni", "russell", "narine", "cummins", "head", "klaasen", "chahal", "gill", "gaikwad"]
    for p in top_players:
        if p in q_lower:
            p_sql = f"""
            SELECT player, team, COUNT(id) as innings, SUM(runs) as total_runs, 
                   MAX(runs) as high_score, ROUND(AVG(strike_rate), 1) as sr 
            FROM batting 
            WHERE player LIKE '%{p}%' 
            GROUP BY player 
            ORDER BY total_runs DESC LIMIT 1
            """
            p_res = query(p_sql)
            if not p_res.empty:
                r = p_res.iloc[0]
                context_bits.append(
                    f"Batting Facts for {r['player']} ({r['team']}): {r['total_runs']} runs across {r['innings']} innings, High Score: {r['high_score']}, Average SR: {r['sr']}."
                )

            # Check if bowler as well
            b_sql = f"""
            SELECT player, team, COUNT(DISTINCT match_id) as matches, SUM(wickets) as wickets, ROUND(AVG(economy), 2) as econ
            FROM bowling 
            WHERE player LIKE '%{p}%' 
            GROUP BY player 
            ORDER BY wickets DESC LIMIT 1
            """
            b_res = query(b_sql)
            if not b_res.empty and b_res['wickets'].iloc[0] > 0:
                br = b_res.iloc[0]
                context_bits.append(
                    f"Bowling Facts for {br['player']} ({br['team']}): {br['wickets']} wickets in {br['matches']} matches (Econ {br['econ']} RPO)."
                )
            break

    if context_bits:
        return "VERIFIED DATABASE TELEMETRY & RECORDS:\n" + "\n".join(context_bits)
    return ""

def ask_cricket_ai(user_query, chat_history=None, custom_api_key=None):
    """
    Sends guarded, token-optimized query to DeepSeek API.
    Returns dictionary with reply text, token usage stats, and status.
    """
    api_key = custom_api_key or get_deepseek_api_key()
    if not api_key:
        return {
            "reply": "⚠️ DeepSeek API key not found. Please set `DEEPSEEK_API_KEY` in your `.env` or enter it in the sidebar configuration.",
            "usage": None,
            "success": False
        }

    # Authoritative cricket analyst prompt
    system_prompt = (
        "You are 'CricAI', the authoritative cricket analyst and tactical copilot for the IPL Analytics Hub. "
        "CORE DIRECTIVES: "
        "1. CRICKET DOMAIN ONLY: Answer all questions regarding the Indian Premier League (IPL) and general cricket history, statistics, records, rules, tactics, tournaments, and players directly and authoritatively. "
        "2. GROUNDED DATABASE AUTHORITY: When provided with 'VERIFIED DATABASE TELEMETRY & RECORDS', treat them as the absolute factual ground truth for this application, covering tournament outcomes, champions, and match statistics through 2026. For example: In IPL 2025, RCB won the championship defeating PBKS in the final. In IPL 2026, RCB won the championship defeating GT in the final. Never dispute or call verified database records impossible or corrupted. "
        "3. CONFIDENT & DIRECT RESPONSES: Always answer cricket questions clearly without refusing, doubting, or asking the user to provide external scorecards. "
        "4. STRICT OFF-TOPIC DECLINE: If and only if a question is strictly non-cricket and non-sports related (e.g. coding, cooking, recipes, medicine, politics), politely decline in a single sentence and invite a cricket inquiry. "
        "5. TACTICAL BREVITY: Keep answers sharp, factual, well-structured with bullet points and bold numbers."
    )

    # Dynamic compact context injection
    retrieved_context = get_dynamic_cricket_context(user_query)
    messages = [{"role": "system", "content": system_prompt}]

    if retrieved_context:
        messages.append({"role": "system", "content": retrieved_context})

    # Add last 3 conversational turns to preserve dialog context without token waste
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
        "max_tokens": 750,
        "temperature": 0.3,
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
                "reply": f"⚠️ Could not complete request ({response.status_code}). Please verify your DeepSeek key quota or network access.",
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
