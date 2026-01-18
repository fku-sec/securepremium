"""Tests for premium engine module"""

import pytest
from datetime import datetime
from securepremium.core.premium_engine import PremiumEngine, PremiumQuote
from securepremium.core.risk_calculator import RiskAssessment


class TestPremiumEngine:
    """Test suite for PremiumEngine"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = PremiumEngine()
        self.test_assessment = RiskAssessment(
            device_id="device_001",
            timestamp=datetime.utcnow(),
            overall_risk_score=0.50,
            behavioral_risk=0.45,
            hardware_risk=0.55,
            network_risk=0.48,
            anomaly_score=0.40,
            threat_indicators=[],
            confidence_level=0.85,
        )

    def test_engine_initialization(self):
        """Test premium engine initializes correctly"""
        assert self.engine is not None
        assert self.engine.base_annual_premium == 120.0
        assert "basic" in self.engine.coverage_tiers
        assert "standard" in self.engine.coverage_tiers
        assert "premium" in self.engine.coverage_tiers

    def test_generate_quote_basic(self):
        """Test generating basic coverage quote"""
        quote = self.engine.generate_quote(
            device_id="device_001",
            risk_assessment=self.test_assessment,
            reputation_score=0.70,
            coverage_level="basic",
        )

        assert isinstance(quote, PremiumQuote)
        assert quote.device_id == "device_001"
        assert quote.coverage_level == "basic"
        assert quote.annual_premium_usd > 0
        assert quote.monthly_premium_usd > 0

    def test_generate_quote_all_tiers(self):
        """Test generating quotes for all coverage tiers"""
        for tier in ["basic", "standard", "premium"]:
            quote = self.engine.generate_quote(
                device_id="device_001",
                risk_assessment=self.test_assessment,
                coverage_level=tier,
            )

            assert quote.coverage_level == tier
            assert quote.annual_premium_usd > 0

    def test_quote_cost_increases_with_risk(self):
        """Test that higher risk increases premium"""
        low_risk_assessment = RiskAssessment(
            device_id="device_low",
            timestamp=datetime.utcnow(),
            overall_risk_score=0.2,
            behavioral_risk=0.1,
            hardware_risk=0.2,
            network_risk=0.15,
            anomaly_score=0.1,
            threat_indicators=[],
            confidence_level=0.90,
        )

        high_risk_assessment = RiskAssessment(
            device_id="device_high",
            timestamp=datetime.utcnow(),
            overall_risk_score=0.8,
            behavioral_risk=0.75,
            hardware_risk=0.85,
            network_risk=0.78,
            anomaly_score=0.80,
            threat_indicators=["Multiple threats"],
            confidence_level=0.85,
        )

        low_quote = self.engine.generate_quote(
            device_id="device_low",
            risk_assessment=low_risk_assessment,
        )

        high_quote = self.engine.generate_quote(
            device_id="device_high",
            risk_assessment=high_risk_assessment,
        )

        assert high_quote.annual_premium_usd > low_quote.annual_premium_usd

    def test_reputation_discount_applied(self):
        """Test that reputation score affects premium"""
        good_reputation_quote = self.engine.generate_quote(
            device_id="device_001",
            risk_assessment=self.test_assessment,
            reputation_score=0.90,
        )

        poor_reputation_quote = self.engine.generate_quote(
            device_id="device_001",
            risk_assessment=self.test_assessment,
            reputation_score=0.20,
        )

        assert good_reputation_quote.annual_premium_usd < poor_reputation_quote.annual_premium_usd

    def test_volume_discount(self):
        """Test volume discount calculation"""
        base_quote = self.engine.generate_quote(
            device_id="device_001",
            risk_assessment=self.test_assessment,
        )

        discounted_quote = self.engine.apply_volume_discount(base_quote, device_count=100)

        assert discounted_quote.annual_premium_usd < base_quote.annual_premium_usd

    def test_volume_discount_rate_10_devices(self):
        """Test volume discount for 10 devices"""
        discounted, rate = self.engine.apply_volume_discount(
            premium=100.0, device_count=10
        )

        assert rate == 0.05
        assert discounted == 95.0

    def test_volume_discount_rate_500_devices(self):
        """Test volume discount for 500 devices"""
        discounted, rate = self.engine.apply_volume_discount(
            premium=100.0, device_count=500
        )

        assert rate == 0.20
        assert discounted == 80.0

    def test_estimate_annual_cost(self):
        """Test organizational annual cost estimation"""
        estimate = self.engine.estimate_annual_cost(
            total_devices=100,
            average_risk_score=0.50,
            average_reputation=0.70,
            coverage_distribution={"basic": 0.3, "standard": 0.5, "premium": 0.2},
        )

        assert "total_annual_cost" in estimate
        assert "subtotal" in estimate
        assert estimate["total_devices"] == 100
        assert estimate["total_annual_cost"] > 0
        assert estimate["cost_per_device_monthly"] > 0

    def test_quote_quote_expiration(self):
        """Test quote expiration date is set"""
        quote = self.engine.generate_quote(
            device_id="device_001",
            risk_assessment=self.test_assessment,
        )

        assert quote.quote_valid_until > quote.quote_timestamp

    def test_quote_invalid_coverage_level(self):
        """Test error handling for invalid coverage level"""
        with pytest.raises(ValueError):
            self.engine.generate_quote(
                device_id="device_001",
                risk_assessment=self.test_assessment,
                coverage_level="invalid_tier",
            )

    def test_quote_serialization(self):
        """Test quote can be serialized to dict"""
        quote = self.engine.generate_quote(
            device_id="device_001",
            risk_assessment=self.test_assessment,
            coverage_level="standard",
        )

        quote_dict = quote.to_dict()

        assert quote_dict["device_id"] == "device_001"
        assert quote_dict["coverage_level"] == "standard"
        assert "annual_premium_usd" in quote_dict
        assert "monthly_premium_usd" in quote_dict


class TestPremiumQuote:
    """Test suite for PremiumQuote data class"""

    def test_quote_creation(self):
        """Test creating premium quote"""
        now = datetime.utcnow()
        from datetime import timedelta

        quote = PremiumQuote(
            device_id="device_001",
            annual_premium_usd=150.0,
            monthly_premium_usd=12.50,
            base_premium=120.0,
            risk_adjustment=1.25,
            reputation_discount=0.0,
            coverage_level="standard",
            quote_timestamp=now,
            quote_valid_until=now + timedelta(days=30),
            terms={"policy_duration_months": 12},
        )

        assert quote.device_id == "device_001"
        assert quote.annual_premium_usd == 150.0

    def test_quote_serialization_roundtrip(self):
        """Test quote serialization and data integrity"""
        now = datetime.utcnow()
        from datetime import timedelta

        quote = PremiumQuote(
            device_id="device_002",
            annual_premium_usd=200.0,
            monthly_premium_usd=16.67,
            base_premium=120.0,
            risk_adjustment=1.67,
            reputation_discount=0.05,
            coverage_level="premium",
            quote_timestamp=now,
            quote_valid_until=now + timedelta(days=30),
            terms={"max_claim": 100000},
        )

        quote_dict = quote.to_dict()

        assert quote_dict["device_id"] == "device_002"
        assert quote_dict["annual_premium_usd"] == 200.0
        assert isinstance(quote_dict["quote_timestamp"], str)
