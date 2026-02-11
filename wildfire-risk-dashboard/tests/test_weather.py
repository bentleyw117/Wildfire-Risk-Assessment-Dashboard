import pytest
from src.wildfire_risk_dashboard import utils
from src.wildfire_risk_dashboard import wildfire_risk_dashboard as wrd

#############################################################

# --- API Testing ---

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


#############################################################

# --- Weather Data Testing ---

def test_extreme_weather_score():
    # Scenario: 35°C (308.15K), 20% Humidity, 40km/h (11.11 m/s)
    mock_weather = {
        "main": {"temp": 308.15, "humidity": 20},
        "wind": {"speed": 11.11}
    }
    
    t_score = wrd.normalize_temperature(mock_weather)
    h_score = wrd.normalize_humidity(mock_weather)
    w_score = wrd.normalize_wind_speed(mock_weather)
    
    # All sub-scores should be 100
    assert t_score == 100
    assert h_score == 100
    assert w_score == 100
    
    # Total weather score should be 100
    assert wrd.calculate_weather_score(t_score, h_score, w_score) == 100.0


def test_moderate_weather_score():
    # Scenario: 20°C (293.15K), 50% Humidity, 20km/h (5.55 m/s)
    # These are exactly in the middle of your 10-30 and 30-70 ranges
    mock_weather = {
        "main": {"temp": 293.15, "humidity": 50},
        "wind": {"speed": 5.55}
    }
    
    t_score = wrd.normalize_temperature(mock_weather)
    h_score = wrd.normalize_humidity(mock_weather)
    w_score = wrd.normalize_wind_speed(mock_weather)
    
    assert t_score == pytest.approx(50.0, 0.1)
    assert h_score == pytest.approx(50.0, 0.1)
    assert w_score == pytest.approx(50.0, 0.1)
    assert wrd.calculate_weather_score(t_score, h_score, w_score) == pytest.approx(50.0, 0.1)


def test_wind_bias_influence():
    # Scenario: 15°C (288.15K) [Low Risk], 60% Humidity [Low Risk], 30km/h (8.33 m/s) [Extreme Risk]
    mock_weather = {
        "main": {"temp": 288.15, "humidity": 60},
        "wind": {"speed": 8.33}
    }
    
    t_score = wrd.normalize_temperature(mock_weather) # Expected: 25.0
    h_score = wrd.normalize_humidity(mock_weather)    # Expected: 25.0
    w_score = wrd.normalize_wind_speed(mock_weather)  # Expected: 100.0
    
    # Calculation Check: (25 * 0.15) + (25 * 0.35) + (100 * 0.5)
    # 3.75 + 8.75 + 50 = 62.5
    final_weather_score = wrd.calculate_weather_score(t_score, h_score, w_score)
    
    assert final_weather_score == pytest.approx(62.5, 0.1)


#############################################################

# --- Slope Data Testing ---

def test_slope_calculation_and_normalization():
    # 1. Setup Mock Data
    lat, lon = 43.5447, -96.7311
    degree_offset = 30 # 30 meters
    
    # Generate coordinates using your function
    coords = wrd.get_neighboring_coords(lat, lon, degree_offset)
    
    # 2. Mock Elevations: Imagine a 30m rise over a 60m distance (West to East)
    # distance between west and east is roughly 60m (30m each way)
    # If dz is 30m and dx is 60m, slope is atan(30/60) approx 26.56 degrees
    mock_elevations = {
        "current": 440,
        "north": 440,
        "east": 470,  # 30 meters higher than West
        "south": 440,
        "west": 440
    }
    
    # 3. Test Steepness Calculation
    slope_deg = wrd.get_steepness(mock_elevations, coords)
    
    # 4. Test Normalization
    risk_score = wrd.normalize_slope(slope_deg)
    
    # Verification (Using approx due to floating point math)
    assert slope_deg > 0
    assert risk_score == pytest.approx((slope_deg / 30) * 100)

def test_flat_ground_slope():
    # Scenario: All elevations are 440m
    mock_elevations = {"current": 440, "north": 440, "east": 440, "south": 440, "west": 440}
    coords = {"north": (1,1), "east": (1,1), "south": (1,1), "west": (1,1)}
    
    assert wrd.get_steepness(mock_elevations, coords) == 0.0
    assert wrd.normalize_slope(0.0) == 0.0
