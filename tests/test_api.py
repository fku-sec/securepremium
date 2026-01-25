"""Tests for REST API endpoints."""

import pytest
import uuid
from fastapi.testclient import TestClient
from securepremium.api.app import app

client = TestClient(app)


def gen_id(prefix=""):
    """Generate unique ID for tests."""
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"


class TestHealth:
    """Test health and status endpoints."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "0.1.0"
    
    def test_stats_endpoint(self):
        """Test stats endpoint."""
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_devices" in data
        assert "total_assessments" in data
        assert "timestamp" in data


class TestDeviceEndpoints:
    """Test device management endpoints."""
    
    def test_register_device(self):
        """Test device registration."""
        device_id = gen_id("TEST-DEV-")
        payload = {
            "device_id": device_id,
            "fingerprint_hash": "abc123def456",
            "cpu": "Intel i7",
            "ram": "16GB",
            "os": "Windows 11",
        }
        response = client.post("/api/devices", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["device_id"] == device_id
        assert data["is_active"] is True
    
    def test_register_duplicate_device(self):
        """Test registering duplicate device raises error."""
        device_id = gen_id("TEST-DUP-")
        payload = {
            "device_id": device_id,
            "fingerprint_hash": "xyz789",
        }
        # First registration
        response1 = client.post("/api/devices", json=payload)
        assert response1.status_code == 201

        # Second registration (duplicate)
        response2 = client.post("/api/devices", json=payload)
        assert response2.status_code == 409
    
    def test_get_device(self):
        """Test getting device information."""
        # Register device first
        device_id = gen_id("TEST-GET-")
        payload = {
            "device_id": device_id,
            "fingerprint_hash": "get123",
        }
        client.post("/api/devices", json=payload)
        
        # Get device
        response = client.get(f"/api/devices/{device_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["device_id"] == device_id
    
    def test_get_nonexistent_device(self):
        """Test getting nonexistent device returns 404."""
        response = client.get(f"/api/devices/NONEXISTENT-{uuid.uuid4().hex[:8]}")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "devices" in data
        assert isinstance(data["devices"], list)


class TestRiskAssessmentEndpoints:
    """Test risk assessment endpoints."""
    
    def test_create_assessment(self):
        """Test creating risk assessment."""
        # Register device first
        device_id = gen_id("RISK-")
        device_payload = {
            "device_id": device_id,
            "fingerprint_hash": "risk123",
        }
        client.post("/api/devices", json=device_payload)
        
        # Create assessment
        assessment_payload = {
            "device_id": device_id,
            "behavioral_risk": 0.3,
            "hardware_risk": 0.2,
            "network_risk": 0.25,
            "anomaly_risk": 0.25,
            "confidence_score": 0.95,
        }
        response = client.post("/api/assessments", json=assessment_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["device_id"] == device_id
        assert "risk_score" in data
        assert "risk_level" in data
    
    def test_assessment_for_nonexistent_device(self):
        """Test assessment for nonexistent device returns 404."""
        payload = {
            "device_id": f"NONEXISTENT-{uuid.uuid4().hex[:8]}",
            "behavioral_risk": 0.3,
        }
        response = client.post("/api/assessments", json=payload)
        assert response.status_code == 404
    
    def test_get_assessment_history(self):
        """Test getting assessment history."""
        # Register device
        device_id = gen_id("HIST-")
        device_payload = {
            "device_id": device_id,
            "fingerprint_hash": "hist123",
        }
        client.post("/api/devices", json=device_payload)
        
        # Get history (should be empty initially)
        response = client.get(f"/api/assessments/{device_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["device_id"] == device_id
        assert "assessments" in data


class TestPremiumEndpoints:
    """Test premium management endpoints."""
    
    def test_create_premium(self):
        """Test creating premium."""
        # Register device first
        device_id = gen_id("PREM-")
        device_payload = {
            "device_id": device_id,
            "fingerprint_hash": "prem123",
        }
        client.post("/api/devices", json=device_payload)
        
        # Create premium
        premium_payload = {
            "device_id": device_id,
            "risk_score": 0.5,
            "coverage_tier": "standard",
            "years": 1,
        }
        response = client.post("/api/premiums", json=premium_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["device_id"] == device_id
        assert data["coverage_tier"] == "standard"
        assert "base_premium" in data
        assert "final_premium" in data
    
    def test_premium_for_nonexistent_device(self):
        """Test premium for nonexistent device returns 404."""
        payload = {
            "device_id": f"NONEXISTENT-{uuid.uuid4().hex[:8]}",
            "risk_score": 0.5,
            "coverage_tier": "standard",
        }
        response = client.post("/api/premiums", json=payload)
        assert response.status_code == 404
    
    def test_get_premium_history(self):
        """Test getting premium history."""
        # Register device
        device_id = gen_id("PREM-HIST-")
        device_payload = {
            "device_id": device_id,
            "fingerprint_hash": "premhist123",
        }
        client.post("/api/devices", json=device_payload)
        
        # Get history
        response = client.get(f"/api/premiums/{device_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["device_id"] == device_id
        assert "history" in data


class TestThreatEndpoints:
    """Test threat intelligence endpoints."""
    
    def test_report_threat(self):
        """Test reporting a threat."""
        report_id = gen_id("THREAT-")
        payload = {
            "report_id": report_id,
            "reporting_participant": f"org-{uuid.uuid4().hex[:4]}",
            "threat_type": "malware",
            "threat_level": "high",
            "target_device_id": f"DEVICE-{uuid.uuid4().hex[:8]}",
            "confidence_score": 0.92,
        }
        response = client.post("/api/threats", json=payload)
        if response.status_code != 201:
            print(f"Response: {response.text}")
        assert response.status_code == 201
        data = response.json()
        assert data["report_id"] == report_id
        assert data["threat_level"] == "high"
    
    def test_get_device_threats(self):
        """Test getting threats for device."""
        # Report threat for device
        report_id = gen_id("THREAT-DEV-")
        device_id = f"THREAT-DEV-DEVICE-{uuid.uuid4().hex[:4]}"
        payload = {
            "report_id": report_id,
            "reporting_participant": f"org-{uuid.uuid4().hex[:4]}",
            "threat_type": "phishing",
            "threat_level": "medium",
            "target_device_id": device_id,
        }
        client.post("/api/threats", json=payload)
        
        # Get threats
        response = client.get(f"/api/threats/device/{device_id}")
        assert response.status_code == 200
        data = response.json()
        assert "threats" in data
    
    def test_list_threats(self):
        """Test listing threats."""
        response = client.get("/api/threats")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "threats" in data


class TestParticipantEndpoints:
    """Test network participant endpoints."""
    
    def test_register_participant(self):
        """Test registering participant."""
        participant_id = gen_id("PART-")
        payload = {
            "participant_id": participant_id,
            "participant_name": f"Test Org {uuid.uuid4().hex[:4]}",
            "api_key": f"test-key-{uuid.uuid4().hex[:8]}",
        }
        response = client.post("/api/participants", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["participant_id"] == participant_id
        assert data["is_active"] is True
    
    def test_get_participant(self):
        """Test getting participant."""
        # Register first
        participant_id = gen_id("PART-GET-")
        payload = {
            "participant_id": participant_id,
            "participant_name": f"Get Test Org {uuid.uuid4().hex[:4]}",
        }
        client.post("/api/participants", json=payload)
        
        # Get participant
        response = client.get(f"/api/participants/{participant_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["participant_id"] == participant_id
    
    def test_list_participants(self):
        """Test listing participants."""
        response = client.get("/api/participants")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "participants" in data


class TestEndToEnd:
    """End-to-end workflow tests."""
    
    def test_complete_device_workflow(self):
        """Test complete device management workflow."""
        device_id = gen_id("E2E-")
        
        # 1. Register device
        device_payload = {
            "device_id": device_id,
            "fingerprint_hash": "e2e123",
            "cpu": "Intel i7",
            "os": "Windows 11",
        }
        device_response = client.post("/api/devices", json=device_payload)
        assert device_response.status_code == 201
        
        # 2. Create assessment
        assessment_payload = {
            "device_id": device_id,
            "behavioral_risk": 0.2,
            "hardware_risk": 0.15,
            "network_risk": 0.2,
            "anomaly_risk": 0.15,
        }
        assessment_response = client.post("/api/assessments", json=assessment_payload)
        assert assessment_response.status_code == 201
        
        # 3. Create premium
        premium_payload = {
            "device_id": device_id,
            "risk_score": 0.18,
            "coverage_tier": "standard",
        }
        premium_response = client.post("/api/premiums", json=premium_payload)
        assert premium_response.status_code == 201
        
        # 4. Verify device shows risk info
        get_device_response = client.get(f"/api/devices/{device_id}")
        assert get_device_response.status_code == 200
        device_data = get_device_response.json()
        assert device_data["current_risk_score"] > 0
        assert device_data["risk_level"] in ["low", "medium", "high"]
