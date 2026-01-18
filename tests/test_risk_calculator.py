"""Tests for risk calculator module"""

import pytest
from datetime import datetime
from securepremium.core.risk_calculator import RiskCalculator, RiskAssessment


class TestRiskCalculator:
    """Test suite for RiskCalculator"""

    def setup_method(self):
        """Setup test fixtures"""
        self.calculator = RiskCalculator()

    def test_risk_calculator_initialization(self):
        """Test risk calculator initializes correctly"""
        assert self.calculator is not None
        assert self.calculator.risk_thresholds["critical"] == 0.85
        assert self.calculator.risk_thresholds["minimal"] == 0.0

    def test_calculate_risk_minimal(self):
        """Test calculation of minimal risk device"""
        device_metrics = {
            "login_failures": 0,
            "total_login_attempts": 100,
            "tpm_status": "healthy",
            "component_mismatch": False,
            "firmware_anomaly": False,
            "disk_encryption_disabled": False,
        }

        assessment = self.calculator.calculate_risk(
            device_id="device_001",
            device_metrics=device_metrics,
        )

        assert isinstance(assessment, RiskAssessment)
        assert assessment.device_id == "device_001"
        assert 0.0 <= assessment.overall_risk_score <= 1.0
        assert assessment.overall_risk_score < 0.3

    def test_calculate_risk_critical(self):
        """Test calculation of critical risk device"""
        device_metrics = {
            "login_failures": 50,
            "total_login_attempts": 100,
            "tpm_status": "compromised",
            "component_mismatch": True,
            "firmware_anomaly": True,
            "disk_encryption_disabled": True,
            "resource_usage_spike": True,
            "unusual_access_time": True,
        }

        assessment = self.calculator.calculate_risk(
            device_id="device_critical",
            device_metrics=device_metrics,
        )

        assert assessment.overall_risk_score > 0.7

    def test_calculate_behavioral_risk(self):
        """Test behavioral risk component calculation"""
        device_metrics = {
            "login_failures": 10,
            "total_login_attempts": 50,
            "resource_usage_spike": True,
            "unusual_access_time": True,
        }

        risk = self.calculator._calculate_behavioral_risk(device_metrics)

        assert 0.0 <= risk <= 1.0

    def test_calculate_hardware_risk(self):
        """Test hardware risk component calculation"""
        device_metrics = {
            "component_mismatch": True,
            "tpm_status": "compromised",
            "firmware_anomaly": True,
            "disk_encryption_disabled": True,
        }

        risk = self.calculator._calculate_hardware_risk(device_metrics)

        assert risk > 0.7

    def test_calculate_network_risk(self):
        """Test network risk component calculation"""
        network_reputation = {
            "is_blacklisted": True,
            "peer_average_risk": 0.6,
            "is_vpn_detected": True,
        }

        risk = self.calculator._calculate_network_risk(
            {}, network_reputation=network_reputation
        )

        assert risk > 0.5

    def test_risk_category_classification(self):
        """Test risk score to category mapping"""
        assert self.calculator.get_risk_category(0.9) == "critical"
        assert self.calculator.get_risk_category(0.75) == "high"
        assert self.calculator.get_risk_category(0.55) == "medium"
        assert self.calculator.get_risk_category(0.35) == "low"
        assert self.calculator.get_risk_category(0.15) == "minimal"

    def test_assessment_to_dict(self):
        """Test RiskAssessment serialization"""
        assessment = RiskAssessment(
            device_id="test_device",
            timestamp=datetime.utcnow(),
            overall_risk_score=0.65,
            behavioral_risk=0.5,
            hardware_risk=0.7,
            network_risk=0.6,
            anomaly_score=0.4,
            threat_indicators=["Unusual behavior detected"],
            confidence_level=0.85,
        )

        result_dict = assessment.to_dict()

        assert result_dict["device_id"] == "test_device"
        assert result_dict["overall_risk_score"] == 0.65
        assert isinstance(result_dict["timestamp"], str)

    def test_confidence_calculation(self):
        """Test assessment confidence calculation"""
        device_metrics_complete = {
            "cpu_usage": 30.0,
            "memory_usage": 50.0,
            "tpm_status": "healthy",
            "login_failures": 2,
            "timestamp": datetime.utcnow(),
        }

        confidence = self.calculator._calculate_confidence(device_metrics_complete)

        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.5

    def test_confidence_low_with_incomplete_data(self):
        """Test confidence is low with incomplete metrics"""
        device_metrics_incomplete = {"cpu_usage": 30.0}

        confidence = self.calculator._calculate_confidence(device_metrics_incomplete)

        assert confidence < 0.5


class TestRiskAssessment:
    """Test suite for RiskAssessment data class"""

    def test_assessment_creation(self):
        """Test creating risk assessment"""
        now = datetime.utcnow()
        assessment = RiskAssessment(
            device_id="device_001",
            timestamp=now,
            overall_risk_score=0.45,
            behavioral_risk=0.40,
            hardware_risk=0.50,
            network_risk=0.35,
            anomaly_score=0.30,
            threat_indicators=["Pattern detected"],
            confidence_level=0.80,
        )

        assert assessment.device_id == "device_001"
        assert assessment.overall_risk_score == 0.45
        assert len(assessment.threat_indicators) == 1

    def test_assessment_serialization_roundtrip(self):
        """Test assessment can be serialized and restored"""
        now = datetime.utcnow()
        assessment = RiskAssessment(
            device_id="device_002",
            timestamp=now,
            overall_risk_score=0.60,
            behavioral_risk=0.55,
            hardware_risk=0.65,
            network_risk=0.58,
            anomaly_score=0.50,
            threat_indicators=["High CPU usage", "Unusual login pattern"],
            confidence_level=0.92,
        )

        serialized = assessment.to_dict()

        assert serialized["device_id"] == "device_002"
        assert serialized["overall_risk_score"] == 0.60
        assert len(serialized["threat_indicators"]) == 2
