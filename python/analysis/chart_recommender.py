"""
Suggests chart types for a dataset, with a reason grounded in the actual
data (not just "you have numeric columns") - e.g. it will only recommend
a boxplot if outliers were actually detected, and names the specific
column pair driving a heatmap/scatter suggestion.

Usage: python chart_recommender.py <file_path>
Prints a JSON array of {chart, reason} objects to stdout.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.io_utils import load_dataset  # noqa: E402
from utils.stats_utils import categorical_column_stats, numeric_column_stats, top_correlations  # noqa: E402

if len(sys.argv) < 2:
    print("Error: Missing file path argument", file=sys.stderr)
    sys.exit(1)

file_path = sys.argv[1]
df = load_dataset(file_path)

numeric_cols = list(df.select_dtypes(include=["number"]).columns)
categorical_cols = list(df.select_dtypes(include=["object"]).columns)

# Identifier-like columns (near-100% unique values, e.g. names/emails/IDs)
# make poor bar/pie candidates, so they're excluded from those suggestions.
chartable_categorical_cols = [
    col for col in categorical_cols
    if not categorical_column_stats(df[col]).get("is_likely_identifier", False)
]

recommendations = []

# Heatmap: only worth it with 3+ numeric columns, and stronger if a
# meaningful correlation actually exists.
if len(numeric_cols) >= 3:
    strongest = top_correlations(df, numeric_cols, top_n=1)
    if strongest and strongest[0]["strength"] in ("strong", "moderate"):
        c = strongest[0]
        reason = (
            f"{len(numeric_cols)} numeric columns available, including a "
            f"{c['strength']} correlation between '{c['column_a']}' and '{c['column_b']}' (r={c['correlation']})"
        )
    else:
        reason = f"{len(numeric_cols)} numeric columns available for correlation analysis"
    recommendations.append({"chart": "heatmap", "reason": reason})

# Scatter: same idea, but works from just 2 numeric columns.
if len(numeric_cols) >= 2:
    strongest = top_correlations(df, numeric_cols, top_n=1)
    if strongest:
        c = strongest[0]
        reason = f"'{c['column_a']}' and '{c['column_b']}' show a {c['strength']} relationship worth plotting"
    else:
        reason = "Multiple numeric columns available for relationship analysis"
    recommendations.append({"chart": "scatter", "reason": reason})

# Boxplot: only recommended when we actually found outliers, since that's
# the whole point of a boxplot.
outlier_cols = []
for col in numeric_cols:
    stats = numeric_column_stats(df[col])
    if stats and stats.get("outlier_count", 0) > 0:
        outlier_cols.append(col)

if outlier_cols:
    recommendations.append({
        "chart": "boxplot",
        "reason": f"Outliers detected in {', '.join(outlier_cols[:3])} — a boxplot highlights the spread and extremes",
    })

# Histogram: any single numeric column is enough.
if len(numeric_cols) >= 1:
    recommendations.append({
        "chart": "histogram",
        "reason": "Numeric column distributions can be visualized with a histogram",
    })

# Bar: needs at least one non-identifier categorical + one numeric column.
if len(chartable_categorical_cols) >= 1 and len(numeric_cols) >= 1:
    recommendations.append({
        "chart": "bar",
        "reason": f"'{chartable_categorical_cols[0]}' can be compared against numeric columns",
    })

# Pie: category proportions (also skips identifier-like columns).
if len(chartable_categorical_cols) >= 1:
    recommendations.append({
        "chart": "pie",
        "reason": f"'{chartable_categorical_cols[0]}' proportions can be visualized as a pie chart",
    })

print(json.dumps(recommendations))
