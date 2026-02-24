import pandas as pd
import numpy as np
import streamlit as st

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Coffee Match", layout="wide")
st.title("Coffee Match — Washington Roasters")

PRODUCTS_PATH = "data/Product_Information.xlsx"
REVIEWS_PATH = "data/Reviews_and_Tasting_Notes.xlsx"
REVIEWS_SHEET = "Reviews with Tasting Notes"

ROAST_POINTS = 3.0
TAG_POINTS_PER_MATCH = 1.0
VALUE_WEIGHT = 2.0

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_products():
    df = pd.read_excel(PRODUCTS_PATH)

    df["tags_clean"] = df["tags"].fillna("").apply(
        lambda x: [t.strip().lower() for t in str(x).split(",") if t.strip()]
    )

    df["roast_type"] = df["roast_type"].fillna("Unknown")
    df["origin"] = df["origin"].fillna("Unspecified")

    df["price_numeric"] = pd.to_numeric(df["price_numeric"], errors="coerce")
    df["price_per_oz"] = pd.to_numeric(df["price_per_oz"], errors="coerce")

    for col in ["decaf", "blend", "single_origin", "available_ground", "has_reviews"]:
        if col in df.columns:
            df[col] = df[col].fillna(False).astype(bool)

    return df


@st.cache_data
def load_reviews():
    try:
        df = pd.read_excel(REVIEWS_PATH, sheet_name=REVIEWS_SHEET)
    except:
        return pd.DataFrame()

    df["product_name"] = df["product_name"].astype(str)
    df["sentiment"] = df["sentiment"].astype(str).str.lower()

    return df


products = load_products()
reviews = load_reviews()

# -----------------------------
# MATCHING LOGIC
# -----------------------------
def apply_filters(df, prefs):
    filtered = df.copy()

    # Decaf
    if prefs["decaf"] == "Decaf only":
        filtered = filtered[filtered["decaf"] == True]
    elif prefs["decaf"] == "Caffeinated only":
        filtered = filtered[filtered["decaf"] == False]

    # Roast
    if prefs["roast"] != "No preference":
        filtered = filtered[
            filtered["roast_type"].str.contains(prefs["roast"], case=False, na=False)
        ]

    # Ground
    if prefs["grind"] == "Ground required":
        filtered = filtered[filtered["available_ground"] == True]

    # Budget
    if prefs["max_price"] is not None:
        filtered = filtered[
            filtered["price_numeric"] <= prefs["max_price"]
        ]

    return filtered


def score_products(df, prefs):
    df = df.copy()
    df["score"] = 0
    df["reason"] = ""

    # Roast match
    if prefs["roast"] != "No preference":
        mask = df["roast_type"].str.contains(prefs["roast"], case=False, na=False)
        df.loc[mask, "score"] += ROAST_POINTS
        df.loc[mask, "reason"] += f"Roast match (+{ROAST_POINTS}). "

    # Tag overlap (vectorized)
    if prefs["tags"]:

        overlaps = (
            df["tags_clean"]
            .explode()
            .isin(prefs["tags"])
            .groupby(level=0)
            .sum()
            .reindex(df.index, fill_value=0)
        )

        tag_bonus = TAG_POINTS_PER_MATCH * overlaps
        df["score"] += tag_bonus
        df.loc[tag_bonus > 0, "reason"] += (
            "Tag overlap (+" + tag_bonus[tag_bonus > 0].round(2).astype(str) + "). "
        )

    # Cheaper per oz gets slight boost
    if df["price_per_oz"].notna().any():
        max_p = df["price_per_oz"].max()
        min_p = df["price_per_oz"].min()
        if max_p > min_p:
            value_score = (max_p - df["price_per_oz"]) / (max_p - min_p)
            value_bonus = VALUE_WEIGHT * value_score

            df["score"] += value_bonus

            df.loc[value_bonus > 0, "reason"] += (
                "Good value (+" 
                + value_bonus[value_bonus > 0].round(2).astype(str)
                + "). "
            )

    return df.sort_values("score", ascending=False)


# -----------------------------
# QUESTIONNAIRE UI
# -----------------------------
st.header("Find Your Coffee")

prefs = {}

prefs["decaf"] = st.radio(
    "Decaf preference",
    ["Either", "Decaf only", "Caffeinated only"]
)

prefs["roast"] = st.selectbox(
    "Roast preference",
    ["No preference"] + sorted(products["roast_type"].unique())
)

prefs["grind"] = st.radio(
    "Need ground coffee available?",
    ["Either", "Ground required"]
)

set_budget = st.checkbox("Set max bag price?")
if set_budget:
    prefs["max_price"] = st.slider(
        "Max price ($)",
        5.0,
        float(products["price_numeric"].max()),
        20.0
    )
else:
    prefs["max_price"] = None

prefs["tags"] = st.multiselect(
    "Tags (optional)",
    sorted({tag for tags in products["tags_clean"] for tag in tags})
)

match_mode = st.radio(
    "Recommendation type",
    ["Single Best Match", "Top 5 Matches"]
)

# -----------------------------
# RUN MATCH
# -----------------------------
if st.button("Find Coffee"):
    filtered = apply_filters(products, prefs)
    scored = score_products(filtered, prefs)

    if scored.empty:
        st.warning("No products match your filters.")
    else:
        if match_mode == "Single Best Match":
            scored = scored.head(1)
        else:
            scored = scored.head(5)

        st.success("Here are your matches:")
        for _, row in scored.iterrows():
            st.subheader(row["product_name"])
            st.write(f"Roaster: {row['roaster']}")
            st.write(f"Roast: {row['roast_type']}")
            st.write(f"Origin: {row['origin']}")
            st.write(f"Price: ${row['price_numeric']:.2f}")
            st.write(f"Score: {row['score']:.2f}")
            st.write(f"Why matched: {row['reason']}")
            st.divider()

st.markdown("---")
st.caption("Coffee Match — DATA 515 Demo")