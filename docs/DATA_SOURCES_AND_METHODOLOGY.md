# Data Sources & Methodology

## Overview

This document describes the data sources, processing logic, and known limitations of the Multi-Hazard Monitor dashboard.

## Core Data Sources

### 1. USGS Earthquake Catalog (FDSN)
- **Endpoint**: `https://earthquake.usgs.gov/fdsnws/event/1/query`
- **Update frequency**: Near real-time
- **Used for**: Magnitude, location, depth, felt reports, tsunami flags
- **Limitations**: Only captures events that are detected and reported. Small events in remote areas may be missing.

### 2. NOAA National Hurricane Center (NHC) + JTWC RSS
- **Sources**: NHC Atlantic/Pacific advisories + JTWC RSS feeds
- **Used for**: Tropical cyclone names, basins, estimated categories, wind speeds
- **Limitations**: RSS feeds are text-based and parsing can be brittle. Best-effort category estimation.

### 3. NOAA Space Weather Prediction Center (SWPC) – Planetary K-index
- **Endpoint**: `https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json`
- **Update frequency**: Every 3 hours
- **Used for**: Geomagnetic activity (Kp index) and G-scale storm levels
- **Relevance to insurance/finance**: Geomagnetic storms can cause power grid disturbances (GIC), satellite anomalies, and aviation impacts.

### 4. NASA/JPL CNEOS Close Approach Data (CAD)
- **Endpoint**: `https://ssd-api.jpl.nasa.gov/cad.api`
- **Used for**: Predicted close approaches of near-Earth objects
- **Filters applied in dashboard**: H < 28 or distance < 6 LD (to focus on potentially material objects)
- **Relevance**: Satellite operators, space insurance, and long-term tail risk.

### 5. FEMA OpenFEMA (NFIP Claims + Disaster Declarations)
- **Endpoints**:
  - `https://www.fema.gov/api/open/v2/FimaNfipClaims`
  - `https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries`
- **Why it matters**: One of the largest public sources of **actual insured loss data** in the United States.
- **Key fields used**:
  - `amountPaidOnBuildingClaim`
  - `amountPaidOnContentsClaim`
  - `amountPaidOnIncreasedCostOfComplianceClaim`
- **Major limitations**:
  - Flood-only (no wind, wildfire, earthquake)
  - Voluntary participation (take-up rate varies dramatically by state and income level)
  - Claims can be filed years after the event (development lag)

## Aggregation & Processing Logic

- All external calls use `@st.cache_data(ttl=...)` for performance.
- NFIP claims are aggregated at **state × year** level for the Insurance Analytics tab.
- Kp data is normalized to lowercase `kp` column for consistency in the UI.
- Close approach data is filtered client-side for relevance.

## Financial Materiality Interpretation Guidance

When using this dashboard for insurance or investment decisions:

1. **NFIP paid amounts** are **gross** paid losses — not net of reinsurance or recoveries.
2. Flood is only one peril. A state with low NFIP losses can still have massive wildfire or hurricane wind losses.
3. Space weather data is currently more relevant for **satellite operators** and **utilities** than for standard property portfolios.
4. Always cross-reference with commercial catastrophe models before making capital or pricing decisions.

## Production Recommendations

For company use:
- Cache results more aggressively or replicate key datasets locally.
- Add internal exposure data (e.g., insured value by ZIP) for true loss ratio views.
- Consider commercial enrichment (e.g., Verisk, CoreLogic, First Street) for vulnerability curves.

---
*This document is intentionally high-level. For detailed field mappings, refer to the official API documentation of each provider.*
