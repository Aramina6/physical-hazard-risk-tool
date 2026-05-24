"""Space Hazards module - Physical Hazard Risk Tool.

Contains Kp index (geomagnetic activity) and Near-Earth Object close approaches.
These are treated as physical / emerging risks that can affect insurance and finance.

Business Context:
- High Kp periods increase risk for power utilities (GIC) and satellite operators.
- This data is relevant for specialty insurance lines and can later be modeled
  as an additional factor in the stress testing framework.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta

@st.cache_data(ttl=1800)
def fetch_kp_index():
    """Fetch recent planetary K-index from NOAA SWPC."""
    url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
    try:
        data = requests.get(url, timeout=15).json()
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df["time_utc"] = pd.to_datetime(df["time_tag"])
        df["kp"] = pd.to_numeric(df["Kp"], errors="coerce")
        df = df.dropna(subset=["kp"]).sort_values("time_utc", ascending=False)
        return df
    except Exception as e:
        st.error(f"Space weather (Kp) error: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def fetch_close_approaches(days_ahead=60, dist_max_au=0.08):
    """Fetch close Earth approaches from JPL CNEOS CAD API."""
    today = datetime.utcnow().date()
    date_min = today.strftime("%Y-%m-%d")
    date_max = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    url = (
        f"https://ssd-api.jpl.nasa.gov/cad.api?"
        f"date-min={date_min}&date-max={date_max}"
        f"&dist-max={dist_max_au}&sort=dist&limit=30&fullname=true"
    )
    try:
        resp = requests.get(url, timeout=20).json()
        if "data" not in resp or not resp.get("data"):
            return pd.DataFrame()
        cols = resp.get("fields", [])
        df = pd.DataFrame(resp["data"], columns=cols)
        df["close_date"] = pd.to_datetime(df["cd"].str.replace(" ", "T", regex=False))
        df["dist_au"] = pd.to_numeric(df["dist"], errors="coerce")
        df["h"] = pd.to_numeric(df["h"], errors="coerce")
        df["v_inf"] = pd.to_numeric(df["v_inf"], errors="coerce")
        df["dist_ld"] = df["dist_au"] / 0.00257
        df["name"] = df["fullname"].fillna(df["des"])
        mask = (df["h"] < 28.0) | (df["dist_ld"] < 6.0)
        df = df[mask].copy()
        return df.sort_values("close_date").reset_index(drop=True)
    except Exception:
        return pd.DataFrame()


def render():
    """Render the Space Hazards module."""
    st.subheader("☄️ Space Hazards (USA)")
    st.caption("Geomagnetic activity (Kp) + Near-Earth Objects (NASA/JPL)")

    kp_df = fetch_kp_index()
    if not kp_df.empty:
        latest = kp_df.iloc[0]
        kp_val = float(latest["kp"])
        st.metric("Latest Kp Index", f"{kp_val:.2f}")
        st.dataframe(kp_df.head(10), use_container_width=True)
    else:
        st.warning("Could not load Kp data.")

    st.divider()
    neo_df = fetch_close_approaches()
    if not neo_df.empty:
        st.dataframe(neo_df.head(8), use_container_width=True)
    else:
        st.info("No significant close approaches in the next 60 days.")
