"""Premium pricing model for insurance calculation"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


@dataclass
class PricingTierConfig:
    """Configuration for a pricing tier"""
    tier_name: str
    base_multiplier: float
    max_annual_claim: int
    deductible: int
    coverage_items: List[str]


class PremiumModel:
    """
    Sophisticated pricing model for device insurance premiums.

    Uses risk assessment, reputation data, and market factors to determine
    competitive yet profitable pricing.
    """

    def __init__(self):
        """Initialize premium model"""
        self.base_premium = 120.0
        self.min_premium = 30.0
        self.max_premium = 500.0

        self.tiers = {
            "basic": PricingTierConfig(
                tier_name="basic",
                base_multiplier=1.0,
                max_annual_claim=5000,
                deductible=500,
                coverage_items=[
                    "malware_removal",
                    "data_recovery",
                    "incident_support",
                ],
            ),
            "standard": PricingTierConfig(
                tier_name="standard",
                base_multiplier=1.5,
                max_annual_claim=25000,
                deductible=250,
                coverage_items=[
                    "malware_removal",
                    "data_recovery",
                    "incident_support",
                    "forensic_analysis",
                    "legal_consultation",
                ],
            ),
            "premium": PricingTierConfig(
                tier_name="premium",
                base_multiplier=2.5,
                max_annual_claim=100000,
                deductible=0,
                coverage_items=[
                    "malware_removal",
                    "data_recovery",
                    "incident_support",
                    "forensic_analysis",
                    "legal_consultation",
                    "24_7_response",
                    "credential_monitoring",
                ],
            ),
        }

        self.volume_discount_brackets = [
            (10, 0.05),
            (50, 0.10),
            (100, 0.15),
            (500, 0.20),
        ]

    def calculate_base_premium(
        self,
        risk_score: float,
        confidence: float,
        coverage_tier: str,
        reputation_score: Optional[float] = None,
    ) -> float:
        """
        Calculate base premium before any adjustments.

        Args:
            risk_score: Device risk score 0-1
            confidence: Confidence in risk assessment 0-1
            coverage_tier: Coverage tier (basic, standard, premium)
            reputation_score: Device reputation score 0-1

        Returns:
            Calculated base premium amount
        """
        if coverage_tier not in self.tiers:
            raise ValueError(f"Unknown coverage tier: {coverage_tier}")

        tier_config = self.tiers[coverage_tier]

        risk_multiplier = self._risk_to_multiplier(risk_score, confidence)
        tier_multiplier = tier_config.base_multiplier

        base_premium = self.base_premium * risk_multiplier * tier_multiplier

        if reputation_score is not None:
            reputation_adjustment = self._reputation_to_adjustment(reputation_score)
            base_premium *= reputation_adjustment

        base_premium = max(self.min_premium, min(base_premium, self.max_premium))

        return base_premium

    def apply_volume_discount(self, premium: float, device_count: int) -> Tuple[float, float]:
        """
        Apply volume discount based on device count.

        Args:
            premium: Original premium amount
            device_count: Total devices in organization

        Returns:
            Tuple of (discounted_premium, discount_rate)
        """
        discount_rate = 0.0

        for threshold, rate in sorted(self.volume_discount_brackets, reverse=True):
            if device_count >= threshold:
                discount_rate = rate
                break

        discounted_premium = premium * (1.0 - discount_rate)

        return discounted_premium, discount_rate

    def calculate_annual_policy_cost(
        self,
        monthly_premium: float,
        policy_months: int,
        includes_discount: bool = False,
        bulk_count: Optional[int] = None,
    ) -> Dict:
        """
        Calculate total annual policy cost with various options.

        Args:
            monthly_premium: Monthly premium amount
            policy_months: Number of months in policy (12, 24, 36)
            includes_discount: Whether bulk discount already applied
            bulk_count: Number of devices if calculating bulk discount

        Returns:
            Dictionary with cost breakdown
        """
        base_cost = monthly_premium * policy_months

        adjustments = {}

        if policy_months == 24:
            adjustments["term_discount"] = 0.05
        elif policy_months == 36:
            adjustments["term_discount"] = 0.10
        else:
            adjustments["term_discount"] = 0.0

        if bulk_count and not includes_discount:
            _, bulk_rate = self.apply_volume_discount(monthly_premium, bulk_count)
            adjustments["bulk_discount"] = bulk_rate

        total_adjustments = sum(adjustments.values())
        total_cost = base_cost * (1.0 - total_adjustments)

        return {
            "base_annual_cost": base_cost,
            "policy_months": policy_months,
            "adjustments": adjustments,
            "total_adjustments_rate": total_adjustments,
            "final_annual_cost": total_cost,
            "monthly_effective_rate": total_cost / policy_months,
        }

    def get_tier_details(self, tier_name: str) -> Dict:
        """
        Get detailed information about a coverage tier.

        Args:
            tier_name: Coverage tier name

        Returns:
            Dictionary with tier details
        """
        if tier_name not in self.tiers:
            raise ValueError(f"Unknown tier: {tier_name}")

        tier = self.tiers[tier_name]

        return {
            "tier_name": tier.tier_name,
            "base_multiplier": tier.base_multiplier,
            "max_annual_claim": tier.max_annual_claim,
            "deductible": tier.deductible,
            "coverage_items": tier.coverage_items,
            "item_count": len(tier.coverage_items),
        }

    def get_all_tiers(self) -> Dict:
        """
        Get information about all available tiers.

        Returns:
            Dictionary with all tier details
        """
        return {tier_name: self.get_tier_details(tier_name) for tier_name in self.tiers.keys()}

    def _risk_to_multiplier(self, risk_score: float, confidence: float) -> float:
        """
        Convert risk score to premium multiplier.

        Args:
            risk_score: Risk score 0-1
            confidence: Assessment confidence 0-1

        Returns:
            Premium multiplier
        """
        if risk_score < 0.2:
            base = 0.60
        elif risk_score < 0.4:
            base = 0.80
        elif risk_score < 0.6:
            base = 1.20
        elif risk_score < 0.8:
            base = 1.80
        else:
            base = 2.50

        confidence_factor = 0.7 + (confidence * 0.3)

        return base * confidence_factor

    def _reputation_to_adjustment(self, reputation_score: float) -> float:
        """
        Convert reputation score to premium adjustment factor.

        Args:
            reputation_score: Reputation score 0-1

        Returns:
            Adjustment multiplier (0.7 to 1.3)
        """
        if reputation_score < 0.3:
            return 1.25
        elif reputation_score < 0.5:
            return 1.10
        elif reputation_score < 0.7:
            return 1.0
        elif reputation_score < 0.85:
            return 0.90
        else:
            return 0.80
