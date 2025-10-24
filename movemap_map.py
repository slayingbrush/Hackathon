import folium
import numpy as np


def scale_color(risk_value):
    """Create a color scale based on risk value from 0-100."""
    # Define color scale from green to red
    colors = ['#2ECC40', '#FFDC00', '#FF851B', '#FF4136', '#85144b']  # green, yellow, orange, red, dark red
    # Create scale points (0, 25, 50, 75, 100)
    scale_points = np.linspace(0, 100, len(colors))
    
    # Find the two colors to interpolate between
    for i in range(len(scale_points) - 1):
        if scale_points[i] <= risk_value <= scale_points[i + 1]:
            # Calculate the position between the two colors (0-1)
            pos = (risk_value - scale_points[i]) / (scale_points[i + 1] - scale_points[i])
            
            # Convert hex to RGB for interpolation
            c1 = tuple(int(colors[i][j:j+2], 16) for j in (1, 3, 5))
            c2 = tuple(int(colors[i+1][j:j+2], 16) for j in (1, 3, 5))
            
            # Interpolate RGB values
            rgb = tuple(int(c1[j] + (c2[j] - c1[j]) * pos) for j in range(3))
            
            # Convert back to hex
            return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
    
    # Handle edge cases
    return colors[-1] if risk_value > 100 else colors[0]


def make_map(lat, lon, df, loc_name):
    """Create Folium map with colored marker."""
    m = folium.Map(location=[lat, lon], zoom_start=13)
    
    # Create color scale
    colors = ['#2ECC40', '#FFDC00', '#FF851B', '#FF4136', '#85144b']  # green, yellow, orange, red, dark red
    colormap = folium.LinearColormap(
        colors=colors,
        vmin=0, vmax=100,
        caption='Risk Index (0-100)'
    )
    colormap.add_to(m)
    
    r = df["predicted_risk"].iloc[0]
    color = scale_color(r)
    html = (
        f"<b>{loc_name}</b><br>"
        f"Median Income: ${int(df['median_income'].iloc[0]):,}<br>"
        f"Poverty Count: {int(df['poverty_count'].iloc[0])}<br>"
        f"Eviction Rate: {df['eviction_rate'].iloc[0]:.1f}%<br>"
        f"Risk Score: <b>{r:.1f}</b>"
    )
    folium.CircleMarker(
        [lat, lon], radius=20, color=color,
        fill=True, fill_color=color, fill_opacity=0.8, popup=html,
        weight=2  # Add a slightly thicker border
    ).add_to(m)
    return m
