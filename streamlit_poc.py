import streamlit as st
import pandas as pd

# Paths to data 
PRODUCTS_PATH = "data/raw/Product_Information.xlsx"
REVIEWS_PATH = "data/raw/Reviews_and_Tasting_Notes.xlsx"
REVIEWS_SHEET = "Reviews with Tasting Notes"

# Set up styling for use in the website 
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
                margin-bottom: 0 !important;
                gap: 0 !important;
            }
            
            /*Page Subtitles*/
            .page-subtitle {
                font-size: 44px;
                color: #a0522d;
                font-family: 'Brush Script MT', cursive, sans-serif;
                text-align: center;
                margin-bottom: 1.5rem;
                margin-top: 0;
            }

            /*Survey Box*/
            .stForm{
            background-color: #ffe4b5 !important;
            }

            /* Align slider vertically to center of its column */
            [data-testid="stSlider"] {
                margin-top: auto;
                margin-bottom: auto;
                padding-top: 1rem;
            }

            /* Make paired columns stretch to match each other's height */
            [data-testid="stHorizontalBlock"] {
                align-items: center !important;  /* vertically center column contents */
            }

            /* Visual divider between question rows */
            .survey-row-divider {
                border-top: 1px solid #c49a6c;
                margin: 1rem 0;
                width: 100%;
            }

            /*Formatting for the text to go above questions in the survey*/
            .survey-question {
                font-size: 24px;
                color: #a0522d ; 
                font-weight: bold;
                margin: 0;
                padding: 0;
                margin-bottom: 0.2rem;
            }

            /*Formatting for the text to go above sliders*/
            .slider-question {
                font-size: 24px;
                color: #BF4064 ; 
                font-weight: bold;
                margin: 0;
                padding: 0;
                margin-bottom: 0.2rem;
            }
            
            /*Formatting for the question boxes */
            .stRadio {
                margin-top: 0 !important;
                margin-bottom: 0.5rem !important;
                gap: 0.25rem !important;
            }

            .stRadio [role="radiogroup"] label p {
                font-size: 18px;
                line-height: 1.6;
                color: #bb6528;
                font-weight: bold;
            }
            
            /* Slider */

            /* Nuke ALL backgrounds inside slider */
            [data-testid="stSlider"] * {
                background: transparent !important;
                background-color: transparent !important;
                box-shadow: none !important;
            }

            /* Repaint the track — target by height (the thin bar) */
            [data-baseweb="slider"] div[style*="height: 0.2"] {
                background: #D6859C !important;
                background-color: #D6859C !important;
            }

            /* Target ALL st-c* track class divs inside slider */
            [data-baseweb="slider"] div[class*="st-c"] {
                background: #D6859C !important;
                background-color: #D6859C !important;
            }

            /* NOT the outer flex container or thumb */
            [data-baseweb="slider"] > div[class*="st-c"] {
                background: transparent !important;
                background-color: transparent !important;
            }

            /* Hide default thumb */
            [data-testid="stSlider"] [role="slider"] {
                background: transparent !important;
                background-color: transparent !important;
                border: none !important;
                box-shadow: none !important;
                width: 30px !important;
                height: 30px !important;
                top: -6px !important;
                position: relative !important;
            }

            /* Heart thumb */
            [data-testid="stSlider"] [role="slider"]::before {
                content: "♥";
                font-size: 28px;
                color: #D6859C;
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                line-height: 1;
            }

            /* Current value above thumb */
            [data-testid="stSlider"] [role="slider"] div,
            [data-testid="stSlider"] [role="slider"] div * {
                color: #D6859C !important;
                background: transparent !important;
                background-color: transparent !important;
                font-weight: bold;
            }

            /* Tick bar container */
            [data-testid="stSliderTickBar"] {
                background: transparent !important;
                background-color: transparent !important;
                display: flex !important;
                justify-content: space-between !important;
                width: 100% !important;
            }

            /* Position tick labels */
            [data-testid="stSliderTickBar"] [data-testid="stMarkdownContainer"]:first-child {
                text-align: left !important;
                order: 1;
            }

            [data-testid="stSliderTickBar"] [data-testid="stMarkdownContainer"]:last-child {
                text-align: right !important;
                order: 2;
            }

            /* The actual "1" and "5" text */
            [data-testid="stSliderTickBar"] [data-testid="stMarkdownContainer"] p {
                color: #D6859C !important;
                background: transparent !important;
                background-color: transparent !important;
                margin: 0 !important;
                font-weight: bold;
            }

            /* Results Box*/
            .results-box {
            display: flex;
            flex-direction: row;
            flex-wrap: wrap;
            align-items: stretch;
            gap: 15px;
            justify-content: space-between;
            background-color: #ffe4b5;
            color: #a0522d ;
            padding: 5px;
            margin: 15px 0;
            font-size: 18px;
            width: 100%;
            box-sizing: border-box;
            border-radius: 12px;
            }

            [data-testid="stMarkdownContainer"] {
                width: 100%;
            }

            /* Results Box Children*/
            .result-sub-box{
            flex: 1 1 150px;  /* grow | shrink | start min width */
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background-color: #ffe4b5;
            color: #a0522d;
            font-weight: bold;
            font-size: 18px;
            text-align: center;
            box-sizing: border-box;
            min-height: 100px;
            border-radius: 8px;
            }

            .sub-box-label {
                font-size: 1.4rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: #6B3920;
                margin-bottom: 4px;
            }

            .sub-box-value {
                font-size: 1.2 rem;
                font-weight: 700;
                color: #a0522d;
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

# Points awarded for matching certain criterea
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

    roast_pref_points = survey_results.get("roast_pref_points", 3)

    # Roast match
    if survey_results["roast"] != "No preference / I'm not sure":
        mask = df["roast_type"].str.contains(survey_results["roast"], case=False, na=False)
        df.loc[mask, "score"] += roast_pref_points
        df.loc[mask, "reason"] += f"Roast match (+{roast_pref_points}). "

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

        # Caffeine
        st.markdown("<div class='survey-question'>Are you looking for a caffeinated or decaf coffee?</div>", unsafe_allow_html=True)
        q1 = st.radio("", ["Caffeinated!⚡", "Decaf 😌"], label_visibility="collapsed")

        st.markdown("<div class='survey-row-divider'></div>", unsafe_allow_html=True)

        # Roast Level
        col_q2, col_s2 = st.columns([1, 1])
        with col_q2:
            st.markdown("<div class='survey-question'>What's your roast preference?</div>", unsafe_allow_html=True)
            q2 = st.radio("Roast", ["Light", "Medium", "Dark", "No preference / I'm not sure"], label_visibility="collapsed")
        with col_s2:
            st.markdown("<div class='slider-question'>How important is roast for your match? (1 = least, 5 = most)</div>", unsafe_allow_html=True)
            q4 = st.slider("Roast importance", 1, 5, 3, label_visibility="collapsed")

        st.markdown("<div class='survey-row-divider'></div>", unsafe_allow_html=True)

        # Ground/Whole
        col_q3, col_s3 = st.columns([1, 1])
        with col_q3:
            st.markdown("<div class='survey-question'>Ground or whole beans (do you have a grinder)?</div>", unsafe_allow_html=True)
            q3 = st.radio("Ground", ["Whole beans (yes)", "Pre-ground (no)"], label_visibility="collapsed")
        with col_s3:
            st.markdown("<div class='slider-question'>How important is ground status for your match? (1 = least, 5 = most)</div>", unsafe_allow_html=True)
            q5 = st.slider("Ground importance", 1, 5, 2, label_visibility="collapsed")

        st.markdown("<div class='survey-row-divider'></div>", unsafe_allow_html=True)

        submitted = st.form_submit_button("Find your match!")

        # make sure that after when the user submits, the data is in the cals form UserPreferences and then we apply the filters 
        # and scoring to get the results page to display the matches based on the survey results.
        # then the class recommendations can be used to display the results in a nice format 
        # (with the reason for the score and all that fun stuff)
       
        if submitted:

            survey_results = {
                "caffeine": q1,
                "roast": q2,
                "roast_pref_points": q4,
                "ground": q3,
                "grind_pref_points": q5,
            }
            st.session_state["survey_results"] = survey_results
            filtered = apply_filters(products, survey_results)
            st.session_state["scored"] = score_products(filtered, survey_results)
            st.session_state["step"] = "results"
            st.rerun()

# Results Page!
if st.session_state["step"] == "results":
    st.set_page_config(page_title="Match Results")
    scored = st.session_state.get("scored")
    if scored.empty:
        st.warning("No products match your filters :(")
    else:
        st.set_page_config(page_title="Match Results", layout="wide")
        st.markdown("<div class='page-title'>💕 Here are your coffee matches! 💕</div>", unsafe_allow_html=True)

        #Top 3 (for now)
        top_3 = scored.head(3)
        match = 0
        
        # Display each match
        for idx, row in top_3.iterrows():
            match += 1
            result_html = (
                f"<div class='results-box'>"                          # open parent
                    f"<div class='result-sub-box'>"                   # open child 1
                        f"<span class='sub-box-label'>Match #{match}</span>"
                        f"<span class='sub-box-value'>{row['product_name']}</span>"
                    f"</div>"                                         # close child 1
                    f"<div class='result-sub-box'>"                   # open child 2
                        f"<span class='sub-box-label'>Match Score</span>"
                        f"<span class='sub-box-value'>{row['score']:.2f}/5</span>"
                    f"</div>"                                         # close child 2
                    f"<div class='result-sub-box'>"                   # open child 3
                        f"<span class='sub-box-label'>Price per oz</span>"
                        f"<span class='sub-box-value'>${row['price_per_oz']:.2f}</span>"
                    f"</div>"                                         # close child 3
                f"</div>"                                             # close parent
            )
            st.markdown(result_html, unsafe_allow_html=True)
