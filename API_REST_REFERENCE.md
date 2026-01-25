# Securepremium REST API Reference

**Version**: 0.1.0  
**Base URL**: `http://localhost:8000/api`  
**Status**: Production Ready

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Health Endpoints](#health-endpoints)
4. [Device Management](#device-management)
5. [Risk Assessment](#risk-assessment)
6. [Premium Calculation](#premium-calculation)
7. [Threat Intelligence](#threat-intelligence)
8. [Network Participants](#network-participants)
9. [Error Handling](#error-handling)
10. [Usage Examples](#usage-examples)

---

## Overview

The Securepremium REST API provides comprehensive device behavior analysis, risk assessment, and insurance premium calculation capabilities. All endpoints support JSON request/response bodies.

### API Response Format

All successful responses include:
```json
{
  "status_code": 200,
  "data": { /* response payload */ },
  "timestamp": "2026-01-25T12:00:00"
}
```

### Data Types

- **device_id**: Unique device identifier (string, max 255 characters)
- **risk_score**: Float between 0.0 and 1.0 (0=no risk, 1=critical risk)
- **timestamp**: ISO 8601 format datetime with milliseconds
- **currency**: USD (Base premium: $120/year)

---

## Authentication

Currently, the API does **not require authentication**. In production, JWT tokens will be required.

**Future Authentication Header**:
```
Authorization: Bearer <jwt_token>
```

---

## Health Endpoints

### Check API Health

**GET** `/health`

Returns the health status of the API server.

**Request**:
```bash
curl -X GET "http://localhost:8000/api/health"
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2026-01-25T12:00:00.000000",
  "version": "0.1.0",
  "database": "connected"
}
```

---

### Get System Statistics

**GET** `/stats`

Returns system-wide statistics including device count, assessments, threats, and participants.

**Request**:
```bash
curl -X GET "http://localhost:8000/api/stats"
```

**Response** (200 OK):
```json
{
  "total_devices": 150,
  "total_assessments": 450,
  "total_threats": 23,
  "total_participants": 8,
  "timestamp": "2026-01-25T12:00:00.000000"
}
```

---

## Device Management

### Register Device

**POST** `/devices`

Register a new device in the system.

**Request Body**:
```json
{
  "device_id": "DEVICE-ABC123",
  "fingerprint_hash": "a1b2c3d4e5f6g7h8",
  "cpu": "Intel Core i7-10700K",
  "ram": "32GB DDR4",
  "os": "Windows 11",
  "os_version": "22H2",
  "hostname": "workstation-001"
}
```

**Response** (201 Created):
```json
{
  "device_id": "DEVICE-ABC123",
  "fingerprint_hash": "a1b2c3d4e5f6g7h8",
  "cpu": "Intel Core i7-10700K",
  "ram": "32GB DDR4",
  "os": "Windows 11",
  "os_version": "22H2",
  "hostname": "workstation-001",
  "registration_date": "2026-01-25T12:00:00.000000",
  "current_risk_score": 0.0,
  "risk_level": "low",
  "is_active": true,
  "security_incidents": 0
}
```

**Errors**:
- `409 Conflict`: Device already registered
- `400 Bad Request`: Invalid device data

---

### Get Device Information

**GET** `/devices/{device_id}`

Retrieve information about a specific device.

**Request**:
```bash
curl -X GET "http://localhost:8000/api/devices/DEVICE-ABC123"
```

**Response** (200 OK):
```json
{
  "device_id": "DEVICE-ABC123",
  "fingerprint_hash": "a1b2c3d4e5f6g7h8",
  "cpu": "Intel Core i7-10700K",
  "ram": "32GB DDR4",
  "os": "Windows 11",
  "os_version": "22H2",
  "hostname": "workstation-001",
  "registration_date": "2026-01-25T12:00:00.000000",
  "current_risk_score": 0.35,
  "risk_level": "medium",
  "is_active": true,
  "security_incidents": 2
}
```

**Errors**:
- `404 Not Found`: Device does not exist

---

### List Devices

**GET** `/devices?risk_level=medium`

List all registered devices with optional filtering.

**Query Parameters**:
- `risk_level` (optional): Filter by risk level ("low", "medium", "high")

**Response** (200 OK):
```json
{
  "total": 150,
  "devices": [
    {
      "device_id": "DEVICE-ABC123",
      "fingerprint_hash": "a1b2c3d4e5f6g7h8",
      "current_risk_score": 0.35,
      "risk_level": "medium",
      "is_active": true
    },
    {
      "device_id": "DEVICE-XYZ789",
      "fingerprint_hash": "h7g6f5e4d3c2b1a0",
      "current_risk_score": 0.52,
      "risk_level": "medium",
      "is_active": true
    }
  ]
}
```

---

### Update Device

**PUT** `/devices/{device_id}`

Update device information.

**Request Body**:
```json
{
  "hostname": "workstation-001-updated",
  "cpu": "Intel Core i7-11700K"
}
```

**Response** (200 OK):
```json
{
  "device_id": "DEVICE-ABC123",
  "hostname": "workstation-001-updated",
  "cpu": "Intel Core i7-11700K",
  "current_risk_score": 0.35,
  "risk_level": "medium",
  "is_active": true
}
```

---

## Risk Assessment

### Create Risk Assessment

**POST** `/assessments`

Analyze and create a risk assessment for a device.

**Request Body**:
```json
{
  "device_id": "DEVICE-ABC123",
  "behavioral_risk": 0.25,
  "hardware_risk": 0.15,
  "network_risk": 0.30,
  "anomaly_risk": 0.20,
  "assessment_reason": "scheduled_scan",
  "confidence_score": 0.92
}
```

**Risk Component Weights**:
- Behavioral Risk: 30% (user activity, application patterns)
- Hardware Risk: 20% (firmware, drivers, physical security)
- Network Risk: 25% (connectivity, configurations, exposure)
- Anomaly Risk: 25% (unusual activity, deviations)

**Risk Score Interpretation**:
- 0.0 - 0.33: Low Risk
- 0.34 - 0.66: Medium Risk
- 0.67 - 1.0: High Risk

**Response** (201 Created):
```json
{
  "id": 1,
  "device_id": "DEVICE-ABC123",
  "risk_score": 0.2725,
  "risk_level": "low",
  "behavioral_risk": 0.25,
  "hardware_risk": 0.15,
  "network_risk": 0.30,
  "anomaly_risk": 0.20,
  "confidence_score": 0.92,
  "assessment_date": "2026-01-25T12:00:00.000000",
  "assessment_reason": "scheduled_scan"
}
```

**Errors**:
- `404 Not Found`: Device not found
- `400 Bad Request`: Invalid risk values

---

### Get Assessment History

**GET** `/assessments/{device_id}?limit=30`

Retrieve risk assessment history for a device.

**Query Parameters**:
- `limit` (optional, default: 30): Number of assessments to return

**Response** (200 OK):
```json
{
  "device_id": "DEVICE-ABC123",
  "total_assessments": 15,
  "latest_risk_score": 0.2725,
  "latest_risk_level": "low",
  "assessments": [
    {
      "id": 1,
      "risk_score": 0.2725,
      "risk_level": "low",
      "assessment_date": "2026-01-25T12:00:00.000000"
    }
  ]
}
```

---

## Premium Calculation

### Calculate Insurance Premium

**POST** `/premiums`

Calculate and create an insurance premium quote for a device.

**Request Body**:
```json
{
  "device_id": "DEVICE-ABC123",
  "risk_score": 0.35,
  "coverage_tier": "standard",
  "years": 1
}
```

**Coverage Tiers**:
- `basic`: Standard coverage, $120/year base
- `standard`: Enhanced coverage, $120/year base
- `premium`: Maximum coverage, $120/year base

**Coverage Limits by Tier** (Annual):
- Basic: $25,000 coverage limit, $1000 deductible
- Standard: $50,000 coverage limit, $500 deductible
- Premium: $100,000 coverage limit, $250 deductible

**Response** (201 Created):
```json
{
  "id": 1,
  "device_id": "DEVICE-ABC123",
  "base_premium": 120.0,
  "final_premium": 265.0,
  "coverage_tier": "standard",
  "annual_deductible": 500.0,
  "coverage_limit": 50000.0,
  "policy_start_date": "2026-01-25T00:00:00.000000",
  "policy_end_date": "2027-01-25T00:00:00.000000",
  "is_active": true
}
```

**Premium Calculation Formula**:
```
Final Premium = Base Premium × (0.5 + (Risk Score × 3.0))
```

Example with risk_score 0.35:
```
Final Premium = $120 × (0.5 + (0.35 × 3.0))
              = $120 × (0.5 + 1.05)
              = $120 × 1.55
              = $186
```

---

### Get Premium History

**GET** `/premiums/{device_id}`

Retrieve all premiums (active and historical) for a device.

**Response** (200 OK):
```json
{
  "device_id": "DEVICE-ABC123",
  "total_policies": 5,
  "active_premium": {
    "id": 5,
    "device_id": "DEVICE-ABC123",
    "final_premium": 265.0,
    "coverage_tier": "standard",
    "is_active": true,
    "policy_start_date": "2026-01-25T00:00:00.000000",
    "policy_end_date": "2027-01-25T00:00:00.000000"
  },
  "history": [
    {
      "id": 5,
      "final_premium": 265.0,
      "coverage_tier": "standard",
      "policy_start_date": "2026-01-25T00:00:00.000000"
    }
  ]
}
```

---

## Threat Intelligence

### Report Threat

**POST** `/threats`

Report a security threat detected in the network.

**Request Body**:
```json
{
  "report_id": "THREAT-20260125-001",
  "reporting_participant": "security-org-001",
  "threat_type": "malware",
  "threat_level": "high",
  "target_device_id": "DEVICE-ABC123",
  "threat_description": "Trojan.Generic detected in memory",
  "confidence_score": 0.95
}
```

**Threat Types**:
- `malware`: Malicious software
- `phishing`: Social engineering attack
- `ransomware`: Extortion software
- `intrusion`: Unauthorized access
- `data_exfiltration`: Data theft
- `exploitation`: Vulnerability exploit
- `anomalous_behavior`: Unusual activity

**Threat Levels**:
- `low`: Informational, minimal impact
- `medium`: Moderate concern, should monitor
- `high`: Significant threat, immediate action needed
- `critical`: Severe threat, emergency response required

**Response** (201 Created):
```json
{
  "id": 1,
  "report_id": "THREAT-20260125-001",
  "reporting_participant": "security-org-001",
  "threat_type": "malware",
  "threat_level": "high",
  "target_device_id": "DEVICE-ABC123",
  "threat_description": "Trojan.Generic detected in memory",
  "confidence_score": 0.95,
  "report_date": "2026-01-25T12:00:00.000000",
  "verification_status": "pending",
  "verification_count": 0
}
```

---

### Get Device Threats

**GET** `/threats/device/{device_id}`

Retrieve all threats reported for a specific device.

**Response** (200 OK):
```json
{
  "total": 3,
  "threat_level": null,
  "threats": [
    {
      "report_id": "THREAT-20260125-001",
      "threat_type": "malware",
      "threat_level": "high",
      "confidence_score": 0.95,
      "verification_status": "pending",
      "report_date": "2026-01-25T12:00:00.000000"
    }
  ]
}
```

---

### List Threats

**GET** `/threats?threat_level=high`

Retrieve threats in the network with optional filtering.

**Query Parameters**:
- `threat_level` (optional): Filter by threat level

**Response** (200 OK):
```json
{
  "total": 15,
  "threat_level": "high",
  "threats": [
    {
      "report_id": "THREAT-20260125-001",
      "threat_type": "malware",
      "threat_level": "high",
      "confidence_score": 0.95,
      "report_date": "2026-01-25T12:00:00.000000"
    }
  ]
}
```

---

## Network Participants

### Register Network Participant

**POST** `/participants`

Register an organization as a participant in the threat intelligence network.

**Request Body**:
```json
{
  "participant_id": "ORG-SECURITY-001",
  "participant_name": "Enterprise Security Team",
  "api_key": "sk-1234567890abcdefghijklmnopqrstuv"
}
```

**Response** (201 Created):
```json
{
  "participant_id": "ORG-SECURITY-001",
  "participant_name": "Enterprise Security Team",
  "is_active": true,
  "total_reports_submitted": 0,
  "total_verifications": 0,
  "reputation_score": 0.5,
  "joined_date": "2026-01-25T12:00:00.000000"
}
```

---

### Get Participant Information

**GET** `/participants/{participant_id}`

Retrieve information about a network participant.

**Response** (200 OK):
```json
{
  "participant_id": "ORG-SECURITY-001",
  "participant_name": "Enterprise Security Team",
  "is_active": true,
  "total_reports_submitted": 12,
  "total_verifications": 8,
  "reputation_score": 0.78,
  "joined_date": "2026-01-25T12:00:00.000000"
}
```

---

### List Network Participants

**GET** `/participants`

Retrieve all active participants in the network.

**Response** (200 OK):
```json
{
  "total": 8,
  "participants": [
    {
      "participant_id": "ORG-SECURITY-001",
      "participant_name": "Enterprise Security Team",
      "is_active": true,
      "reputation_score": 0.78,
      "joined_date": "2026-01-25T12:00:00.000000"
    }
  ]
}
```

---

## Error Handling

### Error Response Format

All errors return a standard error response:

```json
{
  "error": "HTTP 404",
  "detail": "Device DEVICE-ABC123 not found",
  "timestamp": "2026-01-25T12:00:00.000000",
  "request_id": null
}
```

### HTTP Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request body or parameters |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

### Common Error Scenarios

**Device Not Found**:
```json
{
  "error": "HTTP 404",
  "detail": "Device DEVICE-ABC123 not found",
  "timestamp": "2026-01-25T12:00:00.000000"
}
```

**Validation Error**:
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "behavioral_risk"],
      "msg": "ensure this value is less than or equal to 1.0",
      "input": 1.5
    }
  ]
}
```

---

## Usage Examples

### Complete Device Registration and Assessment Workflow

```bash
#!/bin/bash
API="http://localhost:8000/api"

# 1. Register device
DEVICE_ID="DEVICE-$(date +%s)"
echo "Registering device: $DEVICE_ID"
curl -X POST "$API/devices" \
  -H "Content-Type: application/json" \
  -d "{
    \"device_id\": \"$DEVICE_ID\",
    \"fingerprint_hash\": \"abc123def456\",
    \"os\": \"Windows 11\",
    \"cpu\": \"Intel i7\",
    \"ram\": \"16GB\"
  }"

# 2. Create risk assessment
echo "Creating risk assessment..."
curl -X POST "$API/assessments" \
  -H "Content-Type: application/json" \
  -d "{
    \"device_id\": \"$DEVICE_ID\",
    \"behavioral_risk\": 0.25,
    \"hardware_risk\": 0.15,
    \"network_risk\": 0.30,
    \"anomaly_risk\": 0.20
  }"

# 3. Calculate premium
echo "Calculating insurance premium..."
curl -X POST "$API/premiums" \
  -H "Content-Type: application/json" \
  -d "{
    \"device_id\": \"$DEVICE_ID\",
    \"risk_score\": 0.23,
    \"coverage_tier\": \"standard\",
    \"years\": 1
  }"

# 4. Get device summary
echo "Device summary:"
curl -X GET "$API/devices/$DEVICE_ID"
```

### Report Security Threat

```bash
curl -X POST "http://localhost:8000/api/threats" \
  -H "Content-Type: application/json" \
  -d '{
    "report_id": "THREAT-2026-001",
    "reporting_participant": "security-org",
    "threat_type": "malware",
    "threat_level": "high",
    "target_device_id": "DEVICE-ABC123",
    "confidence_score": 0.92
  }'
```

### Query System Statistics

```bash
curl -X GET "http://localhost:8000/api/stats" | python -m json.tool
```

---

## Rate Limiting

Currently not implemented. Planned for future release.

## Versioning

API version follows semantic versioning: `MAJOR.MINOR.PATCH`

Current version: `0.1.0`

## Support

For issues, bugs, or feature requests, please submit to the [GitHub repository](https://github.com/fku-sec/securepremium).

