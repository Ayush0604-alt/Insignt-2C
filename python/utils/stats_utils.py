"""
Statistical helpers used by dataset_summary.py, insight_generator.py, and
chart_recommender.py.

This is the analytical core of the project: it goes beyond mean/median/mode
to compute the things an actual EDA pass looks at - spread, skew, IQR-based
outliers, correlation strength between column pairs, and a single rollup
"data quality score" for the dataset.
"""

import pandas as pd


def numeric_column_stats(series: pd.Series) -> dict:
    """Descriptive stats + IQR outlier detection for one numeric column."""
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return {}

    q1, q3 = clean.quantile(0.25), clean.quantile(0.75)
    iqr = q3 - q1
    lower_fence, upper_fence = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outliers = clean[(clean < lower_fence) | (clean > upper_fence)]

    return {
        "mean": round(float(clean.mean()), 2),
        "median": round(float(clean.median()), 2),
        "std_dev": round(float(clean.std()), 2) if len(clean) > 1 else 0.0,
        "min": round(float(clean.min()), 2),
        "max": round(float(clean.max()), 2),
        "q1": round(float(q1), 2),
        "q3": round(float(q3), 2),
        "iqr": round(float(iqr), 2),
        "skewness": round(float(clean.skew()), 2) if len(clean) > 2 else 0.0,
        "outlier_count": int(len(outliers)),
        "outlier_percentage": round(len(outliers) / len(clean) * 100, 2),
    }


def categorical_column_stats(series: pd.Series) -> dict:
    """Cardinality + top-value stats for one categorical column."""
    clean = series.dropna()
    if clean.empty:
        return {}

    value_counts = clean.value_counts()
    unique_ratio = clean.nunique() / len(clean)

    return {
        "unique_values": int(clean.nunique()),
        "most_common": str(value_counts.index[0]),
        "most_common_count": int(value_counts.iloc[0]),
        "most_common_percentage": round(float(value_counts.iloc[0] / len(clean) * 100), 2),
        # A column where almost every value is unique (e.g. an ID/email
        # column) isn't meaningful for a bar/pie chart - flagging it lets
        # the insight + recommendation engines steer users away from it.
        "is_likely_identifier": bool(unique_ratio > 0.95),
    }


def correlation_strength(value: float) -> str:
    """Bucket a Pearson correlation coefficient into a plain-English label."""
    magnitude = abs(value)
    if magnitude >= 0.7:
        return "strong"
    if magnitude >= 0.4:
        return "moderate"
    if magnitude >= 0.2:
        return "weak"
    return "negligible"


def top_correlations(df: pd.DataFrame, numeric_cols: list, top_n: int = 3) -> list:
    """Return the top N strongest numeric column-pair correlations."""
    if len(numeric_cols) < 2:
        return []

    corr_matrix = df[numeric_cols].corr(numeric_only=True)
    pairs = []

    for i, col_a in enumerate(numeric_cols):
        for col_b in numeric_cols[i + 1:]:
            value = corr_matrix.loc[col_a, col_b]
            if pd.isna(value):
                continue
            rounded_value = round(float(value), 2)
            pairs.append({
                "column_a": col_a,
                "column_b": col_b,
                "correlation": rounded_value,
                # Classify off the same rounded number we display, so a
                # value shown as "0.40" can never be labeled "weak"
                # (which the unrounded 0.399... would otherwise trigger).
                "strength": correlation_strength(rounded_value),
            })

    pairs.sort(key=lambda pair: abs(pair["correlation"]), reverse=True)
    return pairs[:top_n]


def data_quality_score(rows: int, missing_cells: int, total_cells: int, duplicate_rows: int) -> int:
    """A simple 0-100 rollup score: penalize missing data and duplicate rows.

    Missingness is weighted more heavily (up to 60 points) than duplicates
    (up to 40 points) since missing values usually block more analyses than
    a handful of duplicate rows do.
    """
    if rows == 0 or total_cells == 0:
        return 0

    missing_penalty = (missing_cells / total_cells) * 60
    duplicate_penalty = (duplicate_rows / rows) * 40
    score = 100 - missing_penalty - duplicate_penalty
    return max(0, round(score))


def detect_datetime_columns(df: pd.DataFrame, candidate_cols: list) -> list:
    """Best-effort detection of columns that are actually dates/timestamps.

    Only checks object/string columns that aren't already numeric, and
    requires most values to parse successfully to avoid false positives.
    """
    datetime_cols = []
    for col in candidate_cols:
        sample = df[col].dropna().head(50)
        if sample.empty:
            continue
        parsed = pd.to_datetime(sample, errors="coerce", format="mixed")
        if parsed.notna().mean() > 0.9:
            datetime_cols.append(col)
    return datetime_cols
