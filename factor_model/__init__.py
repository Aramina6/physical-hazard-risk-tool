"""Factor Model package.

This package will contain all logic related to:
- Factor extraction / loading (Fama-French, macro, PCA, etc.)
- Covariance matrix construction
- Stress scenario generation by shocking factors
- Portfolio impact calculation

We are starting with pure market factor stress testing (Option A)
before adding physical hazard overlays. This mirrors how real finance
and insurance firms build and stress their risk models.
"""

from . import market_factor_stress

__all__ = ["market_factor_stress"]
