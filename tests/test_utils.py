"""Tests for utility functions"""

import pytest
from datetime import datetime
from securepremium.utils.helpers import (
    setup_logging,
    safe_get,
    normalize_risk_score,
    calculate_percentile,
    format_currency,
    validate_device_id,
    validate_risk_score,
    validate_reputation_score,
)


class TestUtilityFunctions:
    """Test suite for utility helper functions"""

    def test_setup_logging(self):
        """Test logging setup"""
        logger = setup_logging("test_logger", level="INFO")

        assert logger is not None
        assert logger.name == "test_logger"

    def test_safe_get_simple_path(self):
        """Test safe get with simple path"""
        data = {"user": {"name": "John", "age": 30}}

        result = safe_get(data, "user.name")

        assert result == "John"

    def test_safe_get_missing_path(self):
        """Test safe get with missing path"""
        data = {"user": {"name": "John"}}

        result = safe_get(data, "user.email", default="unknown@example.com")

        assert result == "unknown@example.com"

    def test_normalize_risk_score(self):
        """Test risk score normalization"""
        normalized = normalize_risk_score(1.5)

        assert normalized == 1.0

    def test_normalize_risk_score_below_min(self):
        """Test normalization clamps below minimum"""
        normalized = normalize_risk_score(-0.5)

        assert normalized == 0.0

    def test_calculate_percentile(self):
        """Test percentile calculation"""
        values = [1, 2, 3, 4, 5]
        percentile = calculate_percentile(3, values)

        assert 40 <= percentile <= 60

    def test_format_currency_usd(self):
        """Test USD currency formatting"""
        formatted = format_currency(125.50, "USD")

        assert "$125.50" in formatted

    def test_format_currency_eur(self):
        """Test EUR currency formatting"""
        formatted = format_currency(100.0, "EUR")

        assert "€100.00" in formatted

    def test_validate_device_id_valid(self):
        """Test device ID validation with valid ID"""
        assert validate_device_id("device_001_abc123") is True

    def test_validate_device_id_invalid_length(self):
        """Test device ID validation with invalid length"""
        assert validate_device_id("short") is False

    def test_validate_device_id_none(self):
        """Test device ID validation with None"""
        assert validate_device_id(None) is False

    def test_validate_risk_score_valid(self):
        """Test risk score validation"""
        assert validate_risk_score(0.5) is True
        assert validate_risk_score(0.0) is True
        assert validate_risk_score(1.0) is True

    def test_validate_risk_score_invalid(self):
        """Test invalid risk scores"""
        assert validate_risk_score(1.5) is False
        assert validate_risk_score(-0.1) is False

    def test_validate_reputation_score_valid(self):
        """Test reputation score validation"""
        assert validate_reputation_score(0.75) is True

    def test_validate_reputation_score_invalid(self):
        """Test invalid reputation scores"""
        assert validate_reputation_score(1.5) is False
        assert validate_reputation_score(-0.5) is False
