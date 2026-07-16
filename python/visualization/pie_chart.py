"""
Renders a pie chart of the top 10 category proportions for one column.

Usage: python pie_chart.py <file_path> <x_column>
Prints the saved chart's filename to stdout.
"""

import os
import sys
import time

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["text.usetex"] = False
import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.io_utils import clean_column_name, load_dataset  # noqa: E402

if len(sys.argv) < 3:
    print("Error: Usage: pie_chart.py <file_path> <x_column>", file=sys.stderr)
    sys.exit(1)

file_path = sys.argv[1]
x_column = clean_column_name(sys.argv[2])

df = load_dataset(file_path)

if x_column not in df.columns:
    print(f"Error: Invalid column '{x_column}'", file=sys.stderr)
    sys.exit(1)

counts = df[x_column].value_counts().head(10)
if counts.empty:
    print("Error: No valid categorical data", file=sys.stderr)
    sys.exit(1)

# Strip characters that can break matplotlib's text rendering.
safe_labels = [
    str(label).replace("$", "").replace("\\", "").replace("\n", " ")
    for label in counts.index
]

colors = sns.color_palette("pastel", len(counts))

plt.figure(figsize=(8, 8))
plt.pie(counts, labels=safe_labels, autopct="%1.1f%%", colors=colors)
plt.title(f"Top Categories of {x_column}")
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
