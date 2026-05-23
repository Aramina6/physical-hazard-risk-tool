# Multi-Hazard Monitor: Earthquakes • Cyclones • Space Hazards • Insurance Analytics

**Real-time dashboard** tracking global earthquakes (M≥1.0), tropical cyclones, **geomagnetic activity (Kp)**, near-Earth object close approaches, and **US disaster-linked insurance data** (NFIP claims + FEMA declarations).

Powered by open data from **USGS**, **NOAA NHC**, **JTWC**, **NOAA SWPC**, **NASA/JPL CNEOS**, and **FEMA OpenFEMA**.

Live Demo: [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://realtime-disasters-monitoring-cxephdtyww4jf2dwjunnhq.streamlit.app/)

---

## Live App Preview

The dashboard now features **four interactive tabs** with data refreshing every 30 minutes:

### 1. Earthquakes Tab
- Interactive world map (OpenStreetMap) with red markers sized by severity and colored by magnitude.
- Right panel lists the most recent events with depth, felt reports, tsunami risk, and direct USGS links.
- Sidebar slider filters by minimum magnitude.

### 2. Tropical Cyclones Tab
- Blue-themed map and list of active/recent tropical storms, hurricanes, and typhoons.
- Details include Saffir-Simpson category, max winds, basin, and forecast links (NOAA NHC / JTWC).

### 3. Space Hazards (USA) Tab
- **Live Geomagnetic Activity**: Current planetary Kp index + color-coded NOAA G-scale storm level (G0–G5) with recent trend chart.
- **Upcoming Close Approaches**: List of the nearest or larger near-Earth objects expected in the next 60 days (JPL CNEOS CAD API). Shows distance in Lunar Distances (LD), absolute magnitude (H), and velocity.
- **🇺🇸 USA Insurance Exposure Report**: Educational panel on sectors most vulnerable to space weather (power grid, satellites, aviation, pipelines) with historical benchmarks and modeled loss ranges.

### 4. Insurance Analytics (US) Tab — *New*
- **State-level quantitative views** powered by FEMA OpenFEMA:
  - NFIP Redacted Claims (total paid, claim counts) aggregated by state and year
  - Interactive US choropleth map of NFIP payouts
  - Top states bar chart
  - KPI cards (total paid, records, highest-payout state)
  - Sample state × year data table
- Starter version focused on recent years for performance. Includes roadmap notes for deeper correlations with disaster declarations and Space Hazards data.

> All insurance-related content is for educational and situational awareness purposes only.

---

## Features

- **Live Multi-Source Data**: Earthquakes (USGS), Cyclones (NOAA/JTWC), Space Weather (NOAA SWPC), NEOs (NASA/JPL), and Insurance/Disaster data (FEMA OpenFEMA).
- **Interactive Maps**: Earthquakes, cyclones, and now a US state choropleth for NFIP claims.
- **Quantitative Insurance Analytics**: State rankings, totals, and basic aggregations from millions of NFIP claims records.
- **USA-Focused Risk Views**: Both the Space Hazards insurance report and the new Insurance Analytics tab emphasize U.S. exposure.
- **Filtering & Responsiveness**: Minimum intensity slider + clean multi-column layouts.
- **Auto-Refresh**: All data sources cached and refreshed on a 30-minute cadence.

---

## Data Sources

| Hazard / Data Type          | Provider                     | Update Frequency |
|-----------------------------|------------------------------|------------------|
| Earthquakes                 | USGS FDSN                    | ~Real-time       |
| Tropical Cyclones           | NOAA NHC + JTWC RSS          | ~Real-time       |
| Geomagnetic (Kp)            | NOAA SWPC                    | 3-hourly         |
| Near-Earth Objects          | NASA/JPL CNEOS CAD API       | Daily            |
| Disaster Declarations       | FEMA OpenFEMA                | Near real-time   |
| NFIP Claims & Policies      | FEMA OpenFEMA (FimaNfip*)    | Monthly          |

All data is fetched client-side from public APIs. No user accounts or API keys are required for normal operation.

---

## How to Run Locally

```bash
git clone https://github.com/Aramina6/realtime-disasters-monitoring.git
cd realtime-disasters-monitoring

pip install -r requirements.txt
streamlit run app.py
```

After cloning, all four tabs (including the new **Insurance Analytics (US)** tab) will appear automatically.

---

## Development

- Main branch contains the stable version.
- The `feature/space-hazards-usa-insurance` branch contains the Space Hazards tab + the new Insurance Analytics (US) starter tab using real FEMA OpenFEMA data.

Next planned work on this branch includes deeper joins between disaster declarations and NFIP claims, time-series correlations, and cross-filtering with the Space Hazards Kp data.

Contributions and feedback are very welcome!

---

*Disclaimer: This application is for informational and educational purposes only. Insurance loss estimates and analytics are derived from public government data sources and should not be used for underwriting, pricing, or risk transfer decisions without independent professional validation.*