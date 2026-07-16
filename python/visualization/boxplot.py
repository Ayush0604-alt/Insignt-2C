"""
Renders a boxplot for one numeric column (optionally grouped by a
categorical column), so outliers flagged by the analysis engine can
actually be visualized rather than just reported as numbers.

Usage: python boxplot.py <file_path> <x_column> [group_by_column] [color]
Prints the saved chart's filename to stdout.
"""

import os
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns  # noqa: E402

import pandas as pd  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.io_utils import clean_column_name, load_dataset, resolve_color  # noqa: E402

if len(sys.argv) < 3:
    print("Error: Usage: boxplot.py <file_path> <x_column> [group_by_column] [color]", file=sys.stderr)
    sys.exit(1)

file_path = sys.argv[1]
x_column = clean_column_name(sys.argv[2])
group_by = clean_column_name(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].strip() else ""
final_color = resolve_color(sys.argv[4] if len(sys.argv) > 4 else "")

df = load_dataset(file_path)

if x_column not in df.columns:
    print(f"Error: Invalid column '{x_column}'", file=sys.stderr)
    sys.exit(1)

values = df[x_column]
if hasattr(values, "columns"):  # duplicate column name edge case
    values = values.iloc[:, 0]

values = pd.to_numeric(values, errors="coerce")

plt.figure(figsize=(10, 6))

if group_by and group_by in df.columns:
    plot_df = pd.DataFrame({x_column: values, group_by: df[group_by]}).dropna()
    if plot_df.empty:
        print("Error: No valid data after cleaning", file=sys.stderr)
        sys.exit(1)
    # Limit to the 10 largest groups so the chart stays readable.
    top_groups = plot_df[group_by].value_counts().head(10).index
    plot_df = plot_df[plot_df[group_by].isin(top_groups)]
    sns.boxplot(data=plot_df, x=group_by, y=x_column, color=final_color)
    plt.title(f"{x_column} distribution by {group_by}")
    plt.xticks(rotation=45, ha="right")
else:
    clean_values = values.dropna()
    if clean_values.empty:
        print("Error: No valid numeric data in column", file=sys.stderr)
        sys.exit(1)
    sns.boxplot(y=clean_values, color=final_color)
    plt.title(f"{x_column} distribution")

plt.tight_layout()

timestamp = int(time.time())
filename = f"chart_{timestamp}.png"
current_dir = os.path.dirname(__file__)
save_path = os.path.abspath(os.path.join(current_dir, "../../backend/generated_charts", filename))
os.makedirs(os.path.dirname(save_path), exist_ok=True)

plt.savefig(save_path, dpi=150)
plt.close()

print(filename)
