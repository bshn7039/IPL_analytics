"""
Unit Tests for Cricket-Specific Metrics & Edge Cases
"""
import unittest
import numpy as np
from scraper.parser import parse_overs, parse_runs
from processing.transformer import add_batting_metrics, add_bowling_metrics
import pandas as pd

class TestCricketMetrics(unittest.TestCase):

    def test_overs_to_balls_partial(self):
        """3.4 overs means 3 completed overs + 4 extra balls = 22 balls."""
        self.assertEqual(parse_overs("3.4"), 22)
        self.assertEqual(parse_overs(3.4), 22)

    def test_overs_to_balls_full(self):
        """4.0 overs means 24 balls."""
        self.assertEqual(parse_overs("4.0"), 24)
        self.assertEqual(parse_overs(4.0), 24)

    def test_overs_to_balls_single_ball(self):
        """0.1 overs means 1 ball."""
        self.assertEqual(parse_overs("0.1"), 1)

    def test_parse_runs_not_out(self):
        """45* should parse as 45 runs with not_out=True."""
        runs, not_out = parse_runs("45*")
        self.assertEqual(runs, 45)
        self.assertTrue(not_out)

    def test_parse_runs_out(self):
        """82 should parse as 82 runs with not_out=False."""
        runs, not_out = parse_runs("82")
        self.assertEqual(runs, 82)
        self.assertFalse(not_out)

    def test_strike_rate_calculation(self):
        """100 runs off 60 balls = 166.67 strike rate."""
        df = pd.DataFrame([{"runs": 100, "balls": 60, "fours": 8, "sixes": 4}])
        res = add_batting_metrics(df)
        self.assertEqual(res["strike_rate"].iloc[0], 166.67)

    def test_strike_rate_zero_balls(self):
        """Zero balls faced should result in 0.0 strike rate without divide-by-zero error."""
        df = pd.DataFrame([{"runs": 0, "balls": 0, "fours": 0, "sixes": 0}])
        res = add_batting_metrics(df)
        self.assertEqual(res["strike_rate"].iloc[0], 0.0)

    def test_economy_calculation(self):
        """32 runs conceded in 24 balls (4.0 overs) = 8.00 economy."""
        df = pd.DataFrame([{"runs_conceded": 32, "balls_bowled": 24, "wickets": 2}])
        res = add_bowling_metrics(df)
        self.assertEqual(res["economy"].iloc[0], 8.00)

    def test_bowling_average_zero_wickets(self):
        """0 wickets should yield NaN for average without crashing."""
        df = pd.DataFrame([{"runs_conceded": 40, "balls_bowled": 24, "wickets": 0}])
        res = add_bowling_metrics(df)
        self.assertTrue(np.isnan(res["bowling_avg"].iloc[0]))

if __name__ == "__main__":
    unittest.main()
