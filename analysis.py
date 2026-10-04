"""
2025 NFL QB Efficiency Analysis

This script is intentionally straightforward. I wanted to build a first
sports-analytics project that I could understand and explain myself.

Data: nflverse 2025 regular-season player summary.
Sample: 20 quarterbacks with the most pass attempts.
"""

import pandas as pd

DATA_FILE = "data/stats_player_reg_2025.csv"

# 1. Load the data
df = pd.read_csv(DATA_FILE)

# 2. Pick the 20 highest-volume QBs
qbs = (
    df[df["position"] == "QB"]
    .sort_values(["attempts", "games"], ascending=False)
    .head(20)
    .copy()
)

# 3. Build the efficiency metrics
qbs["epa_per_attempt"] = qbs["passing_epa"] / qbs["attempts"]
qbs["yards_per_attempt"] = qbs["passing_yards"] / qbs["attempts"]
qbs["td_rate"] = 100 * qbs["passing_tds"] / qbs["attempts"]
qbs["int_rate"] = 100 * qbs["passing_interceptions"] / qbs["attempts"]
qbs["sack_rate"] = 100 * qbs["sacks_suffered"] / (
    qbs["attempts"] + qbs["sacks_suffered"]
)

# 4. Weight the metrics.
# Higher is better for EPA, CPOE, Y/A and TD rate.
# Lower is better for INT rate and sack rate.
weights = {
    "epa_per_attempt": 0.30,
    "passing_cpoe": 0.20,
    "yards_per_attempt": 0.15,
    "td_rate": 0.10,
    "int_rate": 0.10,
    "sack_rate": 0.15,
}

positive = ["epa_per_attempt", "passing_cpoe", "yards_per_attempt", "td_rate"]
negative = ["int_rate", "sack_rate"]

for metric in positive:
    qbs[metric + "_pct"] = qbs[metric].rank(pct=True) * 100

for metric in negative:
    qbs[metric + "_pct"] = (1 - qbs[metric].rank(pct=True)) * 100

qbs["model_score"] = sum(
    qbs[metric + "_pct"] * weight for metric, weight in weights.items()
)

# The project display grade is rescaled so the sample average is around 75.
# This makes it easier to read as a football grade without changing the order.
mean = qbs["model_score"].mean()
std = qbs["model_score"].std(ddof=0)
qbs["passing_efficiency_grade"] = (
    75 + 9 * ((qbs["model_score"] - mean) / std)
).clip(60, 96)

qbs = qbs.sort_values("passing_efficiency_grade", ascending=False)

print(
    qbs[
        ["player_display_name", "recent_team", "passing_efficiency_grade"]
    ].to_string(index=False)
)
