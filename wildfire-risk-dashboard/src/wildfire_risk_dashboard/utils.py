import os
import requests
from dotenv import load_dotenv

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
