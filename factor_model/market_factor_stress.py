"""Market Factor Stress Testing module (Pure Market - Option A).

Integrated with scenario_library for easy loading of historical and stylized events
(e.g. Iran-Iraq War oil shock) that auto-populate factor shocks + show impacted industries.
"""

import streamlit as st
import pandas as pd
import numpy as np

from .fama_french import fetch_fama_french_factors, get_factor_covariance_matrix

from .scenario_library import get_scenario_names, get_scenario


def render():
    """Render the pure market factor stress testing UI with scenario library."""
    st.subheader("Factor Shock Simulator (Pure Market)")

    with st.expander("How this works (business explanation)", expanded=False):
        st.markdown("""
        We load real daily Fama-French 5-Factor returns + build an annualized 
        covariance matrix from the last 5 years.

        You can either:
        - Load a pre-defined historical/stylized scenario (recommended for decision making), or
        - Manually adjust the factor shocks with the sliders.

        Each scenario also shows which industries are typically most impacted — very useful for portfolio managers and risk teams.
        """)

    # Load real data
    try:
        ff = fetch_fama_french_factors()
        cov_matrix = get_factor_covariance_matrix(lookback_days=1260)
        st.success(f"Loaded Fama-French data from {ff.index.min().date()} to {ff.index.max().date()}")
    except Exception as e:
        st.error(f"Failed to load Fama-French data: {e}")
        return

    # === Scenario Library ===
    st.markdown("**Load Historical or Stylized Scenario**")
    scenario_names = get_scenario_names()
    selected_scenario = st.selectbox(
        "Choose a scenario",
        options=scenario_names,
        index=0,  # Default to Custom
        help="Selecting a scenario will suggest factor shocks based on historical behavior. You can still adjust the sliders."
    )

    scenario = get_scenario(selected_scenario)
    suggested_shocks = scenario['factor_shocks']
    industries = scenario['industries_impacted']
    description = scenario['description']

    if selected_scenario != 'Custom (Manual Shocks)':
        st.info(f"**{selected_scenario}**\n\n{description}")
        st.markdown("**Industries Typically Most Impacted:**")
        for ind in industries:
            st.markdown(f"- {ind}")

    # === Factor Shocks (populated from scenario or manual) ===
    st.markdown("**Factor Shocks (in percent)**")

    # Use session_state to allow scenario to influence sliders
    if 'factor_shocks' not in st.session_state:
        st.session_state.factor_shocks = suggested_shocks

    # If user changed scenario, update session state
    if st.session_state.get('last_scenario') != selected_scenario:
        st.session_state.factor_shocks = suggested_shocks.copy()
        st.session_state.last_scenario = selected_scenario

    col1, col2 = st.columns(2)

    with col1:
        mkt_shock = st.slider("Market (Mkt-RF)", -50, 30, st.session_state.factor_shocks.get('Mkt-RF', 0), 5, key="shock_mkt")
        smb_shock = st.slider("Size (SMB)", -30, 30, st.session_state.factor_shocks.get('SMB', 0), 5, key="shock_smb")
        hml_shock = st.slider("Value (HML)", -30, 30, st.session_state.factor_shocks.get('HML', 0), 5, key="shock_hml")

    with col2:
        rmw_shock = st.slider("Profitability (RMW)", -20, 20, st.session_state.factor_shocks.get('RMW', 0), 5, key="shock_rmw")
        cma_shock = st.slider("Investment (CMA)", -20, 20, st.session_state.factor_shocks.get('CMA', 0), 5, key="shock_cma")
        vix_shock = st.slider("Volatility (VIX proxy)", -30, 80, st.session_state.factor_shocks.get('VIX', 0), 5, key="shock_vix")

    # Update session state with current slider values
    st.session_state.factor_shocks = {
        'Mkt-RF': mkt_shock,
        'SMB': smb_shock,
        'HML': hml_shock,
        'RMW': rmw_shock,
        'CMA': cma_shock,
        'VIX': vix_shock,
    }

    # === Portfolio Betas ===
    st.markdown("**Your Portfolio Factor Loadings (Betas)**")
    col3, col4 = st.columns(2)
    with col3:
        b_mkt = st.number_input("Market Beta", value=1.0, step=0.1, key="beta_mkt")
        b_smb = st.number_input("Size Beta", value=0.3, step=0.1, key="beta_smb")
        b_hml = st.number_input("Value Beta", value=-0.2, step=0.1, key="beta_hml")
    with col4:
        b_rmw = st.number_input("Profitability Beta", value=0.1, step=0.1, key="beta_rmw")
        b_cma = st.number_input("Investment Beta", value=-0.1, step=0.1, key="beta_cma")
        b_vix = st.number_input("Vol Beta", value=0.4, step=0.1, key="beta_vix")

    # Calculations
    shocks_series = pd.Series(st.session_state.factor_shocks) / 100.0
    betas_series = pd.Series({
        'Mkt-RF': b_mkt, 'SMB': b_smb, 'HML': b_hml,
        'RMW': b_rmw, 'CMA': b_cma, 'VIX': b_vix
    })

    expected_impact = (betas_series * shocks_series).sum() * 100
    factor_vol = np.sqrt(betas_series[['Mkt-RF','SMB','HML','RMW','CMA']] @ cov_matrix @ betas_series[['Mkt-RF','SMB','HML','RMW','CMA']]) * 100

    st.subheader("Estimated Portfolio Impact")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Expected Return Impact", f"{expected_impact:.2f}%")
    with c2:
        st.metric("Factor-Driven Volatility (annualized)", f"{factor_vol:.1f}%")

    st.caption("Scenarios are stylized based on historical factor behavior. Always review and adjust for your specific portfolio.")

    with st.expander("View Current Covariance Matrix"):
        st.dataframe(cov_matrix.round(4))
