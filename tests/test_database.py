"""
Unit Tests for Database Engine and Query Wrappers
"""
import unittest
import os
import pandas as pd
from database.db import get_connection, query, create_database, get_db_stats

class TestDatabase(unittest.TestCase):

    def test_database_connection(self):
        """Must establish valid SQLite connection."""
        conn = get_connection()
        self.assertIsNotNone(conn)
        conn.close()

    def test_query_returns_dataframe(self):
        """Any valid SQL query must return a Pandas DataFrame."""
        df = query("SELECT * FROM teams LIMIT 5")
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)

    def test_database_stats_integrity(self):
        """Database must have positive counts for core entities."""
        stats = get_db_stats()
        self.assertGreaterEqual(stats["teams"], 10)
        self.assertGreaterEqual(stats["matches"], 100)
        self.assertGreaterEqual(stats["batting"], 1000)
        self.assertGreaterEqual(stats["bowling"], 1000)

if __name__ == "__main__":
    unittest.main()
