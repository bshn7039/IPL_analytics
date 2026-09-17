"""
Data Validation Module
Asserts logical boundaries and domain rules for cricket statistics.
"""
import logging

logger = logging.getLogger(__name__)

def validate_batting(df):
    """Checks batting records for impossible domain values."""
    errors = []
    if (df["runs"] < 0).any():
        errors.append("Negative runs detected in batting dataset.")
    if (df["balls"] < 0).any():
        errors.append("Negative balls faced detected.")
    if (df["runs"] > 250).any():
        errors.append("Individual score exceeds 250 in a T20 match.")
    if (df["strike_rate"] < 0).any():
        errors.append("Negative strike rate detected.")
    
    if errors:
        for e in errors:
            logger.warning(f"Batting Validation Warning: {e}")
        return False, errors
    return True, []

def validate_bowling(df):
    """Checks bowling records for impossible domain values."""
    errors = []
    if (df["runs_conceded"] < 0).any():
        errors.append("Negative runs conceded detected.")
    if (df["wickets"] < 0).any():
        errors.append("Negative wickets detected.")
    if (df["wickets"] > 10).any():
        errors.append("Bowler wickets exceed 10 in a single innings.")
    if (df["overs"] > 5.0).any():
        errors.append("Bowler overs exceed maximum permitted T20 quota.")
        
    if errors:
        for e in errors:
            logger.warning(f"Bowling Validation Warning: {e}")
        return False, errors
    return True, []

def validate_matches(df):
    """Checks match records for structural integrity."""
    errors = []
    if (df["team1"] == df["team2"]).any():
        errors.append("Identical opposing teams found in match schedule.")
    if df["match_id"].duplicated().any():
        errors.append("Duplicate match IDs discovered.")

    if errors:
        for e in errors:
            logger.warning(f"Match Validation Warning: {e}")
        return False, errors
    return True, []
