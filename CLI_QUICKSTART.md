# Securepremium CLI - Quick Start Guide

## Overview

The Securepremium CLI provides command-line access to the Device Behavior Insurance Protocol, enabling:
- Device registration and profiling
- Real-time risk assessment
- Insurance premium quote generation
- Batch processing for multiple devices
- Network threat intelligence reporting

## Installation

```bash
# Install package with CLI
pip install -e .

# Or install from requirements
pip install -r requirements.txt
```

## Running the CLI

### Using the CLI directly:
```bash
python securepremium_cli.py --help
python securepremium_cli.py device register --help
```

### Or use the installed command:
```bash
securepremium --help
securepremium info
```

## Command Examples

### 1. Device Management

**Register a device:**
```bash
securepremium device register \
  --device-id "CORP-LAP-001" \
  --fingerprint "abc123def456" \
  --cpu "Intel Core i7" \
  --ram "16GB" \
  --os "Windows 11" \
  --version "22H2"
```

**JSON Output:**
```bash
securepremium device register \
  --device-id "CORP-LAP-001" \
  --fingerprint "abc123" \
  --json-output
```

### 2. Risk Assessment

**Assess device risk:**
```bash
securepremium risk assess \
  --device-id "CORP-LAP-001" \
  --login-failures 2 \
  --total-logins 100 \
  --tpm-status healthy
```

### 3. Premium Quotes

**Generate a quote:**
```bash
securepremium quote generate \
  --device-id "CORP-LAP-001" \
  --coverage standard
```

Coverage options: `basic`, `standard`, `premium`

### 4. Batch Processing

**Batch risk analysis:**
```bash
securepremium batch analyze \
  --input-file example_devices.csv \
  --output-file risk_results.csv
```

**Batch quote generation:**
```bash
securepremium batch quote-batch \
  --input-file example_devices.csv \
  --output-file quotes.csv \
  --coverage premium
```

### 5. Network Statistics

**Get network stats:**
```bash
securepremium network stats --network-id org_network
```

**Report device reputation:**
```bash
securepremium network report \
  --network-id org_network \
  --device-id "CORP-LAP-001" \
  --reputation-score 0.85 \
  --threat-level low
```

**View top devices:**
```bash
securepremium network top-devices \
  --network-id org_network \
  --limit 10 \
  --sort-by reputation
```

### 6. System Information

**Display system info:**
```bash
securepremium info
```

## CSV Format for Batch Processing

Required columns for `example_devices.csv`:
```
device_id,login_failures,total_logins,tpm_status,cpu_usage
CORP-LAP-001,2,100,healthy,25.5
CORP-LAP-002,0,50,healthy,10.2
```

## All Commands

```
device       - Device management operations
  register   - Register a new device

risk         - Risk assessment operations
  assess     - Assess device compromise risk

quote        - Premium quote operations
  generate   - Generate premium quote

batch        - Batch processing operations
  analyze    - Batch risk analysis
  quote-batch - Batch quote generation

network      - Network statistics and reporting
  stats      - Get network statistics
  report     - Report device reputation
  top-devices - Show top devices by reputation

info         - Display system information
--help       - Show help for any command
--version    - Show version
```

## Output Formats

All commands support:
- **Text output** (default, formatted for humans)
- **JSON output** (use `--json-output` flag for programmatic access)

## Testing

Run CLI tests:
```bash
pytest tests/test_cli.py -v
```

## Troubleshooting

**Command not found:**
```bash
python securepremium_cli.py <command>
```

**CSV import errors:**
- Check CSV has required columns
- Verify no special characters in device IDs
- Ensure numeric values are properly formatted

**JSON parsing issues:**
- Ensure all `--json-output` flags are used
- Pipe to JSON parser: `securepremium ... --json-output | python -m json.tool`

## Advanced Features

- **Batch processing** with progress bars
- **JSON integration** for automation
- **Multiple coverage tiers** for flexible pricing
- **Network threat intelligence** sharing
- **Comprehensive error handling**

## Documentation

For detailed documentation, see:
- [CLI_GUIDE.md](CLI_GUIDE.md) - Complete CLI documentation
- [README.md](README.md) - Project overview
- [example_usage.py](example_usage.py) - Python API examples
