# Securepremium

## Overview

Securepremium is an enterprise-grade Python library that quantifies device compromise risk as insurance premiums. It combines hardware device fingerprinting, ML-based behavioral analysis, and decentralized threat intelligence to create a comprehensive device security marketplace.

## Key Features

- **Risk-Based Pricing**: Insurance premiums dynamically adjust based on device security posture
- **ML Anomaly Detection**: Identifies abnormal device behavior and security patterns
- **Hardware Fingerprinting Integration**: Hardware-backed device identification via an external provider (optional)
- **Decentralized Threat Network**: Collaborative threat intelligence sharing with reputation mechanisms
- **Volume Discounts**: Organizations benefit from managing device fleets securely
- **Professional-Grade Scoring**: Multi-factor risk assessment combining hardware, behavioral, and network signals
- **Comprehensive Audit Trail**: Cryptographic proof of risk assessments and premium calculations

## Installation

```bash
pip install securepremium
```

Or with all optional dependencies:

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

print(f"Annual Premium: {quote.annual_premium_usd:.2f}")
print(f"Monthly Premium: {quote.monthly_premium_usd:.2f}")
```

## Architecture

### Core Components

**Risk Calculator** (`securepremium.core.risk_calculator`)
- Evaluates device compromise likelihood
- Combines behavioral, hardware, and network risk signals
- Produces comprehensive risk assessment with confidence scores

**Premium Engine** (`securepremium.core.premium_engine`)
- Calculates insurance premiums from risk profiles
- Applies reputation discounts and volume discounts
- Generates professional premium quotes

**Device Scorer** (`securepremium.models.device_scorer`)
- Maintains device trust profiles
- Tracks security incidents and behavioral patterns
- Provides device trustworthiness scoring

**Reputation Network** (`securepremium.network.reputation_network`)
- Decentralized threat intelligence sharing
- Manages collective device reputation scores
- Enables collaborative security threat reporting

**Premium Model** (`securepremium.pricing.premium_model`)
- Sophisticated pricing algorithms
- Coverage tier management
- Cost estimation and analysis

## How It Works

### 1. Device Registration

Devices are registered with hardware fingerprints and system information:

```python
device_profile = device_scorer.register_device(
    device_id="device_001",
    fingerprint_hash="hardware_fingerprint_hash",
    hardware_info={...},
    system_info={...}
)
```

### 2. Risk Assessment

Multi-dimensional risk evaluation:

```python
assessment = risk_calculator.calculate_risk(
    device_id="device_001",
    device_metrics={...},  # Current device state
    historical_data={...},  # Behavioral baseline
    network_reputation={...}  # Network threat data
)
```

Risk components include:
- **Behavioral Risk**: Login patterns, resource usage, access patterns
- **Hardware Risk**: Component integrity, TPM status, firmware anomalies
- **Network Risk**: Geographic patterns, peer reputation, blacklist status
- **Anomaly Score**: ML-detected system abnormalities

### 3. Premium Calculation

Risk scores drive premium pricing:

```python
quote = premium_engine.generate_quote(
    device_id="device_001",
    risk_assessment=assessment,
    reputation_score=0.75,
    coverage_level="standard"
)
```

Premium adjustments:
- Higher risk increases premiums (up to 4x base)
- Better reputation provides discounts (up to 30%)
- Volume discounts for large device fleets (5-20%)
- Coverage tier selection (basic, standard, premium)

### 4. Threat Intelligence Sharing

Organizations report suspicious devices to network:

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

Other organizations query reputation to adjust premiums:

```python
reputation = reputation_network.query_device_reputation("device_id")
print(f"Reputation Score: {reputation.reputation_score:.2f}")
print(f"Risk Level: {reputation_network.get_device_risk_level('device_id')}")
```

## Risk Scoring Details

### Overall Risk Formula

```
Overall Risk = (0.25 × Behavioral) + (0.35 × Hardware) + (0.20 × Network) + (0.20 × Anomaly)
```

### Risk Categories

| Score Range | Category | Premium Impact |
|-------------|----------|----------------|
| 0.00 - 0.30 | Minimal | 0.5x - 0.8x base |
| 0.30 - 0.50 | Low | 0.8x - 1.2x base |
| 0.50 - 0.70 | Medium | 1.2x - 2.0x base |
| 0.70 - 0.85 | High | 2.0x - 3.5x base |
| 0.85 - 1.00 | Critical | 3.5x - 4.0x base |

## Premium Pricing

### Base Premium

Base annual premium: $120 USD

### Coverage Tiers

| Tier | Multiplier | Max Claim | Deductible | Features |
|------|-----------|-----------|-----------|----------|
| Basic | 1.0x | $5,000 | $500 | Malware removal, data recovery, incident support |
| Standard | 1.5x | $25,000 | $250 | + forensic analysis, legal consultation |
| Premium | 2.5x | $100,000 | $0 | + 24/7 response, credential monitoring |

### Reputation Adjustments

| Reputation | Adjustment |
|-----------|-----------|
| < 0.30 | +25% (penalty) |
| 0.30 - 0.50 | +10% (penalty) |
| 0.50 - 0.70 | 0% (neutral) |
| 0.70 - 0.85 | -10% (discount) |
| > 0.85 | -20% (discount) |

### Volume Discounts

| Device Count | Discount |
|------------|----------|
| < 10 | 0% |
| 10-50 | 5% |
| 50-100 | 10% |
| 100-500 | 15% |
| > 500 | 20% |

## Advanced Usage

### Batch Risk Assessment

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

# Estimate organizational cost
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

```python
# Network participant submits threat report
network.register_participant("security_team_1")

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

# Query updated device reputation
intelligence = network.get_threat_intelligence_summary("suspicious_device_xyz")

# Adjust premiums based on network intelligence
updated_quote = premium_engine.generate_quote(
    device_id="suspicious_device_xyz",
    risk_assessment=new_assessment,
    reputation_score=intelligence["reputation"]["reputation_score"]
)
```

## Configuration

Default configuration can be customized:

```python
from securepremium import PremiumEngine

engine = PremiumEngine()
engine.base_annual_premium = 150.0  # Change base premium
engine.risk_thresholds["high"] = 0.65  # Adjust risk categories
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

With coverage reporting:

```bash
pytest tests/ --cov=securepremium --cov-report=html
```

## Security Considerations

- Device fingerprints are hashed and never stored plaintext
- Risk assessments include confidence scores for data quality
- Threat reports are timestamped and attribution is immutable
- Reputation data decays over time to encourage improvement
- All monetary calculations use rounded precision to prevent fraud

## Dependencies

- **device-fingerprinting-pro** >= 2.2.0: Hardware fingerprinting
- **numpy** >= 1.21.0: Numerical operations
- **scikit-learn** >= 1.0.0: ML-based anomaly detection
- **pydantic** >= 2.0.0: Data validation
- **requests** >= 2.28.0: Network communication

## Contributing

Contributions welcome. Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue on GitHub.
