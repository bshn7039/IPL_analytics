"""
Database Management Module
Handles SQLite connection pools, schema initialization, and DataFrame queries.
"""
import os
import sqlite3
import logging
import pandas as pd

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "ipl.db")
DEFAULT_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

def get_connection(db_path=DEFAULT_DB_PATH):
    """Returns a SQLite connection object with foreign key enforcement enabled."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def create_database(db_path=DEFAULT_DB_PATH, schema_path=DEFAULT_SCHEMA_PATH):
    """Initializes tables and indices from schema.sql."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = get_connection(db_path)
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
    logger.info(f"Database schema initialized at {db_path}")

def query(sql, params=None, db_path=DEFAULT_DB_PATH):
    """
    Executes a SQL query and returns results directly as a Pandas DataFrame.
    Gracefully handles empty query results and exceptions.
    """
    conn = get_connection(db_path)
    try:
        if params:
            df = pd.read_sql_query(sql, conn, params=params)
        else:
            df = pd.read_sql_query(sql, conn)
        return df
    except Exception as e:
        logger.error(f"SQL execution failed: {sql} | Error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def execute_non_query(sql, params=None, db_path=DEFAULT_DB_PATH):
    """Executes an INSERT, UPDATE, or DELETE statement."""
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        conn.commit()
        return cur.rowcount
    except Exception as e:
        logger.error(f"SQL execute failed: {e}")
        conn.rollback()
        raise e
    finally:
        conn.close()

def insert_dataframe(table_name, df, db_path=DEFAULT_DB_PATH, if_exists="append"):
    """Appends or replaces records in a target table using a DataFrame."""
    if df is None or df.empty:
        return 0
    conn = get_connection(db_path)
    try:
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)
        conn.commit()
        return len(df)
    finally:
        conn.close()

def get_db_stats(db_path=DEFAULT_DB_PATH):
    """Returns total record counts across all core entities."""
    stats = {}
    tables = ["teams", "players", "matches", "batting", "bowling"]
    for t in tables:
        df = query(f"SELECT COUNT(*) as cnt FROM {t}", db_path=db_path)
        stats[t] = int(df["cnt"].iloc[0]) if not df.empty else 0
    seasons_df = query("SELECT DISTINCT season FROM matches ORDER BY season DESC", db_path=db_path)
    stats["seasons"] = seasons_df["season"].tolist() if not seasons_df.empty else []
    return stats
