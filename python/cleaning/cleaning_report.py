"""
Produces a data-quality report: missing values, duplicate rows, fully
empty columns, and columns that look numeric but are stored as text
(a common real-world data issue, e.g. "1,200" or "$45").

Usage: python cleaning_report.py <file_path>
Prints a single line of JSON to stdout.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.io_utils import load_dataset  # noqa: E402

if len(sys.argv) < 2:
    print("Error: Missing file path argument", file=sys.stderr)
    sys.exit(1)

file_path = sys.argv[1]
df = load_dataset(file_path)

missing_values = {col: int(val) for col, val in df.isnull().sum().items() if val > 0}
duplicate_rows = int(df.duplicated().sum())
empty_columns = [col for col in df.columns if df[col].isnull().all()]
data_types = {col: str(dtype) for col, dtype in df.dtypes.items()}

# Flag object columns where most sampled values look like numbers once
# commas/periods are stripped - a sign the column should be numeric but
# got read in as text (common with currency or thousands-separated data).
numeric_string_columns = []
for col in df.select_dtypes(include=["object"]).columns:
    sample_values = df[col].dropna().astype(str).head(10)
    numeric_like_count = sum(
        1 for value in sample_values
        if value.replace(",", "").replace(".", "").isdigit()
    )
    if numeric_like_count >= 5:
        numeric_string_columns.append(col)

report = {
    "missing_values": missing_values,
    "duplicate_rows": duplicate_rows,
    "empty_columns": empty_columns,
    "data_types": data_types,
    "numeric_string_columns": numeric_string_columns,
}

print(json.dumps(report))
