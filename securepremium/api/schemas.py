"""Pydantic models for API requests and responses."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ========================
# Device Models
# ========================

class DeviceRegisterRequest(BaseModel):
    """Request model for device registration."""
    device_id: str = Field(..., description="Unique device identifier")
    fingerprint_hash: str = Field(..., description="Device hardware fingerprint")
    cpu: Optional[str] = Field(default="Unknown", description="CPU information")
    ram: Optional[str] = Field(default="Unknown", description="RAM amount")
    os: Optional[str] = Field(default="Unknown", description="Operating system")
    os_version: Optional[str] = Field(default="Unknown", description="OS version")
    hostname: Optional[str] = Field(default="Unknown", description="Device hostname")


class DeviceResponse(BaseModel):
    """Response model for device data."""
    device_id: str
    fingerprint_hash: str
    cpu: str
    ram: str
    os: str
    os_version: str
    hostname: str
    registration_date: datetime
    current_risk_score: float
    risk_level: str
    is_active: bool
    security_incidents: int

    model_config = ConfigDict(from_attributes=True)


class DeviceListResponse(BaseModel):
    """Response model for device list."""
    total: int
    devices: List[DeviceResponse]


# ========================
# Risk Assessment Models
# ========================

class RiskAssessmentRequest(BaseModel):
    """Request model for risk assessment."""
    device_id: str
    behavioral_risk: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)
    hardware_risk: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)
    network_risk: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)
    anomaly_risk: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)
    assessment_reason: Optional[str] = Field(default="manual")
    confidence_score: Optional[float] = Field(default=0.95, ge=0.0, le=1.0)


class RiskAssessmentResponse(BaseModel):
    """Response model for risk assessment."""
    id: int
    device_id: str
    risk_score: float
    risk_level: str
    behavioral_risk: float
    hardware_risk: float
    network_risk: float
    anomaly_risk: float
    confidence_score: float
    assessment_date: datetime
    assessment_reason: str

    model_config = ConfigDict(from_attributes=True)


class RiskHistoryResponse(BaseModel):
    """Response model for risk assessment history."""
    device_id: str
    total_assessments: int
    latest_risk_score: float
    latest_risk_level: str
    assessments: List[RiskAssessmentResponse]


# ========================
# Premium Models
# ========================

class PremiumQuoteRequest(BaseModel):
    """Request model for premium quote."""
    device_id: str
    risk_score: Optional[float] = Field(default=0.5, ge=0.0, le=1.0)
    coverage_tier: str = Field(..., description="basic, standard, or premium")
    years: Optional[int] = Field(default=1, ge=1, le=5)


class PremiumResponse(BaseModel):
    """Response model for premium data."""
    id: int
    device_id: str
    base_premium: float
    final_premium: float
    coverage_tier: str
    annual_deductible: float
    coverage_limit: float
    policy_start_date: datetime
    policy_end_date: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class PremiumHistoryResponse(BaseModel):
    """Response model for premium history."""
    device_id: str
    total_policies: int
    active_premium: Optional[PremiumResponse]
    history: List[PremiumResponse]


class PremiumRenewalRequest(BaseModel):
    """Request model for policy renewal."""
    premium_id: int
    new_premium: float
    years: Optional[int] = Field(default=1, ge=1, le=5)


# ========================
# Threat Intelligence Models
# ========================

class ThreatReportRequest(BaseModel):
    """Request model for threat report."""
    report_id: str
    reporting_participant: str
    threat_type: str
    threat_level: str = Field(..., description="low, medium, high, or critical")
    target_device_id: Optional[str] = None
    threat_description: Optional[str] = None
    confidence_score: Optional[float] = Field(default=0.5, ge=0.0, le=1.0)


class ThreatReportResponse(BaseModel):
    """Response model for threat report."""
    id: int
    report_id: str
    reporting_participant: str
    threat_type: str
    threat_level: str
    target_device_id: Optional[str]
    threat_description: Optional[str]
    confidence_score: float
    report_date: datetime
    verification_status: str
    verification_count: int

    model_config = ConfigDict(from_attributes=True)


class ThreatListResponse(BaseModel):
    """Response model for threat list."""
    total: int
    threat_level: Optional[str]
    threats: List[ThreatReportResponse]


class ThreatVerificationRequest(BaseModel):
    """Request model for threat verification."""
    report_id: str
    status: str = Field(..., description="verified, disputed, or unrelated")
    verification_notes: Optional[str]


# ========================
# Network Participant Models
# ========================

class ParticipantRegisterRequest(BaseModel):
    """Request model for participant registration."""
    participant_id: str
    participant_name: str
    api_key: Optional[str]


class ParticipantResponse(BaseModel):
    """Response model for participant data."""
    participant_id: str
    participant_name: str
    is_active: bool
    total_reports_submitted: int
    total_verifications: int
    reputation_score: float
    joined_date: datetime

    model_config = ConfigDict(from_attributes=True)


class ParticipantListResponse(BaseModel):
    """Response model for participant list."""
    total: int
    participants: List[ParticipantResponse]


class ParticipantStatsRequest(BaseModel):
    """Request model for participant statistics update."""
    participant_id: str
    reports_increment: Optional[int] = Field(default=0)
    verifications_increment: Optional[int] = Field(default=0)
    reputation_adjustment: Optional[float] = Field(default=0, ge=-1.0, le=1.0)


# ========================
# Health & Status Models
# ========================

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    timestamp: datetime
    version: str
    database: str


class ErrorResponse(BaseModel):
    """Response model for errors."""
    error: str
    detail: str
    timestamp: datetime
    request_id: Optional[str] = None


class StatsResponse(BaseModel):
    """Response model for system statistics."""
    total_devices: int
    total_assessments: int
    total_threats: int
    total_participants: int
    timestamp: datetime
