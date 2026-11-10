"""Generic file helpers shared by the whole pipeline.

Purpose: read and write CSV files and model files in one place, so every module
fails in the same clear way and none of them repeats this code (DRY).

Used by: load_data (read), main (write processed data and predictions),
infer and main (save and load the model).

Rule: this file stays generic. No column names, no business logic.
"""

from pathlib import Path

import joblib
import pandas as pd


def load_csv(filepath: Path) -> pd.DataFrame:
    """Read a CSV file into a DataFrame. Raise FileNotFoundError if the file is missing."""
    # TODO: replace print with logging (Session 10)
    print(f"Loading CSV: {filepath}")
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"CSV file not found: {filepath}. Check the path in SETTINGS['paths'].")
    return pd.read_csv(filepath)


def save_csv(df: pd.DataFrame, filepath: Path) -> None:
    """Write a DataFrame to a CSV file, creating parent folders, without the index."""
    # TODO: replace print with logging (Session 10)
    print(f"Saving CSV: {filepath}")
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=False)


def save_model(model, filepath: Path) -> None:
    """Save a trained model to disk with joblib, creating parent folders."""
    # TODO: replace print with logging (Session 10)
    print(f"Saving model: {filepath}")
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, filepath)


def load_model(filepath: Path):
    """Load a model saved with save_model. Raise FileNotFoundError if the file is missing."""
    # TODO: replace print with logging (Session 10)
    print(f"Loading model: {filepath}")
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Model file not found: {filepath}. Check the path in SETTINGS['paths'].")
    return joblib.load(filepath)
