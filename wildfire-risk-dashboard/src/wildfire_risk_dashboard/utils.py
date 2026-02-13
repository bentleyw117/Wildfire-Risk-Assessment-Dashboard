import os
import requests
import ee
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Custom Exception for when NDVI cannot be determined
class SatelliteDataError(Exception):
    """Exception raised when satellite data (NDVI) cannot be retrieved."""
    pass

# Initialize the Earth Engine
try:
    ee.Initialize(project='project-acf0062f-af6b-4917-944')
except Exception as e:
    print(f"Earth Engine failed to initialize: {e}")

# looks for .env file and loads the variables into the system.
load_dotenv()

# Assign the key to a variable
API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_geo_coordinates(zipCode, countryCode):
    url = f"http://api.openweathermap.org/geo/1.0/zip?zip={zipCode},{countryCode}&appid={API_KEY}"
    response = requests.get(url)
    return response.json()

def get_weather_data(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}"
    response = requests.get(url)
    return response.json()

def get_ndvi(lat, lon, radius):
    """
    Returns the average NDVI of the defined area.
    
    :param lat: Latitude
    :param lon: Longitude
    :param radius: Radius in meters
    """
    
    # Calculate the date range
    currentDate = datetime.datetime.now().date()
    daysAgo = 60
    pastDate = currentDate - timedelta(days=daysAgo)
    startDate = pastDate.strftime("%Y-%m-%d")
    endDate = currentDate.strftime("%Y-%m-%d")

    # Define the point
    point = ee.Geometry.Point([lon, lat])

    # Access the collection
    ndviCollection = ee.ImageCollection("LANDSAT/COMPOSITES/C02/T1_L2_32DAY_NDVI")

    # Apply filters
    latestImage = ndviCollection \
        .filterBounds(point) \
        .filterDate(startDate, endDate) \
        .sort('system:time_start', False) \
        .first()
    
    # Define the area (buffer) based on radius
    area = point.buffer(radius)

    # Use reduceRegion to calculate the mean NDVI for the pixels in that area
    stats = latestImage.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=area,
        scale=30,  # Landsat resolution is 30m
        maxPixels=1e9
    )

    # Extract the numerical value from the GEE object
    ndviAvg = stats.get('NDVI').getInfo()

   # ! IMPORTANT BELOW: NEEDS IMPROVEMENT
    """
    No Data Handling: If a coordinate is in the middle of the ocean or if cloud cover was 100% for that 60-day window, stats.get('NDVI') might return None.
    """
    if ndviAvg is None:
        raise SatelliteDataError("Satellite data unavailable for this area at this time (possible cloud cover or water).") 
    else:
        return ndviAvg
