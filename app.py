# app.py
"""
Main entry point for Physical Hazard Risk Tool.

This file is intentionally kept thin. It acts as an orchestrator:
- Left sidebar for physical hazard data (supporting context)
- Main area for Market Factor Stress Testing (the primary financial tool)

All heavy logic lives in the physical_hazard/ and factor_model/ packages.
"""

import streamlit as st

# Import from our new clean packages
# (Physical hazard data is now supporting material)
from physical_hazard import earthquakes, tropical_cyclones, space_hazards, nfip_insurance

# Import the new financial core (Option A - pure market factor stress testing first)
from factor_model import market_factor_stress


st.set_page_config(
    page_title="Physical Hazard Risk Tool | Market Factor Stress Testing",
    page_icon="📈",
    layout="wide"
)


# ============================================================
# LEFT SIDEBAR - Physical Hazard Modules (now secondary / context)
# ============================================================
with st.sidebar:
    st.header("Physical Hazard Modules")
    st.caption("Supporting data for exposure & context")
    
    phys_choice = st.radio(
        "Select module",
        options=[
            "Earthquakes",
            "Tropical Cyclones", 
            "Space Hazards (USA)",
            "NFIP Insurance Analytics"
        ],
        index=0
    )
    
    st.divider()
    st.markdown("**Main Tool**")
    st.info("Market Factor Stress Testing\n(Pure Market)")


# ============================================================
# MAIN AREA - Financial / Factor Stress Testing (Primary Focus)
# ============================================================
st.title("Physical Hazard Risk Tool")
st.markdown("**Market Factor Stress Testing + Physical Hazard Context**")

st.header("Market Factor Stress Testing — Pure Market")
st.markdown("""
**Focus**: Pure market factor model + stress scenarios using open data.

Physical hazard modules are available on the **left sidebar** for context when building hybrid scenarios later.
""")

# Render the pure market factor stress testing (this is now the hero feature)
market_factor_stress.render()


# ============================================================
# RENDER SELECTED PHYSICAL MODULE (from left sidebar)
# ============================================================
if phys_choice == "Earthquakes":
    with st.expander("🌍 Earthquakes (USGS) - Last 30 Days", expanded=True):
        earthquakes.render()

elif phys_choice == "Tropical Cyclones":
    with st.expander("🌀 Tropical Cyclones (NOAA / JTWC)", expanded=True):
        tropical_cyclones.render()

elif phys_choice == "Space Hazards (USA)":
    with st.expander("☄️ Space Hazards (USA) - Kp + NEOs", expanded=True):
        space_hazards.render()

elif phys_choice == "NFIP Insurance Analytics":
    with st.expander("🇺🇸 NFIP Insurance Analytics (FEMA)", expanded=True):
        nfip_insurance.render()


st.caption("Physical Hazard Risk Tool • Market Factor Stress Testing + Physical Context • Open Data • Option A: Pure Market First")
