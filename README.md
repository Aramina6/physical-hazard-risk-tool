# Multi-Hazard Monitor: Earthquakes • Cyclones • Space Hazards

**Real-time dashboard** tracking global earthquakes (M≥1.0), tropical cyclones, **geomagnetic activity (Kp)**, and near-Earth object close approaches — with a dedicated **USA Insurance Exposure Report** for space hazards.

Powered by open data from **USGS**, **NOAA NHC**, **JTWC**, **NOAA SWPC**, and **NASA/JPL CNEOS**.

Live Demo: [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://realtime-disasters-monitoring-cxephdtyww4jf2dwjunnhq.streamlit.app/)

---

## Live App Preview

The dashboard features **three interactive tabs** and auto-refreshes fresh data every 30 minutes:

### 1. Earthquakes Tab
- Interactive world map (OpenStreetMap) with red markers sized by severity and colored by magnitude.
- Right panel lists the most recent events with depth, felt reports, tsunami risk, and direct USGS links.
- Sidebar slider filters by minimum magnitude.

### 2. Tropical Cyclones Tab
- Blue-themed map and list of active/recent tropical storms, hurricanes, and typhoons.
- Details include Saffir-Simpson category, max winds, basin, and forecast links (NOAA NHC / JTWC).

### 3. Space Hazards (USA) Tab — *New*
- **Live Geomagnetic Activity**: Current planetary Kp index + color-coded NOAA G-scale storm level (G0–G5) with recent trend chart.
- **Upcoming Close Approaches**: List of the nearest or larger near-Earth objects expected in the next 60 days (sourced from JPL CNEOS CAD API). Shows distance in Lunar Distances (LD), absolute magnitude (H), and relative velocity.
- **🇺🇸 USA Insurance Exposure Report**: Educational panel highlighting key sectors most vulnerable to space weather in the United States:
  - Electric power grid (GIC risk to EHV transformers)
  - Commercial & government satellite fleets
  - Aviation (polar route operations)
  - Oil/gas pipelines & SCADA
- Includes historical benchmarks (1989 Quebec storm, Carrington 1859 scenario) and publicly cited loss ranges from insurance industry studies.

> **Note**: The insurance report is an educational synthesis for situational awareness. It is **not** a substitute for professional catastrophe modeling or actuarial advice.

---

## Features

- **Live Multi-Source Data**: Earthquakes (USGS), Cyclones (NOAA/JTWC), Space Weather (NOAA SWPC Kp), and NEO close approaches (NASA/JPL).
- **Interactive Maps** for earthquakes and cyclones.
- **Space Weather Dashboard**: Real-time Kp index, storm classification, and trend visualization.
- **USA-Focused Insurance Risk View**: Highlights sectors with material exposure to geomagnetic storms and space weather.
- **Filtering & Responsiveness**: Minimum intensity slider, clean two-column layouts, and mobile-friendly design.
- **Auto-Refresh**: All data sources cached and refreshed on a 30-minute cadence.

---

## Data Sources

| Hazard Type          | Provider                  | Update Frequency |
|----------------------|---------------------------|------------------|
| Earthquakes          | USGS FDSN                 | ~Real-time       |
| Tropical Cyclones    | NOAA NHC + JTWC RSS       | ~Real-time       |
| Geomagnetic (Kp)     | NOAA SWPC                 | 3-hourly         |
| Near-Earth Objects   | NASA/JPL CNEOS CAD API    | Daily            |

All data is fetched client-side from public APIs. No user accounts or API keys are required for normal operation.

---

## How to Run Locally

```bash
git clone https://github.com/Aramina6/realtime-disasters-monitoring.git
cd realtime-disasters-monitoring

pip install -r requirements.txt
streamlit run app.py
```

After cloning, the new **Space Hazards (USA)** tab will appear automatically.

---

## Development

- Main branch contains the stable version.
- The `feature/space-hazards-usa-insurance` branch contains the latest addition of the Space Hazards tab and USA insurance report.

Contributions, bug reports, and suggestions for additional hazards or improved insurance analytics are welcome!

---

*Disclaimer: This application is for informational and educational purposes only. Insurance loss estimates are drawn from publicly available scientific and industry literature and should not be used for underwriting, pricing, or risk transfer decisions without independent professional validation.*