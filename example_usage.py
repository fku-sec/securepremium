"""
Complete example demonstrating Device Behavior Insurance Protocol usage.

This example shows a realistic workflow involving:
1. Device registration and profiling
2. Risk assessment
3. Premium calculation
4. Threat intelligence sharing
5. Reputation updates
"""

from datetime import datetime
from securepremium import (
    RiskCalculator,
    PremiumEngine,
    DeviceScorer,
    ReputationNetwork,
)


def example_basic_workflow():
    """
    Basic workflow: Register device, assess risk, generate quote.
    """
    print("=" * 70)
    print("DEVICE BEHAVIOR INSURANCE PROTOCOL - BASIC WORKFLOW")
    print("=" * 70)

    # Initialize components
    risk_calculator = RiskCalculator()
    premium_engine = PremiumEngine()
    device_scorer = DeviceScorer()

    # Step 1: Register a device
    print("\n[Step 1] Registering device...")
    device_profile = device_scorer.register_device(
        device_id="CORP-LAP-001",
        fingerprint_hash="a3f4b9c8d2e1f7a6b5c4d3e2f1a0b9c8",
        hardware_info={
            "cpu": "Intel Core i7-11700K",
            "cores": 8,
            "ram": "32GB",
            "disk_serial": "WDC_WD10EZEX_12345",
        },
        system_info={
            "os": "Windows 11 Pro",
            "version": "22H2",
            "build": "22621",
            "hostname": "CORP-LAP-001",
        },
    )

    print(f"  Device ID: {device_profile.device_id}")
    print(f"  Fingerprint: {device_profile.fingerprint_hash[:16]}...")
    print(f"  OS: {device_profile.system_info['os']}")

    # Step 2: Assess device risk
    print("\n[Step 2] Assessing device risk...")
    device_metrics = {
        "login_failures": 1,
        "total_login_attempts": 145,
        "tpm_status": "healthy",
        "component_mismatch": False,
        "firmware_anomaly": False,
        "disk_encryption_disabled": False,
        "resource_usage_spike": False,
        "unusual_access_time": False,
        "cpu_usage": 22.5,
        "memory_usage": 45.0,
        "timestamp": datetime.utcnow(),
    }

    risk_assessment = risk_calculator.calculate_risk(
        device_id="CORP-LAP-001",
        device_metrics=device_metrics,
    )

    print(f"  Overall Risk Score: {risk_assessment.overall_risk_score:.2%}")
    print(f"  Risk Category: {risk_calculator.get_risk_category(risk_assessment.overall_risk_score)}")
    print(f"  Behavioral Risk: {risk_assessment.behavioral_risk:.2%}")
    print(f"  Hardware Risk: {risk_assessment.hardware_risk:.2%}")
    print(f"  Network Risk: {risk_assessment.network_risk:.2%}")
    print(f"  Assessment Confidence: {risk_assessment.confidence_level:.0%}")

    if risk_assessment.threat_indicators:
        print(f"  Threat Indicators: {', '.join(risk_assessment.threat_indicators)}")

    # Step 3: Calculate device score
    print("\n[Step 3] Calculating device trustworthiness score...")
    device_score, components = device_scorer.calculate_device_score("CORP-LAP-001")

    print(f"  Device Score: {device_score:.2%}")
    print(f"  Score Category: {device_scorer.get_device_score_category(device_score)}")
    print(f"  Component Breakdown:")
    for component, score in components.items():
        print(f"    - {component}: {score:.2%}")

    # Step 4: Generate premium quote
    print("\n[Step 4] Generating insurance premium quote...")
    quote = premium_engine.generate_quote(
        device_id="CORP-LAP-001",
        risk_assessment=risk_assessment,
        reputation_score=device_score,
        coverage_level="standard",
    )

    print(f"  Coverage Level: {quote.coverage_level}")
    print(f"  Annual Premium: ${quote.annual_premium_usd:.2f}")
    print(f"  Monthly Premium: ${quote.monthly_premium_usd:.2f}")
    print(f"  Base Premium: ${quote.base_premium:.2f}")
    print(f"  Risk Adjustment: {quote.risk_adjustment:.2f}x")
    print(f"  Reputation Discount: {quote.reputation_discount:.0%}")
    print(f"  Quote Valid Until: {quote.quote_valid_until.strftime('%Y-%m-%d')}")

    print("\n" + "=" * 70)


def example_threat_network_workflow():
    """
    Threat intelligence workflow: Submit reports, query reputation, update premiums.
    """
    print("\n" + "=" * 70)
    print("DEVICE BEHAVIOR INSURANCE PROTOCOL - THREAT INTELLIGENCE WORKFLOW")
    print("=" * 70)

    # Initialize components
    reputation_network = ReputationNetwork(network_id="enterprise_network")
    premium_engine = PremiumEngine()
    risk_calculator = RiskCalculator()

    # Step 1: Register organizations as network participants
    print("\n[Step 1] Registering organizations to threat intelligence network...")
    organizations = ["Security-Team-A", "Security-Team-B", "Security-Team-C"]

    for org in organizations:
        reputation_network.register_participant(org)
        print(f"  Registered: {org}")

    # Step 2: Submit threat reports
    print("\n[Step 2] Submitting threat intelligence reports...")

    threat_reports = [
        {
            "reporter": "Security-Team-A",
            "device": "DEVICE-SUSPICIOUS-001",
            "threat_type": "malware_detected",
            "severity": "critical",
            "description": "Trojan.GenericKD detected in system processes",
        },
        {
            "reporter": "Security-Team-B",
            "device": "DEVICE-SUSPICIOUS-001",
            "threat_type": "unauthorized_access",
            "severity": "high",
            "description": "Unauthorized remote access attempts logged",
        },
        {
            "reporter": "Security-Team-C",
            "device": "DEVICE-SUSPICIOUS-001",
            "threat_type": "data_exfiltration",
            "severity": "critical",
            "description": "Suspicious outbound data connections detected",
        },
    ]

    for report_data in threat_reports:
        report = reputation_network.submit_threat_report(
            reporter_id=report_data["reporter"],
            device_id=report_data["device"],
            threat_type=report_data["threat_type"],
            severity=report_data["severity"],
            description=report_data["description"],
            evidence_hash="cryptographic_hash_of_evidence_data",
        )

        print(
            f"  Report: {report_data['threat_type']} ({report_data['severity']}) "
            f"from {report_data['reporter']}"
        )

    # Step 3: Query network reputation for device
    print("\n[Step 3] Querying device reputation from network...")

    intelligence = reputation_network.get_threat_intelligence_summary("DEVICE-SUSPICIOUS-001")

    print(f"  Device: DEVICE-SUSPICIOUS-001")
    print(f"  Total Reports: {intelligence['total_reports']}")
    print(f"  Recent Reports (90d): {intelligence['recent_reports_90_days']}")
    print(f"  Verified Reports: {intelligence['verified_reports']}")
    print(f"  Distinct Reporters: {intelligence['distinct_reporters']}")
    print(f"  Reputation Score: {intelligence['reputation']['reputation_score']:.2f}")
    print(f"  Threat Types: {', '.join(intelligence['threat_types'].keys())}")

    # Step 4: Check risk level
    risk_level = reputation_network.get_device_risk_level("DEVICE-SUSPICIOUS-001")

    print(f"\n  Network Risk Assessment: {risk_level.upper()}")

    # Step 5: Generate premium for compromised device
    print("\n[Step 4] Calculating insurance impact...")

    risk_assessment = risk_calculator.calculate_risk(
        device_id="DEVICE-SUSPICIOUS-001",
        device_metrics={
            "login_failures": 85,
            "total_login_attempts": 100,
            "tpm_status": "compromised",
            "component_mismatch": True,
            "firmware_anomaly": True,
        },
    )

    reputation_score = intelligence["reputation"]["reputation_score"]

    quote = premium_engine.generate_quote(
        device_id="DEVICE-SUSPICIOUS-001",
        risk_assessment=risk_assessment,
        reputation_score=reputation_score,
        coverage_level="premium",
    )

    print(f"  Internal Risk Score: {risk_assessment.overall_risk_score:.0%}")
    print(f"  Network Reputation: {reputation_score:.0%}")
    print(f"  Annual Premium: ${quote.annual_premium_usd:.2f}")
    print(f"  Coverage Level: {quote.coverage_level}")
    print(f"  Risk Multiplier: {quote.risk_adjustment:.2f}x")
    print(f"  Reputation Penalty: {-quote.reputation_discount:.0%}")

    # Step 6: Network statistics
    print("\n[Step 5] Network statistics...")

    stats = reputation_network.get_network_statistics()

    print(f"  Network ID: {stats['network_id']}")
    print(f"  Participants: {stats['total_participants']}")
    print(f"  Tracked Devices: {stats['tracked_devices']}")
    print(f"  Total Reports: {stats['total_reports']}")
    print(f"  Average Reputation: {stats['average_reputation_score']:.2f}")
    print(f"  Top Threats: {', '.join([t[0] for t in stats['top_threat_types'][:3]])}")

    print("\n" + "=" * 70)


def example_organizational_cost_analysis():
    """
    Organizational analysis: Estimate costs for device fleet.
    """
    print("\n" + "=" * 70)
    print("DEVICE BEHAVIOR INSURANCE PROTOCOL - ORGANIZATIONAL COST ANALYSIS")
    print("=" * 70)

    premium_engine = PremiumEngine()

    # Step 1: Estimate annual cost for organization
    print("\n[Step 1] Analyzing organizational insurance costs...")

    fleet_data = {
        "total_devices": 250,
        "average_risk_score": 0.42,
        "average_reputation": 0.72,
        "coverage_distribution": {
            "basic": 0.30,
            "standard": 0.50,
            "premium": 0.20,
        },
    }

    cost_estimate = premium_engine.estimate_annual_cost(
        total_devices=fleet_data["total_devices"],
        average_risk_score=fleet_data["average_risk_score"],
        average_reputation=fleet_data["average_reputation"],
        coverage_distribution=fleet_data["coverage_distribution"],
    )

    print(f"  Organization Fleet Size: {cost_estimate['total_devices']} devices")
    print(f"  Average Risk Score: {fleet_data['average_risk_score']:.0%}")
    print(f"  Average Reputation: {fleet_data['average_reputation']:.0%}")

    print("\n  Coverage Distribution:")
    for tier_data in cost_estimate["breakdown_by_coverage"]:
        print(
            f"    {tier_data['coverage_tier'].title()}: "
            f"{tier_data['device_count']} devices "
            f"@ ${tier_data['premium_per_device']:.2f}/year"
        )

    print(f"\n  Cost Summary:")
    print(f"    Subtotal: ${cost_estimate['subtotal']:.2f}")
    print(f"    Volume Discount ({cost_estimate['volume_discount_rate']:.0%}): "
          f"-${cost_estimate['volume_discount_amount']:.2f}")
    print(f"    Total Annual Cost: ${cost_estimate['total_annual_cost']:.2f}")
    print(f"    Cost Per Device/Month: ${cost_estimate['cost_per_device_monthly']:.2f}")

    # Step 2: Show tier details
    print("\n[Step 2] Coverage tier details...")

    tiers = premium_engine.premium_model.get_all_tiers()

    for tier_name, details in tiers.items():
        print(f"\n  {details['tier_name'].upper()} Tier:")
        print(f"    Base Multiplier: {details['base_multiplier']:.1f}x")
        print(f"    Max Annual Claim: ${details['max_annual_claim']:,}")
        print(f"    Deductible: ${details['deductible']}")
        print(f"    Coverage Items ({details['item_count']}):")
        for item in details["coverage_items"]:
            print(f"      - {item.replace('_', ' ').title()}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Run all example workflows
    example_basic_workflow()
    example_threat_network_workflow()
    example_organizational_cost_analysis()

    print("\nAll examples completed successfully!")
