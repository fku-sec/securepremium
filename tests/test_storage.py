"""Tests for storage module (database, repositories, and schema management)."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from securepremium.storage import (
    DatabaseConfig,
    init_db,
    Base,
    DeviceProfile,
    RiskAssessment,
    PremiumRecord,
    ThreateReport,
    NetworkParticipant,
    DeviceRepository,
    RiskAssessmentRepository,
    PremiumRepository,
    ThreatReportRepository,
    NetworkParticipantRepository,
    SchemaManager,
)


@pytest.fixture
def test_db():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    engine.dispose()


class TestDatabaseConfig:
    """Test database configuration."""
    
    def test_sqlite_config(self):
        """Test SQLite database configuration."""
        config = DatabaseConfig("sqlite:///test.db")
        assert config.db_url == "sqlite:///test.db"
        config.initialize()
        assert config.engine is not None
        assert config.SessionLocal is not None
        config.close()
    
    def test_get_session(self):
        """Test getting a database session."""
        config = DatabaseConfig("sqlite:///:memory:")
        config.initialize()
        session = config.get_session()
        assert session is not None
        session.close()
        config.close()
    
    def test_uninitialized_session_raises_error(self):
        """Test that getting session before initialization raises error."""
        config = DatabaseConfig()
        with pytest.raises(RuntimeError):
            config.get_session()


class TestDeviceRepository:
    """Test device repository operations."""
    
    def test_create_device(self, test_db):
        """Test creating a device profile."""
        repo = DeviceRepository(test_db)
        device = repo.create(
            device_id="TEST-001",
            fingerprint_hash="abc123",
            cpu="Intel i7",
            os="Windows 11"
        )
        assert device.device_id == "TEST-001"
        assert device.is_active is True
        assert device.current_risk_score == 0.0
    
    def test_get_device_by_id(self, test_db):
        """Test retrieving device by ID."""
        repo = DeviceRepository(test_db)
        repo.create("TEST-001", "abc123")
        device = repo.get_by_id("TEST-001")
        assert device is not None
        assert device.device_id == "TEST-001"
    
    def test_get_nonexistent_device(self, test_db):
        """Test getting nonexistent device returns None."""
        repo = DeviceRepository(test_db)
        device = repo.get_by_id("NONEXISTENT")
        assert device is None
    
    def test_get_all_active_devices(self, test_db):
        """Test retrieving all active devices."""
        repo = DeviceRepository(test_db)
        repo.create("TEST-001", "abc123")
        repo.create("TEST-002", "def456")
        repo.create("TEST-003", "ghi789", is_active=False)
        
        active = repo.get_all_active()
        assert len(active) == 2
    
    def test_update_device(self, test_db):
        """Test updating device profile."""
        repo = DeviceRepository(test_db)
        repo.create("TEST-001", "abc123")
        updated = repo.update("TEST-001", cpu="Intel i9", ram="32GB")
        assert updated.cpu == "Intel i9"
        assert updated.ram == "32GB"
    
    def test_update_risk_score(self, test_db):
        """Test updating device risk score."""
        repo = DeviceRepository(test_db)
        repo.create("TEST-001", "abc123")
        updated = repo.update_risk_score("TEST-001", 0.75, "high")
        assert updated.current_risk_score == 0.75
        assert updated.risk_level == "high"
    
    def test_get_by_risk_level(self, test_db):
        """Test getting devices by risk level."""
        repo = DeviceRepository(test_db)
        repo.create("TEST-001", "abc123")
        repo.update_risk_score("TEST-001", 0.2, "low")
        repo.create("TEST-002", "def456")
        repo.update_risk_score("TEST-002", 0.8, "high")
        
        high_risk = repo.get_by_risk_level("high")
        assert len(high_risk) == 1
        assert high_risk[0].device_id == "TEST-002"
    
    def test_soft_delete_device(self, test_db):
        """Test soft delete device."""
        repo = DeviceRepository(test_db)
        repo.create("TEST-001", "abc123")
        deleted = repo.delete("TEST-001")
        assert deleted is True
        
        device = repo.get_by_id("TEST-001")
        assert device.is_active is False


class TestRiskAssessmentRepository:
    """Test risk assessment repository operations."""
    
    def test_create_assessment(self, test_db):
        """Test creating risk assessment."""
        repo = RiskAssessmentRepository(test_db)
        assessment = repo.create(
            device_id="TEST-001",
            risk_score=0.65,
            risk_level="medium",
            behavioral_risk=0.3,
            hardware_risk=0.2
        )
        assert assessment.risk_score == 0.65
        assert assessment.risk_level == "medium"
    
    def test_get_latest_assessment(self, test_db):
        """Test getting latest assessment for device."""
        repo = RiskAssessmentRepository(test_db)
        repo.create("TEST-001", 0.5, "low")
        repo.create("TEST-001", 0.75, "high")
        
        latest = repo.get_latest_for_device("TEST-001")
        assert latest.risk_score == 0.75
    
    def test_get_assessment_history(self, test_db):
        """Test getting assessment history."""
        repo = RiskAssessmentRepository(test_db)
        repo.create("TEST-001", 0.5, "low")
        repo.create("TEST-001", 0.65, "medium")
        repo.create("TEST-001", 0.75, "high")
        
        history = repo.get_history("TEST-001")
        assert len(history) == 3
        assert history[0].risk_score == 0.75  # Most recent first
    
    def test_get_by_risk_level(self, test_db):
        """Test getting assessments by risk level."""
        repo = RiskAssessmentRepository(test_db)
        repo.create("TEST-001", 0.2, "low")
        repo.create("TEST-002", 0.8, "high")
        repo.create("TEST-003", 0.85, "high")
        
        high_risk = repo.get_by_risk_level("high")
        assert len(high_risk) == 2


class TestPremiumRepository:
    """Test premium repository operations."""
    
    def test_create_premium(self, test_db):
        """Test creating premium record."""
        now = datetime.utcnow()
        repo = PremiumRepository(test_db)
        premium = repo.create(
            device_id="TEST-001",
            base_premium=100.0,
            final_premium=90.0,
            coverage_tier="standard",
            annual_deductible=500.0,
            coverage_limit=50000.0,
            policy_start_date=now,
            policy_end_date=now + timedelta(days=365)
        )
        assert premium.base_premium == 100.0
        assert premium.final_premium == 90.0
        assert premium.coverage_tier == "standard"
    
    def test_get_active_premium(self, test_db):
        """Test getting active premium for device."""
        now = datetime.utcnow()
        repo = PremiumRepository(test_db)
        repo.create(
            "TEST-001", 100.0, 90.0, "standard", 500.0, 50000.0,
            now, now + timedelta(days=365)
        )
        
        active = repo.get_active_for_device("TEST-001")
        assert active is not None
        assert active.is_active is True
    
    def test_get_premium_history(self, test_db):
        """Test getting premium history."""
        now = datetime.utcnow()
        repo = PremiumRepository(test_db)
        repo.create("TEST-001", 100.0, 90.0, "standard", 500.0, 50000.0,
                   now, now + timedelta(days=365))
        repo.create("TEST-001", 120.0, 100.0, "premium", 1000.0, 100000.0,
                   now, now + timedelta(days=365), is_active=False)
        
        history = repo.get_history("TEST-001")
        assert len(history) == 2
    
    def test_renew_policy(self, test_db):
        """Test renewing a policy."""
        now = datetime.utcnow()
        repo = PremiumRepository(test_db)
        premium = repo.create(
            "TEST-001", 100.0, 90.0, "standard", 500.0, 50000.0,
            now, now + timedelta(days=365)
        )
        
        new_end_date = now + timedelta(days=730)
        renewed = repo.renew_policy(premium.id, 95.0, new_end_date)
        assert renewed.final_premium == 95.0
        assert renewed.policy_end_date == new_end_date


class TestThreatReportRepository:
    """Test threat report repository operations."""
    
    def test_create_threat_report(self, test_db):
        """Test creating threat report."""
        repo = ThreatReportRepository(test_db)
        report = repo.create(
            report_id="THREAT-001",
            reporting_participant="participant-1",
            threat_type="malware",
            threat_level="high",
            target_device_id="TEST-001"
        )
        assert report.report_id == "THREAT-001"
        assert report.threat_level == "high"
    
    def test_get_threats_for_device(self, test_db):
        """Test getting threats for device."""
        repo = ThreatReportRepository(test_db)
        repo.create("THREAT-001", "participant-1", "malware", "high", target_device_id="TEST-001")
        repo.create("THREAT-002", "participant-2", "phishing", "medium", target_device_id="TEST-001")
        repo.create("THREAT-003", "participant-1", "ransomware", "critical", target_device_id="TEST-002")
        
        threats = repo.get_for_device("TEST-001")
        assert len(threats) == 2
    
    def test_get_unverified_reports(self, test_db):
        """Test getting unverified reports."""
        repo = ThreatReportRepository(test_db)
        repo.create("THREAT-001", "participant-1", "malware", "high",
                   verification_status="pending")
        repo.create("THREAT-002", "participant-2", "phishing", "medium",
                   verification_status="verified")
        
        unverified = repo.get_unverified()
        assert len(unverified) == 1
        assert unverified[0].report_id == "THREAT-001"
    
    def test_update_verification_status(self, test_db):
        """Test updating verification status."""
        repo = ThreatReportRepository(test_db)
        repo.create("THREAT-001", "participant-1", "malware", "high")
        updated = repo.update_verification_status("THREAT-001", "verified", 5, 0)
        assert updated.verification_status == "verified"
        assert updated.verification_count == 5


class TestNetworkParticipantRepository:
    """Test network participant repository operations."""
    
    def test_create_participant(self, test_db):
        """Test creating network participant."""
        repo = NetworkParticipantRepository(test_db)
        participant = repo.create(
            participant_id="org-001",
            participant_name="Security Corp",
            api_key="secret-key-123"
        )
        assert participant.participant_id == "org-001"
        assert participant.is_active is True
    
    def test_get_participant_by_id(self, test_db):
        """Test getting participant by ID."""
        repo = NetworkParticipantRepository(test_db)
        repo.create("org-001", "Security Corp")
        participant = repo.get_by_id("org-001")
        assert participant is not None
        assert participant.participant_name == "Security Corp"
    
    def test_get_participant_by_api_key(self, test_db):
        """Test getting participant by API key."""
        repo = NetworkParticipantRepository(test_db)
        repo.create("org-001", "Security Corp", api_key="secret-123")
        participant = repo.get_by_api_key("secret-123")
        assert participant is not None
        assert participant.participant_id == "org-001"
    
    def test_get_top_contributors(self, test_db):
        """Test getting top contributors."""
        repo = NetworkParticipantRepository(test_db)
        p1 = repo.create("org-001", "Security Corp")
        p2 = repo.create("org-002", "Threat Intel")
        
        test_db.query(NetworkParticipant).filter_by(participant_id="org-001").first().total_reports_submitted = 50
        test_db.query(NetworkParticipant).filter_by(participant_id="org-002").first().total_reports_submitted = 100
        test_db.commit()
        
        top = repo.get_top_contributors(10)
        assert len(top) == 2
        assert top[0].participant_id == "org-002"  # Most reports first
    
    def test_update_participant_stats(self, test_db):
        """Test updating participant statistics."""
        repo = NetworkParticipantRepository(test_db)
        repo.create("org-001", "Security Corp")
        updated = repo.update_stats("org-001", reports_increment=5, reputation_adjustment=0.1)
        assert updated.total_reports_submitted == 5
        assert updated.reputation_score == 0.6  # 0.5 + 0.1


class TestSchemaManager:
    """Test schema management operations."""
    
    def test_create_all_tables(self):
        """Test creating all tables."""
        db = init_db("sqlite:///:memory:")
        SchemaManager.create_all_tables()
        tables = SchemaManager.get_all_tables()
        assert "device_profiles" in tables
        assert "risk_assessments" in tables
        assert "premium_records" in tables
        assert "threat_reports" in tables
        db.close()
    
    def test_table_exists(self):
        """Test checking if table exists."""
        db = init_db("sqlite:///:memory:")
        SchemaManager.create_all_tables()
        assert SchemaManager.table_exists("device_profiles") is True
        assert SchemaManager.table_exists("nonexistent_table") is False
        db.close()
    
    def test_get_database_stats(self):
        """Test getting database statistics."""
        db = init_db("sqlite:///:memory:")
        SchemaManager.create_all_tables()
        stats = SchemaManager.get_database_stats()
        assert stats["total_tables"] > 0
        assert "device_profiles" in stats["tables"]
        db.close()
