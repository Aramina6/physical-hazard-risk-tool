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
    page_title="Physical Hazard Risk Tool | Market Factor Stress Testing",
    page_icon="📈",
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
    """Fetch recent planetary K-index from NOAA SWPC.
    The API now returns list of dicts with column 'Kp' (capital K).
    """
    url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
    try:
        data = requests.get(url, timeout=15).json()
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)                    # list of dicts
        df["time_utc"] = pd.to_datetime(df["time_tag"])
        df["kp"] = pd.to_numeric(df["Kp"], errors="coerce")   # capital K
        df = df.dropna(subset=["kp"]).sort_values("time_utc", ascending=False)
        return df
    except Exception as e:
        st.error(f"Space weather (Kp) error: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_close_approaches(days_ahead=60, dist_max_au=0.08):
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

# ----------------------------------------------------------------------
# US INSURANCE & DISASTER DATA – FEMA OpenFEMA
# ----------------------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_fema_disaster_declarations(years_back=8):
    base = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"
    start_year = datetime.utcnow().year - years_back
    url = (
        f"{base}?$format=json&$top=10000"
        f"&$filter=declarationDate ge '{start_year}-01-01'"
        f"&$select=state,incidentType,declarationDate,disasterNumber"
    )
    try:
        data = requests.get(url, timeout=30).json()
        df = pd.DataFrame(data.get("DisasterDeclarationsSummaries", []))
        if not df.empty:
            df["declarationDate"] = pd.to_datetime(df["declarationDate"], errors="coerce")
            df["year"] = df["declarationDate"].dt.year
        return df
    except Exception as e:
        st.error(f"FEMA Declarations error: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_nfip_claims_state_summary(years_back=6):
    """Fetch and aggregate NFIP claims using the correct payment fields from OpenFEMA.
    The schema uses amountPaidOn* columns (not totalPaid).
    """
    base = "https://www.fema.gov/api/open/v2/FimaNfipClaims"
    start_year = datetime.utcnow().year - years_back
    url = (
        f"{base}?$format=json&$top=25000"
        f"&$filter=yearOfLoss ge {start_year}"
        f"&$select=state,yearOfLoss,amountPaidOnBuildingClaim,amountPaidOnContentsClaim,amountPaidOnIncreasedCostOfComplianceClaim"
    )
    try:
        data = requests.get(url, timeout=50).json()
        df = pd.DataFrame(data.get("FimaNfipClaims", []))
        if df.empty:
            return pd.DataFrame()

        for col in ["amountPaidOnBuildingClaim", "amountPaidOnContentsClaim", "amountPaidOnIncreasedCostOfComplianceClaim"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            else:
                df[col] = 0.0

        df["totalPaid"] = (
            df["amountPaidOnBuildingClaim"] +
            df["amountPaidOnContentsClaim"] +
            df["amountPaidOnIncreasedCostOfComplianceClaim"]
        )

        summary = (
            df.groupby(["state", "yearOfLoss"])
            .agg(total_paid=("totalPaid", "sum"), claims_count=("totalPaid", "count"))
            .reset_index()
        )
        summary["total_paid_millions"] = (summary["total_paid"] / 1_000_000).round(1)
        return summary
    except Exception as e:
        st.error(f"NFIP Claims error: {e}")
        return pd.DataFrame()

# ----------------------------------------------------------------------
# RESTRUCTURED UI — Financial Tool First
# Physical hazard modules moved to left sidebar
# ----------------------------------------------------------------------
st.title("Physical Hazard Risk Tool")
st.markdown("**Market Factor Stress Testing + Physical Hazard Context**")

# Left sidebar — Physical Hazard modules (now secondary)
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

# Main content area starts with Market Factor Stress Testing (primary focus)
st.header("Market Factor Stress Testing — Pure Market")
st.markdown("""
**Focus**: Pure market factor model + stress scenarios using open data.

Physical hazard modules are available on the **left sidebar** for context when building hybrid scenarios later.
""")

# ============================================================
# PURE MARKET FACTOR STRESS TESTING (MVP)
# ============================================================

st.subheader("Factor Shock Simulator")

with st.expander("How this works (Factor Model Basics)", expanded=False):
    st.markdown("""
    - We use a simplified multi-factor framework (inspired by Fama-French + macro factors).
    - You shock the factors → we propagate the shocks through a covariance matrix.
    - Result: Stressed portfolio volatility / VaR impact.
    """)

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Factor Shocks (%)**")
    mkt_shock = st.slider("Market (Mkt-RF)", -50, 30, -20, 5)
    smb_shock = st.slider("Size (SMB)", -30, 30, 5, 5)
    hml_shock = st.slider("Value (HML)", -30, 30, -10, 5)
    rmw_shock = st.slider("Profitability (RMW)", -20, 20, 0, 5)
    cma_shock = st.slider("Investment (CMA)", -20, 20, 0, 5)
    vix_shock = st.slider("Volatility (VIX proxy)", -30, 80, 30, 5)

with col2:
    st.markdown("**Portfolio Factor Loadings (Betas)**")
    b_mkt = st.number_input("Market Beta", value=1.0, step=0.1)
    b_smb = st.number_input("Size Beta", value=0.3, step=0.1)
    b_hml = st.number_input("Value Beta", value=-0.2, step=0.1)
    b_rmw = st.number_input("Profitability Beta", value=0.1, step=0.1)
    b_cma = st.number_input("Investment Beta", value=-0.1, step=0.1)
    b_vix = st.number_input("Vol Beta", value=0.4, step=0.1)

# Simple stress calculation (toy model for now)
st.subheader("Stressed Impact (Illustrative)")

factor_shocks = [mkt_shock, smb_shock, hml_shock, rmw_shock, cma_shock, vix_shock]
betas = [b_mkt, b_smb, b_hml, b_rmw, b_cma, b_vix]

# Very simplified "expected return impact" and volatility increase
expected_impact = sum([b * s for b, s in zip(betas, factor_shocks)])

st.metric("Approximate Portfolio Return Impact", f"{expected_impact:.1f}%", 
          delta=f"{expected_impact - 0:.1f}% vs base")

st.caption("Note: This is a simplified illustration. Full version will include a proper covariance matrix and VaR calculation.")

st.info("Next iteration will include: real Fama-French data, full covariance matrix, multiple stress scenarios, and portfolio upload.")

# ============================================================
# RENDER PHYSICAL MODULES (based on left sidebar selection)
# ============================================================

if phys_choice == "Earthquakes":
    with st.expander("🌍 Earthquakes (USGS) - Last 30 Days", expanded=True):
        min_mag = st.slider("Minimum Magnitude", 0.0, 10.0, 1.0, 0.5, key="phys_eq")
        df = fetch_earthquakes_month()
        if not df.empty:
            df = df[df["magnitude"] >= min_mag]
            st.dataframe(df.head(15), use_container_width=True)
        else:
            st.info("No earthquake data available.")

elif phys_choice == "Tropical Cyclones":
    with st.expander("🌀 Tropical Cyclones (NOAA / JTWC)", expanded=True):
        df = fetch_cyclones_month()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No active cyclones (off-season).")

elif phys_choice == "Space Hazards (USA)":
    with st.expander("☄️ Space Hazards (USA) - Kp + NEOs", expanded=True):
        st.markdown("See the original Space Hazards tab logic (Kp + Close Approaches). Full rendering can be restored here.")

elif phys_choice == "NFIP Insurance Analytics":
    with st.expander("🇺🇸 NFIP Insurance Analytics (FEMA)", expanded=True):
        claims = fetch_nfip_claims_state_summary(years_back=5)
        if not claims.empty:
            st.dataframe(claims.head(20), use_container_width=True)
        else:
            st.warning("NFIP data temporarily unavailable in this view.")

st.caption("Physical Hazard Risk Tool • Market Factor Stress Testing + Physical Context • Open Data")
