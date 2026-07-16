"""
Shared helpers used by every script under python/.

Every analysis/visualization script needs to (a) load a CSV/XLSX/JSON file
into a DataFrame and (b) resolve a chart color name to a hex value. That
logic used to be copy-pasted into each script individually; it now lives
here so there is exactly one place to fix a bug or add a file format.
"""

import sys

import pandas as pd

SUPPORTED_EXTENSIONS = (".csv", ".xlsx", ".json")

# Central palette so every chart script (and the frontend color picker)
# stays in sync.
COLOR_MAP = {
    "orange": "#ea580c",
    "blue": "#2563eb",
    "green": "#16a34a",
    "red": "#dc2626",
    "purple": "#9333ea",
    "black": "#111827",
    "pink": "#db2777",
    "yellow": "#ca8a04",
    "brown": "#92400e",
    "gray": "#4b5563",
}

DEFAULT_COLOR = "orange"

# Matplotlib colormap names for the heatmap script - a different concept
# from COLOR_MAP above (which holds flat hex colors), so kept separate.
CMAP_MAP = {
    "orange": "Oranges",
    "blue": "Blues",
    "green": "Greens",
    "red": "Reds",
    "purple": "Purples",
    "gray": "Greys",
}


def resolve_cmap(name: str) -> str:
    """Map a color name to its matplotlib colormap, falling back to the default."""
    key = (name or "").strip().lower()
    return CMAP_MAP.get(key, CMAP_MAP[DEFAULT_COLOR])


def load_dataset(file_path: str) -> pd.DataFrame:
    """Load a CSV, XLSX, or JSON file into a DataFrame.

    Exits with a clear, single-line error message on stdout (so the Node
    layer can surface it to the user) if the format isn't supported or the
    file can't be parsed.
    """
    try:
        if file_path.endswith(".csv"):
            return pd.read_csv(file_path)
        if file_path.endswith(".xlsx"):
            return pd.read_excel(file_path)
        if file_path.endswith(".json"):
            return pd.read_json(file_path)
    except Exception as exc:  # noqa: BLE001 - surface any parse failure cleanly
        print(f"Error: Could not read '{file_path}': {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Error: Unsupported file format. Expected one of {SUPPORTED_EXTENSIONS}", file=sys.stderr)
    sys.exit(1)


def resolve_color(name: str) -> str:
    """Map a color name to its hex value, falling back to the default."""
    key = (name or "").strip().lower()
    return COLOR_MAP.get(key, COLOR_MAP[DEFAULT_COLOR])


def clean_column_name(col: str) -> str:
    """Strip stray brackets/quotes that can leak in from form submissions."""
    return (col or "").replace("[", "").replace("]", "").replace("'", "").replace('"', "").strip()
