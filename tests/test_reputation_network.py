"""Tests for reputation network module"""

import pytest
from datetime import datetime
from securepremium.network.reputation_network import (
    ReputationNetwork,
    ReputationRecord,
    ThreatIntelligenceReport,
)


class TestReputationNetwork:
    """Test suite for ReputationNetwork"""

    def setup_method(self):
        """Setup test fixtures"""
        self.network = ReputationNetwork(network_id="test_network")

    def test_network_initialization(self):
        """Test reputation network initializes correctly"""
        assert self.network is not None
        assert self.network.network_id == "test_network"
        assert len(self.network.participants) == 0
        assert len(self.network.reputation_db) == 0

    def test_register_participant(self):
        """Test participant registration"""
        result = self.network.register_participant("org_001")

        assert result is True
        assert "org_001" in self.network.participants

    def test_register_duplicate_participant(self):
        """Test duplicate participant registration fails"""
        self.network.register_participant("org_001")
        result = self.network.register_participant("org_001")

        assert result is False

    def test_submit_threat_report(self):
        """Test submitting threat report"""
        self.network.register_participant("org_001")

        report = self.network.submit_threat_report(
            reporter_id="org_001",
            device_id="suspicious_device",
            threat_type="malware_detected",
            severity="high",
            description="Trojan detected",
            evidence_hash="hash_of_evidence",
        )

        assert isinstance(report, ThreatIntelligenceReport)
        assert report.device_id == "suspicious_device"
        assert report.threat_type == "malware_detected"

    def test_submit_report_unregistered_reporter(self):
        """Test error when unregistered organization submits report"""
        with pytest.raises(ValueError):
            self.network.submit_threat_report(
                reporter_id="unknown_org",
                device_id="device",
                threat_type="threat",
                severity="high",
                description="desc",
                evidence_hash="hash",
            )

    def test_query_device_reputation(self):
        """Test querying device reputation"""
        self.network.register_participant("org_001")

        self.network.submit_threat_report(
            reporter_id="org_001",
            device_id="suspicious_device",
            threat_type="malware",
            severity="critical",
            description="Malware detected",
            evidence_hash="hash",
        )

        reputation = self.network.query_device_reputation("suspicious_device")

        assert reputation is not None
        assert reputation.device_id == "suspicious_device"
        assert reputation.reputation_score < 0.5

    def test_query_unknown_device_reputation(self):
        """Test querying reputation of unknown device"""
        reputation = self.network.query_device_reputation("unknown_device")

        assert reputation is None

    def test_device_risk_level_classification(self):
        """Test risk level classification"""
        self.network.register_participant("org_001")

        self.network.submit_threat_report(
            reporter_id="org_001",
            device_id="dangerous_device",
            threat_type="malware",
            severity="critical",
            description="Severe malware",
            evidence_hash="hash",
        )

        risk_level = self.network.get_device_risk_level("dangerous_device")

        assert risk_level == "dangerous"

    def test_risk_level_trustworthy(self):
        """Test trustworthy risk level"""
        risk_level = self.network.get_device_risk_level("unknown_device")

        assert risk_level == "unrated"

    def test_verify_report(self):
        """Test report verification"""
        self.network.register_participant("org_001")

        report = self.network.submit_threat_report(
            reporter_id="org_001",
            device_id="device",
            threat_type="threat",
            severity="high",
            description="desc",
            evidence_hash="hash",
        )

        result = self.network.verify_report(report.report_id)

        assert result is True

    def test_network_statistics(self):
        """Test network statistics generation"""
        self.network.register_participant("org_001")
        self.network.register_participant("org_002")

        self.network.submit_threat_report(
            reporter_id="org_001",
            device_id="device_001",
            threat_type="malware",
            severity="high",
            description="desc",
            evidence_hash="hash",
        )

        stats = self.network.get_network_statistics()

        assert "total_participants" in stats
        assert stats["total_participants"] == 2
        assert "tracked_devices" in stats
        assert stats["tracked_devices"] >= 1

    def test_threat_intelligence_summary(self):
        """Test threat intelligence summary"""
        self.network.register_participant("org_001")

        self.network.submit_threat_report(
            reporter_id="org_001",
            device_id="device_001",
            threat_type="malware",
            severity="high",
            description="desc1",
            evidence_hash="hash1",
        )

        self.network.submit_threat_report(
            reporter_id="org_001",
            device_id="device_001",
            threat_type="ransomware",
            severity="critical",
            description="desc2",
            evidence_hash="hash2",
        )

        summary = self.network.get_threat_intelligence_summary("device_001")

        assert summary is not None
        assert summary["total_reports"] >= 2
        assert "malware" in summary["threat_types"]

    def test_reputation_decay_over_time(self):
        """Test reputation decay increases score over time"""
        self.network.register_participant("org_001")

        self.network.submit_threat_report(
            reporter_id="org_001",
            device_id="device",
            threat_type="threat",
            severity="high",
            description="desc",
            evidence_hash="hash",
        )

        record1 = self.network.query_device_reputation("device")
        score1 = record1.reputation_score

        record2 = self.network.query_device_reputation("device")
        score2 = record2.reputation_score

        assert score2 >= score1


class TestReputationRecord:
    """Test suite for ReputationRecord data class"""

    def test_record_creation(self):
        """Test creating reputation record"""
        now = datetime.utcnow()
        record = ReputationRecord(
            device_id="device_001",
            reputation_score=0.45,
            reports_count=3,
            last_updated=now,
            verification_level="verified",
        )

        assert record.device_id == "device_001"
        assert record.reputation_score == 0.45
        assert record.reports_count == 3

    def test_record_serialization(self):
        """Test record serialization to dictionary"""
        now = datetime.utcnow()
        record = ReputationRecord(
            device_id="device_001",
            reputation_score=0.60,
            reports_count=5,
            last_updated=now,
            verification_level="verified",
        )

        record_dict = record.to_dict()

        assert record_dict["device_id"] == "device_001"
        assert record_dict["reputation_score"] == 0.6
        assert isinstance(record_dict["last_updated"], str)


class TestThreatIntelligenceReport:
    """Test suite for ThreatIntelligenceReport data class"""

    def test_report_creation(self):
        """Test creating threat report"""
        now = datetime.utcnow()
        report = ThreatIntelligenceReport(
            report_id="report_001",
            reporter_id="org_001",
            device_id="device_001",
            threat_type="malware",
            severity="high",
            description="Malware detected",
            evidence_hash="hash",
            timestamp=now,
        )

        assert report.report_id == "report_001"
        assert report.threat_type == "malware"
        assert report.verified is False

    def test_report_serialization(self):
        """Test report serialization"""
        now = datetime.utcnow()
        report = ThreatIntelligenceReport(
            report_id="report_001",
            reporter_id="org_001",
            device_id="device_001",
            threat_type="ransomware",
            severity="critical",
            description="Ransomware attack",
            evidence_hash="hash",
            timestamp=now,
            verified=True,
        )

        report_dict = report.to_dict()

        assert report_dict["report_id"] == "report_001"
        assert report_dict["severity"] == "critical"
        assert report_dict["verified"] is True
