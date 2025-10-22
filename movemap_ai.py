# ============================================
# MoveMap AI — Location Intelligence App (v2)
# Author: Ahadu Mengesha
# Features:
#   - User enters city, ZIP, or address
#   - Finds census tract via coordinates
#   - Tries real Census API
#   - Falls back to generated data if API fails
#   - Calculates housing risk
#   - Displays map + metrics
# ============================================

import os
import random
import requests
import pandas as pd
import numpy as np
import folium
from geopy.geocoders import Nominatim
import streamlit as st
from streamlit_folium import st_folium
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error


# ---------------------------
# Helper Functions
# ---------------------------

def get_location_coords(location_name):
    """Convert user input (like city or ZIP) to coordinates."""
    try:
        geolocator = Nominatim(user_agent="movemap_ai")
        location = geolocator.geocode(location_name)
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        st.error(f"Geocoding error: {e}")
    return None, None


def get_census_tract_from_coords(lat, lon):
    """Use FCC API to find which Census tract a point is in."""
    try:
        url = f"https://geo.fcc.gov/api/census/area?lat={lat}&lon={lon}&format=json"
        r = requests.get(url)
        data = r.json()
        tract = data["results"][0]["block_fips"][:11]
        county_name = data["results"][0]["county_name"]
        state_code = data["results"][0]["state_code"]
        return tract, county_name, state_code
    except Exception as e:
        st.error(f"Tract lookup error: {e}")
        return None, None, None


# ---------------------------
# Data Generation / Census
# ---------------------------

def get_single_tract_data(tract_id, key="YOUR_CENSUS_API_KEY", year="2023"):
    """Try to fetch real Census ACS 5-Year data for a given tract."""
    try:
        state_fips = tract_id[:2]
        county_fips = tract_id[2:5]
        tract_fips = tract_id[5:]
        vars = ["B19013_001E", "B17001_002E"]
        url = (
            f"https://api.census.gov/data/{year}/acs/acs5?"
            f"get=NAME,{','.join(vars)}"
            f"&for=tract:{tract_fips}&in=state:{state_fips}+county:{county_fips}&key={key}"
        )
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            raise ValueError(f"Census API error: {r.status_code}")
        df = pd.DataFrame(r.json()[1:], columns=r.json()[0])
        df.rename(
            columns={
                "B19013_001E": "median_income",
                "B17001_002E": "poverty_count",
            },
            inplace=True,
        )
        df["GEOID"] = state_fips + county_fips + tract_fips
        return df
    except Exception as e:
        st.warning(f"Census API failed: {e}")
        return None


def generate_dummy_census_for_tract(tract_id, name="Tract"):
    """Generate fallback mock census data for a single tract."""
    median_income = random.randint(30000, 90000)
    poverty_count = random.randint(100, 800)
    df = pd.DataFrame([{
        "GEOID": tract_id,
        "NAME": name,
        "median_income": median_income,
        "poverty_count": poverty_count
    }])
    return df


def get_single_tract_data_or_dummy(tract_id, name, key="YOUR_CENSUS_API_KEY", year="2023"):
    """Wrapper: Try Census API, else generate synthetic data."""
    census = get_single_tract_data(tract_id, key, year)
    if census is None or census.empty:
        st.info("⚠️ Using generated data instead of real Census data.")
        census = generate_dummy_census_for_tract(tract_id, name)
    return census


# ---------------------------
# Model + Feature Creation
# ---------------------------

def make_features(census):
    """Add dummy Zillow and eviction data for risk scoring."""
    zillow = pd.DataFrame({
        "region_name": [census["NAME"][0]],
        "rent_change_12m": [round(random.uniform(0.02, 0.12), 3)]
    })
    ev = pd.DataFrame({
        "GEOID": [census["GEOID"][0]],
        "eviction_rate": [round(random.uniform(1, 10), 2)]
    })

    df = census.merge(ev, on="GEOID", how="left")
    df = df.merge(zillow, left_on="NAME", right_on="region_name", how="left")
    df["rent_income_ratio"] = df["rent_change_12m"] / df["median_income"].astype(float)
    df["risk_score"] = (
        0.5 * (df["rent_income_ratio"].fillna(0))
        + 0.3 * (df["poverty_count"].astype(float) / 1000)
        + 0.2 * (df["eviction_rate"].fillna(0) / 10)
    ) * 100
    return df


def train_model(df):
    """Train a Random Forest model, or handle single-sample case."""
    X = df[["median_income", "poverty_count", "eviction_rate", "rent_income_ratio"]].fillna(0)
    y = df["risk_score"]

    if len(df) < 5:
        # Too few samples — just simulate prediction
        df["predicted_risk"] = df["risk_score"]
        mae = 0
        model = None
    else:
        from sklearn.model_selection import train_test_split
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.metrics import mean_absolute_error

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestRegressor(n_estimators=200, random_state=42)
        model.fit(X_train, y_train)
        mae = mean_absolute_error(y_test, model.predict(X_test))
        df["predicted_risk"] = model.predict(X)

    return model, df, mae



def make_map(lat, lon, df, location_name):
    """Create a Folium map centered on the user input location."""
    m = folium.Map(location=[lat, lon], zoom_start=13)
    folium.Marker(
        [lat, lon],
        popup=f"{location_name}<br>Predicted Risk: {df['predicted_risk'].iloc[0]:.2f}",
        icon=folium.Icon(color="red", icon="home"),
    ).add_to(m)
    return m


# ---------------------------
# Streamlit UI
# ---------------------------

st.set_page_config(page_title="MoveMap AI", layout="wide")
st.title("🏙️ MoveMap AI — Explore Housing Equity by Location")

st.markdown("""
Type a **city**, **ZIP code**, or **address** to analyze.
If real U.S. Census data isn't available, this app will automatically
generate plausible data for demonstration purposes.
""")

user_input = st.text_input("📍 Enter a location:", "Knoxville, TN")

if st.button("Analyze Location"):
    with st.spinner("Looking up your area..."):
        st.write("🔍 Step 1: Getting coordinates...")
        lat, lon = get_location_coords(user_input)
        st.write("Coordinates:", lat, lon)

        if lat is None:
            st.error("❌ Location not found. Please try a valid city or ZIP.")
        else:
            st.write("🔍 Step 2: Finding census tract...")
            tract_id, county, state = get_census_tract_from_coords(lat, lon)
            st.write("Tract:", tract_id, "| County:", county, "| State:", state)

            if tract_id is None:
                st.error("❌ Could not find tract for this location.")
            else:
                st.success(f"✅ Found tract {tract_id} in {county}, {state}")

                st.write("📥 Step 3: Getting Census or generated data...")
                census = get_single_tract_data_or_dummy(tract_id, name=user_input)
                st.write("Census dataframe shape:", census.shape if census is not None else None)

                if census is None or census.empty:
                    st.error("❌ No data (even dummy) could be created.")
                else:
                    st.write("✅ Data ready. Now computing features...")
                    df = make_features(census)
                    st.write("Data sample:", df.head())

                    st.write("⚙️ Step 4: Running model...")
                    model, df, mae = train_model(df)

                    st.subheader("📊 Neighborhood Data")
                    st.write(df[["NAME", "median_income", "poverty_count", "eviction_rate", "rent_change_12m"]])

                    st.subheader("🔍 Predicted Risk Score")
                    risk_val = df["predicted_risk"].iloc[0]
                    st.metric(label="Predicted Risk (0–100)", value=f"{risk_val:.2f}")

                    st.caption(f"Model Mean Absolute Error (synthetic test): {mae:.2f}")

                    # Map
                    st.subheader("🗺️ Map View")
                    m = make_map(lat, lon, df, user_input)
                    st_folium(m, width=700, height=500)

        st.write("✅ Done.")

