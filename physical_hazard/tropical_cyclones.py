"""Tropical Cyclones module - Physical Hazard Risk Tool.

Handles fetching and rendering of tropical cyclone data from NOAA NHC + JTWC.
Separated for modularity as the project evolves into a financial risk platform.

Business Context:
- Tropical cyclones are a major driver of insured losses (especially in Florida, Texas, Japan, etc.).
- Insurers use this data for exposure management and post-event loss estimation.
- In the future factor model, "Major Hurricane Landfall in Florida" can be treated as a discrete risk factor that can be shocked together with market factors.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

@st.cache_data(ttl=1800)
def fetch_cyclones_month():
    """Fetch recent tropical cyclones from NOAA NHC and JTWC RSS feeds."""
    urls = [
        ("NHC", "https://www.nhc.noaa.gov/index-at.xml"),
        ("JTWC", "https://metoc.navy.mil/jtwc/rss/jtwc.xml")
    ]
    cyclones = []
    for src, url in urls:
        try:
            xml = requests.get(url, timeout=12).text
            root = ET.fromstring(xml)
            for item in root.findall(".//item"):
                title = (item.find("title").text or "").strip()
                link = item.find("link").text or ""
                desc = (item.find("description").text or "").lower()

                if any(k in title.lower() for k in ["tropical", "hurricane", "typhoon"]):
                    name = title.split(":")[0].split("-")[0].strip()
                    basin = "Atlantic" if src == "NHC" else "Pacific/Indian"

                    cat = wind_kts = 0
                    for txt in [title, desc]:
                        if "category 5" in txt: cat, wind_kts = 5, 137
                        elif "category 4" in txt: cat, wind_kts = 4, 113
                        elif "category 3" in txt: cat, wind_kts = 3, 96
                        elif "category 2" in txt: cat, wind_kts = 2, 83
                        elif "category 1" in txt: cat, wind_kts = 1, 64
                        elif "tropical storm" in txt: cat, wind_kts = 0, 34

                    lat, lon = 20.0, -70.0
                    if "lat" in desc and "lon" in desc:
                        try:
                            lat = float(desc.split("lat")[1].split()[0].replace("°", ""))
                            lon = float(desc.split("lon")[1].split()[0].replace("°", ""))
                        except:
                            pass

                    cyclones.append({
                        "name": name,
                        "basin": basin,
                        "category": cat,
                        "max_wind_kts": wind_kts,
                        "impact": "Active advisory" if "active" in desc else "Recent event",
                        "article_link": link,
                        "magnitude": wind_kts / 20,
                        "time_utc": pd.NaT,
                        "lat": lat,
                        "lon": lon,
                        "severity": cat if cat else 1
                    })
        except:
            continue
    return pd.DataFrame(cyclones).drop_duplicates("name")


def render():
    """Render the Tropical Cyclones physical hazard module."""
    st.subheader("🌀 Tropical Cyclones (NOAA NHC + JTWC)")
    df = fetch_cyclones_month()
    if not df.empty:
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = px.scatter_mapbox(
                df, lat="lat", lon="lon",
                size="magnitude", color="severity",
                color_continuous_scale="Blues",
                hover_name="name",
                hover_data=["basin", "category", "max_wind_kts", "impact"],
                zoom=1, height=500
            )
            fig.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.dataframe(df, use_container_width=True)
    else:
        st.info("No active tropical cyclones (off-season).")
