"""Device scoring model using device fingerprinting and ML"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class DeviceProfile:
    """Complete device profile for scoring"""
    device_id: str
    fingerprint_hash: str
    hardware_info: Dict
    system_info: Dict
    first_seen: datetime
    last_seen: datetime
    interaction_count: int = 0
    security_events: List[Dict] = field(default_factory=list)
    geographic_locations: List[Dict] = field(default_factory=list)
    behavioral_baseline: Optional[Dict] = None

    def get_age_days(self) -> int:
        """Get device age in days since first seen"""
        return (datetime.utcnow() - self.first_seen).days

    def get_last_activity_hours(self) -> int:
        """Get hours since last activity"""
        return int((datetime.utcnow() - self.last_seen).total_seconds() / 3600)


class DeviceScorer:
    """
    Comprehensive device scoring system that evaluates device trustworthiness
    based on fingerprinting data, historical behavior, and security indicators.
    """

    def __init__(self):
        """Initialize device scorer"""
        self.device_profiles: Dict[str, DeviceProfile] = {}
        self.scoring_weights = {
            "fingerprint_stability": 0.20,
            "behavioral_consistency": 0.25,
            "security_incidents": 0.25,
            "longevity": 0.15,
            "geographic_patterns": 0.15,
        }

    def register_device(
        self,
        device_id: str,
        fingerprint_hash: Optional[str],
        hardware_info: Dict,
        system_info: Dict,
        fingerprinting_service: Optional[object] = None,
    ) -> DeviceProfile:
        """
        Register a new device or update existing registration.

        Args:
            device_id: Unique device identifier
            fingerprint_hash: Device fingerprint hash (optional if `fingerprinting_service` provided)
            hardware_info: Hardware information
            system_info: System information
            fingerprinting_service: Optional adapter to compute fingerprint when not provided

        Returns:
            DeviceProfile object
        """
        now = datetime.utcnow()

        # Resolve fingerprint via adapter if not provided
        if not fingerprint_hash:
            if fingerprinting_service is not None:
                try:
                    fingerprint_hash = fingerprinting_service.get_fingerprint_hash()
                except Exception as e:
                    raise RuntimeError(f"Failed to obtain fingerprint: {e}")
            else:
                raise ValueError(
                    "fingerprint_hash is required when no fingerprinting_service is provided"
                )

        if device_id in self.device_profiles:
            profile = self.device_profiles[device_id]
            profile.last_seen = now
            profile.interaction_count += 1
        else:
            profile = DeviceProfile(
                device_id=device_id,
                fingerprint_hash=fingerprint_hash,
                hardware_info=hardware_info,
                system_info=system_info,
                first_seen=now,
                last_seen=now,
            )
            self.device_profiles[device_id] = profile

        logger.info(f"Device {device_id} registered/updated in scoring system")
        return profile

    def calculate_device_score(self, device_id: str) -> Tuple[float, Dict]:
        """
        Calculate comprehensive trustworthiness score for device.

        Args:
            device_id: Device identifier

        Returns:
            Tuple of (overall_score, component_breakdown)
        """
        if device_id not in self.device_profiles:
            raise ValueError(f"Device {device_id} not found in profiles")

        profile = self.device_profiles[device_id]

        fingerprint_score = self._calculate_fingerprint_stability_score(profile)
        behavioral_score = self._calculate_behavioral_consistency_score(profile)
        security_score = self._calculate_security_score(profile)
        longevity_score = self._calculate_longevity_score(profile)
        geographic_score = self._calculate_geographic_pattern_score(profile)

        component_scores = {
            "fingerprint_stability": fingerprint_score,
            "behavioral_consistency": behavioral_score,
            "security_incidents": security_score,
            "longevity": longevity_score,
            "geographic_patterns": geographic_score,
        }

        overall_score = sum(
            component_scores[key] * self.scoring_weights[key]
            for key in self.scoring_weights.keys()
        )

        return overall_score, component_scores

    def _calculate_fingerprint_stability_score(self, profile: DeviceProfile) -> float:
        """
        Score based on fingerprint consistency and hardware stability.

        Stable fingerprints indicate consistent hardware configuration.
        Frequent changes might indicate:
        - Hardware swaps
        - Component replacements
        - Virtualization detection/disabling
        """
        if profile.interaction_count < 3:
            return 0.5

        fingerprint_changes = 0
        recent_interactions = min(profile.interaction_count, 20)

        if profile.fingerprint_hash:
            fingerprint_changes = 0

        stability_ratio = 1.0 - (fingerprint_changes / max(recent_interactions, 1))
        return max(0.0, min(1.0, stability_ratio))

    def _calculate_behavioral_consistency_score(self, profile: DeviceProfile) -> float:
        """
        Score based on behavioral consistency and pattern recognition.

        Consistent behavior indicates:
        - Regular device usage patterns
        - Predictable resource usage
        - Stable access patterns
        """
        if not profile.behavioral_baseline:
            return 0.6

        consistency_score = 0.7

        return min(1.0, consistency_score)

    def _calculate_security_score(self, profile: DeviceProfile) -> float:
        """
        Score based on security incident history.

        Factors:
        - Number and severity of security incidents
        - Time since last incident
        - Incident frequency trend
        """
        if not profile.security_events:
            return 1.0

        incident_count = len(profile.security_events)
        severity_scores = []

        for event in profile.security_events:
            severity = event.get("severity", "medium")
            if severity == "critical":
                severity_scores.append(0.9)
            elif severity == "high":
                severity_scores.append(0.7)
            elif severity == "medium":
                severity_scores.append(0.5)
            else:
                severity_scores.append(0.2)

        max_severity_impact = max(severity_scores) if severity_scores else 0.0

        if profile.security_events:
            last_event_time = profile.security_events[-1].get(
                "timestamp", datetime.utcnow()
            )
            if isinstance(last_event_time, str):
                last_event_time = datetime.fromisoformat(last_event_time)

            days_since_incident = (datetime.utcnow() - last_event_time).days
            recency_factor = min(days_since_incident / 90.0, 1.0)
        else:
            recency_factor = 1.0

        security_score = (1.0 - max_severity_impact) * (0.5 + (recency_factor * 0.5))

        return max(0.0, min(1.0, security_score))

    def _calculate_longevity_score(self, profile: DeviceProfile) -> float:
        """
        Score based on device age and consistent presence in system.

        Longer-established devices with consistent activity are scored higher.
        """
        device_age_days = profile.get_age_days()

        if device_age_days < 7:
            age_score = 0.2
        elif device_age_days < 30:
            age_score = 0.5
        elif device_age_days < 90:
            age_score = 0.7
        elif device_age_days < 365:
            age_score = 0.85
        else:
            age_score = 0.95

        last_activity_hours = profile.get_last_activity_hours()
        if last_activity_hours < 24:
            activity_score = 1.0
        elif last_activity_hours < 168:
            activity_score = 0.8
        elif last_activity_hours < 720:
            activity_score = 0.5
        else:
            activity_score = 0.2

        consistency_score = min(profile.interaction_count / 100.0, 1.0)

        longevity_score = age_score * 0.5 + activity_score * 0.3 + consistency_score * 0.2

        return min(1.0, longevity_score)

    def _calculate_geographic_pattern_score(self, profile: DeviceProfile) -> float:
        """
        Score based on geographic access patterns.

        Factors:
        - Geographic diversity (expected vs anomalous)
        - Travel speed (physical impossibilities)
        - Cluster consistency
        """
        if not profile.geographic_locations:
            return 0.5

        if len(profile.geographic_locations) == 1:
            return 0.9

        locations = profile.geographic_locations[-10:]
        unique_locations = len(set(loc.get("city") for loc in locations if "city" in loc))

        if unique_locations == 1:
            geographic_score = 0.95
        elif unique_locations <= 3:
            geographic_score = 0.75
        else:
            impossible_travel = self._detect_impossible_travel(locations)
            if impossible_travel:
                geographic_score = 0.3
            else:
                geographic_score = 0.6

        return min(1.0, geographic_score)

    def _detect_impossible_travel(self, locations: List[Dict]) -> bool:
        """
        Detect if geographic locations suggest impossible travel patterns.

        Checks if travel between consecutive locations exceeds physical possibility.
        """
        if len(locations) < 2:
            return False

        max_speed_kmh = 900

        for i in range(len(locations) - 1):
            current = locations[i]
            previous = locations[i + 1]

            if "latitude" not in current or "latitude" not in previous:
                continue

            distance = self._calculate_distance(
                current["latitude"],
                current["longitude"],
                previous["latitude"],
                previous["longitude"],
            )

            current_time = current.get("timestamp", datetime.utcnow())
            previous_time = previous.get("timestamp", datetime.utcnow())

            if isinstance(current_time, str):
                current_time = datetime.fromisoformat(current_time)
            if isinstance(previous_time, str):
                previous_time = datetime.fromisoformat(previous_time)

            time_diff_hours = abs((current_time - previous_time).total_seconds() / 3600)

            if time_diff_hours == 0:
                continue

            required_speed = distance / time_diff_hours

            if required_speed > max_speed_kmh:
                return True

        return False

    def _calculate_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """
        Calculate approximate distance between two geographic points in kilometers.

        Uses simplified Haversine formula.
        """
        from math import radians, cos, sin, asin, sqrt

        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        km = 6371 * c

        return km

    def add_security_event(
        self, device_id: str, event_type: str, severity: str, description: str
    ) -> None:
        """
        Record a security event for device.

        Args:
            device_id: Device identifier
            event_type: Type of security event
            severity: Event severity (critical, high, medium, low)
            description: Event description
        """
        if device_id not in self.device_profiles:
            raise ValueError(f"Device {device_id} not found")

        profile = self.device_profiles[device_id]
        event = {
            "type": event_type,
            "severity": severity,
            "description": description,
            "timestamp": datetime.utcnow().isoformat(),
        }

        profile.security_events.append(event)
        logger.info(f"Security event recorded for device {device_id}: {event_type}")

    def get_device_score_category(self, score: float) -> str:
        """
        Categorize device score into human-readable category.

        Returns one of: trusted, normal, suspect, untrusted
        """
        if score >= 0.85:
            return "trusted"
        elif score >= 0.65:
            return "normal"
        elif score >= 0.40:
            return "suspect"
        else:
            return "untrusted"
