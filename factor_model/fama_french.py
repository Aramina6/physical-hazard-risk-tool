"""Fama-French factor data loader for the Physical Hazard Risk Tool.

This module is responsible for fetching and preparing the Fama-French 
5-Factor (plus RF) daily data from Ken French's website.

It returns a clean DataFrame with:
- Mkt-RF, SMB, HML, RMW, CMA, RF

Functions:
- fetch_fama_french_factors() -> pd.DataFrame
- get_factor_covariance_matrix(lookback_days=1260) -> pd.DataFrame

Business rationale:
Finance and insurance risk teams almost always start stress testing from
their existing factor risk model (Barra, Axioma, or internal PCA models).
We replicate that exact pattern using the most widely used public factor set.
"""

import pandas as pd
import requests
from io import BytesIO
from zipfile import ZipFile
import streamlit as st


@st.cache_data(ttl=86400)  # Cache for 24 hours

def fetch_fama_french_factors() -> pd.DataFrame:
    """
    Download the latest daily Fama-French 5-Factor data from Ken French.
    Returns a DataFrame indexed by date with columns:
    ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA', 'RF']
    Values are in decimal form (not percent).
    """
    url = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip'

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    with ZipFile(BytesIO(response.content)) as z:
        csv_name = [name for name in z.namelist() if '.CSV' in name.upper()][0]
        with z.open(csv_name) as f:
            df = pd.read_csv(f, skiprows=3)

    df.columns = ['Date', 'Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA', 'RF']
    df = df.dropna()
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
    df = df.set_index('Date')
    df = df.apply(pd.to_numeric, errors='coerce') / 100.0

    return df


def get_factor_covariance_matrix(lookback_days: int = 1260) -> pd.DataFrame:
    """
    Compute annualized covariance matrix of the 5 Fama-French factors
    over the most recent lookback period (default ~5 years of trading days).

    Returns a 5x5 covariance matrix (Mkt-RF, SMB, HML, RMW, CMA).
    """
    df = fetch_fama_french_factors()
    recent = df[['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA']].dropna().tail(lookback_days)
    cov = recent.cov() * 252  # Annualize daily covariance
    return cov
