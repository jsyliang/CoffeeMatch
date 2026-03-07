"""
Purpose:
Convert raw Excel datasets into cleaned CSV files used by the CoffeeMatch
recommendation engine.

Typical workflow:
- Raw Excel files live in data/raw/
- This script generates cleaned CSV files in data/processed/

The processed CSV files are committed to the repository to ensure
reproducibility and simplify project setup.
"""

from pathlib import Path
import pandas as pd


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

PRODUCTS_INPUT = RAW_DIR / "Product_Information.xlsx"
REVIEWS_INPUT = RAW_DIR / "Reviews_and_Tasting_Notes.xlsx"

PRODUCTS_OUTPUT = PROCESSED_DIR / "products_clean.csv"
REVIEWS_OUTPUT = PROCESSED_DIR / "reviews_clean.csv"


def ensure_directories() -> None:
    """Create required output directories if they do not already exist."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_excel_file(file_path: Path) -> pd.DataFrame:
    """
    Load an Excel file into a pandas DataFrame.

    Parameters
    ----------
    file_path : Path
        Path to the Excel file.

    Returns
    -------
    pd.DataFrame
        Loaded DataFrame.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Missing input file: {file_path}")

    return pd.read_excel(file_path)


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize DataFrame column names to lowercase with underscores.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame with standardized column names.
    """
    cleaned_df = df.copy()
    cleaned_df.columns = (
        cleaned_df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )
    return cleaned_df


def remove_unused_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove columns that are not needed for the recommendation system.
    """
    cleaned_df = df.copy()

    cleaned_df = cleaned_df.drop(
        columns=["tags"],
        errors="ignore"
    )

    return cleaned_df


def save_csv(df: pd.DataFrame, output_path: Path) -> None:
    """
    Save a DataFrame to CSV.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to save.
    output_path : Path
        Destination CSV path.
    """
    df.to_csv(output_path, index=False)


def main() -> None:
    """Run the raw Excel to processed CSV pipeline."""
    ensure_directories()

    products_df = load_excel_file(PRODUCTS_INPUT)
    reviews_df = load_excel_file(REVIEWS_INPUT)

    products_df = standardize_column_names(products_df)
    reviews_df = standardize_column_names(reviews_df)

    products_df = remove_unused_columns(products_df)

    save_csv(products_df, PRODUCTS_OUTPUT)
    save_csv(reviews_df, REVIEWS_OUTPUT)

    print(f"Saved products data to {PRODUCTS_OUTPUT}")
    print(f"Saved reviews data to {REVIEWS_OUTPUT}")
    print("Data preparation complete.")


if __name__ == "__main__":
    main()
