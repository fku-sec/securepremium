"""Repository pattern implementations for data access."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from .models import (
    DeviceProfile,
    RiskAssessment,
    PremiumRecord,
    ThreateReport,
    ReportVerification,
    NetworkParticipant,
)


class DeviceRepository:
    """Repository for device profile operations."""
    
    def __init__(self, session: Session):
        """Initialize with database session."""
        self.session = session
    
    def create(self, device_id: str, fingerprint_hash: str, **kwargs) -> DeviceProfile:
        """Create a new device profile."""
        device = DeviceProfile(
            device_id=device_id,
            fingerprint_hash=fingerprint_hash,
            **kwargs
        )
        self.session.add(device)
        self.session.commit()
        return device
    
    def get_by_id(self, device_id: str) -> Optional[DeviceProfile]:
        """Get device by ID."""
        return self.session.query(DeviceProfile).filter(
            DeviceProfile.device_id == device_id
        ).first()
    
    def get_all_active(self, limit: int = 100) -> List[DeviceProfile]:
        """Get all active devices."""
        return self.session.query(DeviceProfile).filter(
            DeviceProfile.is_active == True
        ).limit(limit).all()
    
    def get_by_risk_level(self, risk_level: str, limit: int = 100) -> List[DeviceProfile]:
        """Get devices by risk level."""
        return self.session.query(DeviceProfile).filter(
            DeviceProfile.risk_level == risk_level
        ).limit(limit).all()
    
    def update(self, device_id: str, **kwargs) -> Optional[DeviceProfile]:
        """Update device profile."""
        device = self.get_by_id(device_id)
        if device:
            for key, value in kwargs.items():
                if hasattr(device, key):
                    setattr(device, key, value)
            self.session.commit()
        return device
    
    def update_risk_score(
        self, 
        device_id: str, 
        risk_score: float, 
        risk_level: str
    ) -> Optional[DeviceProfile]:
        """Update device risk score and level."""
        return self.update(
            device_id,
            current_risk_score=risk_score,
            risk_level=risk_level,
            last_assessment_date=datetime.utcnow()
        )
    
    def delete(self, device_id: str) -> bool:
        """Delete device (soft delete by marking inactive)."""
        device = self.update(device_id, is_active=False)
        return device is not None


class RiskAssessmentRepository:
    """Repository for risk assessment operations."""
    
    def __init__(self, session: Session):
        """Initialize with database session."""
        self.session = session
    
    def create(self, device_id: str, risk_score: float, risk_level: str, **kwargs) -> RiskAssessment:
        """Create a new risk assessment."""
        assessment = RiskAssessment(
            device_id=device_id,
            risk_score=risk_score,
            risk_level=risk_level,
            **kwargs
        )
        self.session.add(assessment)
        self.session.commit()
        return assessment
    
    def get_latest_for_device(self, device_id: str) -> Optional[RiskAssessment]:
        """Get latest risk assessment for device."""
        return self.session.query(RiskAssessment).filter(
            RiskAssessment.device_id == device_id
        ).order_by(desc(RiskAssessment.assessment_date)).first()
    
    def get_history(self, device_id: str, limit: int = 30) -> List[RiskAssessment]:
        """Get risk assessment history for device."""
        return self.session.query(RiskAssessment).filter(
            RiskAssessment.device_id == device_id
        ).order_by(desc(RiskAssessment.assessment_date)).limit(limit).all()
    
    def get_by_risk_level(self, risk_level: str, limit: int = 100) -> List[RiskAssessment]:
        """Get assessments by risk level."""
        return self.session.query(RiskAssessment).filter(
            RiskAssessment.risk_level == risk_level
        ).order_by(desc(RiskAssessment.assessment_date)).limit(limit).all()
    
    def get_recent(self, days: int = 7, limit: int = 100) -> List[RiskAssessment]:
        """Get recent assessments from last N days."""
        from datetime import timedelta
        threshold_date = datetime.utcnow() - timedelta(days=days)
        return self.session.query(RiskAssessment).filter(
            RiskAssessment.assessment_date >= threshold_date
        ).order_by(desc(RiskAssessment.assessment_date)).limit(limit).all()


class PremiumRepository:
    """Repository for premium record operations."""
    
    def __init__(self, session: Session):
        """Initialize with database session."""
        self.session = session
    
    def create(
        self,
        device_id: str,
        base_premium: float,
        final_premium: float,
        coverage_tier: str,
        annual_deductible: float,
        coverage_limit: float,
        policy_start_date: datetime,
        policy_end_date: datetime,
        **kwargs
    ) -> PremiumRecord:
        """Create a new premium record."""
        premium = PremiumRecord(
            device_id=device_id,
            base_premium=base_premium,
            final_premium=final_premium,
            coverage_tier=coverage_tier,
            annual_deductible=annual_deductible,
            coverage_limit=coverage_limit,
            policy_start_date=policy_start_date,
            policy_end_date=policy_end_date,
            **kwargs
        )
        self.session.add(premium)
        self.session.commit()
        return premium
    
    def get_active_for_device(self, device_id: str) -> Optional[PremiumRecord]:
        """Get active premium for device."""
        return self.session.query(PremiumRecord).filter(
            and_(
                PremiumRecord.device_id == device_id,
                PremiumRecord.is_active == True
            )
        ).first()
    
    def get_history(self, device_id: str, limit: int = 20) -> List[PremiumRecord]:
        """Get premium history for device."""
        return self.session.query(PremiumRecord).filter(
            PremiumRecord.device_id == device_id
        ).order_by(desc(PremiumRecord.created_date)).limit(limit).all()
    
    def get_by_tier(self, coverage_tier: str, limit: int = 100) -> List[PremiumRecord]:
        """Get premiums by coverage tier."""
        return self.session.query(PremiumRecord).filter(
            and_(
                PremiumRecord.coverage_tier == coverage_tier,
                PremiumRecord.is_active == True
            )
        ).limit(limit).all()
    
    def renew_policy(self, premium_id: int, new_premium: float, new_end_date: datetime) -> Optional[PremiumRecord]:
        """Renew an existing policy."""
        premium = self.session.query(PremiumRecord).filter(PremiumRecord.id == premium_id).first()
        if premium:
            premium.final_premium = new_premium
            premium.policy_end_date = new_end_date
            premium.last_renewal_date = datetime.utcnow()
            self.session.commit()
        return premium


class ThreatReportRepository:
    """Repository for threat report operations."""
    
    def __init__(self, session: Session):
        """Initialize with database session."""
        self.session = session
    
    def create(
        self,
        report_id: str,
        reporting_participant: str,
        threat_type: str,
        threat_level: str,
        **kwargs
    ) -> ThreateReport:
        """Create a new threat report."""
        report = ThreateReport(
            report_id=report_id,
            reporting_participant=reporting_participant,
            threat_type=threat_type,
            threat_level=threat_level,
            **kwargs
        )
        self.session.add(report)
        self.session.commit()
        return report
    
    def get_by_id(self, report_id: str) -> Optional[ThreateReport]:
        """Get report by ID."""
        return self.session.query(ThreateReport).filter(
            ThreateReport.report_id == report_id
        ).first()
    
    def get_for_device(self, device_id: str, limit: int = 50) -> List[ThreateReport]:
        """Get all threat reports for a device."""
        return self.session.query(ThreateReport).filter(
            ThreateReport.target_device_id == device_id
        ).order_by(desc(ThreateReport.report_date)).limit(limit).all()
    
    def get_by_threat_level(self, threat_level: str, limit: int = 100) -> List[ThreateReport]:
        """Get reports by threat level."""
        return self.session.query(ThreateReport).filter(
            ThreateReport.threat_level == threat_level
        ).order_by(desc(ThreateReport.report_date)).limit(limit).all()
    
    def get_unverified(self, limit: int = 50) -> List[ThreateReport]:
        """Get unverified reports."""
        return self.session.query(ThreateReport).filter(
            ThreateReport.verification_status == "pending"
        ).order_by(desc(ThreateReport.report_date)).limit(limit).all()
    
    def update_verification_status(
        self,
        report_id: str,
        status: str,
        verification_count: int = None,
        dispute_count: int = None
    ) -> Optional[ThreateReport]:
        """Update threat report verification status."""
        report = self.get_by_id(report_id)
        if report:
            report.verification_status = status
            if verification_count is not None:
                report.verification_count = verification_count
            if dispute_count is not None:
                report.dispute_count = dispute_count
            self.session.commit()
        return report


class NetworkParticipantRepository:
    """Repository for network participant operations."""
    
    def __init__(self, session: Session):
        """Initialize with database session."""
        self.session = session
    
    def create(
        self,
        participant_id: str,
        participant_name: str,
        api_key: Optional[str] = None
    ) -> NetworkParticipant:
        """Create a new network participant."""
        participant = NetworkParticipant(
            participant_id=participant_id,
            participant_name=participant_name,
            api_key=api_key
        )
        self.session.add(participant)
        self.session.commit()
        return participant
    
    def get_by_id(self, participant_id: str) -> Optional[NetworkParticipant]:
        """Get participant by ID."""
        return self.session.query(NetworkParticipant).filter(
            NetworkParticipant.participant_id == participant_id
        ).first()
    
    def get_by_api_key(self, api_key: str) -> Optional[NetworkParticipant]:
        """Get participant by API key."""
        return self.session.query(NetworkParticipant).filter(
            NetworkParticipant.api_key == api_key
        ).first()
    
    def get_all_active(self, limit: int = 1000) -> List[NetworkParticipant]:
        """Get all active participants."""
        return self.session.query(NetworkParticipant).filter(
            NetworkParticipant.is_active == True
        ).limit(limit).all()
    
    def get_top_contributors(self, limit: int = 10) -> List[NetworkParticipant]:
        """Get top contributors by reports submitted."""
        return self.session.query(NetworkParticipant).order_by(
            desc(NetworkParticipant.total_reports_submitted)
        ).limit(limit).all()
    
    def update_stats(
        self,
        participant_id: str,
        reports_increment: int = 0,
        verifications_increment: int = 0,
        reputation_adjustment: float = 0
    ) -> Optional[NetworkParticipant]:
        """Update participant statistics."""
        participant = self.get_by_id(participant_id)
        if participant:
            participant.total_reports_submitted += reports_increment
            participant.total_verifications += verifications_increment
            participant.reputation_score = max(0, min(1.0, participant.reputation_score + reputation_adjustment))
            participant.last_activity_date = datetime.utcnow()
            self.session.commit()
        return participant
