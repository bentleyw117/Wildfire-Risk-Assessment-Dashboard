# 🔥 Wildfire Risk Assessment Dashboard

An interactive Geospatial Dashboard that calculates localized wildfire risk scores by synthesizing real-time weather data, satellite-derived fuel density (NDVI), and topographical slope analysis.



## 🚀 Key Engineering Features

### 🛠️ Resilient Geocoding Engine (Waterfall Logic)
To ensure global reliability, this project implements a multi-tier geocoding strategy to handle variations in international postal code databases:
* **Primary:** OpenWeatherMap Geocoding API for rapid, lightweight lookups.
* **Quality Guard:** Custom logic to detect "lazy" or generic API responses (e.g., returning only a country name when a city-level result is required).
* **Failover:** High-precision fallback to the **Google Maps Geocoding API**, utilizing query refinement (e.g., appending suffixes like `-000` for Brazil) to force city-level granularity.

### 🛰️ Satellite Data Orchestration
* **Google Earth Engine (GEE):** Programmatic integration with Landsat satellite imagery to calculate the **Normalized Difference Vegetation Index (NDVI)** within a user-defined radius.
* **Dynamic Radius Scaling:** Supports assessment areas from 30m to 100m, intentionally aligned with the native 30m spatial resolution of Landsat sensors.

### ⛰️ Topographical Risk Analysis
* **Terrain Processing:** Implements Horn’s Method to calculate surface steepness from digital elevation models (DEM).
* **Slope Normalization:** Converts raw degrees into a 0-100 risk score based on how slope accelerates wildfire propagation.

---

## 🏗️ Development History & Engineering Process

This project followed a rigorous software development lifecycle (SDLC) to move from a CLI script to a production-ready dashboard:

1. **Feature Branching:** Utilized a `feature/streamlit-frontend` Git branch to isolate UI development from core algorithmic logic, ensuring the "known good" backend remained stable during frontend iteration.
2. **State Management:** Implemented `st.session_state` to persist heavy API computations (Weather/GEE) across Streamlit's rerun cycles, preventing redundant API calls and flickering UI.
3. **Automated Unit Testing:** Developed a `pytest` suite to validate geocoding accuracy across international borders, specifically solving "Zip Code Collisions" where the same postal code exists in multiple countries (e.g., Brazil vs. France).
4. **Waterfall Refinement:** Iteratively improved geocoding logic to handle international edge cases, such as enforcing 8-digit precision for Brazilian CEPs to ensure city-level assessment.

---

## 📊 Technical Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | Streamlit |
| **Visualization** | Plotly (Gauges), Folium (Satellite Maps) |
| **APIs** | OpenWeatherMap, Open-Meteo, Google Maps, Google Earth Engine |
| **Data Processing** | Geopy, Pycountry, Googlemaps SDK |

---

## 🧪 Global Testing Cases
* **Paradise, CA:** Validates high-hazard logic in WUI (Wildland-Urban Interface) zones with extreme slopes.
* **Manaus, Brazil:** Confirms the "Lush/Moisture" logic where high-density rainforest vegetation correctly returns a low risk score.
* **Lake Louise, Canada:** Tests negative NDVI handling for water/ice bodies.

---

## 💡 Cloud FinOps & Optimization
In alignment with **Cloud FinOps** principles, this architecture is optimized for cost-efficiency. By utilizing the lower-cost OpenWeather API as the primary entry point and only escalating to the Google Maps Geocoding API for verified quality gaps, the project minimizes operational overhead while maintaining data integrity.

---

## ⚙️ Setup

1. **Clone & Install:**
   ```bash
   pip install -r requirements.txt

![PyPI version](https://img.shields.io/pypi/v/wildfire-risk-dashboard.svg)
[![Documentation Status](https://readthedocs.org/projects/wildfire-risk-dashboard/badge/?version=latest)](https://wildfire-risk-dashboard.readthedocs.io/en/latest/?version=latest)

A dynamic Python dashboard that assesses real-time wildfire risk by integrating weather APIs and satellite vegetation data.

* PyPI package: https://pypi.org/project/wildfire-risk-dashboard/
* Free software: MIT License
* Documentation: https://wildfire-risk-dashboard.readthedocs.io.

## Credits

This package was created with [Cookiecutter](https://github.com/audreyfeldroy/cookiecutter) and the [audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage) project template.
