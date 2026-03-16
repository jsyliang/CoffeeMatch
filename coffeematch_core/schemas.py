"""
Defines the core data structures used across the CoffeeMatch application.

These schemas describe the expected structure of cleaned product data,
review data, user preference inputs, and recommendation outputs. They
serve as a shared contract between backend modules and the Streamlit UI.
"""

# pylint: disable=too-many-instance-attributes, duplicate-code

from __future__ import annotations
from dataclasses import dataclass, field


PRODUCT_REQUIRED_COLUMNS = [
    "product_key",
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

PRODUCT_INFO_REQUIRED_COLUMNS = [
    "product_key",
    "cafe_name",
    "cafe_address",
    "cafe_city",
    "zip_code",
    "longitude",
    "latitude",
]

SIZE_OPTION_REQUIRED_COLUMNS = [
    "product_key",
    "size",
    "size_oz",
    "price_numeric",
    "price_per_oz",
]

@dataclass
class UserPreferences:
    """
    User selections passed from the UI to the recommendation engine.

    Attributes
    ----------
    roast_type : Optional[str]
        Preferred roast type, such as 'Light', 'Medium', 'Dark', or 'No Preference'.
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

    roast_type: str | None = None
    max_price_per_oz: float | None = None
    decaf: bool | None = None
    ground_required: bool | None = None
    single_origin_preference: bool | None = None
    blend_preference: bool | None = None
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
class CafeLocation:
    """
    Cafe location information associated with a coffee product.
    """

    cafe_name: str | None = None
    cafe_address: str | None = None
    cafe_city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    longitude: float | None = None
    latitude: float | None = None
    google_maps_url: str | None = None


@dataclass
class ReviewData:
    """
    Review information associated with a coffee product.
    """

    tasting_notes: list[str] = field(default_factory=list)
    review_texts: list[str] = field(default_factory=list)


@dataclass
class Recommendation:
    """
    One recommendation returned by the recommendation engine.
    """

    product_key: str
    roaster: str
    product_name: str
    origin: str | None
    roast_type: str | None
    decaf: bool | None
    blend: bool | None
    single_origin: bool | None
    available_ground: bool | None

    reference_price_per_oz: float | None
    reference_size_label: str | None = None
    reference_size_oz: float | None = None
    reference_price_numeric: float | None = None
    reference_size_tier: str | None = None

    score: float = 0.0
    match_reasons: list[str] = field(default_factory=list)
    available_sizes: list[SizeOption] = field(default_factory=list)

    total_reviews: int | None = None
    heart_percentage: float | None = None
    has_reviews: bool | None = None

    tasting_notes: list[str] = field(default_factory=list)
    review_texts: list[str] = field(default_factory=list)

    cafe_location: CafeLocation | None = None
