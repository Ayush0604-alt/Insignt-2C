"""
Renders a histogram + KDE curve for one numeric column.

Usage: python histogram.py <file_path> <x_column> [color] [bins]
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
    print("Error: Usage: histogram.py <file_path> <x_column> [color] [bins]", file=sys.stderr)
    sys.exit(1)

file_path = sys.argv[1]
x_column = clean_column_name(sys.argv[2])
final_color = resolve_color(sys.argv[3] if len(sys.argv) > 3 else "")

try:
    bins = int(sys.argv[4]) if len(sys.argv) > 4 else 20
except ValueError:
    bins = 20

df = load_dataset(file_path)

if x_column not in df.columns:
    print(f"Error: Invalid column '{x_column}'", file=sys.stderr)
    sys.exit(1)

x_data = df.loc[:, x_column]
if isinstance(x_data, pd.DataFrame):
    x_data = x_data.iloc[:, 0]

x_data = pd.to_numeric(x_data, errors="coerce").dropna()

if x_data.empty:
    print("Error: No valid numeric data in column", file=sys.stderr)
    sys.exit(1)

plt.figure(figsize=(10, 6))
sns.histplot(x_data, kde=True, bins=bins, color=final_color)
plt.title(f"Distribution of {x_column}")
plt.xlabel(x_column)
plt.ylabel("Frequency")
plt.tight_layout()

timestamp = int(time.time())
filename = f"chart_{timestamp}.png"
current_dir = os.path.dirname(__file__)
save_path = os.path.abspath(os.path.join(current_dir, "../../backend/generated_charts", filename))
os.makedirs(os.path.dirname(save_path), exist_ok=True)

plt.savefig(save_path, dpi=150)
plt.close()

print(filename)
