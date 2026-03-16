# pylint: disable=missing-module-docstring, missing-function-docstring
import pandas as pd
import pytest

from coffeematch_core.recommendation_engine import (
    build_match_reasons,
    build_product_info_lookup,
    build_reviews_lookup,
    build_size_options,
    compute_component_scores,
    filter_products,
    get_roast_preference_columns,
    is_washington_zip,
    min_max_scale,
    recommend_products,
    sort_recommendations,
    validate_recommendation_columns,
    validate_size_option_columns,
)
from coffeematch_core.schemas import UserPreferences


def make_feature_table() -> pd.DataFrame:
    """Build a small product-level feature table for recommendation tests."""
    return pd.DataFrame(
        {
            "product_key": ["p1", "p2", "p3", "p4"],
            "roaster": ["Roaster A", "Roaster B", "Roaster C", "Roaster D"],
            "product_name": ["Coffee A", "Coffee B", "Coffee C", "Coffee D"],
            "origin": ["Ethiopia", "Colombia", "Brazil", "Kenya"],
            "roast_type": ["Light Roast", "Medium Roast", "Dark Roast", "Medium Roast"],
            "decaf": [False, True, False, False],
            "blend": [False, True, False, True],
            "single_origin": [True, False, True, False],
            "available_ground": [True, False, True, True],
            "url": ["u1", "u2", "u3", "u4"],
            "has_reviews": [True, True, False, True],
            "total_reviews": [10, 5, 0, 20],
            "hearts": [9, 4, 0, 16],
            "heart_percentage": [0.90, 0.70, 0.00, 0.80],
            "roast_light": [1, 0, 0, 0],
            "roast_medium": [0, 1, 0, 1],
            "roast_dark": [0, 0, 1, 0],
            "roast_unknown": [0, 0, 0, 0],
            "size": ["12 oz", "12 oz", "10 oz", "16 oz"],
            "size_oz": [12.0, 12.0, 10.0, 16.0],
            "price_numeric": [18.0, 26.4, 12.0, 28.8],
            "price_per_oz": [1.50, 2.20, 1.20, 1.80],
            "reference_price_per_oz": [1.50, 2.20, 1.20, 1.80],
            "reference_size_label": ["12 oz", "12 oz", "10 oz", "16 oz"],
            "reference_size_oz": [12.0, 12.0, 10.0, 16.0],
            "reference_price_numeric": [18.0, 26.4, 12.0, 28.8],
            "reference_size_tier": ["standard", "standard", "standard", "standard"],
            "value_signal": [0.80, 0.40, 0.95, 0.60],
            "review_strength": [2.0, 1.2, 0.0, 2.8],
        }
    )


def make_products_df() -> pd.DataFrame:
    """Build a size-level products table for available size option tests."""
    return pd.DataFrame(
        {
            "product_key": ["p1", "p1", "p2", "p3"],
            "size": ["12 oz", "24 oz", "12 oz", "10 oz"],
            "size_oz": [12.0, 24.0, 12.0, 10.0],
            "price_numeric": [18.0, 32.0, 26.4, 12.0],
            "price_per_oz": [1.50, 32.0 / 24.0, 2.20, 1.20],
        }
    )


def make_reviews_df() -> pd.DataFrame:
    """Build a small reviews table."""
    return pd.DataFrame(
        {
            "product_name": ["Coffee A", "Coffee A", "Coffee B"],
            "tasting_notes": ["berry", "citrus", None],
            "review_text": ["Excellent cup", "Very bright", "Comforting and smooth"],
        }
    )


def make_product_info_df() -> pd.DataFrame:
    """Build a small product info table."""
    return pd.DataFrame(
        {
            "product_key": ["p1", "p2", "p3"],
            "cafe_name": ["Cafe One", "Cafe Two", None],
            "cafe_address": ["123 Main", "456 Pine", None],
            "cafe_city": ["Seattle", "Portland", None],
            "zip_code": ["98101", "97201", None],
            "longitude": [-122.33, -122.67, None],
            "latitude": [47.61, 45.52, None],
        }
    )


@pytest.mark.parametrize(
    ("roast_type", "expected"),
    [
        (None, []),
        ("No Preference", []),
        ("no preference", []),
        ("Light", ["roast_light"]),
        ("light", ["roast_light"]),
        ("  medium  ", ["roast_medium"]),
        ("Dark", ["roast_dark"]),
        ("espresso", []),
    ],
)
def test_get_roast_preference_columns_returns_expected_columns(
    roast_type,
    expected,
):
    """It should map roast preferences to the expected roast membership columns."""
    assert get_roast_preference_columns(roast_type) == expected


def test_filter_products_returns_all_rows_when_no_preferences_are_set():
    """It should leave the table unchanged when there are no hard filters."""
    feature_table = make_feature_table()
    preferences = UserPreferences()

    result = filter_products(feature_table, preferences)

    assert list(result["product_key"]) == ["p1", "p2", "p3", "p4"]


def test_filter_products_applies_multiple_filters_together():
    """It should keep only rows that satisfy all active hard filters."""
    feature_table = make_feature_table()
    preferences = UserPreferences(
        decaf=False,
        ground_required=True,
        single_origin_preference=True,
        max_price_per_oz=1.60,
    )

    result = filter_products(feature_table, preferences)

    assert list(result["product_key"]) == ["p1", "p3"]


def test_min_max_scale_scales_values_to_zero_and_one():
    """It should scale numeric values to the [0, 1] range."""
    values = pd.Series([10.0, 20.0, 30.0])

    result = min_max_scale(values)

    expected = pd.Series([0.0, 0.5, 1.0])
    pd.testing.assert_series_equal(result, expected)


def test_min_max_scale_returns_ones_when_all_values_are_identical():
    """It should return all ones when the min and max are the same."""
    values = pd.Series([5.0, 5.0, 5.0])

    result = min_max_scale(values)

    expected = pd.Series([1.0, 1.0, 1.0])
    pd.testing.assert_series_equal(result, expected)


def test_validate_recommendation_columns_raises_for_missing_columns():
    """It should raise when required recommendation columns are missing."""
    feature_table = pd.DataFrame({"product_key": ["p1"]})

    with pytest.raises(
        ValueError,
        match="missing required recommendation columns",
    ):
        validate_recommendation_columns(feature_table)


def test_validate_size_option_columns_raises_for_missing_columns():
    """It should raise when required size option columns are missing."""
    products_df = pd.DataFrame({"product_key": ["p1"]})

    with pytest.raises(
        ValueError,
        match="missing required size option columns",
    ):
        validate_size_option_columns(products_df)


@pytest.mark.parametrize(
    ("zip_code", "expected"),
    [
        ("98101", True),
        ("99499", True),
        ("97201", False),
        (None, False),
        ("badzip", False),
    ],
)
def test_is_washington_zip_returns_expected_result(zip_code, expected):
    """It should correctly identify Washington ZIP codes."""
    assert is_washington_zip(zip_code) is expected


def test_google_maps_url_from_address():
    """
    Test that Google Maps URL is correctly generated from address fields.
    """

    df = pd.DataFrame(
        {
            "product_key": ["p1"],
            "cafe_name": ["Test Cafe"],
            "cafe_address": ["123 Pike St"],
            "cafe_city": ["Seattle"],
            "zip_code": ["98101"],
            "latitude": [None],
            "longitude": [None],
        }
    )

    lookup = build_product_info_lookup(df)

    cafe = lookup["p1"]

    assert cafe.google_maps_url is not None
    assert "google.com/maps/search" in cafe.google_maps_url
    assert "Seattle" in cafe.google_maps_url


def test_build_reviews_lookup_groups_notes_and_review_texts():
    """It should group review details by product name and drop missing values."""
    reviews_df = make_reviews_df()

    result = build_reviews_lookup(reviews_df)

    assert result["Coffee A"].tasting_notes == ["berry", "citrus"]
    assert result["Coffee A"].review_texts == ["Excellent cup", "Very bright"]
    assert result["Coffee B"].tasting_notes == []
    assert result["Coffee B"].review_texts == ["Comforting and smooth"]


def test_build_size_options_sorts_sizes_within_each_product():
    """It should build SizeOption lists ordered by size_oz then price_numeric."""
    products_df = make_products_df()

    result = build_size_options(products_df)

    assert [option.size for option in result["p1"]] == ["12 oz", "24 oz"]
    assert result["p1"][0].price_per_oz == 1.50
    assert result["p3"][0].size_oz == 10.0


def test_compute_component_scores_adds_expected_score_columns():
    """It should compute roast, value, popularity, and final score columns."""
    feature_table = make_feature_table()
    preferences = UserPreferences(
        roast_type="Medium",
        roast_weight=0.5,
        price_weight=0.3,
        popularity_weight=0.2,
    )

    result = compute_component_scores(feature_table, preferences)

    assert "roast_match_score" in result.columns
    assert "value_score" in result.columns
    assert "popularity_score" in result.columns
    assert "score" in result.columns

    medium_rows = result[result["product_key"].isin(["p2", "p4"])]
    non_medium_rows = result[result["product_key"].isin(["p1", "p3"])]

    assert all(medium_rows["roast_match_score"] == 1.0)
    assert all(non_medium_rows["roast_match_score"] == 0.0)


def test_compute_component_scores_raises_when_total_weight_is_not_positive():
    """It should raise if the score weights sum to a non-positive value."""
    feature_table = make_feature_table()
    preferences = UserPreferences(
        roast_weight=0.0,
        price_weight=0.0,
        popularity_weight=0.0,
    )

    with pytest.raises(
        ValueError,
        match="weights must sum to a positive value",
    ):
        compute_component_scores(feature_table, preferences)


def test_sort_recommendations_orders_by_score_then_tiebreakers():
    """It should sort strongest recommendations first."""
    scored_df = pd.DataFrame(
        {
            "product_name": ["Zulu", "Alpha", "Bravo"],
            "score": [0.90, 0.90, 0.80],
            "roast_match_score": [1.0, 1.0, 1.0],
            "value_score": [0.50, 0.60, 0.40],
            "popularity_score": [0.50, 0.50, 0.50],
            "total_reviews": [10, 10, 20],
        }
    )

    result = sort_recommendations(scored_df)

    assert list(result["product_name"]) == ["Alpha", "Zulu", "Bravo"]


def test_build_match_reasons_returns_at_most_three_reasons():
    """It should build recommendation reasons and truncate to three."""
    row = pd.Series(
        {
            "roast_match_score": 1.0,
            "value_score": 0.90,
            "reference_size_label": "12 oz",
            "popularity_score": 0.90,
            "has_reviews": True,
            "total_reviews": 10,
            "decaf": True,
            "available_ground": True,
            "single_origin": True,
            "blend": True,
        }
    )
    preferences = UserPreferences(
        roast_type="Medium",
        decaf=True,
        ground_required=True,
        single_origin_preference=True,
        blend_preference=True,
    )

    reasons = build_match_reasons(row, preferences)

    assert len(reasons) == 3
    assert reasons[0] == "Matches your roast preference for Medium"


def test_recommend_products_returns_empty_list_when_all_products_are_filtered_out():
    """It should return an empty list when no products survive hard filters."""
    feature_table = make_feature_table()
    products_df = make_products_df()
    reviews_df = make_reviews_df()
    product_info_df = make_product_info_df()
    preferences = UserPreferences(
        decaf=True,
        ground_required=True,
        single_origin_preference=True,
        max_price_per_oz=1.00,
    )

    result = recommend_products(
        feature_table=feature_table,
        products_df=products_df,
        reviews_df=reviews_df,
        product_info_df=product_info_df,
        preferences=preferences,
        top_n=5,
    )

    assert not result


def test_recommend_products_returns_ranked_recommendation_objects_with_joined_details():
    """It should return ranked Recommendation objects with sizes, reviews, and cafe info."""
    feature_table = make_feature_table()
    products_df = make_products_df()
    reviews_df = make_reviews_df()
    product_info_df = make_product_info_df()
    preferences = UserPreferences(
        roast_type="Medium",
        ground_required=True,
        max_price_per_oz=2.00,
        roast_weight=0.5,
        price_weight=0.3,
        popularity_weight=0.2,
    )

    result = recommend_products(
        feature_table=feature_table,
        products_df=products_df,
        reviews_df=reviews_df,
        product_info_df=product_info_df,
        preferences=preferences,
        top_n=2,
    )

    assert len(result) == 2

    first = result[0]
    second = result[1]

    assert first.product_key == "p4"
    assert second.product_key == "p1"

    assert first.score >= second.score
    assert isinstance(first.match_reasons, list)
    assert isinstance(first.available_sizes, list)

    assert second.available_sizes[0].size == "12 oz"
    assert second.available_sizes[1].size == "24 oz"

    assert second.tasting_notes == ["berry", "citrus"]
    assert second.review_texts == ["Excellent cup", "Very bright"]

    assert second.cafe_location is not None
    assert second.cafe_location.cafe_name == "Cafe One"
    assert second.cafe_location.state == "WA"
