# Storage Module Documentation

## Overview

The Securepremium Storage Module provides a complete data persistence layer for the Device Behavior Insurance Protocol. It enables organizations to store, retrieve, and manage:

- **Device Profiles** - Hardware fingerprints and device information
- **Risk Assessments** - Historical risk scores and evaluations
- **Insurance Premiums** - Policy records and pricing information
- **Threat Intelligence** - Reported threats and verification records
- **Network Participants** - Reputation network member management

## Features

### Multi-Backend Database Support
- **SQLite** - Default for development and testing (file-based)
- **PostgreSQL** - Production deployments with advanced features
- **Easy Extension** - Add support for MySQL, Oracle, etc.

### Data Models

#### DeviceProfile
Stores complete device information:
- Device ID and hardware fingerprint
- CPU, RAM, OS information
- Current risk score and level
- Device activity and security metrics

#### RiskAssessment
Records historical risk evaluations:
- Risk scores (0-1 scale)
- Component-based risk breakdown
- Assessment confidence levels
- Timestamp and assessment context

#### PremiumRecord
Manages insurance policies:
- Base and final premium amounts
- Coverage tier (basic, standard, premium)
- Policy dates and deductible info
- Renewal tracking

#### ThreateReport
Stores threat intelligence:
- Threat type and severity level
- Reporting participant information
- Verification and dispute counts
- Target device linkage

#### NetworkParticipant
Manages reputation network members:
- Participant credentials
- Statistics on reports and verifications
- Reputation scores
- API key management

### Repository Pattern

Access data through specialized repository classes:

```python
from securepremium.storage import (
    DeviceRepository,
    RiskAssessmentRepository,
    PremiumRepository,
    ThreatReportRepository,
    NetworkParticipantRepository,
)

session = db.get_session()
device_repo = DeviceRepository(session)
devices = device_repo.get_all_active()
```

### High-Level Storage Manager

Simplified interface for common operations:

```python
from securepremium.storage import StorageManager

storage = StorageManager()
storage.initialize()

# Store assessment result
storage.store_risk_score("DEVICE-001", 0.65, "medium", ...)

# Get complete device summary
summary = storage.get_device_summary("DEVICE-001")

# Store premium quote
storage.store_premium_quote("DEVICE-001", 120.0, 90.0, "standard", ...)
```

## Installation

### Prerequisites
- Python 3.10+
- SQLAlchemy 2.0+
- Device-fingerprinting-pro
- Pydantic

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from securepremium.storage import SchemaManager; SchemaManager.create_all_tables()"
```

## Usage Examples

### Example 1: Basic Device Registration

```python
from securepremium.storage import init_db, DeviceRepository, SchemaManager

# Initialize database
db = init_db("sqlite:///securepremium.db")
SchemaManager.create_all_tables()

# Register device
session = db.get_session()
device_repo = DeviceRepository(session)

device = device_repo.create(
    device_id="LAPTOP-001",
    fingerprint_hash="abc123def456",
    cpu="Intel i7",
    ram="16GB",
    os="Windows 11",
    hostname="john-laptop"
)

session.close()
```

### Example 2: Store Risk Assessment

```python
from securepremium.storage import RiskAssessmentRepository

session = db.get_session()
assessment_repo = RiskAssessmentRepository(session)

assessment = assessment_repo.create(
    device_id="LAPTOP-001",
    risk_score=0.65,
    risk_level="medium",
    behavioral_risk=0.3,
    hardware_risk=0.2,
    network_risk=0.25,
    anomaly_risk=0.25,
    confidence_score=0.95
)

# Get latest assessment
latest = assessment_repo.get_latest_for_device("LAPTOP-001")
print(f"Risk: {latest.risk_score} ({latest.risk_level})")

session.close()
```

### Example 3: Manage Insurance Premiums

```python
from securepremium.storage import PremiumRepository
from datetime import datetime, timedelta

session = db.get_session()
premium_repo = PremiumRepository(session)

now = datetime.utcnow()
premium = premium_repo.create(
    device_id="LAPTOP-001",
    base_premium=120.0,
    final_premium=90.0,
    coverage_tier="standard",
    annual_deductible=500.0,
    coverage_limit=50000.0,
    policy_start_date=now,
    policy_end_date=now + timedelta(days=365)
)

# Renew existing policy
premium_repo.renew_policy(
    premium_id=premium.id,
    new_premium=95.0,
    new_end_date=now + timedelta(days=730)
)

session.close()
```

### Example 4: Threat Intelligence Network

```python
from securepremium.storage import (
    ThreatReportRepository,
    NetworkParticipantRepository
)

session = db.get_session()
threat_repo = ThreatReportRepository(session)
participant_repo = NetworkParticipantRepository(session)

# Register network participant
participant = participant_repo.create(
    participant_id="ORG-001",
    participant_name="Security Corp",
    api_key="secret-api-key"
)

# Submit threat report
report = threat_repo.create(
    report_id="THREAT-001",
    reporting_participant="ORG-001",
    threat_type="malware",
    threat_level="high",
    target_device_id="LAPTOP-001",
    threat_description="Detected Trojan.Generic",
    confidence_score=0.92
)

# Verify report
threat_repo.update_verification_status(
    report_id="THREAT-001",
    status="verified",
    verification_count=5
)

session.close()
```

### Example 5: High-Level Storage Manager

```python
from securepremium.storage import StorageManager

storage = StorageManager()
storage.initialize()

# Store complete device assessment
storage.store_device_assessment(
    "DEVICE-001",
    fingerprint_hash="abc123",
    cpu="Intel i7",
    os="Windows 11"
)

# Store risk assessment
assessment_id = storage.store_risk_score(
    device_id="DEVICE-001",
    risk_score=0.65,
    risk_level="medium",
    behavioral_risk=0.3
)

# Store premium quote
premium_id = storage.store_premium_quote(
    device_id="DEVICE-001",
    base_premium=120.0,
    final_premium=90.0,
    coverage_tier="standard",
    annual_deductible=500.0,
    coverage_limit=50000.0,
    years=1
)

# Get device summary
summary = storage.get_device_summary("DEVICE-001")
print(f"Device: {summary['device']['id']}")
print(f"Risk Level: {summary['device']['risk_level']}")
print(f"Threats: {len(summary['threats'])}")
```

## Database Configuration

### SQLite (Development)

```python
from securepremium.storage import init_db

# File-based database
db = init_db("sqlite:///securepremium.db")
db.initialize()
```

### PostgreSQL (Production)

```python
from securepremium.storage import init_db

# PostgreSQL connection
db = init_db("postgresql+psycopg2://user:password@localhost/securepremium")
db.initialize()
```

### Environment Variables

```bash
# Set database URL via environment
export DATABASE_URL="postgresql+psycopg2://user:pass@localhost/db"

# Python code will use this automatically
db = init_db()  # Uses DATABASE_URL
```

## Schema Management

### Create Tables

```python
from securepremium.storage import SchemaManager

SchemaManager.create_all_tables()
```

### Check Table Existence

```python
if SchemaManager.table_exists("device_profiles"):
    print("Table exists!")
```

### Get Database Statistics

```python
stats = SchemaManager.get_database_stats()
print(f"Total tables: {stats['total_tables']}")
for table_name, info in stats['tables'].items():
    print(f"  {table_name}: {info['column_count']} columns")
```

### Inspect Table Structure

```python
table_info = SchemaManager.get_table_info("device_profiles")
print(f"Columns: {table_info['columns']}")
print(f"Indexes: {table_info['indexes']}")
print(f"Foreign Keys: {table_info['foreign_keys']}")
```

## Testing

Run comprehensive tests:

```bash
pytest tests/test_storage.py -v

# Run specific test class
pytest tests/test_storage.py::TestDeviceRepository -v

# Run with coverage
pytest tests/test_storage.py --cov=securepremium.storage
```

## Performance Considerations

### Indexing
- Device profiles indexed by device_id and risk_level
- Risk assessments indexed by device and date
- Threat reports indexed by threat level and device
- Improves query performance for high-volume operations

### Connection Pooling
- SQLAlchemy manages connection pools automatically
- Production PostgreSQL deployments benefit from pooling
- Configure via DATABASE_URL parameters

### Batch Operations
- Use repositories for efficient batch inserts
- SQLAlchemy handles transaction management
- Better performance for large data imports

## Troubleshooting

### Issue: "Database not initialized"
**Solution:** Call `initialize()` before using sessions:
```python
db = init_db()
db.initialize()  # Required!
```

### Issue: "UNIQUE constraint failed"
**Solution:** Check for duplicate device IDs or report IDs:
```python
if device_repo.get_by_id("DEVICE-001"):
    device = device_repo.update("DEVICE-001", **updates)
else:
    device = device_repo.create("DEVICE-001", **data)
```

### Issue: "Connection pool overflow"
**Solution:** Ensure sessions are closed properly:
```python
session = db.get_session()
try:
    # Use session
    pass
finally:
    session.close()  # Always close!
```

## API Reference

### DeviceRepository
- `create()` - Create new device
- `get_by_id()` - Retrieve device by ID
- `get_all_active()` - Get all active devices
- `get_by_risk_level()` - Filter by risk level
- `update()` - Update device properties
- `update_risk_score()` - Update risk metrics
- `delete()` - Soft delete (mark inactive)

### RiskAssessmentRepository
- `create()` - Create new assessment
- `get_latest_for_device()` - Get most recent
- `get_history()` - Get assessment history
- `get_by_risk_level()` - Filter by risk level
- `get_recent()` - Get recent assessments

### PremiumRepository
- `create()` - Create new premium record
- `get_active_for_device()` - Get current policy
- `get_history()` - Get all policies
- `get_by_tier()` - Filter by coverage tier
- `renew_policy()` - Renew existing policy

### ThreatReportRepository
- `create()` - Create new threat report
- `get_by_id()` - Retrieve by report ID
- `get_for_device()` - Get threats for device
- `get_by_threat_level()` - Filter by level
- `get_unverified()` - Get pending reports
- `update_verification_status()` - Update status

### NetworkParticipantRepository
- `create()` - Create participant
- `get_by_id()` - Retrieve by ID
- `get_by_api_key()` - Authenticate participant
- `get_all_active()` - Get active members
- `get_top_contributors()` - Get top reporters
- `update_stats()` - Update statistics

## Files

- `securepremium/storage/database.py` - Database configuration and connections
- `securepremium/storage/models.py` - SQLAlchemy ORM models
- `securepremium/storage/repositories.py` - Data access layer
- `securepremium/storage/schema.py` - Schema management utilities
- `securepremium/storage/utils.py` - High-level storage interface
- `tests/test_storage.py` - Comprehensive test suite
- `example_storage_simple.py` - Usage examples

## Contributing

To extend the storage module:

1. Add new models to `models.py`
2. Create repository class in `repositories.py`
3. Add tests in `tests/test_storage.py`
4. Update `__init__.py` exports

## Support

For issues or questions:
- Review test examples in `test_storage.py`
- Check example usage in `example_storage_simple.py`
- Review API Reference in documentation
