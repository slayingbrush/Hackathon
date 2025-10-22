import pandas as pd
import random
import requests
from geopy.geocoders import Nominatim
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error


def get_location_coords(location_name):
    """Convert location name to coordinates."""
    try:
        geolocator = Nominatim(user_agent="movemap_ai")
        loc = geolocator.geocode(location_name)
        return (loc.latitude, loc.longitude) if loc else (None, None)
    except Exception:
        return None, None


def get_census_tract_from_coords(lat, lon):
    """Find Census tract via FCC API."""
    try:
        url = f"https://geo.fcc.gov/api/census/area?lat={lat}&lon={lon}&format=json"
        r = requests.get(url)
        d = r.json()
        t = d["results"][0]["block_fips"][:11]
        return t, d["results"][0]["county_name"], d["results"][0]["state_code"]
    except Exception:
        return None, None, None


def generate_dummy_census_for_tract(tract_id, name="Tract"):
    """Generate mock Census-style data."""
    return pd.DataFrame([{
        "GEOID": tract_id,
        "NAME": name,
        "median_income": random.randint(35000, 95000),
        "poverty_count": random.randint(100, 900),
        "eviction_rate": random.uniform(1, 10),
        "rent_change_12m": random.uniform(0.02, 0.1)
    }])


def make_features(census):
    df = census.copy()
    df["rent_income_ratio"] = df["rent_change_12m"] / df["median_income"]
    df["risk_score"] = (
        0.5 * df["rent_income_ratio"] +
        0.3 * (df["poverty_count"] / 1000) +
        0.2 * (df["eviction_rate"] / 10)
    ) * 100
    return df


def train_model(df):
    """Train model or fallback for small samples."""
    X = df[["median_income", "poverty_count", "eviction_rate", "rent_income_ratio"]]
    y = df["risk_score"]
    if len(df) < 5:
        df["predicted_risk"] = df["risk_score"]
        return None, df, 0
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(Xtr, ytr)
    mae = mean_absolute_error(yte, model.predict(Xte))
    df["predicted_risk"] = model.predict(X)
    return model, df, mae
