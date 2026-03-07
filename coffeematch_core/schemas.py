"""
Defines the core data structures used across the CoffeeMatch application.

These schemas describe the expected structure of cleaned product data,
review data, user preference inputs, and recommendation outputs. They
serve as a shared contract between backend modules and the Streamlit UI.
"""

# pylint: disable=too-many-instance-attributes

from dataclasses import dataclass, field
from typing import List, Optional


PRODUCT_REQUIRED_COLUMNS = [
    "roaster",
    "product_name",
    "origin",
    "roast_type",
    "size",
    "size_oz",
    "price_numeric",
    "price_per_oz",
    "hearts",
    "total_reviews",
    "heart_percentage",
    "has_reviews",
    "decaf",
    "blend",
    "single_origin",
    "available_ground",
    "url",
]

REVIEW_REQUIRED_COLUMNS = [
    "product_name",
    "sentiment",
    "brewing_method",
    "review_text",
    "date",
    "tasting_notes",
]


@dataclass
class UserPreferences:
    """
    User selections passed from the UI to the recommendation engine.

    Attributes
    ----------
    roast_type : Optional[str]
        Preferred roast type, such as 'Light', 'Medium', or 'Dark'.
    max_price_per_oz : Optional[float]
        Maximum acceptable price per ounce. Use None if no limit is set.
    decaf : Optional[bool]
        Whether the user wants decaf. Use None if no preference is set.
    ground_required : Optional[bool]
        Whether the user requires ground coffee availability.
    single_origin_preference : Optional[bool]
        Whether the user prefers single-origin coffee. Use None if no preference.
    blend_preference : Optional[bool]
        Whether the user prefers blends. Use None if no preference.
    roast_weight : float
        Relative weight for roast matching in the ranking stage.
    price_weight : float
        Relative weight for price/value matching in the ranking stage.
    popularity_weight : float
        Relative weight for popularity/review-based ranking.
    """

    roast_type: Optional[str] = None
    max_price_per_oz: Optional[float] = None
    decaf: Optional[bool] = None
    ground_required: Optional[bool] = None
    single_origin_preference: Optional[bool] = None
    blend_preference: Optional[bool] = None
    roast_weight: float = 0.45
    price_weight: float = 0.35
    popularity_weight: float = 0.20


@dataclass
class SizeOption:
    """
    One available size/price option for a coffee product.
    """

    size: str
    size_oz: float
    price_numeric: float
    price_per_oz: float


@dataclass
class Recommendation:
    """
    One recommendation returned by the recommendation engine.
    """
    product_key: str
    roaster: str
    product_name: str
    origin: Optional[str]
    roast_type: Optional[str]
    decaf: Optional[bool]
    blend: Optional[bool]
    single_origin: Optional[bool]
    available_ground: Optional[bool]
    reference_price_per_oz: Optional[float]
    score: float
    match_reasons: List[str] = field(default_factory=list)
    available_sizes: List[SizeOption] = field(default_factory=list)
    total_reviews: Optional[int] = None
    heart_percentage: Optional[float] = None
    has_reviews: Optional[bool] = None
    url: Optional[str] = None
