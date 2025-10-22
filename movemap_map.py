import folium


def make_map(lat, lon, df, loc_name):
    """Create Folium map with colored marker."""
    m = folium.Map(location=[lat, lon], zoom_start=13)
    r = df["predicted_risk"].iloc[0]
    color = "green" if r < 40 else "orange" if r < 70 else "red"
    html = (
        f"<b>{loc_name}</b><br>"
        f"Median Income: ${int(df['median_income'].iloc[0]):,}<br>"
        f"Poverty Count: {int(df['poverty_count'].iloc[0])}<br>"
        f"Eviction Rate: {df['eviction_rate'].iloc[0]:.1f}%<br>"
        f"Risk Score: <b>{r:.1f}</b>"
    )
    folium.CircleMarker(
        [lat, lon], radius=10, color=color,
        fill=True, fill_color=color, fill_opacity=0.8, popup=html
    ).add_to(m)
    return m
