# API Reference

## Core Module (`securepremium.core`)

### RiskCalculator

```python
class RiskCalculator:
    """Comprehensive risk calculation engine"""
    
    def calculate_risk(
        device_id: str,
        device_metrics: Dict,
        historical_data: Optional[Dict] = None,
        network_reputation: Optional[Dict] = None
    ) -> RiskAssessment
    
    def get_risk_category(risk_score: float) -> str
    # Returns: "critical", "high", "medium", "low", "minimal"
```

**Risk Components**:
- Behavioral Risk: Login patterns, resource usage, access anomalies
- Hardware Risk: Component integrity, TPM status, firmware
- Network Risk: Geolocation, peer reputation, blacklist status
- Anomaly Score: ML-detected system abnormalities

### RiskAssessment (Data Class)

```python
@dataclass
class RiskAssessment:
    device_id: str
    timestamp: datetime
    overall_risk_score: float              # 0.0 to 1.0
    behavioral_risk: float
    hardware_risk: float
    network_risk: float
    anomaly_score: float
    threat_indicators: List[str]
    confidence_level: float                # 0.0 to 1.0
    assessment_version: str
    
    def to_dict() -> Dict
```

### PremiumEngine

```python
class PremiumEngine:
    """Premium calculation and quote generation"""
    
    def generate_quote(
        device_id: str,
        risk_assessment: RiskAssessment,
        reputation_score: Optional[float] = None,
        coverage_level: str = "standard",  # "basic", "standard", "premium"
        policy_duration_months: int = 12
    ) -> PremiumQuote
    
    def apply_volume_discount(
        base_quote: PremiumQuote,
        device_count: int
    ) -> PremiumQuote
    
    def estimate_annual_cost(
        total_devices: int,
        average_risk_score: float,
        average_reputation: float,
        coverage_distribution: Dict[str, float]
    ) -> Dict
```

### PremiumQuote (Data Class)

```python
@dataclass
class PremiumQuote:
    device_id: str
    annual_premium_usd: float
    monthly_premium_usd: float
    base_premium: float
    risk_adjustment: float
    reputation_discount: float
    coverage_level: str
    quote_timestamp: datetime
    quote_valid_until: datetime
    terms: Dict
    
    def to_dict() -> Dict
```

---

## Models Module (`securepremium.models`)

### DeviceScorer

```python
class DeviceScorer:
    """Device trustworthiness scoring system"""
    
    def register_device(
        device_id: str,
        fingerprint_hash: str,
        hardware_info: Dict,
        system_info: Dict
    ) -> DeviceProfile
    
    def calculate_device_score(
        device_id: str
    ) -> Tuple[float, Dict]
    # Returns: (overall_score, component_breakdown)
    
    def add_security_event(
        device_id: str,
        event_type: str,
        severity: str,              # "critical", "high", "medium", "low"
        description: str
    ) -> None
    
    def get_device_score_category(score: float) -> str
    # Returns: "trusted", "normal", "suspect", "untrusted"
```

**Score Components**:
- Fingerprint Stability: Hardware consistency
- Behavioral Consistency: Pattern recognition
- Security Incidents: Incident history and severity
- Longevity: Device age and activity
- Geographic Patterns: Travel pattern analysis

### DeviceProfile (Data Class)

```python
@dataclass
class DeviceProfile:
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
    
    def get_age_days() -> int
    def get_last_activity_hours() -> int
```

---

## Network Module (`securepremium.network`)

### ReputationNetwork

```python
class ReputationNetwork:
    """Decentralized threat intelligence network"""
    
    def register_participant(participant_id: str) -> bool
    
    def submit_threat_report(
        reporter_id: str,
        device_id: str,
        threat_type: str,
        severity: str,              # "critical", "high", "medium", "low"
        description: str,
        evidence_hash: str
    ) -> ThreatIntelligenceReport
    
    def query_device_reputation(
        device_id: str
    ) -> Optional[ReputationRecord]
    
    def get_device_risk_level(device_id: str) -> str
    # Returns: "trustworthy", "neutral", "suspicious", "dangerous", "unrated"
    
    def verify_report(
        report_id: str,
        verification_count: int = 2
    ) -> bool
    
    def get_network_statistics() -> Dict
    
    def get_threat_intelligence_summary(device_id: str) -> Optional[Dict]
```

### ReputationRecord (Data Class)

```python
@dataclass
class ReputationRecord:
    device_id: str
    reputation_score: float         # 0.0 to 1.0
    reports_count: int
    last_updated: datetime
    contributors: Set[str]
    threat_history: List[str]
    verification_level: str         # "unverified", "verified"
    
    def to_dict() -> Dict
```

### ThreatIntelligenceReport (Data Class)

```python
@dataclass
class ThreatIntelligenceReport:
    report_id: str
    reporter_id: str
    device_id: str
    threat_type: str
    severity: str
    description: str
    evidence_hash: str
    timestamp: datetime
    verified: bool = False
    
    def to_dict() -> Dict
```

---

## Pricing Module (`securepremium.pricing`)

### PremiumModel

```python
class PremiumModel:
    """Sophisticated pricing model"""
    
    def calculate_base_premium(
        risk_score: float,
        confidence: float,
        coverage_tier: str,
        reputation_score: Optional[float] = None
    ) -> float
    
    def apply_volume_discount(
        premium: float,
        device_count: int
    ) -> Tuple[float, float]
    # Returns: (discounted_premium, discount_rate)
    
    def calculate_annual_policy_cost(
        monthly_premium: float,
        policy_months: int,
        includes_discount: bool = False,
        bulk_count: Optional[int] = None
    ) -> Dict
    
    def get_tier_details(tier_name: str) -> Dict
    def get_all_tiers() -> Dict
```

### PricingTierConfig (Data Class)

```python
@dataclass
class PricingTierConfig:
    tier_name: str
    base_multiplier: float
    max_annual_claim: int
    deductible: int
    coverage_items: List[str]
```

---

## Utils Module (`securepremium.utils`)

### Helper Functions

```python
def setup_logging(name: str, level: str = "INFO") -> logging.Logger

def safe_get(data: Dict, path: str, default: Any = None) -> Any
# Usage: safe_get(data, "user.profile.name")

def normalize_risk_score(
    score: float,
    min_val: float = 0.0,
    max_val: float = 1.0
) -> float

def calculate_percentile(value: float, values: List[float]) -> float

def format_currency(amount: float, currency: str = "USD") -> str

def validate_device_id(device_id: str) -> bool

def validate_risk_score(score: float) -> bool

def validate_reputation_score(score: float) -> bool

def iso_to_datetime(iso_string: str) -> datetime

def datetime_to_iso(dt: datetime) -> str

def serialize_report(report_dict: Dict) -> str

def deserialize_report(json_string: str) -> Dict
```

---

## Data Flow Examples

### Risk Assessment Flow

```
Device Metrics → RiskCalculator.calculate_risk()
                 ├─ Behavioral Risk (25%)
                 ├─ Hardware Risk (35%)
                 ├─ Network Risk (20%)
                 ├─ Anomaly Score (20%)
                 └─ RiskAssessment Output
```

### Premium Calculation Flow

```
RiskAssessment + Reputation → PremiumEngine.generate_quote()
                               ├─ Risk Multiplier
                               ├─ Coverage Multiplier
                               ├─ Reputation Discount
                               └─ PremiumQuote Output
```

### Reputation Update Flow

```
Threat Report → ReputationNetwork.submit_threat_report()
                ├─ Create ThreatIntelligenceReport
                ├─ Update ReputationRecord
                ├─ Apply Severity Impact
                └─ Store in Reputation Database
```

### Device Scoring Flow

```
Device Profile + History → DeviceScorer.calculate_device_score()
                           ├─ Fingerprint Stability
                           ├─ Behavioral Consistency
                           ├─ Security Score
                           ├─ Longevity Score
                           ├─ Geographic Score
                           └─ Weighted Average Score
```

---

## Constants & Thresholds

### Risk Categories

| Category | Range | Premium Impact |
|----------|-------|----------------|
| Minimal | 0.00-0.30 | 0.5x-0.8x |
| Low | 0.30-0.50 | 0.8x-1.2x |
| Medium | 0.50-0.70 | 1.2x-2.0x |
| High | 0.70-0.85 | 2.0x-3.5x |
| Critical | 0.85-1.00 | 3.5x-4.0x |

### Reputation Levels

| Level | Range | Classification |
|-------|-------|-----------------|
| Trustworthy | 0.85-1.00 | Safe |
| Neutral | 0.60-0.85 | Normal |
| Suspicious | 0.35-0.60 | Caution |
| Dangerous | 0.00-0.35 | Risk |
| Unrated | N/A | No Data |

### Device Score Categories

| Score | Category | Meaning |
|-------|----------|---------|
| 0.85+ | Trusted | Highly trustworthy |
| 0.65-0.85 | Normal | Standard device |
| 0.40-0.65 | Suspect | Elevated concern |
| 0.00-0.40 | Untrusted | High risk |

### Coverage Tiers

| Tier | Multiplier | Max Claim | Deductible |
|------|-----------|----------|-----------|
| Basic | 1.0x | $5,000 | $500 |
| Standard | 1.5x | $25,000 | $250 |
| Premium | 2.5x | $100,000 | $0 |

---

## Error Handling

All modules include proper error handling:

```python
# Example: Calculating score for unknown device
try:
    score = device_scorer.calculate_device_score("unknown_device")
except ValueError:
    print("Device not found in registry")

# Example: Invalid coverage tier
try:
    quote = premium_engine.generate_quote(
        device_id="device_001",
        risk_assessment=assessment,
        coverage_level="invalid_tier"
    )
except ValueError:
    print("Invalid coverage level specified")

# Example: Unregistered network participant
try:
    report = reputation_network.submit_threat_report(
        reporter_id="unknown_org",
        device_id="device",
        threat_type="threat",
        severity="high",
        description="desc",
        evidence_hash="hash"
    )
except ValueError:
    print("Organization not registered with network")
```

---

## Type Hints

All functions use comprehensive type hints:

```python
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime

# Example function signature
def calculate_risk(
    device_id: str,
    device_metrics: Dict[str, any],
    historical_data: Optional[Dict[str, float]] = None
) -> RiskAssessment:
    ...
```

---

## Module Imports

```python
# Import main components
from securepremium import (
    RiskCalculator,
    PremiumEngine,
    DeviceScorer,
    ReputationNetwork,
    PremiumModel,
)

# Import data classes
from securepremium.core import RiskAssessment, PremiumQuote
from securepremium.models import DeviceProfile
from securepremium.network import ReputationRecord, ThreatIntelligenceReport

# Import utilities
from securepremium.utils import (
    setup_logging,
    validate_device_id,
    format_currency,
)
```

---

## Configuration

All components accept optional configuration:

```python
# Risk calculator with custom thresholds
calculator = RiskCalculator()
calculator.risk_thresholds["high"] = 0.65

# Premium engine with custom base premium
engine = PremiumEngine()
engine.base_annual_premium = 150.0

# Reputation network with custom decay rate
network = ReputationNetwork(network_id="custom_network")
network.decay_rate = 0.92
```
