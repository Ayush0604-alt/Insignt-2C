"""
Returns the column names for a dataset, split into numeric/categorical
buckets, so the frontend can populate its X/Y column dropdowns.

Usage: python get_columns.py <file_path>
Prints a single line of JSON to stdout.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from io_utils import load_dataset  # noqa: E402

if len(sys.argv) < 2:
    print("Error: Missing file path argument", file=sys.stderr)
    sys.exit(1)

file_path = sys.argv[1]
df = load_dataset(file_path)

numeric_columns = list(df.select_dtypes(include=["number"]).columns)
categorical_columns = list(df.select_dtypes(include=["object"]).columns)

result = {
    "all_columns": list(df.columns),
    "numeric_columns": numeric_columns,
    "categorical_columns": categorical_columns,
}

print(json.dumps(result))
