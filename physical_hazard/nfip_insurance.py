"""NFIP Insurance Analytics module - Physical Hazard Risk Tool.

Handles FEMA NFIP claims and disaster declarations aggregation.
This is the most direct bridge from physical events to financial loss data.

Business Context (why this module exists):
- NFIP is one of the few large-scale public sources of actual insured loss data in the US.
- Insurers and reinsurers use it to validate cat models and understand loss development.
- In the factor modeling framework, "Flood losses in Florida" or "Hurricane landfall claims"
  can be treated as observable outcomes that help calibrate the physical-to-financial mapping.
"""

import streamlit as st
import pandas as pd
import requests
from datetime import datetime

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
    """Aggregate NFIP claims by state and year using correct OpenFEMA fields."""
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


def render():
    """Render the NFIP Insurance Analytics module."""
    st.subheader("🇺🇸 NFIP Insurance Analytics (FEMA)")
    st.caption("State-level flood insurance claims and disaster declarations")

    claims = fetch_nfip_claims_state_summary(years_back=5)
    if not claims.empty:
        st.dataframe(claims.sort_values("total_paid_millions", ascending=False).head(15), use_container_width=True)
    else:
        st.warning("NFIP claims data temporarily unavailable.")

    decls = fetch_fema_disaster_declarations(years_back=5)
    if not decls.empty:
        st.dataframe(decls.head(10), use_container_width=True)
