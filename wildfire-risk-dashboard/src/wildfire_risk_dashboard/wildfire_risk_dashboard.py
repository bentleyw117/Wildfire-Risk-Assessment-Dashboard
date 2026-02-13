"""
For a risk assement tool we use a Dynamic Risk Index that weights environmental factors based on their impact on fire behavior.

To calculate a score between 0 and 100, the algorithm will use the following weights:
    Total Risk = (0.40 x Weather) + (0.40 x Fuel) + (0.20 x Topography)
"""

# Imports
from .utils import get_geo_coordinates, get_weather_data
import math
from geopy import distance

# Global Variables
ONE_DEGREE_OF_LAT_CONST = 111_111


def get_one_degree_of_lon(lat):
    """
    Returns the one degree of longitude at a given latitude.
    
    :param lat: latitude
    """

    return ONE_DEGREE_OF_LAT_CONST * math.cos(math.radians(lat))


#################################################################################

# --- Weather Data Processing ---

def normalize_temperature(weatherData):
    """
    Returns a score between 0-100 based on temperature found in the weather data.
    
    :param weatherData: Converted JSON object containing weather data
    """

    temp = weatherData["main"]["temp"]
    temp -= 273.15
    if temp >= 30:
        return 100
    elif temp <= 10:
        return 0
    else:
        return ((temp - 10) / 20) * 100


def normalize_humidity(weatherData):
    """
    Returns a score between 0-100 based on humidity found in the weather data.
    
    :param weatherData: Converted JSON object containing weather data
    """

    humidity = weatherData["main"]["humidity"]
    if humidity <= 30:
        return 100
    elif humidity >= 70:
        return 0
    else:
        return (1 - ((humidity - 30) / 40)) * 100


def normalize_wind_speed(weatherData):
    """
    Returns a score between 0-100 based on wind speed found in the weather data.
    
    :param weatherData: Converted JSON object containing weather data
    """

    wind = weatherData["wind"]["speed"]
    wind *= 3.6
    if wind >= 30:
        return 100
    elif wind <= 10:
        return 0
    else:
        return ((wind - 10) / 20) * 100


def calculate_weather_score(tempScore, humidityScore, windScore):
    """
    Returns a score between 0-100 based on normalized weather scores.
    Each variable is weighted differently to reflect its impact on fire risk.
    
    :param tempScore: normalized temperature score (0-100)
    :param humidityScore: normalized humidity score (0-100)
    :param windScore: normalized wind speed score (0-100)
    """

    tempScore *= .15
    humidityScore *= .35
    windScore *= .5
    return round(tempScore + humidityScore + windScore, 2)


#################################################################################

# --- Fuel/NDVI Data Processing ---

def normalize_fuel(ndvi):
    """
    Returns a score between 0-100 based on NDVI.
    
    :param ndvi: NDVI score (-1 to 1)
    """
    
    # Water/Snow Guard (No fuel)
    if ndvi < 0:
        return 0
    
    # Barren to Dry Grass (0.0 to 0.2)
    # Risk INCREASES as more dry fuel (NDVI 0.2) is present compared to rock (0.0)
    elif ndvi <= 0.2:
        # Scale 0.0 (10 risk) to 0.2 (100 risk)
        return 10 + (ndvi / 0.2) * 90
        
    # Dry Grass to Lush Green (0.2 to 0.8+)
    # Risk DECREASES as the vegetation becomes more moisture-rich
    else:
        # Scale 0.2 (100 risk) to 0.8 (10 risk)
        # Using the Interpolation Formula: y = y1 + (x - x1) * (y2 - y1) / (x2 - x1)
        score = 100 + (ndvi - 0.2) * (10 - 100) / (0.8 - 0.2)
        return max(10, score) # Clamp it so lush forests don't hit 0


#################################################################################

# --- Slope Data Processing ---

def offset_lat(lat, degree, direction):
    """
    Returns an offset latitude.
    
    :param lat: latitude
    :param degree: degrees to offset
    :param direction: direction to offset
    """

    dLat = degree / ONE_DEGREE_OF_LAT_CONST
    if direction == "north":
        return lat + dLat
    elif direction == "south":
        return lat - dLat


def offset_lon(lat, lon, degree, direction):
    """
    Returns an offset longitude.
    
    :param lat: latitude
    :param lon: longitude
    :param degree: degrees to offset
    :param direction: direction to offset
    """

    dLon = degree / get_one_degree_of_lon(lat)
    if direction == "east":
        return lon + dLon
    elif direction == "west":
        return lon - dLon


def get_neighboring_coords(lat, lon, degree):
    """
    Returns a dictionary of neighboring coordinates of the given coordinates.
    
    :param lat: current latitude
    :param lon: current longitude
    :param degree: degrees to offset
    """

    neighboringCoords = {
        "north": (offset_lat(lat, degree, "north"), lon),
        "east": (lat, offset_lon(lat, lon, degree, "east")),
        "south": (offset_lat(lat, degree, "south"), lon),
        "west": (lat, offset_lon(lat, lon, degree, "west"))
    }
    return neighboringCoords


def get_elevations(elevationData):
    """
    Returns a dictionary of elevations of the current and neighboring coordinates.
    
    :param elevationData: Converted JSON object containing elevation data
    """

    elevations = {
        "current": elevationData["results"][0]["elevation"],
        "north": elevationData["results"][1]["elevation"],
        "east": elevationData["results"][2]["elevation"],
        "south": elevationData["results"][3]["elevation"],
        "west": elevationData["results"][4]["elevation"]
    }
    return elevations


def get_steepness(elevations, coordinates):
    """
    Returns the slope/'steepness' of the current and neighboring coordinates using Horn's Method.
    
    :param elevations: A dictionary of elevations of the current and neighboring coordinates
    :param coordinates: A dictionary of coordinates of the current and neighboring coordinates
    """
    
    dz1 = elevations["east"] - elevations["west"] # (The Rise): This is the Elevation at the East point minus the Elevation at the West point.
    dz2 = elevations["north"] - elevations["south"] # (The Rise): This is the Elevation at the North point minus the Elevation at the South point.
    dx = distance.distance(coordinates["west"], coordinates["east"]).meters # (The Run): This is the horizontal distance (in meters) between your West and East coordinates.
    dy = distance.distance(coordinates["south"], coordinates["north"]).meters # (The Run): This is the horizontal distance (in meters) between your South and North coordinates.

    # Guard against division by zero (flat ground or identical points)
    if dx == 0 or dy == 0:
        return 0.0

    # Horn’s Method
    return math.degrees(math.atan(math.sqrt( ((dz1 / dx) ** 2) + ((dz2 / dy) ** 2) )))


def normalize_slope(slope):
    """
    Returns a score between 0-100 based on slope.
    
    :param slope: slope in degrees
    """
    if slope >= 30:
        return 100
    else:
        return (slope / 30) * 100

#################################################################################

# --- Final Calculations ---

def calculate_risk_score(weatherScore, fuelScore, slopeScore):
    """
    Returns a risk score between 0-100.
    
    :param weatherScore: Normalized weather score (0-100)
    :param fuelScore: Normalized fuel score (0-100)
    :param slopeScore: Normalized slope score (0-100)
    """

    weatherWeight = 0.40
    fuelWeight = 0.40
    slopeWeight = 0.20
    
    total_score = (weatherWeight * weatherScore) + (fuelWeight * fuelScore) + (slopeWeight * slopeScore)
                  
    return round(total_score, 2)
