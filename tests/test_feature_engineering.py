# pylint: disable=missing-module-docstring, missing-function-docstring
import math
import pandas as pd
import pytest

from coffeematch_core.feature_engineering import (
    classify_size_tier,
    compute_adjustment_factors,
    encode_roast_membership,
    build_feature_table,
    validate_feature_columns,
    select_reference_rows
)


@pytest.mark.parametrize(
    ("size_oz", "expected"),
    [
        (10, "standard"),
        (12, "standard"),
        (16, "standard"),
        (24, "mid_bulk"),
        (28, "mid_bulk"),
        (32, "mid_bulk"),
        (80, "large_bulk"),
        (96, "large_bulk"),
        (8, "other"),
        (20, "other"),
        (40, "other"),
    ],
)
def test_classify_size_tier_returns_expected_label(size_oz, expected):
    """It should classify bag sizes into the correct size tier."""
    assert classify_size_tier(size_oz) == expected


def test_classify_size_tier_includes_boundary_values():
    """It should include threshold endpoints in the intended tier ranges."""
    assert classify_size_tier(10) == "standard"
    assert classify_size_tier(16) == "standard"
    assert classify_size_tier(24) == "mid_bulk"
    assert classify_size_tier(32) == "mid_bulk"
    assert classify_size_tier(80) == "large_bulk"


def test_encode_roast_membership_adds_expected_membership_columns():
    """It should map roast labels to the correct overlap-aware membership flags."""
    products_df = pd.DataFrame(
        {
            "roast_type": [
                "Light Roast",
                "Light-Medium Roast",
                "Medium Roast",
                "Medium-Dark Roast",
                "Dark Roast",
                "Unspecified",
                None,
            ]
        }
    )

    result = encode_roast_membership(products_df)

    expected = pd.DataFrame(
        {
            "roast_light": [1, 1, 0, 0, 0, 0, 0],
            "roast_medium": [0, 1, 1, 1, 0, 0, 0],
            "roast_dark": [0, 0, 0, 1, 1, 0, 0],
            "roast_unknown": [0, 0, 0, 0, 0, 1, 1],
        }
    )

    pd.testing.assert_series_equal(
        result["roast_light"],
        expected["roast_light"],
        check_names=False,
    )
    pd.testing.assert_series_equal(
        result["roast_medium"],
        expected["roast_medium"],
        check_names=False,
    )
    pd.testing.assert_series_equal(
        result["roast_dark"],
        expected["roast_dark"],
        check_names=False,
    )
    pd.testing.assert_series_equal(
        result["roast_unknown"],
        expected["roast_unknown"],
        check_names=False,
    )


def test_encode_roast_membership_preserves_original_columns():
    """It should return a copy with new roast columns without changing input values."""
    products_df = pd.DataFrame(
        {
            "product_key": ["p1", "p2"],
            "roast_type": ["Light Roast", "Dark Roast"],
        }
    )

    result = encode_roast_membership(products_df)

    assert list(result["product_key"]) == ["p1", "p2"]
    assert list(result["roast_type"]) == ["Light Roast", "Dark Roast"]


def test_compute_adjustment_factors_returns_expected_ratios():
    """It should compute normalization factors relative to the standard tier."""
    tier_medians = {
        "standard": 2.0,
        "mid_bulk": 1.0,
        "large_bulk": 0.5,
        "other": 3.0,
    }

    result = compute_adjustment_factors(tier_medians)

    assert result["standard"] == 1.0
    assert result["other"] == 1.0
    assert result["mid_bulk"] == 2.0
    assert result["large_bulk"] == 4.0


def test_compute_adjustment_factors_defaults_missing_nonstandard_tiers_to_one():
    """It should default missing non-standard tiers to 1.0."""
    tier_medians = {
        "standard": 2.0,
    }

    result = compute_adjustment_factors(tier_medians)

    assert result == {
        "standard": 1.0,
        "other": 1.0,
        "mid_bulk": 1.0,
        "large_bulk": 1.0,
    }


@pytest.mark.parametrize("invalid_standard", [None, 0, -1.0])
def test_compute_adjustment_factors_raises_for_invalid_standard_median(
    invalid_standard,
):
    """It should raise when the standard tier median is missing or non-positive."""
    tier_medians = {"standard": invalid_standard}

    with pytest.raises(ValueError, match="standard size tier"):
        compute_adjustment_factors(tier_medians)


@pytest.mark.parametrize("bad_value", [None, 0, -2.0])
def test_compute_adjustment_factors_defaults_invalid_nonstandard_tiers_to_one(
    bad_value,
):
    """It should use 1.0 when mid-bulk or large-bulk medians are invalid."""
    tier_medians = {
        "standard": 2.0,
        "mid_bulk": bad_value,
        "large_bulk": bad_value,
    }

    result = compute_adjustment_factors(tier_medians)

    assert result["mid_bulk"] == 1.0
    assert result["large_bulk"] == 1.0


def test_build_feature_table_returns_expected_product_level_features():
    """It should build product-level features with normalized reference pricing."""
    products_df = pd.DataFrame(
        {
            "product_key": ["p1", "p1", "p2"],
            "roaster": ["Roaster A", "Roaster A", "Roaster B"],
            "product_name": ["Coffee A", "Coffee A", "Coffee B"],
            "origin": ["Ethiopia", "Ethiopia", "Colombia"],
            "roast_type": ["Light Roast", "Light Roast", "Dark Roast"],
            "size": ["10 oz", "24 oz", "12 oz"],
            "size_oz": [10, 24, 12],
            "price_numeric": [18.0, 36.0, 20.0],
            "price_per_oz": [1.8, 1.5, 20.0 / 12.0],
            "hearts": [10, 10, 5],
            "total_reviews": [4, 4, 2],
            "heart_percentage": [0.75, 0.75, 0.5],
            "has_reviews": [True, True, True],
            "decaf": [False, False, False],
            "blend": [False, False, True],
            "single_origin": [True, True, False],
            "available_ground": [True, True, False],
            "url": ["url-a", "url-a", "url-b"],
        }
    )

    result = build_feature_table(products_df)

    assert list(result["product_key"]) == ["p1", "p2"]

    coffee_a = result[result["product_key"] == "p1"].iloc[0]
    coffee_b = result[result["product_key"] == "p2"].iloc[0]

    # product aggregation
    assert coffee_a["num_sizes"] == 2
    assert coffee_a["min_size_oz"] == 10
    assert coffee_a["max_size_oz"] == 24

    # roast membership aggregation
    assert coffee_a["roast_light"] == 1
    assert coffee_a["roast_medium"] == 0
    assert coffee_a["roast_dark"] == 0

    assert coffee_b["roast_light"] == 0
    assert coffee_b["roast_dark"] == 1

    # reference row selection:
    # p1 should choose the standard size (10 oz) over the 24 oz bag
    assert coffee_a["reference_size_label"] == "10 oz"
    assert coffee_a["reference_size_oz"] == 10
    assert coffee_a["reference_size_tier"] == "standard"

    # derived metrics
    assert coffee_a["review_volume_log"] == pytest.approx(math.log1p(4))
    assert coffee_b["review_volume_log"] == pytest.approx(math.log1p(2))

    assert coffee_a["value_signal"] > 0
    assert coffee_a["review_strength"] == pytest.approx(0.75 * math.log1p(4))


def test_validate_feature_columns_raises_for_missing_columns():
    """It should raise a clear error when required columns are missing."""
    products_df = pd.DataFrame({"product_key": ["p1"]})

    with pytest.raises(
        ValueError,
        match="missing required feature-engineering columns",
    ):
        validate_feature_columns(products_df)


def test_select_reference_rows_uses_nonstandard_fallback_order():
    """It should prefer mid-bulk, then large-bulk, then smallest available fallback."""
    products_df = pd.DataFrame(
        {
            "product_key": ["p1", "p1", "p2", "p2", "p3", "p3"],
            "size": ["32 oz", "24 oz", "96 oz", "80 oz", "20 oz", "8 oz"],
            "size_oz": [32, 24, 96, 80, 20, 8],
            "price_per_oz": [1.2, 1.3, 0.8, 0.9, 1.4, 1.8],
            "size_tier": [
                "mid_bulk",
                "mid_bulk",
                "large_bulk",
                "large_bulk",
                "other",
                "other",
            ],
        }
    )

    result = select_reference_rows(products_df)

    p1 = result[result["product_key"] == "p1"].iloc[0]
    p2 = result[result["product_key"] == "p2"].iloc[0]
    p3 = result[result["product_key"] == "p3"].iloc[0]

    assert p1["size_oz"] == 24
    assert p2["size_oz"] == 80
    assert p3["size_oz"] == 8
