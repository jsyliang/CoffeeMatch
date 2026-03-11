"""
Load and validate processed CoffeeMatch datasets for downstream feature
engineering and recommendation modules.

This module provides the runtime entry point for cleaned product and review
data stored in data/processed/.
"""

from pathlib import Path
import pandas as pd

from .schemas import PRODUCT_REQUIRED_COLUMNS, REVIEW_REQUIRED_COLUMNS


DATA_DIR = Path("data/processed")
PRODUCTS_FILE = DATA_DIR / "products_clean.csv"
REVIEWS_FILE = DATA_DIR / "reviews_clean.csv"


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: list[str],
    dataset_name: str,
) -> None:
    """
    Validate that a DataFrame contains all required columns.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to validate.
    required_columns : list[str]
        Columns that must be present.
    dataset_name : str
        Human-readable dataset name for error messages.

    Raises
    ------
    ValueError
        If one or more required columns are missing.
    """
    missing_columns = sorted(set(required_columns) - set(df.columns))
    if missing_columns:
        missing_str = ", ".join(missing_columns)
        raise ValueError(
            f"{dataset_name} data is missing required columns: {missing_str}"
        )


def _check_file_exists(file_path: Path | str) -> Path:
    """
    Ensure a processed data file exists before loading.

    Parameters
    ----------
    file_path : Path | str
        File path to check.

    Returns
    -------
    Path
        Resolved Path object.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Missing processed data file: {path}")
    return path


def load_products(file_path: Path | str = PRODUCTS_FILE) -> pd.DataFrame:
    """
    Load and validate processed product data.

    Parameters
    ----------
    file_path : Path | str, default=PRODUCTS_FILE
        Path to the processed products CSV.

    Returns
    -------
    pd.DataFrame
        Validated products DataFrame.
    """
    path = _check_file_exists(file_path)
    products = pd.read_csv(path)

    validate_required_columns(
        df=products,
        required_columns=PRODUCT_REQUIRED_COLUMNS,
        dataset_name="Products",
    )

    return products


def load_reviews(file_path: Path | str = REVIEWS_FILE) -> pd.DataFrame:
    """
    Load and validate processed review data.

    Parameters
    ----------
    file_path : Path | str, default=REVIEWS_FILE
        Path to the processed reviews CSV.

    Returns
    -------
    pd.DataFrame
        Validated reviews DataFrame.
    """
    path = _check_file_exists(file_path)
    reviews = pd.read_csv(path)

    validate_required_columns(
        df=reviews,
        required_columns=REVIEW_REQUIRED_COLUMNS,
        dataset_name="Reviews",
    )

    return reviews


def load_datasets(
    products_path: Path | str = PRODUCTS_FILE,
    reviews_path: Path | str = REVIEWS_FILE,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load both processed CoffeeMatch datasets.

    Parameters
    ----------
    products_path : Path | str, default=PRODUCTS_FILE
        Path to the processed products CSV.
    reviews_path : Path | str, default=REVIEWS_FILE
        Path to the processed reviews CSV.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        Products DataFrame and reviews DataFrame.
    """
    products = load_products(products_path)
    reviews = load_reviews(reviews_path)
    return products, reviews
