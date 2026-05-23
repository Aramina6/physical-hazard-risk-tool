"""Unit tests for data fetchers in the Multi-Hazard Monitoring dashboard.

These tests focus on resilience (empty responses, bad data) and correct aggregation logic.
"""

import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

import app


# Clear Streamlit cache before every test so mocks work reliably
def setup_function():
    try:
        app.fetch_kp_index.clear()
        app.fetch_nfip_claims_state_summary.clear()
        app.fetch_fema_disaster_declarations.clear()
    except Exception:
        pass


class TestFetchKpIndex:
    """Tests for the Kp index fetcher (handles both old and new NOAA API formats)."""

    def test_returns_empty_on_api_failure(self):
        with patch("app.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = []
            mock_get.return_value = mock_response
            df = app.fetch_kp_index()
            assert df.empty

    def test_parses_new_dict_format(self):
        """Current NOAA format returns list of dicts with 'Kp' (capital K)."""
        fake_data = [
            {"time_tag": "2026-05-01T00:00:00", "Kp": 3.5, "a_running": 10, "station_count": 8},
            {"time_tag": "2026-05-01T03:00:00", "Kp": 4.2, "a_running": 15, "station_count": 8},
        ]
        with patch("app.requests.get") as mock_get:
            mock_get.return_value.json.return_value = fake_data
            df = app.fetch_kp_index()
            assert not df.empty
            assert "kp" in df.columns
            # Find the row with the highest value instead of relying on order
            assert df["kp"].max() == 4.2


class TestFetchNifpClaims:
    """Tests for NFIP claims aggregation using correct FEMA fields."""

    def test_returns_empty_when_no_data(self):
        with patch("app.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {"FimaNfipClaims": []}
            df = app.fetch_nfip_claims_state_summary(years_back=2)
            assert df.empty

    def test_correctly_sums_payment_fields(self):
        fake_claims = [
            {
                "state": "FL",
                "yearOfLoss": 2024,
                "amountPaidOnBuildingClaim": 100000,
                "amountPaidOnContentsClaim": 20000,
                "amountPaidOnIncreasedCostOfComplianceClaim": 5000,
            },
            {
                "state": "FL",
                "yearOfLoss": 2024,
                "amountPaidOnBuildingClaim": 50000,
                "amountPaidOnContentsClaim": 10000,
                "amountPaidOnIncreasedCostOfComplianceClaim": 0,
            },
        ]
        with patch("app.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {"FimaNfipClaims": fake_claims}
            summary = app.fetch_nfip_claims_state_summary(years_back=2)

            assert not summary.empty
            # Find the FL 2024 row regardless of order
            row = summary.query("state == 'FL' and yearOfLoss == 2024").iloc[0]
            assert row["total_paid"] == 185000   # 150k + 30k + 5k
            assert row["claims_count"] == 2


class TestFetchDisasterDeclarations:
    """Basic smoke test for FEMA declarations fetcher."""

    def test_handles_empty_response(self):
        with patch("app.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {"DisasterDeclarationsSummaries": []}
            df = app.fetch_fema_disaster_declarations(years_back=1)
            assert df.empty
