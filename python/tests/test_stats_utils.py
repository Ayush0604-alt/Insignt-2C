"""
Unit tests for the statistical core (python/utils/stats_utils.py).

Run with: pytest python/tests -v
(from the repo root, with the python/ dependencies installed)
"""

import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.stats_utils import (  # noqa: E402
    categorical_column_stats,
    correlation_strength,
    data_quality_score,
    detect_datetime_columns,
    numeric_column_stats,
    top_correlations,
)


# ── numeric_column_stats ─────────────────────────────────────

def test_numeric_column_stats_basic_values():
    series = pd.Series([10, 20, 30, 40, 50])
    stats = numeric_column_stats(series)

    assert stats["mean"] == 30
    assert stats["median"] == 30
    assert stats["min"] == 10
    assert stats["max"] == 50
    assert stats["outlier_count"] == 0


def test_numeric_column_stats_detects_outlier():
    # 1000 is far outside the IQR range of the rest of the values.
    series = pd.Series([10, 12, 11, 13, 12, 11, 10, 1000])
    stats = numeric_column_stats(series)

    assert stats["outlier_count"] == 1
    assert stats["outlier_percentage"] > 0


def test_numeric_column_stats_empty_series_returns_empty_dict():
    series = pd.Series([None, None, None])
    assert numeric_column_stats(series) == {}


def test_numeric_column_stats_ignores_non_numeric_junk():
    series = pd.Series(["10", "20", "abc", "40"])
    stats = numeric_column_stats(series)

    # "abc" should be coerced to NaN and dropped, not crash the function.
    assert stats["mean"] == pytest.approx(23.33, rel=0.01)


# ── categorical_column_stats ─────────────────────────────────

def test_categorical_stats_flags_identifier_column():
    series = pd.Series([f"user_{i}" for i in range(100)])
    stats = categorical_column_stats(series)

    assert stats["unique_values"] == 100
    assert stats["is_likely_identifier"] is True


def test_categorical_stats_does_not_flag_low_cardinality_column():
    series = pd.Series(["Sales", "Sales", "Engineering", "Sales", "Marketing"])
    stats = categorical_column_stats(series)

    assert stats["is_likely_identifier"] is False
    assert stats["most_common"] == "Sales"
    assert stats["most_common_count"] == 3


# ── correlation_strength ──────────────────────────────────────

@pytest.mark.parametrize("value,expected", [
    (0.9, "strong"),
    (-0.85, "strong"),
    (0.5, "moderate"),
    (0.3, "weak"),
    (0.05, "negligible"),
])
def test_correlation_strength_buckets(value, expected):
    assert correlation_strength(value) == expected


# ── top_correlations ───────────────────────────────────────────

def test_top_correlations_orders_by_absolute_strength():
    df = pd.DataFrame({
        "a": [1, 2, 3, 4, 5],
        "b": [1, 2, 3, 4, 5],       # perfectly correlated with a
        "c": [5, 3, 4, 1, 2],       # weak/no clear relationship
    })
    results = top_correlations(df, ["a", "b", "c"], top_n=2)

    assert len(results) == 2
    assert results[0]["correlation"] == pytest.approx(1.0)
    assert results[0]["strength"] == "strong"


def test_top_correlations_returns_empty_for_single_column():
    df = pd.DataFrame({"a": [1, 2, 3]})
    assert top_correlations(df, ["a"]) == []


# ── data_quality_score ─────────────────────────────────────────

def test_data_quality_score_perfect_for_clean_data():
    assert data_quality_score(rows=100, missing_cells=0, total_cells=500, duplicate_rows=0) == 100


def test_data_quality_score_penalizes_missing_and_duplicates():
    score = data_quality_score(rows=100, missing_cells=100, total_cells=500, duplicate_rows=20)
    assert 0 <= score < 100


def test_data_quality_score_handles_empty_dataset():
    assert data_quality_score(rows=0, missing_cells=0, total_cells=0, duplicate_rows=0) == 0


# ── detect_datetime_columns ─────────────────────────────────────

def test_detect_datetime_columns_finds_iso_dates():
    df = pd.DataFrame({
        "join_date": ["2021-01-15", "2020-03-22", "2019-07-01", "2018-11-30"],
        "name": ["Alice", "Bob", "Charlie", "Dana"],
    })
    result = detect_datetime_columns(df, ["join_date", "name"])
    assert "join_date" in result
    assert "name" not in result
