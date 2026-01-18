"""Risk calculation engine for device compromise assessment"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class RiskAssessment:
    """Container for device risk assessment results"""
    device_id: str
    timestamp: datetime
    overall_risk_score: float
    behavioral_risk: float
    hardware_risk: float
    network_risk: float
    anomaly_score: float
    threat_indicators: List[str]
    confidence_level: float
    assessment_version: str = "1.0"

    def to_dict(self) -> Dict:
        """Convert assessment to dictionary representation"""
        return {
            "device_id": self.device_id,
            "timestamp": self.timestamp.isoformat(),
            "overall_risk_score": round(self.overall_risk_score, 4),
            "behavioral_risk": round(self.behavioral_risk, 4),
            "hardware_risk": round(self.hardware_risk, 4),
            "network_risk": round(self.network_risk, 4),
            "anomaly_score": round(self.anomaly_score, 4),
            "threat_indicators": self.threat_indicators,
            "confidence_level": round(self.confidence_level, 4),
            "assessment_version": self.assessment_version,
        }


class RiskCalculator:
    """
    Comprehensive risk calculation engine that evaluates device compromise likelihood.
    
    Combines behavioral analysis, hardware integrity checks, network patterns,
    and historical threat data to produce a holistic risk assessment.
    """

    def __init__(self, fingerprinting_service=None, ml_detector=None):
        """
        Initialize the risk calculator with dependencies.

        Args:
            fingerprinting_service: Device fingerprinting service instance
            ml_detector: ML-based anomaly detection service
        """
        self.fingerprinting_service = fingerprinting_service
        self.ml_detector = ml_detector
        self.risk_thresholds = {
            "critical": 0.85,
            "high": 0.70,
            "medium": 0.50,
            "low": 0.30,
            "minimal": 0.0,
        }

    def calculate_risk(
        self,
        device_id: str,
        device_metrics: Dict,
        historical_data: Optional[Dict] = None,
        network_reputation: Optional[Dict] = None,
    ) -> RiskAssessment:
        """
        Calculate comprehensive risk score for a device.

        Args:
            device_id: Unique device identifier
            device_metrics: Current device metrics and telemetry
            historical_data: Historical behavior patterns for comparison
            network_reputation: Reputation data from network

        Returns:
            RiskAssessment object with detailed breakdown
        """
        timestamp = datetime.utcnow()

        # If available, enrich metrics with a fingerprint hash via adapter
        if self.fingerprinting_service and "fingerprint_hash" not in device_metrics:
            try:
                device_metrics["fingerprint_hash"] = self.fingerprinting_service.get_fingerprint_hash()
            except Exception as e:
                logger.warning("Fingerprinting service failed; proceeding without hash: %s", e)

        behavioral_risk = self._calculate_behavioral_risk(device_metrics, historical_data)
        hardware_risk = self._calculate_hardware_risk(device_metrics)
        network_risk = self._calculate_network_risk(device_metrics, network_reputation)
        anomaly_score = self._get_anomaly_score(device_metrics)

        threat_indicators = self._identify_threat_indicators(
            behavioral_risk, hardware_risk, network_risk, anomaly_score
        )

        overall_risk_score = self._aggregate_risk_scores(
            behavioral_risk, hardware_risk, network_risk, anomaly_score
        )

        confidence_level = self._calculate_confidence(device_metrics)

        assessment = RiskAssessment(
            device_id=device_id,
            timestamp=timestamp,
            overall_risk_score=overall_risk_score,
            behavioral_risk=behavioral_risk,
            hardware_risk=hardware_risk,
            network_risk=network_risk,
            anomaly_score=anomaly_score,
            threat_indicators=threat_indicators,
            confidence_level=confidence_level,
        )

        logger.info(
            f"Risk assessment completed for device {device_id}: score={overall_risk_score:.4f}"
        )
        return assessment

    def _calculate_behavioral_risk(
        self, device_metrics: Dict, historical_data: Optional[Dict] = None
    ) -> float:
        """
        Assess behavioral risk based on current device behavior patterns.

        Factors include:
        - Login pattern anomalies
        - Access time deviations
        - Resource usage patterns
        - Authentication failures
        """
        base_score = 0.0

        if "login_failures" in device_metrics:
            failure_rate = device_metrics["login_failures"] / max(
                device_metrics.get("total_login_attempts", 1), 1
            )
            base_score += min(failure_rate * 0.3, 0.3)

        if "resource_usage_spike" in device_metrics:
            if device_metrics["resource_usage_spike"]:
                base_score += 0.15

        if "unusual_access_time" in device_metrics:
            if device_metrics["unusual_access_time"]:
                base_score += 0.10

        if historical_data:
            deviation = self._calculate_statistical_deviation(
                device_metrics, historical_data
            )
            base_score += min(deviation * 0.45, 0.45)

        return min(base_score, 1.0)

    def _calculate_hardware_risk(self, device_metrics: Dict) -> float:
        """
        Assess hardware integrity risk.

        Factors include:
        - Unexpected component changes
        - Hardware serial mismatches
        - TPM integrity indicators
        - Firmware anomalies
        """
        base_score = 0.0

        if "component_mismatch" in device_metrics:
            if device_metrics["component_mismatch"]:
                base_score += 0.40

        if "tpm_status" in device_metrics:
            if device_metrics["tpm_status"] == "compromised":
                base_score += 0.35
            elif device_metrics["tpm_status"] == "unavailable":
                base_score += 0.15

        if "firmware_anomaly" in device_metrics:
            if device_metrics["firmware_anomaly"]:
                base_score += 0.25

        if "disk_encryption_disabled" in device_metrics:
            if device_metrics["disk_encryption_disabled"]:
                base_score += 0.20

        return min(base_score, 1.0)

    def _calculate_network_risk(
        self, device_metrics: Dict, network_reputation: Optional[Dict] = None
    ) -> float:
        """
        Assess network-based risk indicators.

        Factors include:
        - Connection from known malicious IP ranges
        - Network anomaly patterns
        - Peer reputation in network
        - Geographic impossibilities
        """
        base_score = 0.0

        if network_reputation:
            if network_reputation.get("is_blacklisted"):
                base_score += 0.40

            peer_risk = network_reputation.get("peer_average_risk", 0.0)
            base_score += peer_risk * 0.30

            if network_reputation.get("is_vpn_detected"):
                base_score += 0.10

        if "geographic_inconsistency" in device_metrics:
            if device_metrics["geographic_inconsistency"]:
                base_score += 0.20

        return min(base_score, 1.0)

    def _get_anomaly_score(self, device_metrics: Dict) -> float:
        """
        Retrieve ML-based anomaly detection score.

        Returns anomaly score from ML detector if available,
        otherwise calculates based on available metrics.
        """
        if self.ml_detector and "ml_anomaly_score" in device_metrics:
            return device_metrics["ml_anomaly_score"]

        if "anomaly_flags" in device_metrics:
            flag_count = len(device_metrics["anomaly_flags"])
            return min(flag_count * 0.15, 1.0)

        return 0.0

    def _calculate_statistical_deviation(
        self, current_metrics: Dict, historical_data: Dict
    ) -> float:
        """
        Calculate how much current metrics deviate from historical baseline.

        Returns normalized deviation score between 0 and 1.
        """
        deviation_total = 0.0
        compared_metrics = 0

        numeric_keys = ["cpu_usage", "memory_usage", "network_activity", "disk_activity"]

        for key in numeric_keys:
            if key in current_metrics and key in historical_data:
                current = current_metrics[key]
                historical_mean = historical_data.get(f"{key}_mean", 0)
                historical_stddev = historical_data.get(f"{key}_stddev", 1)

                if historical_stddev > 0:
                    z_score = abs((current - historical_mean) / historical_stddev)
                    deviation_total += min(z_score / 3.0, 1.0)
                    compared_metrics += 1

        if compared_metrics > 0:
            return deviation_total / compared_metrics

        return 0.0

    def _identify_threat_indicators(
        self, behavioral_risk: float, hardware_risk: float, network_risk: float, anomaly_score: float
    ) -> List[str]:
        """
        Identify specific threat indicators based on risk components.

        Returns list of threat indicator descriptions.
        """
        indicators = []

        if behavioral_risk > 0.5:
            indicators.append("Abnormal behavioral patterns detected")

        if hardware_risk > 0.5:
            indicators.append("Hardware integrity concerns")

        if network_risk > 0.5:
            indicators.append("Network-based threat indicators")

        if anomaly_score > 0.6:
            indicators.append("ML-detected system anomalies")

        if behavioral_risk > 0.7:
            indicators.append("Severe behavioral deviation from baseline")

        return indicators

    def _aggregate_risk_scores(
        self, behavioral_risk: float, hardware_risk: float, network_risk: float, anomaly_score: float
    ) -> float:
        """
        Aggregate individual risk components into overall risk score.

        Uses weighted average with emphasis on hardware integrity.
        """
        weights = {
            "behavioral": 0.25,
            "hardware": 0.35,
            "network": 0.20,
            "anomaly": 0.20,
        }

        weighted_score = (
            behavioral_risk * weights["behavioral"]
            + hardware_risk * weights["hardware"]
            + network_risk * weights["network"]
            + anomaly_score * weights["anomaly"]
        )

        return min(weighted_score, 1.0)

    def _calculate_confidence(self, device_metrics: Dict) -> float:
        """
        Calculate confidence level in risk assessment.

        Based on data completeness and recency.
        """
        completeness = 0.0
        expected_fields = [
            "cpu_usage",
            "memory_usage",
            "tpm_status",
            "login_failures",
            "timestamp",
        ]

        for field in expected_fields:
            if field in device_metrics:
                completeness += 1.0

        confidence = completeness / len(expected_fields)

        if "timestamp" in device_metrics:
            last_updated = device_metrics["timestamp"]
            if isinstance(last_updated, str):
                from datetime import datetime

                last_updated = datetime.fromisoformat(last_updated)

            time_diff = (datetime.utcnow() - last_updated).total_seconds()
            if time_diff < 3600:
                confidence *= 1.0
            elif time_diff < 86400:
                confidence *= 0.8
            else:
                confidence *= 0.5

        return min(confidence, 1.0)

    def get_risk_category(self, risk_score: float) -> str:
        """
        Categorize risk score into human-readable category.

        Returns one of: critical, high, medium, low, minimal
        """
        if risk_score >= self.risk_thresholds["critical"]:
            return "critical"
        elif risk_score >= self.risk_thresholds["high"]:
            return "high"
        elif risk_score >= self.risk_thresholds["medium"]:
            return "medium"
        elif risk_score >= self.risk_thresholds["low"]:
            return "low"
        else:
            return "minimal"
