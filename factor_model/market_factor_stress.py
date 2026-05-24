"""Market Factor Stress Testing module.

Pure market factor stress testing (Option A).

This module implements a simplified multi-factor shock simulator.
The goal is to let users define shocks to common risk factors
(Market, Size, Value, etc.) and see the approximate impact on a portfolio.

Why this approach?
- Real risk systems (Barra, Axioma, internal bank models) work by
  shocking the underlying factors, not individual positions.
- We follow the same philosophy (see Kapinos 2015, Rosenberg APT framework).
- This keeps the model transparent and easy to extend later with
  physical hazard factors.

Future improvements will include:
- Real Fama-French + macro factor data
- Proper covariance matrix (historical + shrinkage)
- Multiple pre-built stress scenarios
- Portfolio upload
"""

import streamlit as st


def render():
    """Render the pure market factor stress testing UI."""
    st.subheader("Factor Shock Simulator (Pure Market)")

    with st.expander("How this works (business explanation)", expanded=False):
        st.markdown("""
        We use a simplified multi-factor model (inspired by Fama-French 5-factor + volatility).

        You choose how much to shock each factor -> we apply your portfolio's sensitivity (beta)
        to those shocks -> we show the approximate P&L impact.

        This is the same mental model used by banks and insurers when they run
        stress tests on their factor risk models.
        """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Factor Shocks (%)**")
        mkt_shock = st.slider("Market (Mkt-RF)", -50, 30, -20, 5, key="mkt")
        smb_shock = st.slider("Size (SMB)", -30, 30, 5, 5, key="smb")
        hml_shock = st.slider("Value (HML)", -30, 30, -10, 5, key="hml")
        rmw_shock = st.slider("Profitability (RMW)", -20, 20, 0, 5, key="rmw")
        cma_shock = st.slider("Investment (CMA)", -20, 20, 0, 5, key="cma")
        vix_shock = st.slider("Volatility (VIX proxy)", -30, 80, 30, 5, key="vix")

    with col2:
        st.markdown("**Your Portfolio's Factor Loadings (Betas)**")
        b_mkt = st.number_input("Market Beta", value=1.0, step=0.1, key="b_mkt")
        b_smb = st.number_input("Size Beta", value=0.3, step=0.1, key="b_smb")
        b_hml = st.number_input("Value Beta", value=-0.2, step=0.1, key="b_hml")
        b_rmw = st.number_input("Profitability Beta", value=0.1, step=0.1, key="b_rmw")
        b_cma = st.number_input("Investment Beta", value=-0.1, step=0.1, key="b_cma")
        b_vix = st.number_input("Vol Beta", value=0.4, step=0.1, key="b_vix")

    # Simple linear impact (toy model)
    factor_shocks = [mkt_shock, smb_shock, hml_shock, rmw_shock, cma_shock, vix_shock]
    betas = [b_mkt, b_smb, b_hml, b_rmw, b_cma, b_vix]
    expected_impact = sum(b * s for b, s in zip(betas, factor_shocks))

    st.subheader("Estimated Portfolio Impact")
    st.metric("Approximate Return Impact", f"{expected_impact:.1f}%")

    st.caption("This is an illustrative calculation. A production version will use a full covariance matrix and proper factor returns.")
