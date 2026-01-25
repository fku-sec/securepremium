# Storage Module Quick Reference

## Installation & Setup

```python
from securepremium.storage import init_db, SchemaManager

# Initialize database
db = init_db("sqlite:///securepremium.db")
db.initialize()

# Create tables
SchemaManager.create_all_tables()

# Get session
session = db.get_session()
```

## Device Management

```python
from securepremium.storage import DeviceRepository

device_repo = DeviceRepository(session)

# Create device
device = device_repo.create(
    device_id="DEVICE-001",
    fingerprint_hash="abc123",
    cpu="Intel i7",
    ram="16GB",
    os="Windows 11"
)

# Get device
device = device_repo.get_by_id("DEVICE-001")

# Get all active
devices = device_repo.get_all_active()

# Get by risk level
high_risk = device_repo.get_by_risk_level("high")

# Update device
device_repo.update("DEVICE-001", cpu="Intel i9")

# Update risk score
device_repo.update_risk_score("DEVICE-001", 0.65, "medium")

# Delete (soft)
device_repo.delete("DEVICE-001")
```

## Risk Assessment

```python
from securepremium.storage import RiskAssessmentRepository

assessment_repo = RiskAssessmentRepository(session)

# Create assessment
assessment = assessment_repo.create(
    device_id="DEVICE-001",
    risk_score=0.65,
    risk_level="medium",
    behavioral_risk=0.3,
    hardware_risk=0.2,
    network_risk=0.25,
    anomaly_risk=0.25,
    confidence_score=0.95
)

# Get latest
latest = assessment_repo.get_latest_for_device("DEVICE-001")

# Get history
history = assessment_repo.get_history("DEVICE-001", limit=30)

# Get by level
high_risk = assessment_repo.get_by_risk_level("high")

# Get recent (7 days)
recent = assessment_repo.get_recent(days=7)
```

## Premium Management

```python
from securepremium.storage import PremiumRepository
from datetime import datetime, timedelta

premium_repo = PremiumRepository(session)

# Create premium
now = datetime.utcnow()
premium = premium_repo.create(
    device_id="DEVICE-001",
    base_premium=120.0,
    final_premium=90.0,
    coverage_tier="standard",
    annual_deductible=500.0,
    coverage_limit=50000.0,
    policy_start_date=now,
    policy_end_date=now + timedelta(days=365),
    policy_term_years=1
)

# Get active premium
active = premium_repo.get_active_for_device("DEVICE-001")

# Get history
history = premium_repo.get_history("DEVICE-001")

# Get by tier
standard = premium_repo.get_by_tier("standard")

# Renew policy
premium_repo.renew_policy(
    premium_id=premium.id,
    new_premium=95.0,
    new_end_date=now + timedelta(days=730)
)
```

## Threat Intelligence

```python
from securepremium.storage import (
    ThreatReportRepository,
    NetworkParticipantRepository
)

threat_repo = ThreatReportRepository(session)
participant_repo = NetworkParticipantRepository(session)

# Register participant
participant = participant_repo.create(
    participant_id="ORG-001",
    participant_name="Security Corp",
    api_key="secret-key"
)

# Create threat report
threat = threat_repo.create(
    report_id="THREAT-001",
    reporting_participant="ORG-001",
    threat_type="malware",
    threat_level="high",
    target_device_id="DEVICE-001",
    confidence_score=0.92
)

# Get threats for device
threats = threat_repo.get_for_device("DEVICE-001")

# Get by threat level
critical = threat_repo.get_by_threat_level("critical")

# Get unverified
unverified = threat_repo.get_unverified()

# Update verification
threat_repo.update_verification_status(
    "THREAT-001",
    status="verified",
    verification_count=5
)
```

## Network Participants

```python
participant_repo = NetworkParticipantRepository(session)

# Create participant
participant = participant_repo.create(
    participant_id="ORG-001",
    participant_name="Security Corp",
    api_key="secret-key"
)

# Get by ID
participant = participant_repo.get_by_id("ORG-001")

# Authenticate via API key
participant = participant_repo.get_by_api_key("secret-key")

# Get all active
active = participant_repo.get_all_active()

# Get top contributors
top = participant_repo.get_top_contributors(limit=10)

# Update stats
participant_repo.update_stats(
    "ORG-001",
    reports_increment=5,
    verifications_increment=3,
    reputation_adjustment=0.05
)
```

## Schema Management

```python
from securepremium.storage import SchemaManager

# Create all tables
SchemaManager.create_all_tables()

# Check table exists
exists = SchemaManager.table_exists("device_profiles")

# Get all table names
tables = SchemaManager.get_all_tables()

# Get table info
info = SchemaManager.get_table_info("device_profiles")
# Returns: columns, indexes, primary_key, foreign_keys

# Get database stats
stats = SchemaManager.get_database_stats()
# Returns: total_tables and per-table info
```

## High-Level API

```python
from securepremium.storage import StorageManager

storage = StorageManager()
storage.initialize()

# Store device
storage.store_device_assessment(
    "DEVICE-001",
    fingerprint_hash="abc123",
    cpu="Intel i7"
)

# Store risk assessment
assessment_id = storage.store_risk_score(
    device_id="DEVICE-001",
    risk_score=0.65,
    risk_level="medium",
    behavioral_risk=0.3
)

# Store premium
premium_id = storage.store_premium_quote(
    device_id="DEVICE-001",
    base_premium=120.0,
    final_premium=90.0,
    coverage_tier="standard",
    annual_deductible=500.0,
    coverage_limit=50000.0,
    years=1
)

# Store threat
storage.store_threat_report(
    report_id="THREAT-001",
    reporting_participant="ORG-001",
    threat_type="malware",
    threat_level="high",
    target_device_id="DEVICE-001"
)

# Get device summary
summary = storage.get_device_summary("DEVICE-001")
# Returns dict with device, assessments, premium, threats

# Get database stats
stats = storage.get_database_stats()
```

## Configuration

### SQLite (Development)
```python
db = init_db("sqlite:///securepremium.db")
```

### PostgreSQL (Production)
```python
db = init_db("postgresql+psycopg2://user:pass@localhost/dbname")
```

### Environment Variable
```python
import os
db_url = os.getenv("DATABASE_URL", "sqlite:///securepremium.db")
db = init_db(db_url)
```

## Common Patterns

### Create and Close Session
```python
session = db.get_session()
try:
    # Use repositories
    repo = DeviceRepository(session)
    device = repo.get_by_id("DEVICE-001")
finally:
    session.close()
```

### Batch Operations
```python
session = db.get_session()
device_repo = DeviceRepository(session)

for device_id in device_ids:
    device = device_repo.create(device_id=device_id, ...)

session.commit()
session.close()
```

### Transaction Handling
```python
session = db.get_session()
try:
    # Multiple operations
    device_repo.create(...)
    assessment_repo.create(...)
    session.commit()
except Exception as e:
    session.rollback()
    raise
finally:
    session.close()
```

## Data Models Reference

### DeviceProfile
- device_id (unique)
- fingerprint_hash
- cpu, ram, os, os_version, hostname
- registration_date
- current_risk_score, risk_level
- is_active
- security_incidents

### RiskAssessment
- device_id (foreign key)
- assessment_date
- risk_score, risk_level
- behavioral_risk, hardware_risk, network_risk, anomaly_risk
- confidence_score
- assessment_reason

### PremiumRecord
- device_id (foreign key)
- base_premium, final_premium
- coverage_tier
- annual_deductible, coverage_limit
- policy_start_date, policy_end_date
- is_active

### ThreateReport
- report_id (unique)
- reporting_participant
- target_device_id (foreign key)
- threat_type, threat_level
- confidence_score
- verification_status

### ReportVerification
- report_id (foreign key)
- verifier_participant
- verification_type
- verification_date

### NetworkParticipant
- participant_id (unique)
- participant_name
- api_key (unique)
- is_active
- total_reports_submitted
- reputation_score

## Testing

```bash
# Run all storage tests
pytest tests/test_storage.py -v

# Run specific test class
pytest tests/test_storage.py::TestDeviceRepository -v

# Run with coverage
pytest tests/test_storage.py --cov=securepremium.storage

# Quiet mode
pytest tests/test_storage.py -q
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Database not initialized" | Call `db.initialize()` before using |
| "UNIQUE constraint failed" | Check for duplicate IDs, use update() instead |
| "Connection pool overflow" | Always close sessions with `session.close()` |
| "No table named..." | Call `SchemaManager.create_all_tables()` |
| "No module named sqlalchemy" | Install: `pip install sqlalchemy` |

## Performance Tips

1. Use session context managers
2. Close sessions promptly
3. Use batch operations for multiple records
4. Limit query results with parameters
5. Use indexes for frequent queries
6. Consider caching for read-heavy workloads

## Files

- `securepremium/storage/database.py` - Database configuration
- `securepremium/storage/models.py` - ORM models
- `securepremium/storage/repositories.py` - Data access
- `securepremium/storage/schema.py` - Schema management
- `securepremium/storage/utils.py` - High-level API
- `securepremium/storage/__init__.py` - Module exports
- `tests/test_storage.py` - Test suite
- `example_storage_simple.py` - Working examples
