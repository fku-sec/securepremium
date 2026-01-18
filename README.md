# Securepremium

## Overview

Securepremium is a Python library for quantifying device compromise risk through risk-based premium calculation. The system integrates hardware device fingerprinting, behavioral analysis using machine learning, and decentralized threat intelligence to produce risk assessments and corresponding insurance premium quotes.

## Features

- Risk-based premium calculation derived from multi-dimensional device scoring
- Anomaly detection through machine learning analysis of device behavior
- Hardware fingerprinting integration with external provider support
- Decentralized threat intelligence network for collaborative security reporting
- Volume pricing adjustments for organizational device fleet management
- Multi-factor risk assessment incorporating hardware, behavioral, network, and statistical anomaly signals
- Comprehensive audit trail with cryptographic proof of assessments

## Installation

```bash
pip install securepremium
```

To install with development dependencies:

```bash
pip install securepremium[dev]
```

## Quick Start

```python
from securepremium import RiskCalculator, PremiumEngine, DeviceScorer, ReputationNetwork

# Initialize components
risk_calculator = RiskCalculator()
premium_engine = PremiumEngine()
device_scorer = DeviceScorer()
reputation_network = ReputationNetwork(network_id="org_network")

# Register a device
device_profile = device_scorer.register_device(
    device_id="device_001",
    fingerprint_hash="abc123def456",
    hardware_info={"cpu": "Intel Core i7", "ram": "16GB"},
    system_info={"os": "Windows 11", "version": "22H2"}
)

# Calculate risk assessment
risk_assessment = risk_calculator.calculate_risk(
    device_id="device_001",
    device_metrics={
        "login_failures": 2,
        "total_login_attempts": 100,
        "tpm_status": "healthy",
        "cpu_usage": 25.5,
    }
)

print(f"Risk Score: {risk_assessment.overall_risk_score:.2%}")
print(f"Risk Category: {risk_calculator.get_risk_category(risk_assessment.overall_risk_score)}")

# Generate premium quote
quote = premium_engine.generate_quote(
    device_id="device_001",
    risk_assessment=risk_assessment,
    coverage_level="standard"
)

print(f"Annual Premium: ${quote.annual_premium_usd:.2f}")
print(f"Monthly Premium: ${quote.monthly_premium_usd:.2f}")
```

## Architecture

### Core Components

Risk Calculator (securepremium.core.risk_calculator)

Evaluates device compromise likelihood through multi-dimensional scoring. Combines behavioral, hardware, and network risk signals to produce comprehensive risk assessment with associated confidence scores.

Premium Engine (securepremium.core.premium_engine)

Calculates insurance premiums from risk profiles. Applies reputation-based and volume-based adjustments. Generates premium quotes and cost estimates for organizational device fleets.

Device Scorer (securepremium.models.device_scorer)

Maintains device trust profiles and tracks security incidents. Scores device trustworthiness based on behavioral baselines, historical events, and fingerprint stability.

Reputation Network (securepremium.network.reputation_network)

Implements decentralized threat intelligence sharing. Manages collective device reputation scores through participant submissions and verification mechanisms. Enables collaborative security threat reporting with time-based reputation decay.

Premium Model (securepremium.pricing.premium_model)

Implements pricing algorithms incorporating risk-to-multiplier conversion. Manages coverage tier definitions and volume discount schedules. Calculates multi-year policy pricing with adjustment factors.

## Operation

### Device Registration

Devices are registered with hardware fingerprints and system configuration information. The device scorer establishes baseline profiles for subsequent behavioral analysis.

```python
device_profile = device_scorer.register_device(
    device_id="device_001",
    fingerprint_hash="hardware_fingerprint_hash",
    hardware_info={...},
    system_info={...}
)
```

### Risk Assessment

Risk evaluation integrates multiple data sources and scoring mechanisms:

```python
assessment = risk_calculator.calculate_risk(
    device_id="device_001",
    device_metrics={...},
    historical_data={...},
    network_reputation={...}
)
```

Risk components assessed:

- Behavioral Risk: Login attempt patterns, resource utilization, network access patterns
- Hardware Risk: Component integrity status, TPM state, firmware anomalies
- Network Risk: Geographic location consistency, peer reputation, reputation network status
- Anomaly Score: Statistical anomalies detected through machine learning classification

### Premium Calculation

Risk scores determine premium pricing according to defined multiplier schedules:

```python
quote = premium_engine.generate_quote(
    device_id="device_001",
    risk_assessment=assessment,
    reputation_score=0.75,
    coverage_level="standard"
)
```

Premium adjustments include:

- Risk-based multiplier applied to base premium (range: 0.5x to 4.0x)
- Reputation-based discount or penalty (range: -20% to +25%)
- Volume discount for organizational fleet scale (range: 0% to 20%)
- Coverage tier selection affecting claim maximums and deductibles

### Threat Intelligence Reporting

Organizations participate in decentralized threat sharing by submitting threat reports:

```python
reputation_network.register_participant("organization_id")

report = reputation_network.submit_threat_report(
    reporter_id="organization_id",
    device_id="suspicious_device",
    threat_type="credential_harvesting",
    severity="high",
    description="Device exhibited malware characteristics",
    evidence_hash="sha256_hash_of_evidence"
)
```

Reputation queries inform premium adjustments:

```python
reputation = reputation_network.query_device_reputation("device_id")
print(f"Reputation Score: {reputation.reputation_score:.2f}")
print(f"Risk Level: {reputation_network.get_device_risk_level('device_id')}")
```

## Risk Scoring Methodology

### Risk Calculation Formula

Overall risk score is computed as a weighted combination of component scores:

```
Overall Risk = (0.25 × Behavioral) + (0.35 × Hardware) + (0.20 × Network) + (0.20 × Anomaly)
```

Risk scores are normalized to the range [0.0, 1.0] where higher values indicate increased compromise probability.

### Risk Classification

| Score Range | Classification | Premium Multiplier |
|-------------|-----------------|-------------------|
| 0.00 - 0.30 | Minimal Risk | 0.5x - 0.8x |
| 0.30 - 0.50 | Low Risk | 0.8x - 1.2x |
| 0.50 - 0.70 | Medium Risk | 1.2x - 2.0x |
| 0.70 - 0.85 | High Risk | 2.0x - 3.5x |
| 0.85 - 1.00 | Critical Risk | 3.5x - 4.0x |

## Premium Pricing Model

### Base Premium

The base annual premium is $120 USD. All premium calculations apply multipliers and adjustments to this base value.

### Coverage Options

| Tier | Price Multiplier | Maximum Claim | Deductible | Scope |
|------|------------------|---------------|-----------|-------|
| Basic | 1.0x | $5,000 | $500 | Malware remediation, data recovery, incident support |
| Standard | 1.5x | $25,000 | $250 | Forensic analysis, legal consultation, incident response |
| Premium | 2.5x | $100,000 | $0 | 24/7 incident response, credential monitoring, proactive threat assessment |

### Reputation Adjustment Schedule

Device reputation scores from the network affect premium pricing:

| Reputation Score | Adjustment |
|------------------|-----------|
| < 0.30 | +25% (penalty) |
| 0.30 - 0.50 | +10% (penalty) |
| 0.50 - 0.70 | 0% (baseline) |
| 0.70 - 0.85 | -10% (discount) |
| > 0.85 | -20% (discount) |

### Volume Pricing

Organizations managing multiple devices receive volume discounts:

| Device Count | Discount |
|------------|----------|
| < 10 | 0% |
| 10-50 | 5% |
| 50-100 | 10% |
| 100-500 | 15% |
| > 500 | 20% |

## Usage Examples

### Batch Risk Assessment

Processing risk assessments for multiple devices in an organization:

```python
from securepremium.utils import format_currency

devices = ["device_001", "device_002", "device_003"]
assessments = {}

for device_id in devices:
    metrics = fetch_device_metrics(device_id)
    assessment = risk_calculator.calculate_risk(
        device_id=device_id,
        device_metrics=metrics
    )
    assessments[device_id] = assessment

# Estimate organizational cost across fleet
cost_estimate = premium_engine.estimate_annual_cost(
    total_devices=len(devices),
    average_risk_score=sum(a.overall_risk_score for a in assessments.values()) / len(assessments),
    average_reputation=0.65,
    coverage_distribution={"basic": 0.3, "standard": 0.5, "premium": 0.2}
)

print(f"Total Annual Cost: {format_currency(cost_estimate['total_annual_cost'])}")
print(f"Per Device Monthly: {format_currency(cost_estimate['cost_per_device_monthly'])}")
```

### Threat Intelligence Integration

Integrating with the decentralized threat network to report and query threat information:

```python
# Register organization as network participant
network.register_participant("security_team_1")

# Submit threat report for suspicious device
report = network.submit_threat_report(
    reporter_id="security_team_1",
    device_id="suspicious_device_xyz",
    threat_type="malware_detected",
    severity="critical",
    description="Trojan.GenericKD detected in system memory",
    evidence_hash="hash_of_forensic_report"
)

# Verify report accuracy
network.verify_report(report.report_id)

# Query threat intelligence summary for device
intelligence = network.get_threat_intelligence_summary("suspicious_device_xyz")

# Recalculate premium based on updated threat intelligence
updated_quote = premium_engine.generate_quote(
    device_id="suspicious_device_xyz",
    risk_assessment=new_assessment,
    reputation_score=intelligence["reputation"]["reputation_score"]
)
```

## Configuration

System configuration can be customized through the engine and calculator interfaces:

```python
from securepremium import PremiumEngine

engine = PremiumEngine()

# Adjust base premium amount
engine.base_annual_premium = 150.0

# Modify risk classification thresholds
engine.risk_thresholds["high"] = 0.65
```

## Testing

Execute the test suite:

```bash
pytest tests/ -v
```

Generate coverage report:

```bash
pytest tests/ --cov=securepremium --cov-report=html
```

## Security Considerations

Implementation incorporates security best practices:

- Device fingerprints are stored in hashed form, never plaintext
- Risk assessment confidence scores indicate data quality and certainty
- Threat reports are immutable with cryptographic timestamping
- Reputation data implements decay functions to reflect current device state
- Financial calculations use fixed-point arithmetic to prevent floating-point precision issues

## Dependencies

Core dependencies:

- device-fingerprinting-pro (>= 2.2.0): Hardware fingerprinting service interface
- numpy (>= 1.21.0): Numerical computation and array operations
- scikit-learn (>= 1.0.0): Machine learning algorithms for anomaly detection
- pydantic (>= 2.0.0): Data model validation and serialization
- requests (>= 2.28.0): HTTP client for network communication

## Contribution

Contributions are accepted through the standard process:

1. Fork the repository
2. Create a feature branch for your changes
3. Add tests covering new functionality
4. Verify all tests pass
5. Submit pull request for review

## License

MIT License. See LICENSE file for full terms.

## Support

For technical support, issue reporting, or contributions, please access the project repository.
