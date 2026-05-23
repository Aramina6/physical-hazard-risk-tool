# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Multi-Hazard Monitor – Earthquakes, Cyclones & Space Hazards",
    page_icon="⚠️",
    layout="wide"
)

# ----------------------------------------------------------------------
# EARTHQUAKES – USGS FDSN (30-day, min-mag 1.0)
# ----------------------------------------------------------------------
@st.cache_data(ttl=1800)
def fetch_earthquakes_month():
    end = datetime.utcnow().strftime("%Y-%m-%d")
    start = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
    url = (
        f"https://earthquake.usgs.gov/fdsnws/event/1/query?"
        f"format=geojson&starttime={start}&endtime={end}"
        f"&minmagnitude=1&orderby=time"
    )
    try:
        data = requests.get(url, timeout=15).json()
        rows = []
        for f in data.get("features", []):
            p = f["properties"]
            g = f["geometry"]["coordinates"]
            rows.append({
                "name": f"M{p['mag']:.1f}",
                "location": p["place"],
                "impact": f"{p.get('felt', 0)} felt reports",
                "tsunami": bool(p.get("tsunami", 0)),
                "depth_km": g[2],
                "detail_url": p.get("detail", ""),
                "magnitude": p["mag"],
                "time_utc": pd.to_datetime(p["time"], unit="ms"),
                "lat": g[1],
                "lon": g[0],
                "severity": min(int(p["mag"] * 2), 10)
            })
        return pd.DataFrame(rows).sort_values("time_utc", ascending=False)
    except Exception as e:
        st.error(f"Earthquakes error: {e}")
        return pd.DataFrame()

# ----------------------------------------------------------------------
# TROPICAL CYCLONES – NOAA NHC + JTWC RSS
# ----------------------------------------------------------------------
@st.cache_data(ttl=1800)
def fetch_cyclones_month():
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
                        except: pass

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
        except: continue
    return pd.DataFrame(cyclones).drop_duplicates("name")

# ----------------------------------------------------------------------
# SPACE HAZARDS – NOAA SWPC Kp + NASA/JPL CNEOS Close Approaches (USA Insurance)
# ----------------------------------------------------------------------
@st.cache_data(ttl=1800)
def fetch_kp_index():
    """Fetch recent planetary K-index from NOAA SWPC."""
    url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
    try:
        data = requests.get(url, timeout=15).json()
        if not data or len(data) < 2:
            return pd.DataFrame()
        # First row is header
        header = data[0]
        rows = data[1:]
        df = pd.DataFrame(rows, columns=header)
        df["time_utc"] = pd.to_datetime(df["time_tag"])
        df["kp"] = pd.to_numeric(df["kp"], errors="coerce")
        df = df.dropna(subset=["kp"]).sort_values("time_utc", ascending=False)
        return df
    except Exception as e:
        st.error(f"Space weather (Kp) error: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_close_approaches(days_ahead=60, dist_max_au=0.08):
    """Fetch close Earth approaches from JPL Small-Body Database (CNEOS CAD API).
    No API key required for basic queries."""
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
        # Approximate lunar distances (1 LD ≈ 0.00257 AU)
        df["dist_ld"] = df["dist_au"] / 0.00257
        df["name"] = df["fullname"].fillna(df["des"])
        # Filter for more interesting objects (larger or very close)
        mask = (df["h"] < 28.0) | (df["dist_ld"] < 6.0)
        df = df[mask].copy()
        return df.sort_values("close_date").reset_index(drop=True)
    except Exception:
        return pd.DataFrame()

# ----------------------------------------------------------------------
# UI
# ----------------------------------------------------------------------
st.title("Multi-Hazard Monitor – Earthquakes, Cyclones & Space Hazards")
st.markdown("Real-time data from **USGS**, **NOAA NHC**, **JTWC**, **NOAA SWPC** & **NASA/JPL CNEOS**")

min_intensity = st.sidebar.slider("Minimum Intensity", 0.0, 10.0, 1.0, 0.5)

tab_eq, tab_tc, tab_space = st.tabs(["Earthquakes", "Tropical Cyclones", "Space Hazards (USA)"])

# --- Earthquakes ---
with tab_eq:
    df = fetch_earthquakes_month()
    if not df.empty:
        df = df[df["magnitude"] >= min_intensity]
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = px.scatter_mapbox(
                df, lat="lat", lon="lon",
                size="severity", color="magnitude",
                color_continuous_scale="Reds",
                hover_name="name",
                hover_data=["location", "depth_km", "impact", "tsunami"],
                zoom=1, height=560
            )
            fig.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("Recent Events")
            for _, r in df.head(12).iterrows():
                st.markdown(f"**{r['name']}** – {r['location']}")
                st.caption(f"Depth: {r['depth_km']:.1f} km | Felt: {r['impact']} | Tsunami: {'Yes' if r['tsunami'] else 'No'}")
                st.markdown(f"[USGS Detail]({r['detail_url']})")
                st.divider()
    else:
        st.info("No earthquake data.")

# --- Cyclones ---
with tab_tc:
    df = fetch_cyclones_month()
    if not df.empty:
        df = df[df["magnitude"] >= min_intensity]
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = px.scatter_mapbox(
                df, lat="lat", lon="lon",
                size="magnitude", color="severity",
                color_continuous_scale="Blues",
                hover_name="name",
                hover_data=["basin", "category", "max_wind_kts", "impact"],
                zoom=1, height=560
            )
            fig.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("Active / Recent Storms")
            for _, r in df.iterrows():
                st.markdown(f"**{r['name']}** – {r['basin']}")
                st.caption(f"Cat {r['category']} | {r['max_wind_kts']} kts | {r['impact']}")
                st.markdown(f"[Forecast]({r['article_link']})")
                st.divider()
    else:
        st.info("No active cyclones (off-season).")

# --- Space Hazards & USA Insurance Report ---
with tab_space:
    st.markdown("**Space Weather & Near-Earth Objects** — focused insurance risk view for the United States")
    st.caption("Live geomagnetic activity (NOAA SWPC) + upcoming close approaches (NASA/JPL CNEOS). For educational and situational awareness purposes.")

    # Current Kp / Space Weather
    kp_df = fetch_kp_index()
    if not kp_df.empty:
        latest = kp_df.iloc[0]
        kp_val = float(latest["kp"])

        if kp_val >= 9.0:
            g_level, g_desc = "G5 Extreme", "#c0392b"
        elif kp_val >= 8.0:
            g_level, g_desc = "G4 Severe", "#e67e22"
        elif kp_val >= 7.0:
            g_level, g_desc = "G3 Strong", "#f39c12"
        elif kp_val >= 6.0:
            g_level, g_desc = "G2 Moderate", "#f1c40f"
        elif kp_val >= 5.0:
            g_level, g_desc = "G1 Minor", "#27ae60"
        else:
            g_level, g_desc = "Quiet (G0)", "#7f8c8d"

        kcol1, kcol2, kcol3 = st.columns([1, 1, 1.2])
        with kcol1:
            st.metric(label="Latest Planetary Kp", value=f"{kp_val:.2f}")
        with kcol2:
            st.metric(label="Observation Time (UTC)", value=str(latest["time_utc"])[:19])
        with kcol3:
            st.markdown(f"**Geomagnetic Storm Level**: <span style='color:{g_desc};font-weight:700'>{g_level}</span>", unsafe_allow_html=True)

        # Recent Kp trend (last ~40 points ~ 3+ days)
        trend = kp_df.head(40).sort_values("time_utc")
        fig_kp = px.line(
            trend, x="time_utc", y="kp",
            title="Kp Index Trend (recent)",
            markers=True, height=260
        )
        fig_kp.update_yaxes(range=[0, 9.5], title="Kp")
        fig_kp.update_traces(line_color="#e74c3c")
        st.plotly_chart(fig_kp, use_container_width=True)
    else:
        st.warning("Could not load live Kp index data.")

    st.divider()

    # Two-column layout: Close approaches | Insurance Report
    neo_df = fetch_close_approaches()
    neo_col, ins_col = st.columns([1.05, 1.15])

    with neo_col:
        st.subheader("☄️ Upcoming Close Approaches")
        st.caption("Next 60 days | Closest or larger objects (H < 28 or <6 LD)")
        if not neo_df.empty:
            for _, r in neo_df.head(9).iterrows():
                nm = str(r.get("name", r.get("des", "Object")))[:42]
                d_ld = float(r.get("dist_ld", 0))
                hh = float(r.get("h", 99))
                dt = str(r.get("close_date", ""))[:10]
                size = "tiny" if hh > 27 else ("small" if hh > 24 else ("medium" if hh > 20 else "large"))
                st.markdown(f"**{nm}**")
                st.caption(f"{dt} • ~{d_ld:.2f} LD • H={hh:.1f} ({size}) • {float(r.get('v_inf', 0)):.0f} km/s")
                st.divider()
            st.caption("Source: [JPL CNEOS CAD](https://ssd-api.jpl.nasa.gov/doc/cad.html) – Not all objects are potentially hazardous.")
        else:
            st.info("No qualifying close approaches found in the next 60 days, or temporary data issue.")

    with ins_col:
        st.subheader("🇺🇸 USA Insurance Exposure Report")
        # Dynamic risk note
        risk_note = "Low" if kp_val < 5 else ("Elevated" if kp_val < 7 else "High")
        st.markdown(f"**Current space weather risk for USA infrastructure**: **{risk_note}** (Kp {kp_val:.1f} / {g_level})")

        st.markdown("""
**Key Exposed Sectors (United States)**

- **Electric Power Transmission & Distribution**  
  High-latitude and northeastern states are most vulnerable to Geomagnetically Induced Currents (GIC). A severe (G4–G5) storm can damage or destroy extra-high-voltage transformers, leading to long-duration blackouts. Industry and government studies model potential economic losses from a Carrington-scale event in the range of **hundreds of billions to >$2 trillion**.

- **Satellite Operators & Space Assets**  
  The U.S. commercial satellite fleet (Starlink, OneWeb, GEO comms, Earth observation, GPS augmentation) numbers in the thousands. Increased atmospheric drag, surface charging, and single-event upsets during solar storms represent a growing insured value.

- **Aviation & Polar Routes**  
  During solar proton events and strong geomagnetic storms, airlines reroute polar flights, incurring extra fuel and crew costs. Radiation exposure considerations for crews and passengers also factor into insurance.

- **Oil, Gas & Pipeline Infrastructure**  
  GIC can interfere with pipeline integrity monitoring systems and SCADA networks.

**Historical / Scenario Benchmarks (public literature)**
- 1989 Quebec G5 storm: ~6 million customers without power for hours to days.
- 1859 Carrington Event (extreme benchmark): Modern repeat scenarios frequently cited by insurers and Lloyd’s reports with potential insured losses in the **$100B – low trillions** range depending on severity and duration.

*This report is an educational synthesis of public scientific and industry sources (NOAA, NASA, USGS, National Academies, Lloyd’s reports). It is not actuarial advice or a catastrophe model output. For underwriting or risk transfer decisions, consult qualified catastrophe modelers and current scientific literature.*
""")

    st.sidebar.info("Data auto-refreshes every 30 min | USGS – NOAA (NHC/SWPC) – JTWC – NASA/JPL")

# Footer note
st.caption("Enhanced with Space Hazards & USA Insurance view • Open data only • Not for operational decision-making without professional validation")
