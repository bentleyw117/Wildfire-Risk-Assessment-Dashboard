# 🔥 Wildfire Risk Assessment Dashboard

An interactive Geospatial Data Engineering project that calculates localized wildfire risk scores by synthesizing real-time weather data, satellite-derived fuel density (NDVI), and topographical slope analysis.

This dashboard provides a high-precision look at environmental hazards, processing data within a specific 30m to 500m radius to help identify risk at the property or neighborhood level.

---

## 🚀 Key Engineering Features

### 🛠️ Resilient Geocoding Engine (Waterfall Logic)
To ensure global reliability, I implemented a multi-tier geocoding strategy to handle variations in international postal code databases:
* **Primary API:** Utilizes OpenWeatherMap Geocoding for rapid, lightweight lookups.
* **Quality Guard:** Custom logic detects "generic" API responses (e.g., when an API returns only a country name instead of a specific city).
* **Failover System:** High-precision fallback to the **Google Maps Geocoding API**, utilizing query refinement to force city-level granularity for complex international formats.

### 🛰️ Satellite Data Orchestration
* **Google Earth Engine (GEE):** Programmatic integration with Landsat satellite imagery to calculate the **Normalized Difference Vegetation Index (NDVI)**.
* **Scientific Alignment:** The dashboard supports dynamic radius scaling (30m–100m) specifically aligned with the native 30m spatial resolution of Landsat sensors.

### ⛰️ Topographical Risk Analysis
* **Horn’s Method:** Implements advanced terrain processing to calculate surface steepness from digital elevation models (DEM).
* **Slope Normalization:** Raw degrees are converted into a 0-100 risk score, accounting for how steep terrain accelerates wildfire propagation.

---

## 🏗️ Challenges Overcome & Optimization

### 🌐 Solving the "Zip Code Collision"
During development, I identified a significant data integrity issue where numeric zip codes overlapped across different countries (e.g., zip `69450` existing in both Brazil and France). 
* **The Fix:** Developed a `pytest` suite to enforce "Country Guard" validation. If the primary API returns a result from the wrong country, the system automatically triggers the Google Maps failover.
* **Format Precision:** Identified that Brazilian 5-digit codes often returned generic results; implemented a "self-healing" logic that appends the `-000` CEP suffix to force city-level accuracy.

### ⚡ Performance & State Management
* **Redundant Call Prevention:** Used Streamlit `session_state` to persist heavy API computations (Weather and Earth Engine data). This prevents the app from re-running expensive calculations every time a user adjusts a UI toggle.
* **API Optimization:** Engineered the backend to prioritize lower-latency data sources first, only escalating to premium providers when a "Quality Gap" is detected in the data.

---

## 📊 Technical Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | Streamlit |
| **Visuals** | Plotly (Gauges), Folium (Satellite Maps) |
| **APIs** | OpenWeatherMap, Open-Meteo, Google Maps, Google Earth Engine |
| **Data** | Geopy, Pycountry, Googlemaps SDK, NumPy |

---

## 🧪 Testing Suite
The project includes a comprehensive `pytest` architecture to validate environmental logic:
* **Extreme Weather:** Tests scoring accuracy for high-heat/low-humidity scenarios.
* **Terrain Validation:** Mocks 3D coordinate grids to verify Horn's Method slope calculations.
* **International Logic:** Validates geocoding for diverse regions including London (GB), Sydney (AU), and Codajás (BR).

---

## ⚙️ Setup & Usage

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Environment Variables:**
   Configure `OPENWEATHER_API_KEY` and `GOOGLECLOUD_API_KEY` in a `.env` file.
3. **Run the Dashboard:**
   ```bash
   streamlit run app.py
   ```

---

## 👨‍💻 Recruitment Demo Guide
To see the dashboard's robustness in action, try these inputs:
1. **Standard Mode:** Enter Zip `69450` and Country `BR` to see the automated fallback handle a complex international location.
2. **Advanced Mode:** Toggle "Advanced Coordinate Mode" to input exact Latitude/Longitude for a specific forest-bordering property.

---

## Credits

This package was created with [Cookiecutter](https://github.com/audreyfeldroy/cookiecutter) and the [audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage) project template.
