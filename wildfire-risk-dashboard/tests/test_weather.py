import pytest
from src.wildfire_risk_dashboard import utils

def test_get_geo_coordinates():
    """Verify that we can get coordinates for Sioux Falls."""
    geo = utils.get_geo_coordinates("57106", "US")

    # Assertions check the data
    assert geo["name"] == "Sioux Falls"
    assert "lat" in geo
    assert "lon" in geo



def test_get_weather_data():
    """Verify that the weather API returns valid data."""
    # Use hardcoded coordinates for Sioux Falls
    weather = utils.get_weather_data(43.5447, -96.7311)
    
    # Check if the response contains the expected weather keys
    assert "main" in weather
    assert "temp" in weather["main"]
    assert "humidity" in weather["main"]