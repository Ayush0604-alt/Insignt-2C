"""
Renders a bar chart: value counts for a single categorical column, or
mean-of-Y-grouped-by-X when a numeric Y column is also provided.

Usage: python bar_chart.py <file_path> <x_column> [y_column] [color]
Prints the saved chart's filename to stdout.
"""

import os
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.io_utils import clean_column_name, load_dataset, resolve_color  # noqa: E402

if len(sys.argv) < 3:
    print("Error: Usage: bar_chart.py <file_path> <x_column> [y_column] [color]", file=sys.stderr)
    sys.exit(1)

file_path = sys.argv[1]
x_column = clean_column_name(sys.argv[2])
y_column = clean_column_name(sys.argv[3]) if len(sys.argv) > 3 else ""
final_color = resolve_color(sys.argv[4] if len(sys.argv) > 4 else "")

df = load_dataset(file_path)

if x_column not in df.columns:
    print(f"Error: Invalid X column '{x_column}'", file=sys.stderr)
    sys.exit(1)

x_data = df.loc[:, x_column]
if isinstance(x_data, pd.DataFrame):
    x_data = x_data.iloc[:, 0]

plt.figure(figsize=(12, 6))

if y_column and y_column in df.columns:
    y_data = df.loc[:, y_column]
    if isinstance(y_data, pd.DataFrame):
        y_data = y_data.iloc[:, 0]
    y_data = pd.to_numeric(y_data, errors="coerce")

    plot_df = pd.DataFrame({x_column: x_data, y_column: y_data}).dropna()
    if plot_df.empty:
        print("Error: No valid data after cleaning", file=sys.stderr)
        sys.exit(1)

    # Top 15 categories by mean Y value, so wide categorical columns
    # stay readable.
    agg = plot_df.groupby(x_column)[y_column].mean().nlargest(15).reset_index()

    sns.barplot(data=agg, x=x_column, y=y_column, color=final_color)
    plt.title(f"Average {y_column} by {x_column}")
    plt.xlabel(x_column)
    plt.ylabel(f"Mean {y_column}")
else:
    counts = x_data.value_counts().head(15)
    if counts.empty:
        print("Error: No valid categorical data", file=sys.stderr)
        sys.exit(1)

    sns.barplot(x=counts.index.astype(str), y=counts.values, color=final_color)
    plt.title(f"Value Counts of {x_column}")
    plt.xlabel(x_column)
    plt.ylabel("Count")

plt.xticks(rotation=45, ha="right")
plt.tight_layout()

timestamp = int(time.time())
filename = f"chart_{timestamp}.png"
current_dir = os.path.dirname(__file__)
save_path = os.path.abspath(os.path.join(current_dir, "../../backend/generated_charts", filename))
os.makedirs(os.path.dirname(save_path), exist_ok=True)

plt.savefig(save_path, dpi=150)
plt.close()

print(filename)
