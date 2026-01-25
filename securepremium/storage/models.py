"""SQLAlchemy ORM models for data persistence."""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class DeviceProfile(Base):
    """Device profile stored in database."""
    
    __tablename__ = "device_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255), unique=True, index=True, nullable=False)
    fingerprint_hash = Column(String(512), nullable=False)
    cpu = Column(String(255), default="Unknown")
    ram = Column(String(100), default="Unknown")
    os = Column(String(255), default="Unknown")
    os_version = Column(String(255), default="Unknown")
    hostname = Column(String(255), default="Unknown")
    
    # Device metadata
    registration_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_assessment_date = Column(DateTime)
    total_assessments = Column(Integer, default=0)
    
    # Current risk state
    current_risk_score = Column(Float, default=0.0)
    risk_level = Column(String(50), default="low")
    
    # Device activity
    is_active = Column(Boolean, default=True)
    activity_score = Column(Float, default=0.0)
    
    # Device health
    security_incidents = Column(Integer, default=0)
    last_incident_date = Column(DateTime)
    
    # Relationships
    assessments = relationship("RiskAssessment", back_populates="device")
    premiums = relationship("PremiumRecord", back_populates="device")
    
    __table_args__ = (
        Index("idx_device_id_active", "device_id", "is_active"),
        Index("idx_risk_level", "risk_level"),
    )


class RiskAssessment(Base):
    """Risk assessment records."""
    
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255), ForeignKey("device_profiles.device_id"), nullable=False)
    
    # Assessment details
    assessment_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(50), nullable=False)
    
    # Component scores
    behavioral_risk = Column(Float, default=0.0)
    hardware_risk = Column(Float, default=0.0)
    network_risk = Column(Float, default=0.0)
    anomaly_risk = Column(Float, default=0.0)
    
    # Assessment context
    assessment_reason = Column(String(255), default="scheduled")
    assessor_type = Column(String(50), default="automated")
    confidence_score = Column(Float, default=0.95)
    
    # Additional data
    assessment_data = Column(JSON)
    
    # Relationships
    device = relationship("DeviceProfile", back_populates="assessments")
    
    __table_args__ = (
        Index("idx_device_risk", "device_id", "assessment_date"),
        Index("idx_assessment_date", "assessment_date"),
    )


class PremiumRecord(Base):
    """Insurance premium records."""
    
    __tablename__ = "premium_records"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255), ForeignKey("device_profiles.device_id"), nullable=False)
    
    # Premium calculation
    base_premium = Column(Float, nullable=False)
    risk_multiplier = Column(Float, default=1.0)
    reputation_discount = Column(Float, default=0.0)
    volume_discount = Column(Float, default=0.0)
    final_premium = Column(Float, nullable=False)
    
    # Coverage details
    coverage_tier = Column(String(50), nullable=False)  # basic, standard, premium
    annual_deductible = Column(Float, nullable=False)
    coverage_limit = Column(Float, nullable=False)
    
    # Policy details
    policy_start_date = Column(DateTime, nullable=False)
    policy_end_date = Column(DateTime, nullable=False)
    policy_term_years = Column(Integer, default=1)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_renewal_date = Column(DateTime)
    
    # Relationships
    device = relationship("DeviceProfile", back_populates="premiums")
    
    __table_args__ = (
        Index("idx_device_premium", "device_id", "is_active"),
        Index("idx_policy_dates", "policy_start_date", "policy_end_date"),
    )


class ThreateReport(Base):
    """Threat intelligence reports in reputation network."""
    
    __tablename__ = "threat_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(255), unique=True, index=True, nullable=False)
    
    # Report source and target
    reporting_participant = Column(String(255), nullable=False)
    target_device_id = Column(String(255), ForeignKey("device_profiles.device_id"))
    
    # Threat details
    threat_type = Column(String(100), nullable=False)
    threat_level = Column(String(50), nullable=False)  # low, medium, high, critical
    threat_description = Column(String(1000))
    threat_indicators = Column(JSON)
    
    # Confidence and evidence
    confidence_score = Column(Float, default=0.5)
    evidence_data = Column(JSON)
    
    # Report lifecycle
    report_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    verification_status = Column(String(50), default="pending")  # pending, verified, disputed
    verification_count = Column(Integer, default=0)
    dispute_count = Column(Integer, default=0)
    
    # Relationships
    verifications = relationship("ReportVerification", back_populates="report")
    
    __table_args__ = (
        Index("idx_threat_date", "report_date"),
        Index("idx_threat_level", "threat_level"),
        Index("idx_target_device", "target_device_id"),
    )


class ReportVerification(Base):
    """Verification records for threat reports."""
    
    __tablename__ = "report_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(255), ForeignKey("threat_reports.report_id"), nullable=False)
    
    # Verification details
    verifier_participant = Column(String(255), nullable=False)
    verification_type = Column(String(50), nullable=False)  # verified, disputed, unrelated
    verification_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    verification_notes = Column(String(1000))
    
    # Relationships
    report = relationship("ThreateReport", back_populates="verifications")


class NetworkParticipant(Base):
    """Reputation network participants."""
    
    __tablename__ = "network_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(String(255), unique=True, index=True, nullable=False)
    participant_name = Column(String(255), nullable=False)
    
    # Network credentials
    api_key = Column(String(512), unique=True)
    is_active = Column(Boolean, default=True)
    
    # Participant statistics
    total_reports_submitted = Column(Integer, default=0)
    total_verifications = Column(Integer, default=0)
    reputation_score = Column(Float, default=0.5)
    
    # Metadata
    joined_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity_date = Column(DateTime)
    
    __table_args__ = (
        Index("idx_participant_active", "participant_id", "is_active"),
    )
