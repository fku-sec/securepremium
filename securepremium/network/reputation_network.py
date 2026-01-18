"""Decentralized reputation network for threat intelligence sharing"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
import logging
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class ReputationRecord:
    """Individual reputation record for a device"""
    device_id: str
    reputation_score: float
    reports_count: int
    last_updated: datetime
    contributors: Set[str] = field(default_factory=set)
    threat_history: List[str] = field(default_factory=list)
    verification_level: str = "unverified"

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "device_id": self.device_id,
            "reputation_score": round(self.reputation_score, 4),
            "reports_count": self.reports_count,
            "last_updated": self.last_updated.isoformat(),
            "contributor_count": len(self.contributors),
            "threat_history": self.threat_history[-10:],
            "verification_level": self.verification_level,
        }


@dataclass
class ThreatIntelligenceReport:
    """Threat intelligence report from network participant"""
    report_id: str
    reporter_id: str
    device_id: str
    threat_type: str
    severity: str
    description: str
    evidence_hash: str
    timestamp: datetime
    verified: bool = False

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "report_id": self.report_id,
            "reporter_id": self.reporter_id,
            "device_id": self.device_id,
            "threat_type": self.threat_type,
            "severity": self.severity,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "verified": self.verified,
        }


class ReputationNetwork:
    """
    Decentralized reputation network for sharing device threat intelligence.

    Enables organizations to:
    - Report suspicious device activity
    - Query device reputation
    - Contribute to collective threat intelligence
    - Build collaborative trust scores
    """

    def __init__(self, network_id: str = "default"):
        """
        Initialize reputation network.

        Args:
            network_id: Identifier for this network instance
        """
        self.network_id = network_id
        self.reputation_db: Dict[str, ReputationRecord] = {}
        self.threat_reports: Dict[str, List[ThreatIntelligenceReport]] = {}
        self.participants: Set[str] = set()
        self.report_history: List[ThreatIntelligenceReport] = []
        self.decay_rate = 0.95

    def register_participant(self, participant_id: str) -> bool:
        """
        Register organization as network participant.

        Args:
            participant_id: Unique participant identifier

        Returns:
            True if registration successful
        """
        if participant_id in self.participants:
            logger.warning(f"Participant {participant_id} already registered")
            return False

        self.participants.add(participant_id)
        logger.info(f"Participant {participant_id} registered to network {self.network_id}")
        return True

    def submit_threat_report(
        self,
        reporter_id: str,
        device_id: str,
        threat_type: str,
        severity: str,
        description: str,
        evidence_hash: str,
    ) -> ThreatIntelligenceReport:
        """
        Submit threat intelligence report about device.

        Args:
            reporter_id: Organization reporting the threat
            device_id: Device being reported
            threat_type: Type of threat
            severity: Threat severity (critical, high, medium, low)
            description: Detailed description
            evidence_hash: Cryptographic hash of evidence

        Returns:
            ThreatIntelligenceReport object
        """
        if reporter_id not in self.participants:
            raise ValueError(f"Reporter {reporter_id} not registered as participant")

        report_id = self._generate_report_id(device_id, reporter_id)

        report = ThreatIntelligenceReport(
            report_id=report_id,
            reporter_id=reporter_id,
            device_id=device_id,
            threat_type=threat_type,
            severity=severity,
            description=description,
            evidence_hash=evidence_hash,
            timestamp=datetime.utcnow(),
        )

        if device_id not in self.threat_reports:
            self.threat_reports[device_id] = []

        self.threat_reports[device_id].append(report)
        self.report_history.append(report)

        self._update_reputation_from_report(device_id, report)

        logger.info(
            f"Threat report submitted for device {device_id} by {reporter_id}: {threat_type}"
        )
        return report

    def query_device_reputation(self, device_id: str) -> Optional[ReputationRecord]:
        """
        Query reputation data for device.

        Args:
            device_id: Device identifier

        Returns:
            ReputationRecord if device has reports, None otherwise
        """
        if device_id not in self.reputation_db:
            return None

        record = self.reputation_db[device_id]

        record = self._apply_reputation_decay(record)

        return record

    def get_device_risk_level(self, device_id: str) -> str:
        """
        Get human-readable risk level based on reputation.

        Args:
            device_id: Device identifier

        Returns:
            Risk level: trustworthy, neutral, suspicious, dangerous
        """
        record = self.query_device_reputation(device_id)

        if record is None:
            return "unrated"

        score = record.reputation_score

        if score >= 0.85:
            return "trustworthy"
        elif score >= 0.60:
            return "neutral"
        elif score >= 0.35:
            return "suspicious"
        else:
            return "dangerous"

    def verify_report(self, report_id: str, verification_count: int = 2) -> bool:
        """
        Mark report as verified if threshold met.

        Args:
            report_id: Report identifier
            verification_count: Number of verifications required

        Returns:
            True if report became verified
        """
        for reports in self.threat_reports.values():
            for report in reports:
                if report.report_id == report_id:
                    report.verified = True
                    logger.info(f"Report {report_id} marked as verified")
                    return True

        return False

    def get_network_statistics(self) -> Dict:
        """
        Get network statistics and metrics.

        Returns:
            Dictionary with network statistics
        """
        total_devices = len(self.reputation_db)
        total_reports = len(self.report_history)
        total_participants = len(self.participants)

        severity_breakdown = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }

        for report in self.report_history:
            if report.severity in severity_breakdown:
                severity_breakdown[report.severity] += 1

        average_reputation = 0.0
        if total_devices > 0:
            average_reputation = sum(
                record.reputation_score for record in self.reputation_db.values()
            ) / total_devices

        threat_types = {}
        for report in self.report_history:
            threat_types[report.threat_type] = threat_types.get(report.threat_type, 0) + 1

        return {
            "network_id": self.network_id,
            "total_participants": total_participants,
            "tracked_devices": total_devices,
            "total_reports": total_reports,
            "average_reputation_score": round(average_reputation, 4),
            "severity_breakdown": severity_breakdown,
            "top_threat_types": sorted(threat_types.items(), key=lambda x: x[1], reverse=True)[
                :5
            ],
        }

    def get_threat_intelligence_summary(self, device_id: str) -> Optional[Dict]:
        """
        Get comprehensive threat intelligence summary for device.

        Args:
            device_id: Device identifier

        Returns:
            Summary dictionary or None if no data
        """
        if device_id not in self.threat_reports:
            return None

        reports = self.threat_reports[device_id]
        reputation = self.query_device_reputation(device_id)

        if not reports:
            return None

        recent_reports = [r for r in reports if (datetime.utcnow() - r.timestamp).days < 90]

        threat_types = {}
        for report in reports:
            threat_types[report.threat_type] = threat_types.get(report.threat_type, 0) + 1

        return {
            "device_id": device_id,
            "total_reports": len(reports),
            "recent_reports_90_days": len(recent_reports),
            "reputation": reputation.to_dict() if reputation else None,
            "threat_types": threat_types,
            "latest_report_timestamp": max(r.timestamp for r in reports).isoformat(),
            "verified_reports": sum(1 for r in reports if r.verified),
            "distinct_reporters": len(set(r.reporter_id for r in reports)),
        }

    def _update_reputation_from_report(
        self, device_id: str, report: ThreatIntelligenceReport
    ) -> None:
        """
        Update device reputation based on new threat report.

        Args:
            device_id: Device identifier
            report: New threat report
        """
        if device_id not in self.reputation_db:
            self.reputation_db[device_id] = ReputationRecord(
                device_id=device_id,
                reputation_score=0.5,
                reports_count=0,
                last_updated=datetime.utcnow(),
            )

        record = self.reputation_db[device_id]

        severity_impact = {
            "critical": 0.40,
            "high": 0.25,
            "medium": 0.12,
            "low": 0.05,
        }

        impact = severity_impact.get(report.severity, 0.10)
        record.reputation_score = max(0.0, record.reputation_score - impact)

        record.reports_count += 1
        record.last_updated = datetime.utcnow()
        record.contributors.add(report.reporter_id)
        record.threat_history.append(report.threat_type)

        if report.verified:
            record.verification_level = "verified"

    def _apply_reputation_decay(self, record: ReputationRecord) -> ReputationRecord:
        """
        Apply time-based reputation decay.

        Reputation gradually improves over time without new negative reports.

        Args:
            record: Reputation record

        Returns:
            Updated record
        """
        days_since_update = (datetime.utcnow() - record.last_updated).days

        if days_since_update > 0:
            decay_factor = self.decay_rate ** days_since_update
            old_score = record.reputation_score
            record.reputation_score = old_score + ((1.0 - old_score) * (1.0 - decay_factor))

        return record

    def _generate_report_id(self, device_id: str, reporter_id: str) -> str:
        """
        Generate unique report identifier.

        Args:
            device_id: Device identifier
            reporter_id: Reporter identifier

        Returns:
            Report ID hash
        """
        content = f"{device_id}:{reporter_id}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
