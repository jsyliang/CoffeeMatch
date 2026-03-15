# pylint: disable=missing-module-docstring, missing-function-docstring
import pandas as pd
import pytest

from scripts import prepare_data


def test_ensure_directories_creates_processed_dir(tmp_path, monkeypatch):
    """It should create the processed output directory if it does not exist."""
    processed_dir = tmp_path / "processed"

    monkeypatch.setattr(prepare_data, "PROCESSED_DIR", processed_dir)

    prepare_data.ensure_directories()

    assert processed_dir.exists()
    assert processed_dir.is_dir()


def test_load_excel_file_reads_existing_excel_file(tmp_path):
    """It should load an existing Excel file into a DataFrame."""
    input_path = tmp_path / "input.xlsx"
    expected = pd.DataFrame(
        {
            "roaster": ["Roaster A"],
            "product_name": ["Coffee A"],
        }
    )
    expected.to_excel(input_path, index=False)

    result = prepare_data.load_excel_file(input_path)

    pd.testing.assert_frame_equal(result, expected)


def test_load_excel_file_raises_for_missing_file(tmp_path):
    """It should raise FileNotFoundError when the Excel file is missing."""
    missing_path = tmp_path / "missing.xlsx"

    with pytest.raises(FileNotFoundError, match="Missing input file"):
        prepare_data.load_excel_file(missing_path)


def test_standardize_column_names_returns_cleaned_copy():
    """It should lowercase, trim, and underscore-separate column names."""
    raw_df = pd.DataFrame(
        {
            " Roaster ": ["A"],
            "Product Name": ["Coffee A"],
            "Price Per Oz": [1.5],
        }
    )

    result = prepare_data.standardize_column_names(raw_df)

    assert list(result.columns) == ["roaster", "product_name", "price_per_oz"]
    assert list(raw_df.columns) == [" Roaster ", "Product Name", "Price Per Oz"]


def test_remove_unused_columns_drops_tags_when_present():
    """It should drop the tags column when it exists."""
    raw_df = pd.DataFrame(
        {
            "product_name": ["Coffee A"],
            "tags": ["berry, floral"],
        }
    )

    result = prepare_data.remove_unused_columns(raw_df)

    assert "tags" not in result.columns
    assert "tags" in raw_df.columns


def test_remove_unused_columns_leaves_df_unchanged_when_tags_missing():
    """It should not fail when the tags column is absent."""
    raw_df = pd.DataFrame(
        {
            "product_name": ["Coffee A"],
            "roaster": ["Roaster A"],
        }
    )

    result = prepare_data.remove_unused_columns(raw_df)

    pd.testing.assert_frame_equal(result, raw_df)


def test_create_product_key_builds_key_from_roaster_and_product_name():
    """It should create product_key using trimmed roaster and product name."""
    raw_df = pd.DataFrame(
        {
            "roaster": [" Roaster A "],
            "product_name": [" Coffee A "],
        }
    )

    result = prepare_data.create_product_key(raw_df)

    assert result["product_key"].tolist() == ["Roaster A | Coffee A"]


def test_save_csv_writes_dataframe_to_csv(tmp_path):
    """It should save a DataFrame to the requested CSV path."""
    output_path = tmp_path / "output.csv"
    expected = pd.DataFrame(
        {
            "product_key": ["p1"],
            "value": [1],
        }
    )

    prepare_data.save_csv(expected, output_path)

    result = pd.read_csv(output_path)
    pd.testing.assert_frame_equal(result, expected)


def test_main_runs_full_pipeline_and_writes_outputs(tmp_path, monkeypatch, capsys):
    """It should run the full preparation pipeline and write both processed CSV files."""
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()

    products_input = raw_dir / "Product_Information.xlsx"
    reviews_input = raw_dir / "Reviews_and_Tasting_Notes.xlsx"
    products_output = processed_dir / "products_clean.csv"
    reviews_output = processed_dir / "reviews_clean.csv"

    products_df = pd.DataFrame(
        {
            "Roaster": ["Roaster A"],
            "Product Name": ["Coffee A"],
            "Tags": ["berry"],
        }
    )
    reviews_df = pd.DataFrame(
        {
            "Product Name": ["Coffee A"],
            "Review Text": ["Excellent"],
            "Tasting Notes": ["berry"],
        }
    )

    products_df.to_excel(products_input, index=False)
    reviews_df.to_excel(reviews_input, index=False)

    monkeypatch.setattr(prepare_data, "RAW_DIR", raw_dir)
    monkeypatch.setattr(prepare_data, "PROCESSED_DIR", processed_dir)
    monkeypatch.setattr(prepare_data, "PRODUCTS_INPUT", products_input)
    monkeypatch.setattr(prepare_data, "REVIEWS_INPUT", reviews_input)
    monkeypatch.setattr(prepare_data, "PRODUCTS_OUTPUT", products_output)
    monkeypatch.setattr(prepare_data, "REVIEWS_OUTPUT", reviews_output)

    prepare_data.main()

    assert products_output.exists()
    assert reviews_output.exists()

    products_result = pd.read_csv(products_output)
    reviews_result = pd.read_csv(reviews_output)

    assert list(products_result.columns) == ["roaster", "product_name", "product_key"]
    assert products_result["product_key"].tolist() == ["Roaster A | Coffee A"]

    assert list(reviews_result.columns) == ["product_name", "review_text", "tasting_notes"]

    captured = capsys.readouterr()
    assert "Saved products data to" in captured.out
    assert "Saved reviews data to" in captured.out
    assert "Data preparation complete." in captured.out
