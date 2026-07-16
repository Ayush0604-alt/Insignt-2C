"""
Renders a scatter plot between two numeric columns, with a fitted trend
line and the Pearson correlation coefficient annotated on the chart.

Usage: python scatter_plot.py <file_path> <x_column> <y_column> [color]
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

if len(sys.argv) < 4:
    print("Error: Usage: scatter_plot.py <file_path> <x_column> <y_column> [color]", file=sys.stderr)
    sys.exit(1)

file_path = sys.argv[1]
x_column = clean_column_name(sys.argv[2])
y_column = clean_column_name(sys.argv[3])
final_color = resolve_color(sys.argv[4] if len(sys.argv) > 4 else "")

df = load_dataset(file_path)

if x_column not in df.columns:
    print(f"Error: Invalid X column '{x_column}'", file=sys.stderr)
    sys.exit(1)
if y_column not in df.columns:
    print(f"Error: Invalid Y column '{y_column}'", file=sys.stderr)
    sys.exit(1)

x_data = df.loc[:, x_column]
y_data = df.loc[:, y_column]
if isinstance(x_data, pd.DataFrame):
    x_data = x_data.iloc[:, 0]
if isinstance(y_data, pd.DataFrame):
    y_data = y_data.iloc[:, 0]

x_data = pd.to_numeric(x_data, errors="coerce")
y_data = pd.to_numeric(y_data, errors="coerce")

plot_df = pd.DataFrame({x_column: x_data, y_column: y_data}).dropna()

if plot_df.empty:
    print("Error: No valid numeric data after cleaning", file=sys.stderr)
    sys.exit(1)

plt.figure(figsize=(10, 6))
sns.regplot(
    data=plot_df,
    x=x_column,
    y=y_column,
    color=final_color,
    scatter_kws={"alpha": 0.7},
    line_kws={"color": "#111827", "linewidth": 1.5},
)

# Annotate the correlation so the chart tells the same story as the
# insights panel, not just a cloud of points.
if len(plot_df) > 1:
    correlation = plot_df[x_column].corr(plot_df[y_column])
    plt.annotate(
        f"r = {correlation:.2f}",
        xy=(0.02, 0.96),
        xycoords="axes fraction",
        fontsize=11,
        fontweight="bold",
        va="top",
    )

plt.title(f"{y_column} vs {x_column}")
plt.xlabel(x_column)
plt.ylabel(y_column)
plt.tight_layout()

timestamp = int(time.time())
filename = f"chart_{timestamp}.png"
save_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../backend/generated_charts", filename)
)
os.makedirs(os.path.dirname(save_path), exist_ok=True)

plt.savefig(save_path, dpi=150)
plt.close()

print(filename)
