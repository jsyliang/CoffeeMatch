import pandas as pd
import pytest

from coffeematch_core.feature_engineering import (
    classify_size_tier,
    compute_adjustment_factors,
    encode_roast_membership,
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