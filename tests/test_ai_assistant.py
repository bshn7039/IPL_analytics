"""
Unit Tests for AI Cricket Analyst Engine and Safe SQL Execution
"""
import unittest
import pandas as pd
from analytics.ai_assistant import (
    safe_execute_sql,
    get_dynamic_cricket_context,
    get_deepseek_api_key,
    DATABASE_TOOLS,
    DATABASE_SCHEMA_DESCRIPTION
)

class TestAiAssistant(unittest.TestCase):

    def test_safe_execute_sql_valid_query(self):
        """Must successfully execute read-only SELECT queries."""
        result = safe_execute_sql("SELECT COUNT(*) as total_matches FROM matches")
        self.assertIn("total_matches", result)
        self.assertNotIn("Error", result)

    def test_safe_execute_sql_blocks_mutations(self):
        """Must strictly block DROP, DELETE, UPDATE, INSERT, ALTER."""
        mutations = [
            "DROP TABLE matches",
            "DELETE FROM batting",
            "UPDATE matches SET winner = 'RCB'",
            "INSERT INTO teams (team_name, short_name) VALUES ('Test', 'TST')",
            "ALTER TABLE matches ADD COLUMN test_col TEXT",
            "TRUNCATE TABLE matches"
        ]
        for m in mutations:
            result = safe_execute_sql(m)
            self.assertIn("Error:", result, f"Failed to block mutation: {m}")

    def test_safe_execute_sql_blocks_non_select(self):
        """Must block non-SELECT statements."""
        result = safe_execute_sql("EXEC sp_test")
        self.assertIn("Error: Only read-only SELECT", result)

    def test_dynamic_cricket_context_champions(self):
        """Must provide grounded champion context for 2025 and 2026."""
        ctx_2026 = get_dynamic_cricket_context("who won 2026 ipl")
        self.assertIn("RCB", ctx_2026)
        self.assertIn("CHAMPION", ctx_2026)

        ctx_2025 = get_dynamic_cricket_context("who won 2025 ipl")
        self.assertIn("RCB", ctx_2025)

    def test_dynamic_cricket_context_most_wins_2026(self):
        """Must inject standings context when asked for most wins in 2026."""
        ctx = get_dynamic_cricket_context("who won the most matches in 2026 ipl")
        self.assertIn("RCB: 10 wins", ctx)

    def test_dynamic_cricket_context_database_access(self):
        """Must report live database online status and match counts."""
        ctx = get_dynamic_cricket_context("can you access the database")
        self.assertIn("LIVE DATABASE STATUS: ONLINE", ctx)
        self.assertIn("matches", ctx)

    def test_database_tools_schema_structure(self):
        """Database tools must define valid OpenAI-compatible function calling."""
        self.assertEqual(len(DATABASE_TOOLS), 1)
        tool = DATABASE_TOOLS[0]
        self.assertEqual(tool["type"], "function")
        self.assertEqual(tool["function"]["name"], "execute_sql_query")
        self.assertIn("query", tool["function"]["parameters"]["properties"])

if __name__ == "__main__":
    unittest.main()
