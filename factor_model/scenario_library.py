"""Scenario Library for Market Factor Stress Testing (Pure Market - Option A).

This module defines historical and stylized stress scenarios as vectors of factor shocks.
It follows industry best practice (Kapinos 2015, Lopez 2005, Rosenberg APT framework):
scenarios are expressed as shocks to underlying risk factors rather than individual securities.

Each scenario includes:
- factor_shocks: dict of % shocks to Fama-French + volatility factors
- industries_impacted: list of sectors most affected (for business context / decision making)
- description: short explanation of the economic narrative

Usage:
    from factor_model.scenario_library import SCENARIOS, get_scenario
    scenario = get_scenario('Iran-Iraq War (1980-88) / Major Middle East Oil Shock')
    shocks = scenario['factor_shocks']
    industries = scenario['industries_impacted']
"""

SCENARIOS = {
    'Custom (Manual Shocks)': {
        'factor_shocks': {
            'Mkt-RF': 0,
            'SMB': 0,
            'HML': 0,
            'RMW': 0,
            'CMA': 0,
            'VIX': 0,
        },
        'industries_impacted': ['All sectors (user-defined)'],
        'description': 'Start with zero shocks and manually adjust factors using the sliders.',
    },

    'Iran-Iraq War (1980-88) / Major Middle East Oil Shock': {
        'factor_shocks': {
            'Mkt-RF': -22,
            'SMB': +8,
            'HML': +25,
            'RMW': -5,
            'CMA': -12,
            'VIX': +45,
        },
        'industries_impacted': [
            'Energy (strongly positive - oil price spike)',
            'Financials (mixed - credit risk up, some lenders benefit)',
            'Consumer Discretionary (negative - higher energy costs hurt spending)',
            'Transportation & Airlines (strongly negative)',
            'Utilities (mixed - higher input costs)',
            'Materials (positive if commodity exposure)',
        ],
        'description': (
            'Prolonged conflict between Iran and Iraq caused major oil supply disruptions and price spikes. '
            'Energy stocks (especially small/mid-cap) outperformed dramatically while broad markets sold off. '
            'High inflation and volatility environment. Classic stagflation-type factor rotation with strong HML and Energy outperformance.'
        ),
    },

    '1990 Gulf War (Iraq invades Kuwait)': {
        'factor_shocks': {
            'Mkt-RF': -18,
            'SMB': +5,
            'HML': +18,
            'RMW': -3,
            'CMA': -8,
            'VIX': +35,
        },
        'industries_impacted': [
            'Energy',
            'Aerospace & Defense (positive)',
            'Financials (mixed)',
            'Consumer Staples (relative outperformer)',
        ],
        'description': (
            'Sudden invasion led to sharp oil price spike and brief recession fears. '
            'Strong rotation into Value and Energy. Markets recovered quickly once coalition military response began.'
        ),
    },

    '2008 Global Financial Crisis': {
        'factor_shocks': {
            'Mkt-RF': -45,
            'SMB': -25,
            'HML': -15,
            'RMW': -20,
            'CMA': -10,
            'VIX': +120,
        },
        'industries_impacted': [
            'Financials (devastated - banking crisis)',
            'Real Estate (collapse)',
            'Consumer Discretionary (sharp drop in spending)',
            'Industrials',
            'Energy (hit late in the crisis)',
        ],
        'description': (
            'Systemic banking and liquidity crisis. Massive negative shocks across almost all factors, especially Market and Size. '
            'Volatility exploded to historic levels. Worst drawdown in modern history for most equity and factor portfolios.'
        ),
    },

    '2020 COVID-19 Crash & Recovery': {
        'factor_shocks': {
            'Mkt-RF': -35,
            'SMB': -15,
            'HML': -25,
            'RMW': +10,
            'CMA': -5,
            'VIX': +85,
        },
        'industries_impacted': [
            'Energy (worst hit - demand collapse)',
            'Financials',
            'Industrials & Travel / Airlines (devastated)',
            'Technology (relative outperformer after initial crash)',
            'Healthcare & Consumer Staples (defensive winners)',
        ],
        'description': (
            'Sharp liquidity-driven selloff followed by unprecedented monetary and fiscal response. '
            'Classic growth / low-quality rotation. High volatility with extremely rapid recovery in many factors.'
        ),
    },

    '2022 Russia-Ukraine Invasion + Inflation Shock': {
        'factor_shocks': {
            'Mkt-RF': -22,
            'SMB': -8,
            'HML': +12,
            'RMW': -8,
            'CMA': -5,
            'VIX': +40,
        },
        'industries_impacted': [
            'Energy (strong positive - commodity spike)',
            'Materials & Commodities',
            'Financials (mixed - higher rates help net interest margins)',
            'Consumer Discretionary (negative - inflation + war uncertainty)',
            'Technology Growth (negative - higher discount rates)',
        ],
        'description': (
            'Geopolitical shock combined with sudden inflation spike. Strong rotation into Value, Energy, and Commodities. '
            'Growth stocks sold off hard. Excellent modern example of commodity + value factor outperformance during conflict and inflation.'
        ),
    },
}


def get_scenario_names():
    """Return list of available scenario names for UI dropdown."""
    return list(SCENARIOS.keys())


def get_scenario(name: str):
    """Return the scenario dict for a given name. Falls back to Custom if not found."""
    return SCENARIOS.get(name, SCENARIOS['Custom (Manual Shocks)'])
