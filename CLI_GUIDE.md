# Securepremium CLI Documentation

## Overview

The Securepremium CLI provides command-line access to all core functionality of the Device Behavior Insurance Protocol, including device registration, risk assessment, premium quote generation, batch processing, and network statistics reporting.

## Installation

```bash
# Install package with CLI support
pip install -e .

# Or use the CLI entry point directly
python securepremium_cli.py
```

## Commands Overview

### Device Management

#### Register a Device
```bash
securepremium device register \
  --device-id CORP-LAP-001 \
  --fingerprint abc123def456 \
  --cpu "Intel Core i7" \
  --ram "16GB" \
  --os "Windows 11" \
  --version "22H2" \
  --hostname "CORP-LAP-001"
```

Output as JSON:
```bash
securepremium device register \
  --device-id CORP-LAP-001 \
  --fingerprint abc123def456 \
  --json-output
```

### Risk Assessment

#### Assess Device Risk
```bash
securepremium risk assess \
  --device-id CORP-LAP-001 \
  --login-failures 2 \
  --total-logins 100 \
  --tpm-status healthy \
  --cpu-usage 25.5
```

Output as JSON:
```bash
securepremium risk assess \
  --device-id CORP-LAP-001 \
  --json-output
```

### Premium Quotes

#### Generate Single Quote
```bash
securepremium quote generate \
  --device-id CORP-LAP-001 \
  --coverage standard
```

Coverage options: `basic`, `standard`, `premium`

### Batch Processing

#### Batch Risk Analysis

Input CSV format (example):
```csv
device_id,login_failures,total_logins,tpm_status,cpu_usage
CORP-LAP-001,2,100,healthy,25.5
CORP-LAP-002,0,50,healthy,10.2
CORP-LAP-003,5,100,degraded,75.3
```

Command:
```bash
securepremium batch analyze \
  --input-file devices.csv \
  --output-file results.csv \
  --format csv
```

Output as JSON:
```bash
securepremium batch analyze \
  --input-file devices.csv \
  --output-file results.json \
  --format json
```

#### Batch Quote Generation
```bash
securepremium batch quote-batch \
  --input-file devices.csv \
  --output-file quotes.csv \
  --coverage standard
```

### Network Statistics

#### Get Network Statistics
```bash
securepremium network stats --network-id org_network
```

#### Report Device Reputation
```bash
securepremium network report \
  --network-id org_network \
  --device-id CORP-LAP-001 \
  --reputation-score 0.85 \
  --threat-level low
```

#### Show Top Devices
```bash
securepremium network top-devices \
  --network-id org_network \
  --limit 10 \
  --sort-by reputation
```

### System Information

#### Display System Info
```bash
securepremium info
```

## JSON Output

All commands support `--json-output` flag for programmatic integration:

```bash
securepremium device register \
  --device-id CORP-LAP-001 \
  --fingerprint abc123def456 \
  --json-output
```

Returns:
```json
{
  "device_id": "CORP-LAP-001",
  "status": "registered",
  "fingerprint": "abc123def456",
  "timestamp": "2026-01-18T10:30:45.123456"
}
```

## Batch Processing Examples

### Example 1: Analyze Multiple Devices

Create `devices.csv`:
```csv
device_id,login_failures,total_logins,tpm_status,cpu_usage
CORP-LAP-001,2,100,healthy,25.5
CORP-LAP-002,0,50,healthy,10.2
CORP-LAP-003,5,100,degraded,75.3
CORP-LAP-004,1,200,healthy,45.1
```

Run analysis:
```bash
securepremium batch analyze --input-file devices.csv --output-file risk_results.csv
```

### Example 2: Generate Quotes for Fleet

```bash
securepremium batch quote-batch \
  --input-file devices.csv \
  --output-file fleet_quotes.csv \
  --coverage premium
```

Output (`fleet_quotes.csv`):
```csv
device_id,coverage,annual_premium,monthly_premium,timestamp
CORP-LAP-001,premium,$1250.00,$104.17,2026-01-18T10:30:45.123456
CORP-LAP-002,premium,$950.00,$79.17,2026-01-18T10:30:45.123456
...
```

## Use Cases

### 1. New Device Onboarding
```bash
# Register device
securepremium device register --device-id DEV-NEW-001 --fingerprint xyz789

# Assess risk immediately
securepremium risk assess --device-id DEV-NEW-001

# Generate quote
securepremium quote generate --device-id DEV-NEW-001 --coverage standard
```

### 2. Fleet Assessment
```bash
# Export device list to CSV first, then:
securepremium batch analyze --input-file fleet.csv --output-file fleet_risk.csv
securepremium batch quote-batch --input-file fleet.csv --output-file fleet_costs.csv
```

### 3. Network Monitoring
```bash
# Get network statistics
securepremium network stats --network-id corp_security_net

# View high-risk devices
securepremium network top-devices --network-id corp_security_net --limit 5

# Report suspicious device
securepremium network report \
  --network-id corp_security_net \
  --device-id SUSPECT-001 \
  --reputation-score 0.95 \
  --threat-level high
```

### 4. Programmatic Integration
```bash
# Get JSON output for scripting
securepremium risk assess --device-id DEV-001 --json-output | python parse_result.py

# Batch process with error handling
securepremium batch analyze --input-file devices.csv --output-file results.json --format json
```

## Advanced Options

### Sort Network Devices
```bash
# By reputation (highest first)
securepremium network top-devices --network-id org_net --sort-by reputation

# By device ID (alphabetical)
securepremium network top-devices --network-id org_net --sort-by device_id
```

### Coverage Tiers
- **basic**: Essential coverage ($500-800/year)
- **standard**: Standard coverage ($800-1200/year)
- **premium**: Comprehensive coverage ($1200-2000/year)

## Error Handling

CLI commands return appropriate exit codes:
- `0`: Success
- `1`: General error
- `2`: Invalid argument

Example error output:
```
✗ Error registering device: Device ID already exists
```

## Tips & Best Practices

1. **Batch Processing**: Use CSV for large device fleets (100+ devices)
2. **JSON Output**: Integrate with scripts using `--json-output`
3. **Network Reporting**: Keep threat intelligence current by reporting issues
4. **CSV Format**: Ensure required columns exist in input files
5. **Performance**: Process large batches in parallel using system tools

## Troubleshooting

### Command Not Found
```bash
# Ensure package is installed
pip install -e .

# Or use Python directly
python securepremium_cli.py device register --help
```

### CSV Import Issues
- Verify column names match expected format
- Ensure no special characters in device IDs
- Check numeric values are properly formatted

### Network Connection
- Verify network ID is valid
- Check device IDs exist before reporting
- Ensure reputation scores are between 0-1
