"""Premium engine for calculating device insurance costs"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class PremiumQuote:
    """Container for insurance premium quote"""
    device_id: str
    annual_premium_usd: float
    monthly_premium_usd: float
    base_premium: float
    risk_adjustment: float
    reputation_discount: float
    coverage_level: str
    quote_timestamp: datetime
    quote_valid_until: datetime
    terms: Dict

    def to_dict(self) -> Dict:
        """Convert quote to dictionary representation"""
        return {
            "device_id": self.device_id,
            "annual_premium_usd": round(self.annual_premium_usd, 2),
            "monthly_premium_usd": round(self.monthly_premium_usd, 2),
            "base_premium": round(self.base_premium, 2),
            "risk_adjustment": round(self.risk_adjustment, 4),
            "reputation_discount": round(self.reputation_discount, 4),
            "coverage_level": self.coverage_level,
            "quote_timestamp": self.quote_timestamp.isoformat(),
            "quote_valid_until": self.quote_valid_until.isoformat(),
            "terms": self.terms,
        }


class PremiumEngine:
    """
    Calculates insurance premiums based on device risk profile,
    reputation data, and coverage requirements.
    """

    def __init__(self, reputation_network=None, premium_model=None):
        """
        Initialize premium engine with required services.

        Args:
            reputation_network: Reputation network service
            premium_model: Premium pricing model
        """
        self.reputation_network = reputation_network
        self.premium_model = premium_model

        self.base_annual_premium = 120.0
        self.coverage_tiers = {
            "basic": {"multiplier": 1.0, "max_claim": 5000},
            "standard": {"multiplier": 1.5, "max_claim": 25000},
            "premium": {"multiplier": 2.5, "max_claim": 100000},
        }

    def generate_quote(
        self,
        device_id: str,
        risk_assessment,
        reputation_score: Optional[float] = None,
        coverage_level: str = "standard",
        policy_duration_months: int = 12,
    ) -> PremiumQuote:
        """
        Generate insurance premium quote for device.

        Args:
            device_id: Unique device identifier
            risk_assessment: RiskAssessment object from risk calculator
            reputation_score: Device reputation score (0-1)
            coverage_level: Coverage tier (basic, standard, premium)
            policy_duration_months: Policy duration in months

        Returns:
            PremiumQuote object with pricing details
        """
        if coverage_level not in self.coverage_tiers:
            raise ValueError(f"Invalid coverage level: {coverage_level}")

        timestamp = datetime.utcnow()
        quote_valid_until = timestamp + timedelta(days=30)

        risk_score = risk_assessment.overall_risk_score
        confidence = risk_assessment.confidence_level

        risk_multiplier = self._calculate_risk_multiplier(risk_score, confidence)

        if reputation_score is None:
            reputation_score = 0.5

        reputation_discount = self._calculate_reputation_discount(reputation_score)

        coverage_multiplier = self.coverage_tiers[coverage_level]["multiplier"]

        annual_premium = (
            self.base_annual_premium
            * risk_multiplier
            * coverage_multiplier
            * (1.0 - reputation_discount)
        )

        monthly_premium = annual_premium / 12.0

        if policy_duration_months != 12:
            annual_premium = (annual_premium / 12.0) * policy_duration_months

        quote = PremiumQuote(
            device_id=device_id,
            annual_premium_usd=annual_premium,
            monthly_premium_usd=monthly_premium,
            base_premium=self.base_annual_premium,
            risk_adjustment=risk_multiplier,
            reputation_discount=reputation_discount,
            coverage_level=coverage_level,
            quote_timestamp=timestamp,
            quote_valid_until=quote_valid_until,
            terms={
                "policy_duration_months": policy_duration_months,
                "max_annual_claim": self.coverage_tiers[coverage_level]["max_claim"],
                "risk_score": round(risk_score, 4),
                "confidence_level": round(confidence, 4),
                "reputation_score": round(reputation_score, 4),
                "threat_indicators": risk_assessment.threat_indicators,
            },
        )

        logger.info(
            f"Premium quote generated for device {device_id}: ${annual_premium:.2f}/year"
        )
        return quote

    def _calculate_risk_multiplier(self, risk_score: float, confidence: float) -> float:
        """
        Calculate premium multiplier based on risk score and assessment confidence.

        Risk scoring:
        - 0.0 - 0.3: Low risk (0.5x - 0.8x)
        - 0.3 - 0.5: Medium risk (0.8x - 1.2x)
        - 0.5 - 0.7: High risk (1.2x - 2.0x)
        - 0.7 - 1.0: Critical risk (2.0x - 4.0x)
        """
        if risk_score < 0.3:
            base_multiplier = 0.5 + (risk_score / 0.3) * 0.3
        elif risk_score < 0.5:
            base_multiplier = 0.8 + ((risk_score - 0.3) / 0.2) * 0.4
        elif risk_score < 0.7:
            base_multiplier = 1.2 + ((risk_score - 0.5) / 0.2) * 0.8
        else:
            base_multiplier = 2.0 + ((risk_score - 0.7) / 0.3) * 2.0

        confidence_factor = 0.5 + (confidence * 0.5)
        adjusted_multiplier = base_multiplier * confidence_factor

        return min(adjusted_multiplier, 4.0)

    def _calculate_reputation_discount(self, reputation_score: float) -> float:
        """
        Calculate premium discount based on device reputation.

        High reputation devices receive discounts up to 30%.
        Low reputation devices receive penalty (negative discount).

        Args:
            reputation_score: Reputation score 0-1

        Returns:
            Discount factor 0-0.3 (positive discount) or negative (premium increase)
        """
        if reputation_score < 0.3:
            return -0.15

        elif reputation_score < 0.5:
            return (reputation_score - 0.3) / 0.2 * -0.10

        elif reputation_score < 0.7:
            return ((reputation_score - 0.5) / 0.2) * 0.05

        else:
            return 0.10 + ((reputation_score - 0.7) / 0.3) * 0.20

    def apply_volume_discount(
        self, base_quote: PremiumQuote, device_count: int
    ) -> PremiumQuote:
        """
        Apply volume discount for organizations with multiple devices.

        Args:
            base_quote: Original premium quote
            device_count: Total number of devices in organization

        Returns:
            Updated PremiumQuote with volume discount applied
        """
        if device_count < 10:
            discount_rate = 0.0
        elif device_count < 50:
            discount_rate = 0.05
        elif device_count < 100:
            discount_rate = 0.10
        elif device_count < 500:
            discount_rate = 0.15
        else:
            discount_rate = 0.20

        adjusted_annual = base_quote.annual_premium_usd * (1.0 - discount_rate)
        adjusted_monthly = adjusted_annual / 12.0

        updated_quote = PremiumQuote(
            device_id=base_quote.device_id,
            annual_premium_usd=adjusted_annual,
            monthly_premium_usd=adjusted_monthly,
            base_premium=base_quote.base_premium,
            risk_adjustment=base_quote.risk_adjustment,
            reputation_discount=base_quote.reputation_discount + discount_rate,
            coverage_level=base_quote.coverage_level,
            quote_timestamp=base_quote.quote_timestamp,
            quote_valid_until=base_quote.quote_valid_until,
            terms={**base_quote.terms, "volume_discount": discount_rate},
        )

        return updated_quote

    def estimate_annual_cost(
        self,
        total_devices: int,
        average_risk_score: float,
        average_reputation: float,
        coverage_distribution: Dict[str, float],
    ) -> Dict:
        """
        Estimate total annual insurance cost for organization.

        Args:
            total_devices: Total number of devices
            average_risk_score: Average risk score across fleet
            average_reputation: Average reputation score
            coverage_distribution: Dict with keys basic, standard, premium

        Returns:
            Cost breakdown and projections
        """
        if not sum(coverage_distribution.values()) == 1.0:
            raise ValueError("Coverage distribution must sum to 1.0")

        device_quotes = []

        for coverage_tier, percentage in coverage_distribution.items():
            device_count = int(total_devices * percentage)

            risk_multiplier = self._calculate_risk_multiplier(average_risk_score, 0.8)
            reputation_discount = self._calculate_reputation_discount(average_reputation)
            coverage_multiplier = self.coverage_tiers[coverage_tier]["multiplier"]

            annual_premium = (
                self.base_annual_premium
                * risk_multiplier
                * coverage_multiplier
                * (1.0 - reputation_discount)
            )

            device_quotes.append(
                {
                    "coverage_tier": coverage_tier,
                    "device_count": device_count,
                    "premium_per_device": annual_premium,
                    "total_premium": annual_premium * device_count,
                }
            )

        total_cost = sum(q["total_premium"] for q in device_quotes)
        volume_discount = self._calculate_volume_discount_rate(total_devices)
        discounted_total = total_cost * (1.0 - volume_discount)

        return {
            "total_devices": total_devices,
            "breakdown_by_coverage": device_quotes,
            "subtotal": total_cost,
            "volume_discount_rate": volume_discount,
            "volume_discount_amount": total_cost - discounted_total,
            "total_annual_cost": discounted_total,
            "cost_per_device_monthly": discounted_total / 12.0 / total_devices,
        }

    def _calculate_volume_discount_rate(self, device_count: int) -> float:
        """Calculate volume discount rate based on device count"""
        if device_count < 10:
            return 0.0
        elif device_count < 50:
            return 0.05
        elif device_count < 100:
            return 0.10
        elif device_count < 500:
            return 0.15
        else:
            return 0.20
