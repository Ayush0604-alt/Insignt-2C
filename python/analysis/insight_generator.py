"""
Generates a list of plain-English insight strings from a dataset - the
kind of "story" an analyst tells after a first EDA pass, rather than a
raw stat dump. Backed by the same numeric/categorical/correlation helpers
that power dataset_summary.py, so the numbers stay consistent across
both panels of the app.

Usage: python insight_generator.py <file_path>
Prints a JSON array of strings to stdout.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.io_utils import load_dataset  # noqa: E402
from utils.stats_utils import (  # noqa: E402
    categorical_column_stats,
    data_quality_score,
    detect_datetime_columns,
    numeric_column_stats,
    top_correlations,
)

if len(sys.argv) < 2:
    print("Error: Missing file path argument", file=sys.stderr)
    sys.exit(1)

file_path = sys.argv[1]
df = load_dataset(file_path)

insights = []
rows, cols = df.shape
numeric_cols = list(df.select_dtypes(include=["number"]).columns)
categorical_cols = list(df.select_dtypes(include=["object"]).columns)

# ── Overview ────────────────────────────────────────────────
insights.append(
    f"Dataset contains {rows:,} rows and {cols} columns "
    f"({len(numeric_cols)} numeric, {len(categorical_cols)} categorical)."
)

total_missing = int(df.isnull().sum().sum())
total_cells = rows * cols
missing_pct = round(total_missing / total_cells * 100, 1) if total_cells else 0
duplicate_rows = int(df.duplicated().sum())

quality_score = data_quality_score(rows, total_missing, total_cells, duplicate_rows)
if quality_score >= 90:
    quality_label = "excellent, minimal cleaning needed"
elif quality_score >= 70:
    quality_label = "good, with some missing or duplicate data to address"
elif quality_score >= 50:
    quality_label = "fair, meaningful cleaning is recommended before analysis"
else:
    quality_label = "poor, significant missing or duplicate data present"
insights.append(f"Overall data quality score: {quality_score}/100 ({quality_label}).")

# ── Missing data ────────────────────────────────────────────
if total_missing == 0:
    insights.append("No missing values detected in any column.")
else:
    missing_by_col = df.isnull().sum()
    worst_missing = missing_by_col[missing_by_col > 0].sort_values(ascending=False)
    top_col = worst_missing.index[0]
    top_pct = round(worst_missing.iloc[0] / rows * 100, 1)
    insights.append(
        f"{total_missing:,} missing values found ({missing_pct}% of all cells); "
        f"'{top_col}' is the most affected column at {top_pct}% missing."
    )

# ── Duplicates ──────────────────────────────────────────────
if duplicate_rows > 0:
    dup_pct = round(duplicate_rows / rows * 100, 1)
    insights.append(f"{duplicate_rows:,} duplicate rows detected ({dup_pct}% of the dataset).")

# ── Numeric columns: outliers + skew ─────────────────────────
flags_added = 0
MAX_NUMERIC_FLAGS = 6

for col in numeric_cols:
    if flags_added >= MAX_NUMERIC_FLAGS:
        break

    stats = numeric_column_stats(df[col])
    if not stats:
        continue

    if stats["outlier_count"] > 0:
        insights.append(
            f"'{col}' has {stats['outlier_count']} outlier value(s) "
            f"({stats['outlier_percentage']}%) outside the typical IQR range "
            f"[{stats['q1']}, {stats['q3']}]."
        )
        flags_added += 1

    if abs(stats["skewness"]) >= 1 and flags_added < MAX_NUMERIC_FLAGS:
        direction = (
            "right, a few unusually high values pull the average up"
            if stats["skewness"] > 0
            else "left, a few unusually low values pull the average down"
        )
        insights.append(
            f"'{col}' is skewed {direction} — median ({stats['median']}) may summarize it "
            f"better than the mean ({stats['mean']})."
        )
        flags_added += 1

# ── Categorical columns ───────────────────────────────────────
for col in categorical_cols[:5]:
    stats = categorical_column_stats(df[col])
    if not stats:
        continue

    if stats["is_likely_identifier"]:
        insights.append(
            f"'{col}' looks like an identifier column ({stats['unique_values']} unique values) "
            f"and isn't useful for grouping or charting."
        )
    elif stats["most_common_percentage"] >= 50:
        insights.append(
            f"'{col}' is dominated by '{stats['most_common']}' "
            f"({stats['most_common_percentage']}% of rows)."
        )

# ── Correlations ────────────────────────────────────────────
for corr in top_correlations(df, numeric_cols, top_n=2):
    direction = "increases" if corr["correlation"] > 0 else "decreases"
    insights.append(
        f"'{corr['column_a']}' and '{corr['column_b']}' show a {corr['strength']} relationship "
        f"(r={corr['correlation']}); as one rises, the other typically {direction}."
    )

# ── Date columns ────────────────────────────────────────────
datetime_candidates = detect_datetime_columns(df, categorical_cols)
if datetime_candidates:
    insights.append(
        f"Detected likely date column(s): {', '.join(datetime_candidates)} — "
        f"consider a time-based trend view."
    )

print(json.dumps(insights))
