"""
Integration test verifying the CoffeeMatch UI pipeline.

This test ensures the same sequence executed by the Streamlit UI
runs successfully:

1. Load datasets
2. Build feature table
3. Create user preferences (simulating UI inputs)
4. Generate recommendations
5. Validate returned objects
"""

from coffeematch_core.data_loader import load_datasets
from coffeematch_core.feature_engineering import build_feature_table
from coffeematch_core.recommendation_engine import recommend_products
from coffeematch_core.schemas import UserPreferences, Recommendation


def test_ui_pipeline_end_to_end():
    """
    Ensure the full CoffeeMatch recommendation pipeline runs successfully
    and returns valid Recommendation objects.
    """

    # Step 1 — Load datasets
    products_df, reviews_df, product_info_df = load_datasets()

    # Basic sanity checks
    assert products_df is not None
    assert reviews_df is not None
    assert product_info_df is not None
    assert len(products_df) > 0

    # Step 2 — Build feature table
    feature_table = build_feature_table(products_df)

    assert feature_table is not None
    assert len(feature_table) > 0

    # Step 3 — Simulate user survey inputs
    preferences = UserPreferences(
        roast_type="Medium",
        decaf=False,
        ground_required=False,
        single_origin_preference=False,
        blend_preference=None,
        roast_weight=3,
        price_weight=4,
        popularity_weight=2,
    )

    # Step 4 — Generate recommendations
    recommendations = recommend_products(
        feature_table=feature_table,
        products_df=products_df,
        reviews_df=reviews_df,
        product_info_df=product_info_df,
        preferences=preferences,
        top_n=5,
    )

    # Step 5 — Validate outputs
    assert isinstance(recommendations, list)

    if recommendations:
        first_rec = recommendations[0]

        # Ensure returned object type
        assert isinstance(first_rec, Recommendation)

        # Check required fields
        assert first_rec.product_name is not None
        assert first_rec.roaster is not None
        assert first_rec.score >= 0

        # Match reasons should be generated
        assert isinstance(first_rec.match_reasons, list)
