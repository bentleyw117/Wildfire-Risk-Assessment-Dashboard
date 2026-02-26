import streamlit as st
import pycountry as pc
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from wildfire_risk_dashboard.src.wildfire_risk_dashboard import utils
import wildfire_risk_dashboard.src.wildfire_risk_dashboard.wildfire_risk_dashboard as wrd

# --- Helper Functions ---
def display_risk_gauge(score):
    # Determine color based on risk level
    if score < 33:
        color = "#2ecc71"  # Green
        label = "LOW"
    elif score < 66:
        color = "#f39c12"  # Orange
        label = "MODERATE"
    else:
        color = "#e74c3c"  # Red
        label = "HIGH"

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        title = {'text': f"Risk Level: {label}", 'font': {'size': 24}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 33], 'color': 'rgba(46, 204, 113, 0.3)'},
                {'range': [33, 66], 'color': 'rgba(243, 156, 18, 0.3)'},
                {'range': [66, 100], 'color': 'rgba(231, 76, 60, 0.3)'}
            ],
        }
    ))
    
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    return fig


def display_map(lat, lon, radius):
    # Ensure radius is a float to prevent scaling bugs
    radiusMeters = float(radius)
    
    # Create the base map using satellite imagery
    m = folium.Map(
        location=[lat, lon], 
        zoom_start=16, 
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google'
    )

    # Add a marker for the center point
    folium.Marker([lat, lon], popup="Assessment Center").add_to(m)

    # Add the radius circle
    folium.Circle(
        radius=radiusMeters,
        location=[lat, lon],
        color="crimson",
        fill=True,
        fill_color="crimson",
        fill_opacity=0.2,
        tooltip=f"Analyzing {radiusMeters} meter radius",
        popup=f"{radius}m Assessment Area"
    ).add_to(m)

    return m


# --- Page Configuration ---
st.set_page_config(page_title="Wildfire Risk Assessment", page_icon="🔥", layout="wide")
st.title("🔥 Wildfire Risk Assessment")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("📍 Location Inputs")
    try:
        zipCode = st.text_input("Zip Code", placeholder="eg. 57104")
        countryCode = st.text_input("Country Code", value="US", help="Use ISO Alpha-2 (e.g., US, CA, GB)")
        int(zipCode) # Guard against non-numeric
        if not pc.countries.get(alpha_2=countryCode): # Guard against non-countrycode
            raise ValueError
    except ValueError:
        st.warning(f"⚠️ Invalid zip code or country code")

    radius = st.slider("Assessment Radius (meters)", 10, 500, 30)

    calculateButton = st.button("Calculate Risk Score", type="primary")

# --- Initialize Session State ---
if "risk_results" not in st.session_state:
    st.session_state.risk_results = None

# --- Main App Logic ---
if calculateButton:
    if not zipCode or not countryCode:
        st.error("Please provide both a Zip Code and Country Code.")
    else:
        try:
            with st.spinner("Analyzing environment..."):
                # Get Geo-Coordinates
                geoData = utils.get_geo_coordinates(zipCode, countryCode)
                latitude, longitude = utils.grab_coordinates(geoData)

                # Weather Processing
                weatherData = utils.get_weather_data(latitude, longitude)
                tempScore = wrd.normalize_temperature(weatherData)
                humidityScore = wrd.normalize_humidity(weatherData)
                windScore = wrd.normalize_wind_speed(weatherData)
                weatherScore = wrd.calculate_weather_score(tempScore, humidityScore, windScore)

                # Fuel/NDVI Processing
                try:
                    ndvi = utils.get_ndvi(latitude, longitude, radius)
                    fuelScore = wrd.normalize_fuel(ndvi) # normalizing NDVI
                except utils.SatelliteDataError as e:
                    st.warning(f"⚠️ Fuel Risk Unavailable: {e}")
                    fuelScore = 0

                # Topograpgy Processing
                neighboringCoords = wrd.get_neighboring_coords(latitude, longitude, radius)
                elevationData = utils.get_elevation_data(neighboringCoords)
                elevations = wrd.grab_elevations(elevationData)
                slope = wrd.get_steepness(elevations, neighboringCoords)
                slopeScore = wrd.normalize_slope(slope)

                # Final Calculation
                riskScore = wrd.calculate_risk_score(weatherScore, fuelScore, slopeScore)

                # Save everything to session state
                st.session_state.risk_results = {
                    "riskScore": riskScore,
                    "weatherScore": weatherScore,
                    "fuelScore": fuelScore,
                    "slopeScore": slopeScore,
                    "lat": latitude,
                    "lon": longitude,
                    "radius": radius
                }

                
                
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Persistent display logic
if st.session_state.risk_results:
    results = st.session_state.risk_results
    riskScore = results["riskScore"]
    weatherScore = results["weatherScore"]
    fuelScore = results["fuelScore"]
    slopeScore = results["slopeScore"]
    latitude = results["lat"]
    longitude = results["lon"]
    radius = results["radius"]

    if riskScore >= 66:
        st.error(f"### CURRENT RISK: HIGH ({riskScore}%)")
    elif riskScore >= 33:
        st.warning(f"### CURRENT RISK: MODERATE ({riskScore}%)")
    else:
        st.success(f"### CURRENT RISK: LOW ({riskScore}%)")

    # Create Columns for the Dashboard look
    col1, col2 = st.columns([1, 1])

    # --- Display Results ---
    with col1:
        st.plotly_chart(display_risk_gauge(riskScore), width='stretch')

        # Add a text description under the gauge
        if riskScore > 66:
            st.error("🚨 **High Wildfire Hazard!** Conditions are favorable for rapid fire spread.")
        elif riskScore > 33:
            st.warning("⚠️ **Moderate Hazard.** Caution is advised in vegetated areas.")
        else:
            st.success("✅ **Low Hazard.** Environmental factors are currently stable.")
    
    with col2:
        st.subheader("Assessment Area")
        # Display the interactive map
        st_folium(display_map(latitude, longitude, radius), height=300, width=None, key="assesment_map")

        st.write("---")
        st.subheader("Factor Breakdown")

        # Weather Progress
        st.write(f"🌡️ Weather: {weatherScore}%")
        st.progress(weatherScore / 100)

        # Fuel Progress
        st.write(f"🌿 Fuel: {fuelScore}%")
        st.progress(fuelScore / 100)

        # Slope Progress
        st.write(f"⛰️ Slope: {slopeScore}%")
        st.progress(slopeScore / 100)
else:
    st.info("Enter a location on the left and click 'Calculate Risk' to begin.")
