"""Device Behavior Insurance Protocol

A comprehensive system for quantifying device compromise risk as insurance premiums,
integrating ML-based device scoring with decentralized threat intelligence networks.
"""

__version__ = "0.1.0"
__author__ = "Security Team"
__license__ = "MIT"

from securepremium.core.risk_calculator import RiskCalculator
from securepremium.core.premium_engine import PremiumEngine
from securepremium.models.device_scorer import DeviceScorer
from securepremium.network.reputation_network import ReputationNetwork
from securepremium.pricing.premium_model import PremiumModel
from securepremium.integration.fingerprinting import DeviceFingerprintingService

__all__ = [
    "RiskCalculator",
    "PremiumEngine",
    "DeviceScorer",
    "ReputationNetwork",
    "PremiumModel",
    "DeviceFingerprintingService",
]
