"""Market Factor Stress Testing module (Pure Market - Option A).

This is the current implementation of pure market factor stress testing.
It now uses real Fama-French 5-Factor data + covariance matrix.
"""

import streamlit as st
import pandas as pd
import numpy as np

from .fama_french import fetch_fama_french_factors, get_factor_covariance_matrix


def render():
    """Render the pure market factor stress testing UI using real data."""
    st.subheader("Factor Shock Simulator (Pure Market)")

    with st.expander("How this works (business explanation)", expanded=False):
        st.markdown("""
        We load real daily Fama-French 5-Factor returns + build an annualized 
        covariance matrix from the last 5 years.

        You choose shocks to each factor → we compute the portfolio impact 
        using your betas and the factor covariance.

        This follows the same logic used by professional risk systems 
        (Barra, Axioma, internal bank models).
        """)

    # Load real data
    try:
        ff = fetch_fama_french_factors()
        cov_matrix = get_factor_covariance_matrix(lookback_days=1260)  # ~5 years
        st.success(f"Loaded Fama-French data from {ff.index.min().date()} to {ff.index.max().date()}")
    except Exception as e:
        st.error(f"Failed to load Fama-French data: {e}")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Factor Shocks (in percent)**")
        shocks = {
            "Mkt-RF": st.slider("Market (Mkt-RF)", -50, 30, -20, 5),
            "SMB":    st.slider("Size (SMB)",     -30, 30, 5, 5),
            "HML":    st.slider("Value (HML)",    -30, 30, -10, 5),
            "RMW":    st.slider("Profitability (RMW)", -20, 20, 0, 5),
            "CMA":    st.slider("Investment (CMA)", -20, 20, 0, 5),
        }

    with col2:
        st.markdown("**Your Portfolio Factor Loadings (Betas)**")
        betas = {
            "Mkt-RF": st.number_input("Market Beta", value=1.0, step=0.1),
            "SMB":    st.number_input("Size Beta", value=0.3, step=0.1),
            "HML":    st.number_input("Value Beta", value=-0.2, step=0.1),
            "RMW":    st.number_input("Profitability Beta", value=0.1, step=0.1),
            "CMA":    st.number_input("Investment Beta", value=-0.1, step=0.1),
        }

    # Compute expected return impact using linear factor model
    factor_shocks = pd.Series(shocks) / 100.0
    portfolio_betas = pd.Series(betas)

    expected_return_impact = (portfolio_betas * factor_shocks).sum() * 100

    # Approximate stressed volatility using the covariance matrix
    # (simplified: we ignore the specific risk for now)
    factor_vol_shock = np.sqrt(portfolio_betas @ cov_matrix @ portfolio_betas) * 100

    st.subheader("Estimated Impact")

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Expected Return Impact", f"{expected_return_impact:.2f}%")
    with c2:
        st.metric("Approx. Factor-Driven Volatility (annualized)", f"{factor_vol_shock:.1f}%")

    st.caption("This uses the last 5 years of real Fama-French factor returns to build the covariance matrix.")

    with st.expander("View Covariance Matrix (annualized, last 5 years)"):
        st.dataframe(cov_matrix.round(4))
