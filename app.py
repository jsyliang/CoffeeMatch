import streamlit as st
import pandas as pd
from pathlib import Path
from coffeematch_core.data_loader import load_datasets
from coffeematch_core.schemas import UserPreferences
from coffeematch_core.feature_engineering import build_feature_table
from coffeematch_core.recommendation_engine import recommend_products

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
                font-size: 96px;
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
                margin-bottom: 2.5rem;
                margin-top: 0;
            }

            /*Survey Box*/
            .stForm{
            background-color: #ffe4b5 !important;
            }

            .stForm > div:first-child {
            padding-top: 30px;
            }

            /*Align slider vertically to center of its column*/
            [data-testid="stSlider"] {
                margin-top: auto;
                margin-bottom: auto;
                padding-top: 1rem;
            }

            /* Make paired columns stretch to match each other's height */
            [data-testid="stHorizontalBlock"] {
                align-items: center !important;  /* vertically center column contents */
            }

            /*Visual divider between question rows*/
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

            /* Submit Button */
            div.stFormSubmitButton {
            display: flex;
            justify-content: center;
            }
 
            div.stFormSubmitButton > button {
            background-color: #D6859C;
            color: white;
            border: none;
            border-radius: 20px;
            padding: 10px 30px;
            }

            div.stFormSubmitButton > button:hover {
                background-color: #BF4064;
                color: white;
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
def load_data() -> pd.DataFrame:
    """Load the cleaned products dataset."""
    return load_datasets()


@st.cache_data
def load_feature_table(products_df: pd.DataFrame) -> pd.DataFrame:
    """Build the product-level feature table once per app session."""
    return build_feature_table(products_df)


products_df, reviews_df, product_info_df = load_data()
feature_table = load_feature_table(products_df)

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
    st.markdown("<div class='page-subtitle'>Find the Washington Bean of your Dreams</div>",unsafe_allow_html=True)
    
    with st.form("survey_form"):

        # Header Qs
        col_q1, col_s1 = st.columns([1, 1])
        
        with col_q1:
            st.markdown("<div class='slider-question'>"
                        "<i style='font-size:30px; color: #a0522d; white-space: pre;'>"
                        "☕   ☕   ☕   Coffee Questions   ☕   ☕   ☕"
                        "</i>"
                        "<br><br>"
                        "</div>", 
                        unsafe_allow_html=True)
        
        with col_s1:
            st.markdown("<div class='slider-question'>"
                        "<i style='font-size:30px; white-space: pre;'>"
                        "♥    ♥    ♥    Match Maker Weights    ♥    ♥    ♥"
                        "</i>"
                        "<br><br>"
                        "</div>", 
                        unsafe_allow_html=True)
        

        #Origin Preference - Boolean True if single origin, also weights for price in 2nd column 
        col_q2, col_s2 = st.columns([1, 1])
        
        with col_q2:
            st.markdown("<div class='survey-question'>"
                        "Are you only interested in single origin beans?"
                        "</div>",
                        unsafe_allow_html=True)
            a2 = st.radio("",["Single origin only", "No preference"], label_visibility = "collapsed")
       
        with col_s2:
            st.markdown("<div class='slider-question'>"
                        "Importance of lower price (1 = least, 5 = most)"
                        "</div>", 
                        unsafe_allow_html=True)
            a6 = st.slider("Price importance", 1, 5, 5, label_visibility="collapsed")

        #Ground or Whole - Boolean True is ground required, also popularity weights in second column  
        col_q3, col_s3 = st.columns([1, 1])
        
        with col_q3:
            st.markdown("<div class='survey-question'>"
                        "Ground or whole beans (do you have a grinder)?"
                        "</div>", 
                        unsafe_allow_html=True)
            a3 = st.radio("", ["Whole beans (yes)", "Pre-ground (no)"], label_visibility="collapsed")
        
        with col_s3:
            st.markdown("<div class='slider-question'>"
                        "Importance of product popularity (1 = least, 5 = most)"
                        "</div>", 
                        unsafe_allow_html=True)
            a7 = st.slider("Popularity importance", 1, 5, 3, label_visibility="collapsed")

        #Roast preference - importance of weight (float) and string 
        col_q4, col_s4 = st.columns([1, 1])
        
        with col_q4:
            st.markdown("<div class='survey-question'>"
                        "What's your roast preference?"
                        "</div>", 
                        unsafe_allow_html=True)
            a4 = st.radio("Roast", ["Light", "Medium", "Dark", "No preference / I'm not sure"], label_visibility="collapsed")

        with col_s4:
            st.markdown("<div class='slider-question'>"
                        "Importance of roast preference (1 = least, 5 = most)"
                        "</div>", 
                        unsafe_allow_html=True)
            a5 = st.slider("Roast importance", 1, 5, 3, label_visibility="collapsed")

        #Caffeine content - Boolean True if decaf 
        col_q5, col_s5 = st.columns([1, 1])
        
        with col_q5:
            st.markdown("<div class='survey-question'>Are you looking for a caffeinated or decaf coffee?</div>", unsafe_allow_html=True)
            a1 = st.radio("",["Caffeinated! 🤩", "Decaf 😌"], label_visibility = "collapsed")
        
        with col_s5:
            st.markdown("", unsafe_allow_html=True) # Empty 


        submitted = st.form_submit_button("Find your matches!")
        if submitted:
            
            # redefine survey responses 
            if a1 == 'Decaf 😌':
                a1 = True
            else:
                a1 = False

            if a2 == 'Single origin only':
                a2 = True
            else:
                a2 = False
            
            if a3 == 'Pre-ground (no)':
                a3 = True
            else:
                a3 = False
            
            # create user preferences 
            survey_results = UserPreferences(
                roast_type= a4,
                decaf= a1,
                ground_required= a3,
                single_origin_preference= a2,
                roast_weight= float(a5),
                price_weight= float(a6),
                popularity_weight= float(a7) 
            )

            recommendations = recommend_products(
                feature_table=feature_table,
                products_df=products_df,
                reviews_df=reviews_df,
                product_info_df=product_info_df,
                preferences=survey_results,
                top_n=5, # could make a UI for how many matches the user wants to see 
            )
            
            st.session_state["survey_results"] = recommendations 
            st.session_state["step"] = "results"
            st.rerun()

# Results Page!

if st.session_state["step"] == "results":
    st.set_page_config(page_title="Match Results")
    
    survey_results = st.session_state.get("survey_results")

    # if survey_results.empty:
    #     st.warning("No products match your filters :(")
    if False:
        pass
    else:
        st.set_page_config(page_title="Match Results", layout="wide")
        st.markdown("<div class='page-title'>💕 Here are your coffee matches! 💕</div>", unsafe_allow_html=True)
        
        # Display each match
        for rank, rec in enumerate(survey_results, start=1):

            #Preload a few strings to avoid doing stuff in the html
            if rec.cafe_location and rec.cafe_location.cafe_address and rec.cafe_location.google_maps_url:
                cafe_info = (
                    f"{rec.cafe_location.cafe_name}<br>"
                    f"<span style='font-size:12px;'>"
                    f"<a href='{rec.cafe_location.google_maps_url}' target='_blank'>{rec.cafe_location.cafe_address}</a>"
                    f"</span>"
                )
            elif rec.cafe_location and rec.cafe_location.cafe_name:
                cafe_info = rec.cafe_location.cafe_name
            else:
                cafe_info = "No cafes for this product"
                    
            sizes_str = ', '.join(f"{s.size} (${s.price_numeric:.2f})" for s in rec.available_sizes)
            tasting_str = ', '.join(dict.fromkeys(str(t) for t in rec.tasting_notes))
            rec.score = rec.score * 100

            #Html code 
            result_html = (
                f"<div class='results-box'>"                          # open parent
                    f"<div class='result-sub-box'>"                   # open child 1
                        f"<span class='sub-box-value' style='font-size:24px; color:#BF4064;'>{rec.product_name} <br> "
                        f"<span style='font-size:14px; color:#D6859C;'>{rec.roast_type}</span><br>"
                        f"<span style='font-size:14px; color:#D6859C;'>Roaster: {rec.roaster}</span><br>"
                        f"<span style='font-size:14px; color:#D6859C;'>Notes: {tasting_str}</span></span>"
                    f"</div>"                                         # close child 1
                    f"<div class='result-sub-box'>"                   # open child 2  #D6859C
                        f"<span class='sub-box-label'><u>Match Score</u></span>"
                        f"<span class='sub-box-value'>{rec.score:.0f}%</span>"
                    f"</div>"                                         # close child 2
                    f"<div class='result-sub-box'>"                   # open child 3
                        f"<span class='sub-box-label'><u>Products</u></span>"
                        f"<span class='sub-box-value'>{sizes_str}</span>"
                    f"</div>"                                         # close child 3
                    f"<div class='result-sub-box'>"                   # open child 4
                        f"<span class='sub-box-label'><u>Try Before you Buy</u></span>"
                        f"<span class='sub-box-value'>{cafe_info}</span>"
                    f"</div>"                                         # close child 4
                f"</div>"                                             # close parent
            )
            st.markdown(result_html, unsafe_allow_html=True)