"""
Feature engineering utilities for CoffeeMatch.

This module transforms processed size-level product data into a
product-level feature table for the recommendation engine.

Design principles
-----------------
- Recommendations are made at the product level, not the size level.
- Value comparisons should remain fair across products sold in
  different bag sizes.
- Bulk bags should not dominate rankings simply because they have a
  lower raw price per ounce.
- A single reference row is selected per product for value comparison.
- Median-based adjustment factors normalize bulk pricing relative to
  standard retail bags.

Reference row rule
------------------
For each product:
1. If a standard size (10-16 oz) exists, use the bag closest to 12 oz.
2. Else if a mid-bulk size (24-32 oz) exists, use the smallest
   available mid-bulk bag.
3. Else if a large-bulk size (>= 80 oz) exists, use the smallest
   available large-bulk bag.
4. Otherwise, use the smallest available bag overall.

Normalization rule
------------------
reference_price_per_oz = reference_price_per_oz_raw * adjustment_factor

Adjustment factors are computed from dataset medians:
- standard: 1.0
- mid_bulk: median_standard / median_mid_bulk
- large_bulk: median_standard / median_large_bulk
- other: 1.0
"""

from __future__ import annotations

import math
import pandas as pd

from .schemas import PRODUCT_REQUIRED_COLUMNS, SIZE_OPTION_REQUIRED_COLUMNS

STANDARD_MIN_OZ = 10
STANDARD_MAX_OZ = 16
STANDARD_TARGET_OZ = 12
MID_BULK_MIN_OZ = 24
MID_BULK_MAX_OZ = 32
LARGE_BULK_MIN_OZ = 80

FEATURE_REQUIRED_COLUMNS = tuple(PRODUCT_REQUIRED_COLUMNS)


def validate_feature_columns(products_df: pd.DataFrame) -> None:
    """
    Validate that all required input columns exist before feature engineering.

    Parameters
    ----------
    products_df : pd.DataFrame
        Processed products dataset.

    Raises
    ------
    ValueError
        If one or more required columns are missing.
    """
    missing_columns = sorted(
        set(FEATURE_REQUIRED_COLUMNS) - set(products_df.columns)
    )
    if missing_columns:
        missing_str = ", ".join(missing_columns)
        raise ValueError(
            "Products data is missing required feature-engineering columns: "
            f"{missing_str}"
        )


def encode_roast_membership(products_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add overlapping roast membership features.

    Mapping:
    - Light Roast -> roast_light
    - Light-Medium Roast -> roast_light, roast_medium
    - Medium Roast -> roast_medium
    - Medium-Dark Roast -> roast_medium, roast_dark
    - Dark Roast -> roast_dark
    - Unspecified / missing -> roast_unknown

    Parameters
    ----------
    products_df : pd.DataFrame
        Product dataset containing roast_type.

    Returns
    -------
    pd.DataFrame
        Copy of the input DataFrame with roast membership columns added.
    """
    df = products_df.copy()

    df["roast_light"] = 0
    df["roast_medium"] = 0
    df["roast_dark"] = 0
    df["roast_unknown"] = 0

    df.loc[df["roast_type"] == "Light Roast", "roast_light"] = 1
    df.loc[
        df["roast_type"] == "Light-Medium Roast",
        ["roast_light", "roast_medium"],
    ] = 1
    df.loc[df["roast_type"] == "Medium Roast", "roast_medium"] = 1
    df.loc[
        df["roast_type"] == "Medium-Dark Roast",
        ["roast_medium", "roast_dark"],
    ] = 1
    df.loc[df["roast_type"] == "Dark Roast", "roast_dark"] = 1
    df.loc[
        df["roast_type"].isin(["Unspecified"]) | df["roast_type"].isna(),
        "roast_unknown",
    ] = 1

    return df


def classify_size_tier(size_oz: float) -> str:
    """
    Classify a bag size into a size tier.

    Parameters
    ----------
    size_oz : float
        Bag size in ounces.

    Returns
    -------
    str
        Size tier label.
    """
    if STANDARD_MIN_OZ <= size_oz <= STANDARD_MAX_OZ:
        return "standard"
    if MID_BULK_MIN_OZ <= size_oz <= MID_BULK_MAX_OZ:
        return "mid_bulk"
    if size_oz >= LARGE_BULK_MIN_OZ:
        return "large_bulk"
    return "other"


def add_size_tier(products_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a size_tier column derived from size_oz.

    Parameters
    ----------
    products_df : pd.DataFrame
        Product dataset containing size_oz.

    Returns
    -------
    pd.DataFrame
        Copy with size_tier column added.
    """
    df = products_df.copy()
    df["size_tier"] = df["size_oz"].apply(classify_size_tier)
    return df

def compute_tier_medians(products_df: pd.DataFrame) -> dict[str, float]:
    """
    Compute median raw price_per_oz for each size tier.

    Parameters
    ----------
    products_df : pd.DataFrame
        Product dataset containing size_tier and price_per_oz.

    Returns
    -------
    dict[str, float]
        Mapping from size tier to median price_per_oz.
    """
    return (
        products_df.groupby("size_tier")["price_per_oz"]
        .median()
        .dropna()
        .to_dict()
    )


def compute_adjustment_factors(tier_medians: dict[str, float]) -> dict[str, float]:
    """
    Compute normalization factors relative to the standard tier.

    Parameters
    ----------
    tier_medians : dict[str, float]
        Median raw price_per_oz by size tier.

    Returns
    -------
    dict[str, float]
        Adjustment factor by size tier.

    Raises
    ------
    ValueError
        If the standard tier median is unavailable or invalid.
    """
    standard_median = tier_medians.get("standard")
    if standard_median is None or standard_median <= 0:
        raise ValueError(
            "Cannot compute adjustment factors because the standard size tier "
            "has no valid median price_per_oz."
        )

    adjustment_factors: dict[str, float] = {
        "standard": 1.0,
        "other": 1.0,
    }

    for tier in ("mid_bulk", "large_bulk"):
        median_price = tier_medians.get(tier)
        if median_price is None or median_price <= 0:
            adjustment_factors[tier] = 1.0
        else:
            adjustment_factors[tier] = standard_median / median_price

    return adjustment_factors


def _select_reference_row_for_product(product_rows: pd.DataFrame) -> pd.Series:
    """
    Select the single reference row used for fair product-level comparison.

    Selection rule:
    1. Standard tier -> choose bag closest to 12 oz.
    2. Mid-bulk tier -> choose smallest available mid-bulk bag.
    3. Large-bulk tier -> choose smallest available large-bulk bag.
    4. Otherwise -> choose smallest available bag overall.

    Tie-breakers favor lower price_per_oz and then smaller size_oz.

    Parameters
    ----------
    product_rows : pd.DataFrame
        All size rows for one product.

    Returns
    -------
    pd.Series
        The selected reference row.
    """
    standard_rows = product_rows[product_rows["size_tier"] == "standard"].copy()
    if not standard_rows.empty:
        standard_rows["distance_to_12"] = (
            standard_rows["size_oz"] - STANDARD_TARGET_OZ
        ).abs()
        standard_rows = standard_rows.sort_values(
            by=["distance_to_12", "price_per_oz", "size_oz"],
            ascending=[True, True, True],
        )
        return standard_rows.iloc[0]

    mid_bulk_rows = product_rows[product_rows["size_tier"] == "mid_bulk"].copy()
    if not mid_bulk_rows.empty:
        mid_bulk_rows = mid_bulk_rows.sort_values(
            by=["size_oz", "price_per_oz"],
            ascending=[True, True],
        )
        return mid_bulk_rows.iloc[0]

    large_bulk_rows = product_rows[product_rows["size_tier"] == "large_bulk"].copy()
    if not large_bulk_rows.empty:
        large_bulk_rows = large_bulk_rows.sort_values(
            by=["size_oz", "price_per_oz"],
            ascending=[True, True],
        )
        return large_bulk_rows.iloc[0]

    fallback_rows = product_rows.sort_values(
        by=["size_oz", "price_per_oz"],
        ascending=[True, True],
    )
    return fallback_rows.iloc[0]


def select_reference_rows(products_df: pd.DataFrame) -> pd.DataFrame:
    """
    Select one reference row per product.

    Parameters
    ----------
    products_df : pd.DataFrame
        Size-level products dataset with size_tier.

    Returns
    -------
    pd.DataFrame
        One selected reference row per product.
    """
    selected_rows = []

    for _, product_rows in products_df.groupby("product_key"):
        selected_row = _select_reference_row_for_product(product_rows)
        selected_rows.append(selected_row)

    reference_rows = pd.DataFrame(selected_rows).reset_index(drop=True)
    return reference_rows


def apply_reference_adjustment(reference_rows: pd.DataFrame,
    adjustment_factors: dict[str, float]) -> pd.DataFrame:
    """
    Apply size-tier normalization to selected reference rows.

    Parameters
    ----------
    reference_rows : pd.DataFrame
        One reference row per product.
    adjustment_factors : dict[str, float]
        Adjustment factor by size tier.

    Returns
    -------
    pd.DataFrame
        Reference rows with normalized reference_price_per_oz.
    """
    df = reference_rows.copy()
    df["reference_adjustment_factor"] = (
        df["size_tier"].map(adjustment_factors).fillna(1.0)
    )
    df["reference_price_per_oz"] = (
        df["price_per_oz"] * df["reference_adjustment_factor"]
    )
    return df


def build_reference_features(reference_rows: pd.DataFrame) -> pd.DataFrame:
    """
    Extract product-level features from selected reference rows.

    Parameters
    ----------
    reference_rows : pd.DataFrame
        Adjusted reference rows, one per product.

    Returns
    -------
    pd.DataFrame
        Product-level reference features keyed by product_key.
    """
    reference_features = reference_rows[
        SIZE_OPTION_REQUIRED_COLUMNS
        + [
            "size_tier",
            "reference_adjustment_factor",
            "reference_price_per_oz",
        ]
    ].copy()

    reference_features = reference_features.rename(
        columns={
            "size": "reference_size_label",
            "size_oz": "reference_size_oz",
            "price_numeric": "reference_price_numeric",
            "price_per_oz": "reference_price_per_oz_raw",
            "size_tier": "reference_size_tier",
        }
    )

    return reference_features


def aggregate_product_features(products_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate size-level rows into product-level features.

    Parameters
    ----------
    products_df : pd.DataFrame
        Size-level products dataset with engineered roast features.

    Returns
    -------
    pd.DataFrame
        Product-level feature table.
    """
    product_features = products_df.groupby("product_key").agg(
        roaster=("roaster", "first"),
        product_name=("product_name", "first"),
        origin=("origin", "first"),
        roast_type=("roast_type", "first"),
        decaf=("decaf", "first"),
        blend=("blend", "first"),
        available_ground=("available_ground", "first"),
        single_origin=("single_origin", "first"),
        url=("url", "first"),
        has_reviews=("has_reviews", "first"),
        hearts=("hearts", "first"),
        total_reviews=("total_reviews", "first"),
        heart_percentage=("heart_percentage", "first"),
        roast_light=("roast_light", "max"),
        roast_medium=("roast_medium", "max"),
        roast_dark=("roast_dark", "max"),
        roast_unknown=("roast_unknown", "max"),
        num_sizes=("size_oz", "nunique"),
        min_size_oz=("size_oz", "min"),
        max_size_oz=("size_oz", "max"),
        min_price_numeric=("price_numeric", "min"),
        max_price_numeric=("price_numeric", "max"),
    )

    return product_features.reset_index()


def add_derived_product_features(product_features: pd.DataFrame) -> pd.DataFrame:
    """
    Add numeric features useful for downstream recommendation scoring.

    Parameters
    ----------
    product_features : pd.DataFrame
        Product-level feature table.

    Returns
    -------
    pd.DataFrame
        Feature table with additional derived columns.
    """
    df = product_features.copy()

    df["review_volume_log"] = df["total_reviews"].fillna(0).apply(math.log1p)

    df["value_signal"] = 0.0
    valid_reference_mask = df["reference_price_per_oz"] > 0
    df.loc[valid_reference_mask, "value_signal"] = (
        1 / df.loc[valid_reference_mask, "reference_price_per_oz"]
    )

    df["review_strength"] = (
        df["heart_percentage"].fillna(0) * df["review_volume_log"]
    )

    return df


def build_feature_table(products_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build the final product-level feature table for recommendation.

    Parameters
    ----------
    products_df : pd.DataFrame
        Processed size-level product dataset.

    Returns
    -------
    pd.DataFrame
        Product-level feature table ready for the recommendation engine.
    """
    validate_feature_columns(products_df)

    size_level_df = encode_roast_membership(products_df)
    size_level_df = add_size_tier(size_level_df)

    tier_medians = compute_tier_medians(size_level_df)
    adjustment_factors = compute_adjustment_factors(tier_medians)

    reference_rows = select_reference_rows(size_level_df)
    reference_rows = apply_reference_adjustment(
        reference_rows,
        adjustment_factors,
    )
    reference_features = build_reference_features(reference_rows)

    product_features = aggregate_product_features(size_level_df)

    feature_table = product_features.merge(
        reference_features,
        on="product_key",
        how="left",
    )

    feature_table = add_derived_product_features(feature_table)

    return feature_table
