"""
Produces a JSON summary of a dataset for the "Summary" panel of the app.

Beyond basic shape/missingness (what the original version did), this now
reports the kind of statistics an actual exploratory data analysis pass
needs: spread (std dev, IQR), skew, IQR-based outlier counts per numeric
column, cardinality for categorical columns, the strongest correlations
between numeric columns, and a single rollup data-quality score.

Usage: python dataset_summary.py <file_path>
Prints a single line of JSON to stdout.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.io_utils import load_dataset  # noqa: E402
from utils.stats_utils import (  # noqa: E402
    categorical_column_stats,
    data_quality_score,
    numeric_column_stats,
    top_correlations,
)

if len(sys.argv) < 2:
    print("Error: Missing file path argument", file=sys.stderr)
    sys.exit(1)

file_path = sys.argv[1]
df = load_dataset(file_path)

rows, columns = int(df.shape[0]), int(df.shape[1])
total_cells = rows * columns

missing_values = {col: int(val) for col, val in df.isnull().sum().items()}
total_missing = int(sum(missing_values.values()))
duplicate_rows = int(df.duplicated().sum())
data_types = {col: str(dtype) for col, dtype in df.dtypes.items()}

numeric_cols = list(df.select_dtypes(include=["number"]).columns)
categorical_cols = list(df.select_dtypes(include=["object"]).columns)

numeric_summary = {col: numeric_column_stats(df[col]) for col in numeric_cols}
categorical_summary = {col: categorical_column_stats(df[col]) for col in categorical_cols}

summary = {
    "rows": rows,
    "columns": columns,
    "missing_values": missing_values,
    "missing_percentage": round(total_missing / total_cells * 100, 2) if total_cells else 0,
    "duplicate_rows": duplicate_rows,
    "data_types": data_types,
    "numeric_summary": numeric_summary,
    "categorical_summary": categorical_summary,
    "top_correlations": top_correlations(df, numeric_cols),
    "data_quality_score": data_quality_score(rows, total_missing, total_cells, duplicate_rows),
}

print(json.dumps(summary))
