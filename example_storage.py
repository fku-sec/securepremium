"""
Storage Module Integration Example

This example demonstrates how to use the Securepremium storage module
to persist device data, risk assessments, premiums, and threat intelligence.
"""

import os
import sys
from datetime import datetime, timedelta

from securepremium.storage import (
    init_db,
    SchemaManager,
    DeviceRepository,
    RiskAssessmentRepository,
    PremiumRepository,
    ThreatReportRepository,
    NetworkParticipantRepository,
    StorageManager,
)
from securepremium.core.risk_calculator import RiskCalculator
from securepremium.core.premium_engine import PremiumEngine

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def example_1_basic_device_storage():
    """Example 1: Basic device registration and storage."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Device Registration and Storage")
    print("="*70)
    
    # Initialize database
    db = init_db("sqlite:///securepremium_example.db")
    SchemaManager.create_all_tables()
    print("[OK] Database initialized")
    
    # Create device repository
    session = db.get_session()
    device_repo = DeviceRepository(session)
    
    # Register multiple devices
    devices = [
        {
            "device_id": "CORP-LAPTOP-001",
            "fingerprint_hash": "a1b2c3d4e5f6",
            "cpu": "Intel Core i7-12700K",
            "ram": "16GB DDR5",
            "os": "Windows 11 Pro",
            "os_version": "22621.1344",
            "hostname": "john-laptop",
        },
        {
            "device_id": "CORP-SERVER-001",
            "fingerprint_hash": "f6e5d4c3b2a1",
            "cpu": "Intel Xeon Gold 6348",
            "ram": "64GB DDR4",
            "os": "Ubuntu Linux 22.04",
            "os_version": "22.04.1 LTS",
            "hostname": "mail-server",
        },
    ]
    
    for device_info in devices:
        device = device_repo.create(**device_info)
        print(f"[OK] Device registered: {device.device_id}")
    
    # Query devices
    active_devices = device_repo.get_all_active()
    print(f"\nTotal active devices: {len(active_devices)}")
    for device in active_devices:
        print(f"  - {device.device_id}: {device.hostname} ({device.os})")
    
    session.close()


def example_2_risk_assessments():
    """Example 2: Store and retrieve risk assessments."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Risk Assessment Storage")
    print("="*70)
    
    db = init_db("sqlite:///securepremium_example.db")
    session = db.get_session()
    
    device_repo = DeviceRepository(session)
    assessment_repo = RiskAssessmentRepository(session)
    risk_calc = RiskCalculator()
    
    # Get a device
    device = device_repo.get_by_id("CORP-LAPTOP-001")
    print(f"Assessing device: {device.device_id}")
    
    # Simulate multiple assessments over time
    base_score = 0.4
    for i in range(3):
        # Create assessment data
        device_data = {
            "device_id": device.device_id,
            "os": device.os,
            "last_update": datetime.utcnow() - timedelta(days=i*7),
            "software_patches_applied": 20 - i*2,
            "known_vulnerabilities": i * 2,
            "failed_login_attempts": i * 5,
        }
        
        # Calculate risk
        risk_score = base_score + (i * 0.1)
        risk_level = "low" if risk_score < 0.33 else "medium" if risk_score < 0.66 else "high"
        
        # Store assessment
        assessment = assessment_repo.create(
            device_id=device.device_id,
            risk_score=risk_score,
            risk_level=risk_level,
            behavioral_risk=risk_score * 0.3,
            hardware_risk=risk_score * 0.2,
            network_risk=risk_score * 0.25,
            anomaly_risk=risk_score * 0.25,
            assessment_reason="scheduled",
            confidence_score=0.95,
        )
        print(f"✓ Assessment {i+1}: Risk {risk_score:.2f} ({risk_level})")
    
    # Get latest assessment
    latest = assessment_repo.get_latest_for_device(device.device_id)
    print(f"\nLatest assessment: {latest.risk_score:.2f} ({latest.risk_level})")
    
    # Get assessment history
    history = assessment_repo.get_history(device.device_id)
    print(f"Total assessments stored: {len(history)}")
    
    # Update device with current risk
    device_repo.update_risk_score(
        device.device_id,
        latest.risk_score,
        latest.risk_level
    )
    print(f"✓ Device risk updated: {latest.risk_score:.2f}")
    
    session.close()


def example_3_premium_policies():
    """Example 3: Store and manage insurance premiums."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Premium Policy Storage")
    print("="*70)
    
    db = init_db("sqlite:///securepremium_example.db")
    session = db.get_session()
    
    device_repo = DeviceRepository(session)
    assessment_repo = RiskAssessmentRepository(session)
    premium_repo = PremiumRepository(session)
    
    # Get devices and calculate premiums
    devices = device_repo.get_all_active()
    
    for device in devices:
        latest_assessment = assessment_repo.get_latest_for_device(device.device_id)
        
        if latest_assessment:
            # Calculate premium directly
            base = 120.0
            risk_multiplier = 0.5 + (latest_assessment.risk_score * 3.0)
            final = base * risk_multiplier
            tier = "standard" if latest_assessment.risk_score < 0.7 else "premium"
            
            # Store premium
            now = datetime.utcnow()
            premium = premium_repo.create(
                device_id=device.device_id,
                base_premium=base,
                final_premium=final,
                coverage_tier=tier,
                annual_deductible=500.0,
                coverage_limit=50000.0,
                policy_start_date=now,
                policy_end_date=now + timedelta(days=365),
            )
            
            print(f"✓ Premium created for {device.device_id}")
            print(f"  Base: ${base:.2f}")
            print(f"  Final: ${final:.2f}")
            print(f"  Tier: {tier}")
    
    session.close()


def example_4_threat_intelligence():
    """Example 4: Threat report storage and network management."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Threat Intelligence Network")
    print("="*70)
    
    db = init_db("sqlite:///securepremium_example.db")
    session = db.get_session()
    
    threat_repo = ThreatReportRepository(session)
    participant_repo = NetworkParticipantRepository(session)
    
    # Register network participants
    participants = [
        ("CORP-SEC", "Corporate Security Team"),
        ("THREAT-INTEL", "Global Threat Intelligence"),
        ("ISP-PROVIDER", "Internet Service Provider"),
    ]
    
    for participant_id, name in participants:
        participant_repo.create(
            participant_id=participant_id,
            participant_name=name,
            api_key=f"api-key-{participant_id.lower()}"
        )
        print(f"✓ Registered participant: {name}")
    
    # Submit threat reports
    print("\nSubmitting threat reports...")
    threats = [
        {
            "report_id": "THREAT-2024-001",
            "reporting_participant": "THREAT-INTEL",
            "threat_type": "malware",
            "threat_level": "high",
            "target_device_id": "CORP-LAPTOP-001",
            "threat_description": "Trojan.GenericKD detected",
            "confidence_score": 0.92,
        },
        {
            "report_id": "THREAT-2024-002",
            "reporting_participant": "CORP-SEC",
            "threat_type": "phishing",
            "threat_level": "medium",
            "target_device_id": "CORP-SERVER-001",
            "threat_description": "Phishing email campaign targeting domain",
            "confidence_score": 0.78,
        },
    ]
    
    for threat in threats:
        threat_repo.create(**threat)
        print(f"✓ Threat report: {threat['report_id']}")
    
    # Get threats for device
    device_threats = threat_repo.get_for_device("CORP-LAPTOP-001")
    print(f"\nThreats for CORP-LAPTOP-001: {len(device_threats)}")
    for threat in device_threats:
        print(f"  - {threat.threat_type} ({threat.threat_level}): {threat.threat_description}")
    
    session.close()


def example_5_storage_manager():
    """Example 5: Using high-level StorageManager interface."""
    print("\n" + "="*70)
    print("EXAMPLE 5: High-Level Storage Manager")
    print("="*70)
    
    db = init_db("sqlite:///securepremium_example.db")
    storage = StorageManager()
    storage.initialize()
    
    # Get device summary
    print("\nDevice Summary for CORP-LAPTOP-001:")
    summary = storage.get_device_summary("CORP-LAPTOP-001")
    
    if summary:
        print(f"  Device ID: {summary['device']['id']}")
        print(f"  Hostname: {summary['device']['hostname']}")
        print(f"  OS: {summary['device']['os']}")
        print(f"  Risk Score: {summary['device']['current_risk_score']:.2f}")
        print(f"  Risk Level: {summary['device']['risk_level']}")
        
        print(f"\n  Recent Assessments: {len(summary['recent_assessments'])}")
        for i, assessment in enumerate(summary['recent_assessments'][:3]):
            print(f"    {i+1}. Score: {assessment['score']:.2f} ({assessment['level']})")
        
        print(f"\n  Threats: {len(summary['threats'])}")
        for threat in summary['threats']:
            print(f"    - {threat['type']} ({threat['level']})")
    
    # Get database statistics
    print("\nDatabase Statistics:")
    stats = storage.get_database_stats()
    print(f"  Total tables: {stats['total_tables']}")
    for table_name, table_info in stats['tables'].items():
        print(f"  - {table_name}: {table_info['column_count']} columns")


def cleanup():
    """Clean up example database."""
    import time
    if os.path.exists("securepremium_example.db"):
        try:
            time.sleep(0.5)  # Allow connections to close
            os.remove("securepremium_example.db")
            print("✓ Cleaned up example database")
        except PermissionError:
            print("⚠ Could not delete database file (file still in use)")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("SECUREPREMIUM STORAGE MODULE EXAMPLES")
    print("="*70)
    
    # Clean up old database first
    if os.path.exists("securepremium_example.db"):
        try:
            os.remove("securepremium_example.db")
            print("✓ Removed old database")
        except:
            pass
    
    try:
        example_1_basic_device_storage()
        example_2_risk_assessments()
        example_3_premium_policies()
        example_4_threat_intelligence()
        example_5_storage_manager()
        
        print("\n" + "="*70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*70)
        
    finally:
        cleanup()
