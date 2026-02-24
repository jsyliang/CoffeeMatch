# app.py (Dash MVP version)
from __future__ import annotations

import math
import pandas as pd

from dash import Dash, html, dcc, Input, Output, State, callback

# Optional styling (Bootstrap). If you don't want it, remove and simplify layout.
try:
    import dash_bootstrap_components as dbc
    BOOTSTRAP = dbc.themes.BOOTSTRAP
except Exception:
    dbc = None
    BOOTSTRAP = None

DATA_PATH = "data/Product_Information.xlsx"

# -----------------------------
# Data loading + light cleaning
# -----------------------------
def to_bool(x) -> bool:
    if pd.isna(x):
        return False
    if isinstance(x, bool):
        return x
    s = str(x).strip().lower()
    return s in {"true", "1", "yes", "y"}

def clean_tags(val):
    if pd.isna(val):
        return []
    if isinstance(val, list):
        return [str(t).strip() for t in val if str(t).strip()]
    s = str(val).strip()
    if s.startswith("[") and s.endswith("]"):
        s = s.strip("[]")
    parts = [p.strip(" '\"") for p in s.replace(";", ",").split(",")]
    return sorted({p for p in parts if p})

def load_products() -> pd.DataFrame:
    df = pd.read_excel(DATA_PATH)
    df.columns = [c.strip() for c in df.columns]

    # Ensure key columns exist
    for col in ["roaster", "product_name", "roast_type", "tags", "url",
                "price_per_oz", "hearts", "has_reviews", "heart_percentage",
                "available_ground", "decaf", "origin"]:
        if col not in df.columns:
            df[col] = pd.NA

    # Normalize
    df["roast_type"] = df["roast_type"].astype(str).str.strip().str.lower().replace({"nan": ""})
    df["available_ground"] = df["available_ground"].apply(to_bool)
    df["decaf"] = df["decaf"].apply(to_bool)
    df["has_reviews"] = df["has_reviews"].apply(to_bool)

    df["tags_clean"] = df["tags"].apply(clean_tags)

    # Make sure price is numeric
    df["price_per_oz"] = pd.to_numeric(df["price_per_oz"], errors="coerce")
    df["hearts"] = pd.to_numeric(df["hearts"], errors="coerce").fillna(0)

    # heart_percentage can be missing; keep numeric if present
    df["heart_percentage"] = pd.to_numeric(df["heart_percentage"], errors="coerce")

    return df


# -----------------------------
# Recommendation logic (MVP)
# -----------------------------
TAG_POINTS_PER_MATCH = 0.8
POPULARITY_WEIGHT = 0.6
VALUE_WEIGHT = 0.8

def score_and_reason(df: pd.DataFrame, prefs: dict) -> pd.DataFrame:
    out = df.copy()
    out["score"] = 0.0
    out["reason"] = ""

    # Explicit matches first (added later into reason for finalists)

    # Tag overlap
    tags = prefs.get("tags", [])
    if tags:
        tag_set = set(tags)

        def overlap_count(row_tags):
            return len(set(row_tags).intersection(tag_set))

        overlaps = out["tags_clean"].apply(overlap_count)
        out["score"] += TAG_POINTS_PER_MATCH * overlaps
        out.loc[overlaps > 0, "reason"] += "Tag overlap. "

    # Popularity (use heart_percentage if available, otherwise fallback to hearts)
    if out["heart_percentage"].notna().any():
        hp = out["heart_percentage"].fillna(0)
        hp_min, hp_max = float(hp.min()), float(hp.max())
        if hp_max > hp_min:
            hp_norm = (hp - hp_min) / (hp_max - hp_min)
            out["score"] += POPULARITY_WEIGHT * hp_norm
            out.loc[out["heart_percentage"].notna(), "reason"] += "Popular reviews. "
    else:
        # Fallback: normalize hearts
        h = out["hearts"].fillna(0)
        h_min, h_max = float(h.min()), float(h.max())
        if h_max > h_min:
            h_norm = (h - h_min) / (h_max - h_min)
            out["score"] += 0.3 * h_norm
            out.loc[h > 0, "reason"] += "Liked by users. "

    # Value (lower $/oz is better)
    if out["price_per_oz"].notna().any():
        p = out["price_per_oz"]
        p_min, p_max = float(p.min()), float(p.max())
        if p_max > p_min:
            value_norm = (p_max - p) / (p_max - p_min)  # 0..1
            out["score"] += VALUE_WEIGHT * value_norm
            out.loc[p.notna(), "reason"] += "Good value. "

    return out


def recommend(products: pd.DataFrame, prefs: dict) -> list[dict]:
    df = products.copy()

    # Hard filters
    decaf_pref = prefs.get("decaf", "Either")
    if decaf_pref == "Decaf":
        df = df[df["decaf"] == True]
    elif decaf_pref == "Caffeinated":
        df = df[df["decaf"] == False]

    roast_types = prefs.get("roast_types", [])
    if roast_types:
        roast_types = [r.strip().lower() for r in roast_types]
        df = df[df["roast_type"].isin(roast_types)]

    max_price = prefs.get("max_price_per_oz")
    if max_price is not None:
        df = df[df["price_per_oz"].isna() | (df["price_per_oz"] <= float(max_price))]

    # If user requires ground availability (strict), filter here:
    # if prefs.get("needs_ground", False):
    #     df = df[df["available_ground"] == True]

    if df.empty:
        return []

    ranked = score_and_reason(df, prefs).sort_values("score", ascending=False)

    # Strengthen reason with explicit matches
    results = []
    for _, row in ranked.iterrows():
        r = row.to_dict()
        explicit = []
        if prefs.get("decaf") != "Either":
            explicit.append(f"Matches caffeine: {prefs['decaf'].lower()}.")
        if roast_types:
            explicit.append(f"Matches roast: {row.get('roast_type','')}.")
        if max_price is not None and pd.notna(row.get("price_per_oz")):
            explicit.append(f"Within budget (${row['price_per_oz']:.2f}/oz).")

        r["reason"] = (" ".join(explicit) + " " if explicit else "") + (r.get("reason") or "")
        results.append(r)

    return results


# -----------------------------
# Build Dash UI
# -----------------------------
products_df = load_products()

roast_options = sorted([r for r in products_df["roast_type"].dropna().unique().tolist() if r])
all_tags = sorted({t for tags in products_df["tags_clean"] for t in tags})

app = Dash(__name__, external_stylesheets=[BOOTSTRAP] if BOOTSTRAP else None)
server = app.server  # for deployment platforms that look for "server"

def controls_panel():
    # Use dbc if available, otherwise plain html.Div
    if dbc:
        return dbc.Card(
            dbc.CardBody([
                html.H4("Tell us what you like"),
                html.Label("Mode"),
                dcc.RadioItems(
                    id="mode",
                    options=[
                        {"label": "Best match", "value": "best"},
                        {"label": "Top 5", "value": "top5"},
                    ],
                    value="best",
                    inline=True,
                ),
                html.Hr(),

                html.Label("Caffeine"),
                dcc.Dropdown(
                    id="decaf",
                    options=["Either", "Caffeinated", "Decaf"],
                    value="Either",
                    clearable=False
                ),

                html.Br(),
                html.Label("Roast level(s)"),
                dcc.Dropdown(
                    id="roast_types",
                    options=roast_options,
                    value=[],
                    multi=True
                ),

                html.Br(),
                html.Label("Budget ($ per oz max)"),
                dcc.Slider(
                    id="max_price_per_oz",
                    min=0.10,
                    max=5.00,
                    step=0.05,
                    value=2.00,
                    tooltip={"placement": "bottom", "always_visible": False},
                ),

                html.Br(),
                html.Label("Tags (optional)"),
                dcc.Dropdown(
                    id="tags",
                    options=all_tags,
                    value=[],
                    multi=True,
                    placeholder="Select tags..."
                ),

                html.Br(),
                dbc.Button("Recommend", id="btn_recommend", color="primary", className="w-100"),
                html.Div(id="error_box", style={"marginTop": "12px"}),
            ]),
            style={"height": "100%"}
        )
    else:
        return html.Div([
            html.H3("Tell us what you like"),
            html.Label("Mode"),
            dcc.RadioItems(
                id="mode",
                options=[
                    {"label": "Best match", "value": "best"},
                    {"label": "Top 5", "value": "top5"},
                ],
                value="best",
            ),
            html.Br(),
            html.Label("Caffeine"),
            dcc.Dropdown(id="decaf", options=["Either", "Caffeinated", "Decaf"], value="Either", clearable=False),
            html.Br(),
            html.Label("Roast level(s)"),
            dcc.Dropdown(id="roast_types", options=roast_options, value=[], multi=True),
            html.Br(),
            html.Label("Budget ($ per oz max)"),
            dcc.Slider(id="max_price_per_oz", min=0.10, max=5.00, step=0.05, value=2.00),
            html.Br(),
            html.Label("Tags (optional)"),
            dcc.Dropdown(id="tags", options=all_tags, value=[], multi=True),
            html.Br(),
            html.Button("Recommend", id="btn_recommend"),
            html.Div(id="error_box", style={"marginTop": "12px", "color": "crimson"}),
        ])

def results_panel():
    if dbc:
        return dbc.Card(dbc.CardBody([
            html.H4("Recommendations"),
            html.Div(id="results")
        ]))
    return html.Div([html.H3("Recommendations"), html.Div(id="results")])

def page_layout():
    title = html.H2("☕ CoffeeMatch — Washington Local Coffee Recommendations", style={"marginBottom": "16px"})
    if dbc:
        return dbc.Container([
            title,
            dbc.Row([
                dbc.Col(controls_panel(), md=4),
                dbc.Col(results_panel(), md=8),
            ], className="g-3")
        ], fluid=True)
    return html.Div([
        title,
        html.Div([
            html.Div(controls_panel(), style={"width": "30%", "display": "inline-block", "verticalAlign": "top"}),
            html.Div(results_panel(), style={"width": "68%", "display": "inline-block", "paddingLeft": "2%"}),
        ])
    ])

app.layout = page_layout()


def render_result_card(r: dict):
    # Build a compact “card” for each recommendation
    header = html.H4(f"{r.get('roaster','')} — {r.get('product_name','')}", style={"marginBottom": "6px"})
    reason = html.P(r.get("reason", ""), style={"marginTop": "0px"})

    roast = r.get("roast_type", "")
    ppo = r.get("price_per_oz", None)
    hearts = r.get("hearts", 0)
    has_reviews = r.get("has_reviews", False)
    origin = r.get("origin", "")
    tags = r.get("tags_clean", []) or []
    url = r.get("url", "")

    metrics = html.Ul([
        html.Li(f"Roast: {roast}" if roast else "Roast: —"),
        html.Li(f"$/oz: {ppo:.2f}" if isinstance(ppo, (int, float)) and not math.isnan(ppo) else "$/oz: —"),
        html.Li(f"Hearts: {int(hearts) if pd.notna(hearts) else 0}"),
        html.Li(f"Has reviews: {'Yes' if has_reviews else 'No'}"),
    ])

    extras = []
    if origin and str(origin).strip().lower() != "nan":
        extras.append(html.Div([html.Strong("Origin: "), html.Span(str(origin))]))
    if tags:
        extras.append(html.Div([html.Strong("Tags: "), html.Span(", ".join(tags[:12]))]))
    if url and str(url).strip().lower() != "nan":
        extras.append(html.Div(html.A("View product", href=url, target="_blank")))

    if dbc:
        return dbc.Card(dbc.CardBody([header, reason, metrics] + extras), style={"marginBottom": "12px"})
    return html.Div([header, reason, metrics] + extras,
                    style={"border": "1px solid #ddd", "borderRadius": "8px", "padding": "12px", "marginBottom": "12px"})


@callback(
    Output("results", "children"),
    Output("error_box", "children"),
    Input("btn_recommend", "n_clicks"),
    State("mode", "value"),
    State("decaf", "value"),
    State("roast_types", "value"),
    State("max_price_per_oz", "value"),
    State("tags", "value"),
    prevent_initial_call=True
)
def on_recommend(n_clicks, mode, decaf, roast_types, max_price_per_oz, tags):
    prefs = {
        "top_n": 1 if mode == "best" else 5,
        "decaf": decaf,
        "roast_types": roast_types or [],
        "max_price_per_oz": max_price_per_oz,
        "tags": tags or [],
    }

    results = recommend(products_df, prefs)

    if not results:
        msg = "No coffees matched those constraints. Try relaxing roast/decaf/budget or removing tags."
        if dbc:
            return [], dbc.Alert(msg, color="warning")
        return [], html.Div(msg, style={"color": "crimson"})

    top_n = prefs["top_n"]
    cards = [render_result_card(r) for r in results[:top_n]]

    if dbc:
        return cards, None
    return cards, ""


if __name__ == "__main__":
    app.run(debug=True)