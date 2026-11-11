"""Load the raw data file, and nothing else.

Purpose: read the raw CSV and fail fast, with a clear message, if the path is a
folder or the file is empty. Without this entry point, a wrong path or an empty
file would only show up as a confusing error in a later module.

Used by: main (it passes the raw data path from SETTINGS).
Next module: clean_data receives the DataFrame exactly as it was read.

Rule: read only. No cleaning, no date parsing, no column names.
"""

from pathlib import Path

import pandas as pd

from src import utils


def _check_not_a_folder(raw_data_path: Path) -> None:
    """Raise ValueError if the path points to a folder instead of a file."""
    if raw_data_path.is_dir():
        raise ValueError(
            f"Raw data path is a folder, not a file: {raw_data_path}. "
            "Check SETTINGS['paths']['raw_data']."
        )


def load_raw_data(raw_data_path: Path) -> pd.DataFrame:
    """Read the raw CSV untouched. Raise if the path is a folder, missing or the file is empty."""
    # TODO: replace print with logging (Session 10)
    print(f"Loading raw data: {raw_data_path}")
    raw_data_path = Path(raw_data_path)
    _check_not_a_folder(raw_data_path)
    try:
        df = utils.load_csv(raw_data_path)  # raises FileNotFoundError if the file is missing
    except pd.errors.EmptyDataError as error:  # a blank file has no columns at all
        raise ValueError(f"Raw data file is empty (no columns): {raw_data_path}.") from error
    if df.empty:  # a header-only file has columns but no rows
        raise ValueError(f"Raw data file is empty (no rows): {raw_data_path}. Check the file content.")
    return df
