import streamlit as st
import emoji 
import pandas as pd 
import numpy as np

# Paths to data 
PRODUCTS_PATH = "data/Product_Information.xlsx"
REVIEWS_PATH = "data/Reviews_and_Tasting_Notes.xlsx"
REVIEWS_SHEET = "Reviews with Tasting Notes"

# Set up styling classes for use in the website 
st.markdown("""
        <style>
            /*Page Background Colors*/
            
            .stApp {
                background: linear-gradient(to bottom, #ffe4b5, #8b4513);
            }

            /*Page Titles*/

            .page-title {
                font-size: 116px;
                font-family: 'Brush Script MT', cursive, sans-serif;
                color: #a0522d;
                text-align: center;
                margin-bottom: 0 !important
                gap: 0 !important;
            }
            
            /*Page Subtitles*/

            .page-subtitle {
                font-size: 44px;
                color: #a0522d;
                font-family: 'Brush Script MT', cursive, sans-serif;
                text-align: center;
                margin-bottom: 1.5rem !important;
                margin-top: 0 !important;
            }

            /*Survey Box*/
            .stForm{
            background-color: #ffe4b5 !important;
            }

            /*Formatting for the text to go above questions in the survey*/

            .survey-question {
                font-size: 24px;
                color: #a0522d ; 
                font-weight: bold;
                margin: 0 !important;
                padding: 0 !important;
                margin-bottom: 0.2rem !important;
            }
            
            /*Formatting for the question boxes */

            .stRadio {
                margin-top: 0 !important;
                margin-bottom: 0.5rem !important;
                gap: 0.25rem !important;
            }

            .stRadio [role="radiogroup"] label p {
                font-size: 18px !important;
                line-height: 1.6 !important;
                color: #bb6528 !important;
                font-weight: bold !important;
            }

            /* Results Box*/

            .results-box {
            background-color: #ffe4b5 !important;
            color: #a0522d ;
            padding: 20px;
            margin: 20px 0;
            font-size: 18px;
            
        }
        </style>
        """, unsafe_allow_html=True)

# Data Loading (load out datasets and store for later use)
#st.cache is a Streamlit decorator that caches the output of a function.
#When you call a function decorated with @st.cache_data, Streamlit stores its result.
#If you call the function again with the same arguments, Streamlit returns the cached result instead of re-running the function.
#This helps speed things up and keep things responsive

@st.cache_data
def load_products():
    product_df = pd.read_excel(PRODUCTS_PATH)

    product_df["tags_clean"] = product_df["tags"].fillna("").apply(
        lambda x: [t.strip().lower() for t in str(x).split(",") if t.strip()]
    )

    product_df["roast_type"] = product_df["roast_type"].fillna("Unknown")
    product_df["origin"] = product_df["origin"].fillna("Unspecified")

    product_df["price_numeric"] = pd.to_numeric(product_df["price_numeric"], errors="coerce")
    product_df["price_per_oz"] = pd.to_numeric(product_df["price_per_oz"], errors="coerce")

    for col in ["decaf", "blend", "single_origin", "available_ground", "has_reviews"]:
        if col in product_df.columns:
            product_df[col] = product_df[col].fillna(False).astype(bool)

    return product_df

@st.cache_data
def load_reviews():
    try:
        reviews_df = pd.read_excel(REVIEWS_PATH, sheet_name=REVIEWS_SHEET)
    except:
        return pd.DataFrame()

    reviews_df["product_name"] = reviews_df["product_name"].astype(str)
    reviews_df["sentiment"] = reviews_df["sentiment"].astype(str).str.lower()

    return reviews_df


products = load_products()
reviews = load_reviews()

# Matching Algorithm 

# Points awarded for matching certain criterea (TODO: tune based on user survey if we do it)
ROAST_POINTS = 3.0
VALUE_WEIGHT = 2.0

def apply_filters(df, survey_results):
    filtered = df.copy()

    # Decaf or Caff
    if survey_results["caffeine"] == "Decaf 😌":
        filtered = filtered[filtered["decaf"] == True]
    else: 
        filtered = filtered[filtered["decaf"] == False]

    # Roast Level
    if survey_results["roast"] != "No preference / I'm not sure":
        filtered = filtered[
            filtered["roast_type"].str.contains(survey_results["roast"], case=False, na=False)
        ]

    # Ground or Whole 
    if survey_results["ground"] == "Pre-ground (no)":
        filtered = filtered[filtered["available_ground"] == True]

    return filtered

def score_products(df, survey_results):
    df = df.copy()
    df["score"] = 0
    df["reason"] = ""

    # Roast match
    if survey_results["roast"] != "No preference / I'm not sure":
        mask = df["roast_type"].str.contains(survey_results["roast"], case=False, na=False)
        df.loc[mask, "score"] += ROAST_POINTS
        df.loc[mask, "reason"] += f"Roast match (+{ROAST_POINTS}). "

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


# Set the website so the starting state is the survey page
if "step" not in st.session_state:
    st.session_state["step"] = "survey"


# What are states? 
# Basically the "state of the website". Changes will be stored,
# but if we don't switch from one state to the next for example
# our survey and results page would be displayed on top of eachother.
# we use st.rerun() to stop the current script and rerun with out updated state 

# Survey Page 
if st.session_state["step"] == "survey":
    st.set_page_config(page_title="Coffee Match", layout="wide")
    st.markdown("<div class='page-title'>Coffee Match</div>",unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>☕ Find the Washington Bean of your Dreams ☕</div>",unsafe_allow_html=True)
    with st.form("survey_form"):

        #Caffeine content 
        st.markdown("<div class='survey-question'>Are you looking for a caffeinated or decaf coffee?</div>", unsafe_allow_html=True)
        q1 = st.radio("",["Caffeinated! 🤩", "Decaf 😌"], label_visibility = "collapsed")

        #Roast preference
        st.markdown("<div class='survey-question'>What's your roast preference?</div>", unsafe_allow_html=True)
        q2 = st.radio("",["Light", "Medium", "Dark", "No preference / I'm not sure"], label_visibility = "collapsed")

        #Ground or Whole
        st.markdown("<div class='survey-question'>Ground or whole beans (do you have a coffee grinder)?</div>", unsafe_allow_html=True)
        q3 = st.radio("",["Whole beans (yes)", "Pre-ground (no)"], label_visibility = "collapsed")
        
        submitted = st.form_submit_button("Find your match!")
        if submitted:
            survey_results = {"caffeine": q1, "roast": q2, "ground": q3,}
            st.session_state["survey_results"] = survey_results
            filtered = apply_filters(products, survey_results)
            st.session_state["scored"] =  score_products(filtered, survey_results)
            st.session_state["step"] = "results"
            st.rerun()

# Results Page!
if st.session_state["step"] == "results":
    scored = st.session_state.get("scored")
    if scored.empty:
        st.warning("No products match your filters :(")
    else:
        st.set_page_config(page_title="Match Results", layout="wide")
        st.markdown("<div class='page-title'>💕 Here are your coffee matches! 💕</div>", unsafe_allow_html=True)
    
        #Top 3 (for now)
        top_3 = scored.head(3)
        
        # Display each match
        for idx, row in top_3.iterrows():
            st.markdown(f"""
            <div class='results-box'>
                <h3>{row['product_name']}</h3>
                <p><b>Score:</b> {row['score']:.2f}</p>
            </div>
            """, unsafe_allow_html=True)