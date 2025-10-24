
# MoveMap AI 


import streamlit as st
from streamlit_folium import st_folium

from movemap_helpers import (
    get_location_coords,
    get_census_tract_from_coords,
    generate_dummy_census_for_tract,
    make_features,
    train_model,
    make_synthetic_dataset,
    train_model_on_train_test,
)
from movemap_map import make_map
import movemap_ui as ui


st.set_page_config(page_title="MoveMap AI", layout="wide", page_icon="🏙️")
ui.inject_css()

# (helper functions and map are moved into movemap_helpers.py and movemap_map.py)

# Sidebar

import os
local_logo = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
if os.path.exists(local_logo):
    st.sidebar.image(local_logo, width=120)
else:
    st.sidebar.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/City_skyline_icon.svg/1200px-City_skyline_icon.svg.png",
        width=100,
    )
st.sidebar.title("MoveMap AI")
st.sidebar.markdown(
    "Visualize **housing risk and equity** using simulated data and AI modeling."
)
st.sidebar.markdown("---")
st.sidebar.caption("Developed by UTK NSBE")


#  Main Interface

st.title("MoveMap AI — Intelligent Housing Risk Explorer")
st.write(
    "Enter any **city, ZIP code, or neighborhood** to visualize "
    "housing affordability and displacement risk."
)

# ---------------- Session State ------------------
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "results" not in st.session_state:
    st.session_state.results = {}

user_input = st.text_input("Search for a location:", "Knoxville, TN")

# Button Logic 
if st.button("Analyze Location"):
    progress_placeholder = st.empty()
    loading_container = progress_placeholder.container()
    
    with st.spinner(""):
        # Create a multi-column layout for the loading animation
        col1, col2, col3 = loading_container.columns([1, 3, 1])
        
        # Initialize progress and status
        progress_bar = col2.progress(0)
        status_text = col2.empty()
        
        # Step 1: Getting coordinates (use centralized ui.loading_html)
        status_text.markdown(ui.loading_html("🔍", "Locating coordinates..."), unsafe_allow_html=True)
        progress_bar.progress(20)
        lat, lon = get_location_coords(user_input)
        
        if lat is None:
            loading_container.empty()
            st.error(" Location not found. Try another search.")
        else:
            # Step 2: Finding census tract
            status_text.markdown(ui.loading_html("📍", "Analyzing neighborhood boundaries..."), unsafe_allow_html=True)
            progress_bar.progress(40)
            tract_id, county, state = get_census_tract_from_coords(lat, lon)
            
            if tract_id is None:
                loading_container.empty()
                st.error(" Could not find tract for this location.")
            else:
                # Step 3: Generating and analyzing data
                status_text.markdown(ui.loading_html("🏘️", "Processing neighborhood metrics..."), unsafe_allow_html=True)
                progress_bar.progress(60)
                census = generate_dummy_census_for_tract(tract_id, user_input)
                
                # Simulated delay for visual effect
                import time
                time.sleep(0.5)
                
                status_text.markdown(ui.loading_html("🤖", "Running AI risk analysis..."), unsafe_allow_html=True)
                progress_bar.progress(80)

                # Create separate synthetic datasets for train and test so the model must generalize
                train_df = make_synthetic_dataset(tract_id, user_input, n=50)
                test_df = make_synthetic_dataset(tract_id, user_input, n=20)

                # Compute features and risk scores for both
                train_df = make_features(train_df)
                test_df = make_features(test_df)

                # Compute features for the single-census sample we'll predict for
                predict_df = make_features(census)

                # Train on train_df and evaluate on test_df
                model, pred_df, mae = train_model_on_train_test(train_df, test_df, predict_df)

                # If the training function returned predictions, use that for display
                if pred_df is not None and "predicted_risk" in pred_df.columns:
                    df = pred_df
                else:
                    # Fallback: show the single sample with its true risk
                    df = predict_df
                
                # Final animation
                status_text.markdown(ui.loading_html("✨", "Preparing your custom visualization..."), unsafe_allow_html=True)
                progress_bar.progress(100)
                
                # Add a small delay for the final animation
                time.sleep(0.3)
                
                st.session_state.results = {
                    "lat": lat, "lon": lon, "county": county, "state": state,
                    "df": df, "mae": mae, "risk": df.get("predicted_risk", df.get("risk_score")).iloc[0]
                }
                st.session_state.analysis_done = True
                
                # Clear the loading animation and rerun
                loading_container.empty()
                st.rerun()

# ---------------- Display Results ----------------
if st.session_state.analysis_done:
    r = st.session_state.results
    df = r["df"]

    st.subheader(" Neighborhood Data")
    st.dataframe(
        df[["median_income", "poverty_count", "eviction_rate", "rent_change_12m"]],
        use_container_width=True
    )

    st.metric("Predicted Risk (0-100)", f"{r['risk']:.2f}")
    st.caption("Color Scale: 🟢 Low  | 🟠 Moderate  | 🔴 High")

    st.subheader("🗺️ Map Visualization")
    m = make_map(r["lat"], r["lon"], df, user_input)
    st_folium(m, width=900, height=550)

    st.caption(f"Model (synthetic) MAE: {r['mae']:.2f}")

# ---------------- Reset Option -------------------
if st.sidebar.button("Reset Session"):
    st.session_state.analysis_done = False
    st.session_state.results = {}
    st.rerun()  # ✅ simple reset
