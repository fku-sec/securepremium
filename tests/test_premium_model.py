"""Tests for premium model module"""

import pytest
from securepremium.pricing.premium_model import PremiumModel, PricingTierConfig


class TestPremiumModel:
    """Test suite for PremiumModel"""

    def setup_method(self):
        """Setup test fixtures"""
        self.model = PremiumModel()

    def test_model_initialization(self):
        """Test premium model initializes correctly"""
        assert self.model is not None
        assert self.model.base_premium == 120.0
        assert "basic" in self.model.tiers
        assert "standard" in self.model.tiers
        assert "premium" in self.model.tiers

    def test_calculate_base_premium_low_risk(self):
        """Test base premium for low risk device"""
        premium = self.model.calculate_base_premium(
            risk_score=0.2,
            confidence=0.9,
            coverage_tier="standard",
        )

        assert premium > self.model.min_premium
        assert premium < self.model.base_premium

    def test_calculate_base_premium_high_risk(self):
        """Test base premium for high risk device"""
        premium = self.model.calculate_base_premium(
            risk_score=0.8,
            confidence=0.9,
            coverage_tier="standard",
        )

        assert premium > self.model.base_premium

    def test_coverage_tier_multipliers(self):
        """Test coverage tier affects premium"""
        basic = self.model.calculate_base_premium(
            risk_score=0.5,
            confidence=0.9,
            coverage_tier="basic",
        )

        standard = self.model.calculate_base_premium(
            risk_score=0.5,
            confidence=0.9,
            coverage_tier="standard",
        )

        premium = self.model.calculate_base_premium(
            risk_score=0.5,
            confidence=0.9,
            coverage_tier="premium",
        )

        assert basic < standard < premium

    def test_reputation_score_affects_premium(self):
        """Test reputation score adjustment"""
        good_rep = self.model.calculate_base_premium(
            risk_score=0.5,
            confidence=0.9,
            coverage_tier="standard",
            reputation_score=0.9,
        )

        poor_rep = self.model.calculate_base_premium(
            risk_score=0.5,
            confidence=0.9,
            coverage_tier="standard",
            reputation_score=0.1,
        )

        assert good_rep < poor_rep

    def test_volume_discount_10_devices(self):
        """Test volume discount for 10 devices"""
        premium, discount = self.model.apply_volume_discount(100.0, 10)

        assert discount == 0.05
        assert premium == 95.0

    def test_volume_discount_50_devices(self):
        """Test volume discount for 50 devices"""
        premium, discount = self.model.apply_volume_discount(100.0, 50)

        assert discount == 0.10
        assert premium == 90.0

    def test_volume_discount_500_devices(self):
        """Test volume discount for 500 devices"""
        premium, discount = self.model.apply_volume_discount(100.0, 500)

        assert discount == 0.20
        assert premium == 80.0

    def test_calculate_annual_policy_cost_12_months(self):
        """Test annual policy cost calculation"""
        cost = self.model.calculate_annual_policy_cost(
            monthly_premium=10.0,
            policy_months=12,
        )

        assert cost["base_annual_cost"] == 120.0
        assert cost["final_annual_cost"] == 120.0

    def test_calculate_annual_policy_cost_24_months_discount(self):
        """Test 2-year policy gets term discount"""
        cost = self.model.calculate_annual_policy_cost(
            monthly_premium=10.0,
            policy_months=24,
        )

        assert "term_discount" in cost["adjustments"]
        assert cost["adjustments"]["term_discount"] == 0.05

    def test_get_tier_details(self):
        """Test getting tier details"""
        details = self.model.get_tier_details("standard")

        assert details["tier_name"] == "standard"
        assert "max_annual_claim" in details
        assert "coverage_items" in details

    def test_get_all_tiers(self):
        """Test getting all tier details"""
        all_tiers = self.model.get_all_tiers()

        assert "basic" in all_tiers
        assert "standard" in all_tiers
        assert "premium" in all_tiers

    def test_invalid_coverage_tier_error(self):
        """Test error for invalid coverage tier"""
        with pytest.raises(ValueError):
            self.model.calculate_base_premium(
                risk_score=0.5,
                confidence=0.9,
                coverage_tier="invalid_tier",
            )


class TestPricingTierConfig:
    """Test suite for PricingTierConfig"""

    def test_tier_config_creation(self):
        """Test creating pricing tier configuration"""
        config = PricingTierConfig(
            tier_name="test_tier",
            base_multiplier=1.5,
            max_annual_claim=50000,
            deductible=250,
            coverage_items=["item1", "item2"],
        )

        assert config.tier_name == "test_tier"
        assert config.base_multiplier == 1.5
        assert len(config.coverage_items) == 2
