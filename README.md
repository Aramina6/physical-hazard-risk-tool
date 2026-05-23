# Multi-Hazard Monitor: Earthquakes, Cyclones, Space Hazards & Insurance Analytics

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
- **USA Insurance Exposure Report**: Educational panel on sectors most vulnerable to space weather (power grid, satellites, aviation, pipelines) with historical benchmarks and modeled loss ranges.

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

## Development & Contribution

### Repository Standards

This project follows **production-style engineering practices** suitable for insurance, banking, or climate-risk teams:

- `SKILLS.md` — Strategic context on climate risk, financial materiality, and how insurers / banks / scientists use this data.
- `docs/DATA_SOURCES_AND_METHODOLOGY.md` — Detailed explanation of every data source and its limitations.
- `tests/` — Unit tests with mocking for all external data fetchers.
- GitHub Actions CI runs the test suite on every push and pull request.

### Running Locally

```bash
git clone https://github.com/Aramina6/realtime-disasters-monitoring.git
cd realtime-disasters-monitoring

python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\Activate on Windows

pip install -r requirements.txt
streamlit run app.py
```

### Running Tests

```bash
pip install pytest
pytest tests/ -v
```

### Adding New Features

Before adding new data sources or visualizations, please read `SKILLS.md` for context on financial materiality and how different stakeholders interpret climate risk data.

When modifying data fetchers:
- Add or update unit tests in `tests/`
- Document limitations in `docs/`
- Provide clear interpretation guidance in the UI

---

*Built with care for risk professionals who need transparent, open-data views of climate and geophysical hazards.*
