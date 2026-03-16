# pylint: disable=missing-module-docstring, missing-function-docstring

from pathlib import Path

import pandas as pd
import pytest

from coffeematch_core.data_loader import (
    validate_required_columns,
    _check_file_exists,
    load_products,
    load_reviews,
    load_product_info,
    load_datasets
)


def test_validate_required_columns_passes_when_all_columns_exist():
    df = pd.DataFrame(
        {
            "product_key": ["p1"],
            "product_name": ["Test Coffee"],
        }
    )

    validate_required_columns(
        df=df,
        required_columns=["product_key", "product_name"],
        dataset_name="Products",
    )


def test_validate_required_columns_raises_for_missing_columns():
    df = pd.DataFrame(
        {
            "product_key": ["p1"],
        }
    )

    with pytest.raises(ValueError, match="missing required columns"):
        validate_required_columns(
            df=df,
            required_columns=["product_key", "product_name"],
            dataset_name="Products",
        )


def test_check_file_exists_returns_path_when_file_exists(tmp_path):
    file_path = tmp_path / "sample.csv"
    file_path.write_text("col1,col2\n1,2\n", encoding="utf-8")

    result = _check_file_exists(file_path)

    assert result == Path(file_path)


def test_check_file_exists_raises_for_missing_file(tmp_path):
    missing_file = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError, match="Missing processed data file"):
        _check_file_exists(missing_file)


def test_load_products_reads_valid_csv(tmp_path):
    df = pd.DataFrame(
        {
            "product_key": ["p1"],
            "roaster": ["Test Roaster"],
            "product_name": ["Test Coffee"],
            "origin": ["Ethiopia"],
            "roast_type": ["Medium Roast"],
            "size": ["12 oz"],
            "size_oz": [12],
            "price_numeric": [18],
            "price_per_oz": [1.5],
            "hearts": [10],
            "total_reviews": [5],
            "heart_percentage": [0.9],
            "has_reviews": [True],
            "decaf": [False],
            "blend": [False],
            "single_origin": [True],
            "available_ground": [True],
            "url": ["example.com"],
        }
    )

    csv_file = tmp_path / "products.csv"
    df.to_csv(csv_file, index=False)

    result = load_products(csv_file)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert result.iloc[0]["product_key"] == "p1"


def test_load_reviews_reads_valid_csv(tmp_path):
    df = pd.DataFrame(
        {
            "product_name": ["Test Coffee"],
            "sentiment": ["positive"],
            "brewing_method": ["pour over"],
            "review_text": ["Very good coffee"],
            "date": ["2024-01-01"],
            "tasting_notes": ["chocolate"],
        }
    )

    csv_file = tmp_path / "reviews.csv"
    df.to_csv(csv_file, index=False)

    result = load_reviews(csv_file)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert result.iloc[0]["product_name"] == "Test Coffee"


def test_load_product_info_reads_valid_csv_and_applies_na_values(tmp_path):
    df = pd.DataFrame(
        {
            "product_key": ["p1"],
            "cafe_name": ["Test Cafe"],
            "cafe_address": ["No_cafe_identified_in_King"],
            "cafe_city": ["Seattle"],
            "zip_code": ["98101"],
            "longitude": [-122.33],
            "latitude": [47.61],
        }
    )

    csv_file = tmp_path / "product_info.csv"
    df.to_csv(csv_file, index=False)

    result = load_product_info(csv_file)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert pd.isna(result.iloc[0]["cafe_address"])

def test_load_datasets_returns_all_three_dataframes(tmp_path):
    products_df = pd.DataFrame(
        {
            "product_key": ["p1"],
            "roaster": ["Test Roaster"],
            "product_name": ["Test Coffee"],
            "origin": ["Ethiopia"],
            "roast_type": ["Medium Roast"],
            "size": ["12 oz"],
            "size_oz": [12],
            "price_numeric": [18],
            "price_per_oz": [1.5],
            "hearts": [10],
            "total_reviews": [5],
            "heart_percentage": [0.9],
            "has_reviews": [True],
            "decaf": [False],
            "blend": [False],
            "single_origin": [True],
            "available_ground": [True],
            "url": ["example.com"],
        }
    )

    reviews_df = pd.DataFrame(
        {
            "product_name": ["Test Coffee"],
            "sentiment": ["positive"],
            "brewing_method": ["pour over"],
            "review_text": ["Very good coffee"],
            "date": ["2024-01-01"],
            "tasting_notes": ["chocolate"],
        }
    )

    product_info_df = pd.DataFrame(
        {
            "product_key": ["p1"],
            "cafe_name": ["Test Cafe"],
            "cafe_address": ["123 Main St"],
            "cafe_city": ["Seattle"],
            "zip_code": ["98101"],
            "longitude": [-122.33],
            "latitude": [47.61],
        }
    )

    products_file = tmp_path / "products.csv"
    reviews_file = tmp_path / "reviews.csv"
    product_info_file = tmp_path / "product_info.csv"

    products_df.to_csv(products_file, index=False)
    reviews_df.to_csv(reviews_file, index=False)
    product_info_df.to_csv(product_info_file, index=False)

    products, reviews, product_info = load_datasets(
        products_path=products_file,
        reviews_path=reviews_file,
        product_info_path=product_info_file,
    )

    assert len(products) == 1
    assert len(reviews) == 1
    assert len(product_info) == 1
