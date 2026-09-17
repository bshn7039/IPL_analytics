"""
Parser Helpers
Cricket-specific data extraction and normalization routines.
Special attention to cricket math:
- 3.4 overs = 3 overs + 4 balls = 22 balls.
- Not out notation: "45*" -> 45 runs, not out flag.
"""
import re

TEAM_MAPPING = {
    "Mumbai Indians": "MI",
    "Chennai Super Kings": "CSK",
    "Royal Challengers Bangalore": "RCB",
    "Royal Challengers Bengaluru": "RCB",
    "Kolkata Knight Riders": "KKR",
    "Delhi Capitals": "DC",
    "Delhi Daredevils": "DC",
    "Rajasthan Royals": "RR",
    "Punjab Kings": "PBKS",
    "Kings XI Punjab": "PBKS",
    "Sunrisers Hyderabad": "SRH",
    "Gujarat Titans": "GT",
    "Lucknow Super Giants": "LSG",
    "Rising Pune Supergiant": "RPS",
    "Rising Pune Supergiants": "RPS",
    "Gujarat Lions": "GL",
    "Deccan Chargers": "DEC"
}

def standardize_team_name(raw_name):
    """Maps full or variant team names to canonical 2-4 letter abbreviation."""
    if not raw_name or not isinstance(raw_name, str):
        return "UNK"
    clean = raw_name.strip()
    if clean in TEAM_MAPPING:
        return TEAM_MAPPING[clean]
    for short in set(TEAM_MAPPING.values()):
        if clean.upper() == short:
            return short
    for full, short in TEAM_MAPPING.items():
        if full.lower() in clean.lower() or clean.lower() in full.lower():
            return short
    return clean[:4].upper()

def parse_player_name(raw_name):
    """
    Cleans captain/wicketkeeper annotations, trailing symbols, extra whitespace.
    e.g. 'Virat Kohli (c)' -> 'Virat Kohli', 'MS Dhoni †' -> 'MS Dhoni'
    """
    if not raw_name:
        return ""
    cleaned = str(raw_name)
    # Strip (c), (wk), [c], etc.
    cleaned = re.sub(r"\s*[\(\[][c†wWkK/\s]+[\)\]]", "", cleaned)
    # Strip standalone symbols
    cleaned = re.sub(r"[†*]", "", cleaned)
    return " ".join(cleaned.split()).strip()

def parse_runs(raw_val):
    """
    Extracts run count and not-out status.
    e.g. '82*' -> (82, True), '45' -> (45, False), '0' -> (0, False)
    """
    if raw_val is None:
        return 0, False
    val_str = str(raw_val).strip()
    not_out = "*" in val_str or "not out" in val_str.lower()
    clean_digits = re.sub(r"[^\d]", "", val_str)
    runs = int(clean_digits) if clean_digits else 0
    return runs, not_out

def parse_overs(overs_val):
    """
    Converts cricket overs notation to total balls bowled.
    CRICKET SPECIFIC MATH:
    3.4 overs means 3 complete overs (18 balls) + 4 extra balls = 22 balls.
    4.0 overs means 24 balls.
    0.5 overs means 5 balls.
    """
    if overs_val is None:
        return 0
    try:
        val_str = str(overs_val).strip()
        if "." in val_str:
            parts = val_str.split(".")
            completed_overs = int(parts[0]) if parts[0] else 0
            extra_balls = int(parts[1]) if len(parts) > 1 and parts[1] else 0
        else:
            completed_overs = int(val_str)
            extra_balls = 0
        return completed_overs * 6 + extra_balls
    except (ValueError, TypeError):
        return 0

def parse_match_result(result_text):
    """
    Parses natural language match result string.
    e.g. 'MI won by 5 wickets' -> {'winner': 'MI', 'margin': 5, 'margin_type': 'wickets'}
    """
    if not result_text or not isinstance(result_text, str):
        return {"winner": "No Result", "margin": 0, "margin_type": "none"}
    
    clean = result_text.strip()
    match = re.search(r"(\b[\w\s]+?)\s+won\s+by\s+(\d+)\s+(wicket|run|runs|wickets)", clean, re.IGNORECASE)
    if match:
        winner_raw = match.group(1).strip()
        margin = int(match.group(2))
        margin_type = "wickets" if "wicket" in match.group(3).lower() else "runs"
        winner = standardize_team_name(winner_raw)
        return {"winner": winner, "margin": margin, "margin_type": margin_type}
    
    if "tie" in clean.lower() or "super over" in clean.lower():
        return {"winner": "Tie", "margin": 0, "margin_type": "tie"}
        
    return {"winner": standardize_team_name(clean), "margin": 0, "margin_type": "none"}
