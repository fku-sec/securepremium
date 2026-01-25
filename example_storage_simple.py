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

# Set UTF-8 encoding for Windows
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def example_1_basic_device_storage():
    """Example 1: Basic device registration and storage."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Device Registration and Storage")
    print("="*70)
    
    db = init_db("sqlite:///securepremium_example.db")
    SchemaManager.create_all_tables()
    print("[OK] Database initialized")
    
    session = db.get_session()
    device_repo = DeviceRepository(session)
    
    devices = [
        {
            "device_id": "CORP-LAPTOP-001",
            "fingerprint_hash": "a1b2c3d4e5f6",
            "cpu": "Intel Core i7",
            "ram": "16GB DDR5",
            "os": "Windows 11",
            "os_version": "22621",
            "hostname": "john-laptop",
        },
        {
            "device_id": "CORP-SERVER-001",
            "fingerprint_hash": "f6e5d4c3b2a1",
            "cpu": "Intel Xeon",
            "ram": "64GB DDR4",
            "os": "Ubuntu 22.04",
            "os_version": "22.04.1",
            "hostname": "mail-server",
        },
    ]
    
    for device_info in devices:
        device = device_repo.create(**device_info)
        print(f"[OK] Device registered: {device.device_id}")
    
    active_devices = device_repo.get_all_active()
    print(f"\nTotal active devices: {len(active_devices)}")
    for device in active_devices:
        print(f"  - {device.device_id}: {device.hostname}")
    
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
    
    device = device_repo.get_by_id("CORP-LAPTOP-001")
    print(f"Assessing device: {device.device_id}")
    
    for i in range(3):
        risk_score = 0.4 + (i * 0.1)
        risk_level = "low" if risk_score < 0.33 else "medium" if risk_score < 0.66 else "high"
        
        assessment_repo.create(
            device_id=device.device_id,
            risk_score=risk_score,
            risk_level=risk_level,
            behavioral_risk=risk_score * 0.3,
            hardware_risk=risk_score * 0.2,
            network_risk=risk_score * 0.25,
            anomaly_risk=risk_score * 0.25,
            confidence_score=0.95,
        )
        print(f"[OK] Assessment {i+1}: Risk {risk_score:.2f} ({risk_level})")
    
    latest = assessment_repo.get_latest_for_device(device.device_id)
    print(f"\nLatest assessment: {latest.risk_score:.2f} ({latest.risk_level})")
    
    history = assessment_repo.get_history(device.device_id)
    print(f"Total assessments stored: {len(history)}")
    
    device_repo.update_risk_score(device.device_id, latest.risk_score, latest.risk_level)
    print(f"[OK] Device risk updated: {latest.risk_score:.2f}")
    
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
    
    devices = device_repo.get_all_active()
    
    for device in devices:
        latest_assessment = assessment_repo.get_latest_for_device(device.device_id)
        
        if latest_assessment:
            base = 120.0
            risk_multiplier = 0.5 + (latest_assessment.risk_score * 3.0)
            final = base * risk_multiplier
            tier = "standard" if latest_assessment.risk_score < 0.7 else "premium"
            
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
            
            print(f"[OK] Premium for {device.device_id}")
            print(f"  Base: ${base:.2f}, Final: ${final:.2f}, Tier: {tier}")
    
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
    
    participants = [
        ("CORP-SEC", "Corporate Security"),
        ("THREAT-INTEL", "Threat Intelligence"),
        ("ISP-PROVIDER", "ISP"),
    ]
    
    for participant_id, name in participants:
        participant_repo.create(
            participant_id=participant_id,
            participant_name=name,
            api_key=f"api-{participant_id}"
        )
        print(f"[OK] Registered: {name}")
    
    print("\nSubmitting threat reports...")
    threats = [
        {
            "report_id": "THREAT-2024-001",
            "reporting_participant": "THREAT-INTEL",
            "threat_type": "malware",
            "threat_level": "high",
            "target_device_id": "CORP-LAPTOP-001",
            "threat_description": "Trojan detected",
            "confidence_score": 0.92,
        },
        {
            "report_id": "THREAT-2024-002",
            "reporting_participant": "CORP-SEC",
            "threat_type": "phishing",
            "threat_level": "medium",
            "target_device_id": "CORP-SERVER-001",
            "threat_description": "Phishing campaign",
            "confidence_score": 0.78,
        },
    ]
    
    for threat in threats:
        threat_repo.create(**threat)
        print(f"[OK] Report: {threat['report_id']}")
    
    device_threats = threat_repo.get_for_device("CORP-LAPTOP-001")
    print(f"\nThreats for CORP-LAPTOP-001: {len(device_threats)}")
    for threat in device_threats:
        print(f"  - {threat.threat_type} ({threat.threat_level})")
    
    session.close()


def example_5_storage_manager():
    """Example 5: Using high-level StorageManager interface."""
    print("\n" + "="*70)
    print("EXAMPLE 5: High-Level Storage Manager")
    print("="*70)
    
    db = init_db("sqlite:///securepremium_example.db")
    storage = StorageManager()
    storage.initialize()
    
    print("\nDevice Summary for CORP-LAPTOP-001:")
    summary = storage.get_device_summary("CORP-LAPTOP-001")
    
    if summary:
        print(f"  Device ID: {summary['device']['id']}")
        print(f"  Hostname: {summary['device']['hostname']}")
        print(f"  Risk Score: {summary['device']['current_risk_score']:.2f}")
        print(f"  Risk Level: {summary['device']['risk_level']}")
        
        print(f"\n  Recent Assessments: {len(summary['recent_assessments'])}")
        for i, assessment in enumerate(summary['recent_assessments'][:3]):
            print(f"    {i+1}. Score: {assessment['score']:.2f}")
        
        print(f"\n  Threats: {len(summary['threats'])}")
        for threat in summary['threats']:
            print(f"    - {threat['type']}")
    
    print("\nDatabase Statistics:")
    stats = storage.get_database_stats()
    print(f"  Total tables: {stats['total_tables']}")
    for table_name in list(stats['tables'].keys())[:5]:
        print(f"  - {table_name}")


def cleanup():
    """Clean up example database."""
    import time
    if os.path.exists("securepremium_example.db"):
        try:
            time.sleep(0.5)
            os.remove("securepremium_example.db")
            print("[OK] Database cleaned up")
        except Exception as e:
            print(f"[WARN] Could not delete database: {e}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("SECUREPREMIUM STORAGE MODULE EXAMPLES")
    print("="*70)
    
    # Clean up old database
    if os.path.exists("securepremium_example.db"):
        try:
            os.remove("securepremium_example.db")
            print("[OK] Removed old database")
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
