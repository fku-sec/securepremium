"""High-level storage utilities and helpers."""

from typing import Optional
from datetime import datetime, timedelta

from securepremium.core.risk_calculator import RiskCalculator
from securepremium.core.premium_engine import PremiumEngine
from securepremium.models.device_scorer import DeviceScorer

from .database import get_db_config
from .repositories import (
    DeviceRepository,
    RiskAssessmentRepository,
    PremiumRepository,
    ThreatReportRepository,
    NetworkParticipantRepository,
)
from .schema import SchemaManager


class StorageManager:
    """High-level storage management interface."""
    
    def __init__(self):
        """Initialize storage manager."""
        self.db_config = get_db_config()
    
    def initialize(self) -> None:
        """Initialize database and create all tables."""
        SchemaManager.create_all_tables()
    
    def get_device_repo(self) -> DeviceRepository:
        """Get device repository."""
        return DeviceRepository(self.db_config.get_session())
    
    def get_assessment_repo(self) -> RiskAssessmentRepository:
        """Get risk assessment repository."""
        return RiskAssessmentRepository(self.db_config.get_session())
    
    def get_premium_repo(self) -> PremiumRepository:
        """Get premium repository."""
        return PremiumRepository(self.db_config.get_session())
    
    def get_threat_repo(self) -> ThreatReportRepository:
        """Get threat report repository."""
        return ThreatReportRepository(self.db_config.get_session())
    
    def get_participant_repo(self) -> NetworkParticipantRepository:
        """Get network participant repository."""
        return NetworkParticipantRepository(self.db_config.get_session())
    
    def store_device_assessment(self, device_id: str, **device_info) -> str:
        """
        Store a complete device assessment.
        
        Args:
            device_id: Unique device identifier
            **device_info: Device information (fingerprint, cpu, os, etc.)
            
        Returns:
            Device ID if successful
        """
        device_repo = self.get_device_repo()
        device = device_repo.create(device_id=device_id, **device_info)
        return device.device_id
    
    def store_risk_score(
        self,
        device_id: str,
        risk_score: float,
        risk_level: str,
        **assessment_details
    ) -> int:
        """
        Store a risk assessment result.
        
        Args:
            device_id: Device identifier
            risk_score: Risk score (0-1)
            risk_level: Risk level (low, medium, high, critical)
            **assessment_details: Additional assessment data
            
        Returns:
            Assessment ID
        """
        assessment_repo = self.get_assessment_repo()
        device_repo = self.get_device_repo()
        
        # Create assessment
        assessment = assessment_repo.create(
            device_id=device_id,
            risk_score=risk_score,
            risk_level=risk_level,
            **assessment_details
        )
        
        # Update device risk
        device_repo.update_risk_score(device_id, risk_score, risk_level)
        
        return assessment.id
    
    def store_premium_quote(
        self,
        device_id: str,
        base_premium: float,
        final_premium: float,
        coverage_tier: str,
        annual_deductible: float,
        coverage_limit: float,
        years: int = 1,
    ) -> int:
        """
        Store a premium quote/policy.
        
        Args:
            device_id: Device identifier
            base_premium: Base premium amount
            final_premium: Final premium after discounts
            coverage_tier: Coverage tier (basic, standard, premium)
            annual_deductible: Deductible amount
            coverage_limit: Maximum coverage
            years: Policy term in years
            
        Returns:
            Premium record ID
        """
        premium_repo = self.get_premium_repo()
        now = datetime.utcnow()
        
        premium = premium_repo.create(
            device_id=device_id,
            base_premium=base_premium,
            final_premium=final_premium,
            coverage_tier=coverage_tier,
            annual_deductible=annual_deductible,
            coverage_limit=coverage_limit,
            policy_start_date=now,
            policy_end_date=now + timedelta(days=365*years),
            policy_term_years=years
        )
        
        return premium.id
    
    def store_threat_report(
        self,
        report_id: str,
        reporting_participant: str,
        threat_type: str,
        threat_level: str,
        target_device_id: Optional[str] = None,
        **report_data
    ) -> str:
        """
        Store a threat report.
        
        Args:
            report_id: Unique report identifier
            reporting_participant: Reporting organization/participant
            threat_type: Type of threat
            threat_level: Threat severity level
            target_device_id: Device that was threatened
            **report_data: Additional report data
            
        Returns:
            Report ID
        """
        threat_repo = self.get_threat_repo()
        
        report = threat_repo.create(
            report_id=report_id,
            reporting_participant=reporting_participant,
            threat_type=threat_type,
            threat_level=threat_level,
            target_device_id=target_device_id,
            **report_data
        )
        
        return report.report_id
    
    def get_device_summary(self, device_id: str) -> dict:
        """
        Get complete device summary including all assessments and policies.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Dictionary with device data, assessments, and premiums
        """
        device_repo = self.get_device_repo()
        assessment_repo = self.get_assessment_repo()
        premium_repo = self.get_premium_repo()
        threat_repo = self.get_threat_repo()
        
        device = device_repo.get_by_id(device_id)
        if not device:
            return {}
        
        return {
            "device": {
                "id": device.device_id,
                "fingerprint": device.fingerprint_hash,
                "cpu": device.cpu,
                "ram": device.ram,
                "os": device.os,
                "os_version": device.os_version,
                "hostname": device.hostname,
                "registered": device.registration_date.isoformat(),
                "current_risk_score": device.current_risk_score,
                "risk_level": device.risk_level,
                "is_active": device.is_active,
                "security_incidents": device.security_incidents,
            },
            "recent_assessments": [
                {
                    "date": a.assessment_date.isoformat(),
                    "score": a.risk_score,
                    "level": a.risk_level,
                    "behavioral_risk": a.behavioral_risk,
                    "hardware_risk": a.hardware_risk,
                    "network_risk": a.network_risk,
                }
                for a in assessment_repo.get_history(device_id, limit=5)
            ],
            "active_premium": {
                "tier": premium_repo.get_active_for_device(device_id).coverage_tier
                if premium_repo.get_active_for_device(device_id) else None,
                "premium": premium_repo.get_active_for_device(device_id).final_premium
                if premium_repo.get_active_for_device(device_id) else None,
            },
            "threats": [
                {
                    "id": t.report_id,
                    "type": t.threat_type,
                    "level": t.threat_level,
                    "date": t.report_date.isoformat(),
                    "status": t.verification_status,
                }
                for t in threat_repo.get_for_device(device_id, limit=10)
            ],
        }
    
    def get_database_stats(self) -> dict:
        """Get database statistics."""
        return SchemaManager.get_database_stats()
