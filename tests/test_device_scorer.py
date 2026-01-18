"""Tests for device scorer module"""

import pytest
from datetime import datetime
from securepremium.models.device_scorer import DeviceScorer, DeviceProfile


class TestDeviceScorer:
    """Test suite for DeviceScorer"""

    def setup_method(self):
        """Setup test fixtures"""
        self.scorer = DeviceScorer()

    def test_scorer_initialization(self):
        """Test device scorer initializes correctly"""
        assert self.scorer is not None
        assert len(self.scorer.device_profiles) == 0
        assert "fingerprint_stability" in self.scorer.scoring_weights

    def test_register_device(self):
        """Test device registration"""
        profile = self.scorer.register_device(
            device_id="device_001",
            fingerprint_hash="hash_001",
            hardware_info={"cpu": "Intel Core i7", "ram": "16GB"},
            system_info={"os": "Windows 11"},
        )

        assert isinstance(profile, DeviceProfile)
        assert profile.device_id == "device_001"
        assert profile.interaction_count == 1
        assert "device_001" in self.scorer.device_profiles

    def test_register_device_update(self):
        """Test device re-registration updates profile"""
        profile1 = self.scorer.register_device(
            device_id="device_001",
            fingerprint_hash="hash_001",
            hardware_info={"cpu": "Intel"},
            system_info={"os": "Windows"},
        )

        profile2 = self.scorer.register_device(
            device_id="device_001",
            fingerprint_hash="hash_001",
            hardware_info={"cpu": "Intel"},
            system_info={"os": "Windows"},
        )

        assert profile2.interaction_count == 2

    def test_calculate_device_score(self):
        """Test device score calculation"""
        self.scorer.register_device(
            device_id="device_001",
            fingerprint_hash="hash_001",
            hardware_info={"cpu": "Intel"},
            system_info={"os": "Windows"},
        )

        score, components = self.scorer.calculate_device_score("device_001")

        assert 0.0 <= score <= 1.0
        assert "fingerprint_stability" in components
        assert "behavioral_consistency" in components
        assert "security_incidents" in components

    def test_device_not_found_error(self):
        """Test error when calculating score for unknown device"""
        with pytest.raises(ValueError):
            self.scorer.calculate_device_score("unknown_device")

    def test_add_security_event(self):
        """Test adding security event to device"""
        self.scorer.register_device(
            device_id="device_001",
            fingerprint_hash="hash_001",
            hardware_info={"cpu": "Intel"},
            system_info={"os": "Windows"},
        )

        self.scorer.add_security_event(
            device_id="device_001",
            event_type="malware_detected",
            severity="high",
            description="Trojan detected in system",
        )

        profile = self.scorer.device_profiles["device_001"]
        assert len(profile.security_events) == 1

    def test_security_event_affects_score(self):
        """Test that security events lower device score"""
        self.scorer.register_device(
            device_id="device_001",
            fingerprint_hash="hash_001",
            hardware_info={"cpu": "Intel"},
            system_info={"os": "Windows"},
        )

        score_before = self.scorer.calculate_device_score("device_001")[0]

        self.scorer.add_security_event(
            device_id="device_001",
            event_type="intrusion_attempt",
            severity="critical",
            description="Unauthorized access detected",
        )

        score_after = self.scorer.calculate_device_score("device_001")[0]

        assert score_after < score_before

    def test_score_category_classification(self):
        """Test score to category mapping"""
        assert self.scorer.get_device_score_category(0.90) == "trusted"
        assert self.scorer.get_device_score_category(0.70) == "normal"
        assert self.scorer.get_device_score_category(0.50) == "suspect"
        assert self.scorer.get_device_score_category(0.20) == "untrusted"

    def test_device_age_calculation(self):
        """Test device age calculation"""
        now = datetime.utcnow()
        from datetime import timedelta

        profile = DeviceProfile(
            device_id="device_001",
            fingerprint_hash="hash_001",
            hardware_info={},
            system_info={},
            first_seen=now - timedelta(days=30),
            last_seen=now,
        )

        age = profile.get_age_days()

        assert age == 30

    def test_last_activity_hours_calculation(self):
        """Test last activity hours calculation"""
        now = datetime.utcnow()
        from datetime import timedelta

        profile = DeviceProfile(
            device_id="device_001",
            fingerprint_hash="hash_001",
            hardware_info={},
            system_info={},
            first_seen=now,
            last_seen=now - timedelta(hours=24),
        )

        hours = profile.get_last_activity_hours()

        assert hours == 24

    def test_multiple_devices_independent_scores(self):
        """Test that multiple devices have independent scores"""
        self.scorer.register_device(
            device_id="device_001",
            fingerprint_hash="hash_001",
            hardware_info={"cpu": "Intel"},
            system_info={"os": "Windows"},
        )

        self.scorer.register_device(
            device_id="device_002",
            fingerprint_hash="hash_002",
            hardware_info={"cpu": "AMD"},
            system_info={"os": "Linux"},
        )

        self.scorer.add_security_event(
            device_id="device_001",
            event_type="malware",
            severity="high",
            description="Test",
        )

        score_device1 = self.scorer.calculate_device_score("device_001")[0]
        score_device2 = self.scorer.calculate_device_score("device_002")[0]

        assert score_device1 < score_device2


class TestDeviceProfile:
    """Test suite for DeviceProfile data class"""

    def test_profile_creation(self):
        """Test creating device profile"""
        now = datetime.utcnow()
        profile = DeviceProfile(
            device_id="device_001",
            fingerprint_hash="hash_001",
            hardware_info={"cpu": "Intel Core i7"},
            system_info={"os": "Windows 11"},
            first_seen=now,
            last_seen=now,
        )

        assert profile.device_id == "device_001"
        assert profile.fingerprint_hash == "hash_001"
        assert profile.interaction_count == 0
        assert len(profile.security_events) == 0
