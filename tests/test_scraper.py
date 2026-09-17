"""
Unit Tests for Scraper Parsers and Utilities
"""
import unittest
from scraper.scraper_utils import get_headers
from scraper.parser import (
    standardize_team_name, parse_player_name, parse_match_result
)

class TestScraper(unittest.TestCase):

    def test_get_headers_structure(self):
        """Headers must include User-Agent and standard browser headers."""
        headers = get_headers()
        self.assertIn("User-Agent", headers)
        self.assertIn("Accept", headers)

    def test_team_standardization(self):
        """Must correctly map team name variations to official short names."""
        self.assertEqual(standardize_team_name("Mumbai Indians"), "MI")
        self.assertEqual(standardize_team_name("Chennai Super Kings"), "CSK")
        self.assertEqual(standardize_team_name("Royal Challengers Bengaluru"), "RCB")
        self.assertEqual(standardize_team_name("Royal Challengers Bangalore"), "RCB")
        self.assertEqual(standardize_team_name("KKR"), "KKR")

    def test_player_name_cleanup(self):
        """Should strip captaincy (c) and keeper (†) symbols and extra whitespace."""
        self.assertEqual(parse_player_name("Virat Kohli (c)"), "Virat Kohli")
        self.assertEqual(parse_player_name("MS Dhoni †"), "MS Dhoni")
        self.assertEqual(parse_player_name("  Rohit Sharma  "), "Rohit Sharma")

    def test_match_result_parsing(self):
        """Should extract winner and margin correctly."""
        res = parse_match_result("MI won by 5 wickets")
        self.assertEqual(res["winner"], "MI")
        self.assertEqual(res["margin"], 5)
        self.assertEqual(res["margin_type"], "wickets")

if __name__ == "__main__":
    unittest.main()
