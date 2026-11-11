"""Tests for src/load_data.py: reading the raw CSV, failing fast on bad input."""

import pytest

from src.load_data import load_raw_data


def test_unit_load_raw_data_returns_expected_shape(tmp_path):
    """A small CSV loads untouched: same rows, same columns, same values."""
    csv_path = tmp_path / "raw.csv"
    csv_path.write_text("a,b\n1,x\n2,y\n3,z\n")

    df = load_raw_data(csv_path)

    assert df.shape == (3, 2)
    assert list(df.columns) == ["a", "b"]
    assert df.loc[0, "b"] == "x"


@pytest.mark.parametrize("content", ["", "a,b\n"], ids=["blank_file", "header_only"])
def test_unit_load_raw_data_empty_file_raises(tmp_path, content):
    """A file with no columns or no rows must fail early with a clear message."""
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text(content)

    with pytest.raises(ValueError, match="empty"):
        load_raw_data(csv_path)


def test_unit_load_raw_data_folder_raises(tmp_path):
    """A path that points to a folder, not a file, must fail with a clear message."""
    with pytest.raises(ValueError, match="folder"):
        load_raw_data(tmp_path)


def test_integration_load_raw_data_reads_file_written_by_utils(tmp_path):
    """A file written by utils.save_csv must come back identical through load_raw_data."""
    import pandas as pd  # imported here: only this test builds a DataFrame
    from src.utils import save_csv

    df = pd.DataFrame({"a": [1, 2, 3], "b": [0.5, 1.5, 2.5]})
    csv_path = tmp_path / "raw" / "data.csv"
    save_csv(df, csv_path)

    loaded = load_raw_data(csv_path)

    pd.testing.assert_frame_equal(loaded, df)

