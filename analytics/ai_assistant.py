"""
AI Cricket Analyst Engine (Powered by DeepSeek)
Features:
- Live, read-only SQL query execution via function calling / tool calling
- Dynamic database context injection with champion/final and standings tracking
- Strict domain guardrails (IPL, cricket statistics, tactical strategies)
- Multi-turn tool execution loop with aggregated token telemetry
- Safe SQL execution (SELECT-only, injection-safe)
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

DATABASE_SCHEMA_DESCRIPTION = """
Tables in SQLite database (seasons 2019 to 2026):
1. matches (523 total matches across 2019-2026):
   - match_id (TEXT): Unique match identifier (e.g. 'IPL_2026_001')
   - season (INTEGER): 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026
   - date (TEXT): YYYY-MM-DD
   - team1 (TEXT), team2 (TEXT): Team codes (CSK, DC, GT, KKR, LSG, MI, PBKS, RCB, RR, SRH)
   - venue (TEXT), city (TEXT)
   - toss_winner (TEXT), toss_decision (TEXT: 'bat' or 'field')
   - winner (TEXT): Winning team short code
   - result (TEXT): Win margin description (e.g. 'RCB won by 92 runs')

2. batting (8,200+ records):
   - id (INTEGER PRIMARY KEY)
   - match_id (TEXT)
   - innings (INTEGER: 1 or 2)
   - team (TEXT), player (TEXT)
   - runs (INTEGER), balls (INTEGER), fours (INTEGER), sixes (INTEGER)
   - strike_rate (REAL), boundary_runs (INTEGER), boundary_percentage (REAL)
   - is_fifty (INTEGER: 0 or 1), is_hundred (INTEGER: 0 or 1)
   - dismissal (TEXT), not_out (INTEGER: 0 or 1)

3. bowling (6,300+ records):
   - id (INTEGER PRIMARY KEY)
   - match_id (TEXT)
   - innings (INTEGER: 1 or 2)
   - team (TEXT), player (TEXT)
   - overs (REAL), balls_bowled (INTEGER), maidens (INTEGER)
   - runs_conceded (INTEGER), wickets (INTEGER), economy (REAL)
   - bowling_avg (REAL), bowling_sr (REAL)

4. teams:
   - team_id (INTEGER), team_name (TEXT), short_name (TEXT)

5. players:
   - player_id (INTEGER), player_name (TEXT), team_short (TEXT), role (TEXT)
"""

DATABASE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "execute_sql_query",
            "description": (
                "Execute a read-only SQL SELECT query against the IPL SQLite database to retrieve "
                "verified live match records, points/wins standings, player stats, bowling figures, "
                "head-to-head records, and venue history. Only SELECT queries are permitted."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A valid SQLite SELECT statement. E.g.: SELECT winner, COUNT(*) as wins FROM matches WHERE season = 2026 AND winner IS NOT NULL GROUP BY winner ORDER BY wins DESC"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

def get_deepseek_api_key():
    """Resolves API key securely without exposing it in source control."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "DEEPSEEK_API_KEY" in st.secrets:
            return st.secrets["DEEPSEEK_API_KEY"]
    except Exception:
        pass
    return os.getenv("DEEPSEEK_API_KEY", "")

def safe_execute_sql(sql_query: str) -> str:
    """Executes a read-only SELECT query safely and returns tabular text or error message."""
    clean_sql = sql_query.strip().rstrip(";")
    if not clean_sql:
        return "Error: Empty query provided."

    first_word = clean_sql.split()[0].upper()
    if first_word not in ("SELECT", "WITH", "PRAGMA", "EXPLAIN"):
        return "Error: Only read-only SELECT or WITH statements are allowed."

    # Prevent mutations
    for forbidden in ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE", "REPLACE"]:
        if re.search(rf"\b{forbidden}\b", clean_sql, re.IGNORECASE):
            return f"Error: Mutation '{forbidden}' is forbidden. Read-only queries only."

    try:
        df = query(clean_sql)
        if df.empty:
            return "Query executed successfully. 0 rows returned."
        # Truncate if too large to prevent token explosion
        if len(df) > 35:
            df_slice = df.head(35)
            return df_slice.to_string(index=False) + f"\n... ({len(df) - 35} more rows truncated)"
        return df.to_string(index=False)
    except Exception as e:
        return f"SQL Execution Error: {str(e)}"

def get_dynamic_cricket_context(user_query):
    """
    Extracts relevant entities (team, player, season, tournament champions, database status)
    from user query and pre-fetches verified SQL facts.
    """
    context_bits = []
    q_lower = user_query.lower()

    # ── 0. DATABASE STATUS INQUIRY ──
    if any(phrase in q_lower for phrase in ["access the database", "access database", "query database", "database access", "connect to database"]):
        try:
            m_count = query("SELECT COUNT(*) as c FROM matches")["c"].iloc[0]
            b_count = query("SELECT COUNT(*) as c FROM batting")["c"].iloc[0]
            bw_count = query("SELECT COUNT(*) as c FROM bowling")["c"].iloc[0]
            p_count = query("SELECT COUNT(*) as c FROM players")["c"].iloc[0]
            context_bits.append(
                f"LIVE DATABASE STATUS: ONLINE. You have full live read-only SQL query access to the local SQLite database via 'execute_sql_query'. "
                f"Database contents: {m_count} matches (seasons 2019-2026), {b_count:,} batting records, {bw_count:,} bowling records, {p_count} players."
            )
        except Exception:
            pass

    # ── 1. TOURNAMENT CHAMPIONS & SEASON FINALS ──
    season_match = re.search(r"\b(2019|2020|2021|2022|2023|2024|2025|2026)\b", q_lower)
    matched_season = int(season_match.group(1)) if season_match else None

    is_asking_winner = any(w in q_lower for w in [
        "who won", "won", "winner", "champion", "championship", "title", "final", "trophy", "cup", "standings", "most matches", "most wins"
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

        # Season wins leaderboard if asking about most wins / standings
        if matched_season and any(w in q_lower for w in ["most matches", "most wins", "standings", "points table", "leaderboard", "table", "best team"]):
            standings_sql = f"""
            SELECT winner, COUNT(*) as wins
            FROM matches
            WHERE season = {matched_season} AND winner IS NOT NULL
            GROUP BY winner
            ORDER BY wins DESC
            """
            s_df = query(standings_sql)
            if not s_df.empty:
                standings_str = ", ".join([f"{r['winner']}: {r['wins']} wins" for _, r in s_df.iterrows()])
                context_bits.append(f"Official Match Wins Leaderboard for IPL {matched_season}: {standings_str}.")

    # ── 2. TEAM RECORD IDENTIFICATION ──
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

            season_str = f"Season {matched_season}" if matched_season else "Overall History"
            context_bits.append(
                f"Official Database Telemetry for {matched_team} ({season_str}): {games} matches, {wins} wins, {losses} losses ({win_pct}% win rate)."
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
    Sends guarded, tool-equipped query to DeepSeek API.
    Executes live SQL queries when requested by the model.
    Returns dictionary with reply text, token usage stats, executed queries, and status.
    """
    api_key = custom_api_key or get_deepseek_api_key()
    if not api_key:
        return {
            "reply": "⚠️ DeepSeek API key not found. Please set `DEEPSEEK_API_KEY` in your `.env` or enter it in the sidebar configuration.",
            "usage": None,
            "executed_queries": [],
            "success": False
        }

    system_prompt = (
        "You are 'CricAI', the premier AI Cricket Analyst and Tactical Telemetry Copilot for the IPL Analytics Hub.\n"
        "CORE DIRECTIVES:\n"
        "1. CRICKET DOMAIN ONLY: Answer all questions regarding the Indian Premier League (IPL) and general cricket history, statistics, records, rules, tactics, tournaments, and players directly and authoritatively.\n"
        "2. LIVE DATABASE ACCESS: You have DIRECT, REAL-TIME, UNRESTRICTED READ-ONLY SQL ACCESS to the IPL SQLite database via the 'execute_sql_query' tool.\n"
        "   - When the user asks for match results, win counts, standings, team comparisons, player averages, records, or asks whether you can access the database, USE 'execute_sql_query' to retrieve verified live data from the database.\n"
        "   - If asked whether you can access the database, confirm enthusiastically that you have full live SQL access to the SQLite database and describe the available data.\n"
        "   - NEVER refuse a cricket question by saying 'I don't have access to the database' or 'my records don't contain match-by-match win totals' — you HAVE the 'execute_sql_query' tool, so execute the query and answer directly!\n"
        "3. GROUNDED DATABASE AUTHORITY:\n"
        "   - IPL 2026: Champion is RCB (defeated GT by 92 runs in the final on 2026-05-26 at Dharamsala). RCB won 10 matches total in 2026.\n"
        "   - IPL 2025: Champion is RCB (defeated PBKS in the final).\n"
        "   - IPL 2024: Champion is KKR (defeated SRH in the final).\n"
        "   - IPL 2023: Champion is CSK (defeated GT in the final).\n"
        "   - IPL 2022: Champion is GT (defeated RR in the final).\n"
        "   - IPL 2021: Champion is CSK (defeated KKR in the final).\n"
        "   - IPL 2020: Champion is MI (defeated DC in the final).\n"
        "   - IPL 2019: Champion is MI (defeated CSK in the final).\n"
        "   Never dispute or call verified database records impossible or corrupted.\n"
        "4. TACTICAL BREVITY & POLISH: Keep answers sharp, factual, well-structured with Markdown tables, bold numbers, and bullet points.\n"
        "5. STRICT OFF-TOPIC DECLINE: If and only if a question is strictly non-cricket and non-sports related (e.g. coding, cooking, recipes, medicine, politics), politely decline in a single sentence and invite a cricket inquiry.\n\n"
        f"DATABASE SCHEMA:\n{DATABASE_SCHEMA_DESCRIPTION}"
    )

    retrieved_context = get_dynamic_cricket_context(user_query)
    messages = [{"role": "system", "content": system_prompt}]

    if retrieved_context:
        messages.append({"role": "system", "content": retrieved_context})

    # Add last 3 conversational turns to preserve dialog context without token waste
    if chat_history:
        for msg in chat_history[-3:]:
            if isinstance(msg, dict) and msg.get("role") in ["user", "assistant"] and msg.get("content"):
                messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": user_query})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    executed_queries = []
    total_prompt_tokens = 0
    total_completion_tokens = 0

    max_tool_iterations = 2
    for iteration in range(max_tool_iterations + 1):
        payload = {
            "model": DEFAULT_MODEL,
            "messages": messages,
            "tools": DATABASE_TOOLS,
            "max_tokens": 850,
            "temperature": 0.25,
            "stream": False
        }

        try:
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=25)
            if response.status_code != 200:
                err_msg = f"API Error ({response.status_code}): {response.text}"
                logger.error(err_msg)
                return {
                    "reply": f"⚠️ Could not complete request ({response.status_code}). Please verify your DeepSeek key quota or network access.",
                    "usage": None,
                    "executed_queries": executed_queries,
                    "success": False
                }

            data = response.json()
            choice = data["choices"][0]
            msg = choice["message"]
            usage = data.get("usage", {})
            total_prompt_tokens += usage.get("prompt_tokens", 0)
            total_completion_tokens += usage.get("completion_tokens", 0)

            # Check if model requested tool call(s)
            tool_calls = msg.get("tool_calls")
            if tool_calls and iteration < max_tool_iterations:
                messages.append(msg)
                for tc in tool_calls:
                    fn_name = tc.get("function", {}).get("name")
                    fn_args_str = tc.get("function", {}).get("arguments", "{}")
                    try:
                        fn_args = json.loads(fn_args_str)
                    except Exception:
                        fn_args = {}

                    if fn_name == "execute_sql_query":
                        sql = fn_args.get("query", "")
                        logger.info(f"CricAI executing SQL: {sql}")
                        executed_queries.append(sql)
                        result_text = safe_execute_sql(sql)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc["id"],
                            "content": result_text
                        })
                    else:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc["id"],
                            "content": f"Error: Unknown tool '{fn_name}'"
                        })
                # Loop again to let DeepSeek synthesize the tool response
                continue

            # Final assistant message received
            reply_text = msg.get("content", "").strip()
            total_usage = {
                "prompt_tokens": total_prompt_tokens,
                "completion_tokens": total_completion_tokens,
                "total_tokens": total_prompt_tokens + total_completion_tokens
            }
            return {
                "reply": reply_text,
                "usage": total_usage,
                "executed_queries": executed_queries,
                "success": True
            }

        except Exception as e:
            logger.error(f"DeepSeek Request Exception: {e}")
            return {
                "reply": f"⚠️ Connection error: {str(e)}",
                "usage": None,
                "executed_queries": executed_queries,
                "success": False
            }

    # Fallback if iterations exceeded
    return {
        "reply": "⚠️ Query processing exceeded maximum telemetry iterations.",
        "usage": None,
        "executed_queries": executed_queries,
        "success": False
    }
