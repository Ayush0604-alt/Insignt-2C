"""
Renders a correlation heatmap across every numeric column in the dataset.

Usage: python heatmap.py <file_path> [color]
Prints the saved chart's filename to stdout.
"""

import os
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.io_utils import load_dataset, resolve_cmap  # noqa: E402

if len(sys.argv) < 2:
    print("Error: Usage: heatmap.py <file_path> [color]", file=sys.stderr)
    sys.exit(1)

file_path = sys.argv[1]
final_cmap = resolve_cmap(sys.argv[2] if len(sys.argv) > 2 else "")

df = load_dataset(file_path)

numeric_df = df.select_dtypes(include=["number"])
if numeric_df.shape[1] < 2:
    print("Error: Need at least 2 numeric columns for a correlation heatmap", file=sys.stderr)
    sys.exit(1)

corr = numeric_df.corr()

plt.figure(figsize=(10, 8))
sns.heatmap(corr, annot=True, cmap=final_cmap, fmt=".2f")
plt.title("Correlation Heatmap")
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
