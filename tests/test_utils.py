"""Tests for src/utils.py: generic file helpers (CSV and model read/write)."""

import pandas as pd
import pytest

from src.utils import load_csv, load_model, save_csv, save_model


def _make_df() -> pd.DataFrame:
    """Tiny DataFrame with integers, floats and text, used by the CSV tests."""
    return pd.DataFrame({"a": [1, 2, 3], "b": [0.5, 1.5, 2.5], "c": ["x", "y", "z"]})


def test_unit_save_then_load_csv_returns_same_data(tmp_path):
    """Write a DataFrame and read it back: the content must be identical."""
    df = _make_df()
    filepath = tmp_path / "nested" / "out.csv"  # the parent folder does not exist yet

    save_csv(df, filepath)
    loaded = load_csv(filepath)

    pd.testing.assert_frame_equal(loaded, df)


def test_unit_load_csv_missing_file_raises(tmp_path):
    """A path that does not exist must fail early, with the path in the message."""
    missing = tmp_path / "does_not_exist.csv"

    with pytest.raises(FileNotFoundError, match="does_not_exist.csv"):
        load_csv(missing)


def test_integration_save_then_load_model_gives_same_predictions(tmp_path):
    """A model saved to disk and loaded back must predict exactly like the original."""
    from sklearn.linear_model import LinearRegression  # imported here: only this test needs it

    X = pd.DataFrame({"x": [1.0, 2.0, 3.0, 4.0]})
    y = [2.0, 4.0, 6.0, 8.0]
    model = LinearRegression().fit(X, y)
    filepath = tmp_path / "models" / "model.joblib"  # the parent folder does not exist yet

    save_model(model, filepath)
    reloaded = load_model(filepath)

    assert reloaded.predict(X).tolist() == model.predict(X).tolist()
