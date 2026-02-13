import sys
from pathlib import Path

# Add the src directory to the system path so Python can find your module
src_path = str(Path(__file__).parent / "wildfire-risk-dashboard" / "src")
if src_path not in sys.path:
    sys.path.append(src_path)
"""
try:
    ndvi = utils.get_ndvi(lat, lon, 30)
    fuel_score = wrd.normalize_fuel(ndvi)
except utils.SatelliteDataError as e:
    st.warning(f"⚠️ Fuel Risk Unavailable: {e}")
    fuel_score = 0 
""" # Or handle as you see fit