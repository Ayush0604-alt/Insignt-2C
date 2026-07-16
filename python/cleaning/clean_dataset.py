"""
Applies the cleaning options selected in the UI (remove duplicates, drop
missing rows, fill missing values) and writes the result to a new CSV in
backend/cleaned_data/.

Usage: python clean_dataset.py <file_path> <remove_duplicates> <drop_missing> <missing_strategy>
  remove_duplicates / drop_missing: "true" or "false"
  missing_strategy: "mean" | "median" | "mode" | "" (none)
Prints the absolute path of the saved file to stdout.
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.io_utils import load_dataset  # noqa: E402

if len(sys.argv) < 5:
    print("Error: Usage: clean_dataset.py <file_path> <remove_duplicates> <drop_missing> <missing_strategy>", file=sys.stderr)
    sys.exit(1)

file_path = sys.argv[1]
remove_duplicates = sys.argv[2] == "true"
drop_missing = sys.argv[3] == "true"
missing_strategy = sys.argv[4]

df = load_dataset(file_path)

if remove_duplicates:
    df = df.drop_duplicates()

if drop_missing:
    df = df.dropna()

if missing_strategy == "mean":
    numeric_cols = df.select_dtypes(include=["number"]).columns
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].mean())

elif missing_strategy == "median":
    numeric_cols = df.select_dtypes(include=["number"]).columns
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())

elif missing_strategy == "mode":
    for col in df.columns:
        mode_series = df[col].mode()
        if not mode_series.empty:
            df[col] = df[col].fillna(mode_series[0])

timestamp = int(time.time())
filename = f"cleaned_{timestamp}.csv"

current_dir = os.path.dirname(os.path.abspath(__file__))
cleaned_data_dir = os.path.abspath(os.path.join(current_dir, "../../backend/cleaned_data"))
os.makedirs(cleaned_data_dir, exist_ok=True)

save_path = os.path.join(cleaned_data_dir, filename)
df.to_csv(save_path, index=False)

print(save_path.strip())
