import os
import requests
import ee
from datetime import datetime, timedelta
from dotenv import load_dotenv
import googlemaps
import pycountry as pc

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
OW_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GC_API_KEY = os.getenv("GOOGLECLOUD_API_KEY")
gmaps = googlemaps.Client(key=GC_API_KEY)

def get_geo_coordinates(zipCode, countryCode):
    # Try open weather api
    owmURL = f"http://api.openweathermap.org/geo/1.0/zip?zip={zipCode},{countryCode}&appid={OW_API_KEY}"
    owmResponse = requests.get(owmURL).json()

    # Check if it's the right country AND that the name isn't just "Brazil" or "United States"
    # If OWM returns a generic name, we want Google to give us the specific city
    # If OWM gives us a result, we check if it's actually detailed.
    # If the name is just the Country Name or the Zip Code, we force Google.
    if "lat" in owmResponse and owmResponse.get("country") == countryCode.upper():
        owm_name = owmResponse.get("name", "")
        country_name = pc.countries.get(alpha_2=countryCode).name
        
        # If the name is better than just the country name, use it!
        if owm_name.lower() != country_name.lower() and owm_name != zipCode:
            return owmResponse

    # Fallback to Google Maps
    # Google is much stricter with the 'components' filter
    geocodeResult = gmaps.geocode(
        f"{zipCode}", 
        components={"country": countryCode.upper()}
    )
    
    if geocodeResult:
        # Extract location data from the first result
        location = geocodeResult[0]['geometry']['location']
        return {
            "lat": location['lat'],
            "lon": location['lng'],
            "name": geocodeResult[0]['formatted_address'],
            "source": "google" # Helpful for debugging
        }
    
    # If both fail, return None or raise an error
    return None


def grab_coordinates(geoData):
    if geoData is None:
        raise ValueError("Could not find coordinates for this location.")
    lat = geoData["lat"]
    lon = geoData["lon"]
    return lat, lon

def get_weather_data(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OW_API_KEY}"
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
    currentDate = datetime.now().date()
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

def get_elevation_data(coordsDic):
    url = f"https://api.open-meteo.com/v1/elevation?latitude={coordsDic["north"][0]},{coordsDic["east"][0]},{coordsDic["south"][0]},{coordsDic["west"][0]}&longitude={coordsDic["north"][1]},{coordsDic["east"][1]},{coordsDic["south"][1]},{coordsDic["west"][1]}"
    response = requests.get(url)
    return response.json()
