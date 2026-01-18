"""Main CLI module for Securepremium."""

import json
import csv
from pathlib import Path
from typing import Optional
import click
from datetime import datetime
from tabulate import tabulate

from securepremium.core.risk_calculator import RiskCalculator
from securepremium.core.premium_engine import PremiumEngine
from securepremium.models.device_scorer import DeviceScorer
from securepremium.network.reputation_network import ReputationNetwork


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Securepremium CLI - Device Risk Assessment and Insurance Premium Calculator"""
    pass


# ========================
# Device Registration
# ========================

@cli.group()
def device():
    """Device management commands"""
    pass


@device.command()
@click.option("--device-id", required=True, help="Unique device identifier")
@click.option("--fingerprint", required=True, help="Device fingerprint hash")
@click.option("--cpu", default="Unknown", help="CPU information")
@click.option("--ram", default="Unknown", help="RAM amount")
@click.option("--os", default="Unknown", help="Operating system")
@click.option("--version", default="Unknown", help="OS version")
@click.option("--hostname", default="Unknown", help="Device hostname")
@click.option("--json-output", is_flag=True, help="Output as JSON")
def register(device_id, fingerprint, cpu, ram, os, version, hostname, json_output):
    """Register a new device in the system"""
    try:
        scorer = DeviceScorer()
        
        device_profile = scorer.register_device(
            device_id=device_id,
            fingerprint_hash=fingerprint,
            hardware_info={"cpu": cpu, "ram": ram},
            system_info={"os": os, "version": version, "hostname": hostname}
        )
        
        if json_output:
            click.echo(json.dumps({
                "device_id": device_id,
                "status": "registered",
                "fingerprint": fingerprint,
                "timestamp": datetime.now().isoformat()
            }, indent=2))
        else:
            click.secho("[OK] Device registered successfully", fg="green")
            click.echo(f"  Device ID: {device_id}")
            click.echo(f"  Fingerprint: {fingerprint}")
            click.echo(f"  CPU: {cpu}")
            click.echo(f"  RAM: {ram}")
            click.echo(f"  OS: {os} {version}")
    except Exception as e:
        click.secho(f"[ERROR] Error registering device: {str(e)}", fg="red")
        raise click.Abort()


# ========================
# Risk Assessment
# ========================

@cli.group()
def risk():
    """Risk assessment commands"""
    pass


@risk.command()
@click.option("--device-id", required=True, help="Device to assess")
@click.option("--login-failures", type=int, default=0, help="Number of login failures")
@click.option("--total-logins", type=int, default=100, help="Total login attempts")
@click.option("--tpm-status", default="healthy", help="TPM status")
@click.option("--cpu-usage", type=float, default=25.0, help="CPU usage percentage")
@click.option("--json-output", is_flag=True, help="Output as JSON")
def assess(device_id, login_failures, total_logins, tpm_status, cpu_usage, json_output):
    """Assess risk for a device"""
    try:
        calculator = RiskCalculator()
        
        risk_assessment = calculator.calculate_risk(
            device_id=device_id,
            device_metrics={
                "login_failures": login_failures,
                "total_login_attempts": total_logins,
                "tpm_status": tpm_status,
                "cpu_usage": cpu_usage,
            }
        )
        
        risk_category = calculator.get_risk_category(risk_assessment.overall_risk_score)
        
        if json_output:
            click.echo(json.dumps({
                "device_id": device_id,
                "risk_score": risk_assessment.overall_risk_score,
                "risk_category": risk_category,
                "confidence": risk_assessment.confidence_level,
                "timestamp": datetime.now().isoformat()
            }, indent=2))
        else:
            click.echo(f"\nRisk Assessment for {device_id}")
            click.echo("-" * 50)
            color = "red" if risk_category == "high" else "yellow" if risk_category == "medium" else "green"
            click.secho(f"Risk Score: {risk_assessment.overall_risk_score:.2%}", fg=color, bold=True)
            click.echo(f"Risk Category: {risk_category.upper()}")
            click.echo(f"Confidence: {risk_assessment.confidence_level:.2%}")
            click.echo(f"Assessment Date: {datetime.now().isoformat()}")
    except Exception as e:
        click.secho(f"[ERROR] Error assessing risk: {str(e)}", fg="red")
        raise click.Abort()


# ========================
# Premium Quotes
# ========================

@cli.group()
def quote():
    """Premium quote commands"""
    pass


@quote.command()
@click.option("--device-id", required=True, help="Device to quote")
@click.option("--coverage", type=click.Choice(["basic", "standard", "premium"]), 
              default="standard", help="Coverage level")
@click.option("--json-output", is_flag=True, help="Output as JSON")
def generate(device_id, coverage, json_output):
    """Generate a premium quote for a device"""
    try:
        risk_calculator = RiskCalculator()
        premium_engine = PremiumEngine()
        
        # First, calculate risk
        risk_assessment = risk_calculator.calculate_risk(
            device_id=device_id,
            device_metrics={
                "login_failures": 0,
                "total_login_attempts": 100,
                "tpm_status": "healthy",
                "cpu_usage": 25.0,
            }
        )
        
        # Then generate quote
        quote = premium_engine.generate_quote(
            device_id=device_id,
            risk_assessment=risk_assessment,
            coverage_level=coverage
        )
        
        if json_output:
            click.echo(json.dumps({
                "device_id": device_id,
                "coverage": coverage,
                "annual_premium": quote.annual_premium_usd,
                "monthly_premium": quote.monthly_premium_usd,
                "timestamp": datetime.now().isoformat()
            }, indent=2))
        else:
            click.echo(f"\nPremium Quote for {device_id}")
            click.echo("-" * 50)
            click.echo(f"Coverage Level: {coverage.upper()}")
            click.secho(f"Annual Premium: ${quote.annual_premium_usd:.2f}", fg="cyan", bold=True)
            click.echo(f"Monthly Premium: ${quote.monthly_premium_usd:.2f}")
            click.echo(f"Quote Date: {datetime.now().isoformat()}")
    except Exception as e:
        click.secho(f"[ERROR] Error generating quote: {str(e)}", fg="red")
        raise click.Abort()


# ========================
# Batch Operations
# ========================

@cli.group()
def batch():
    """Batch processing commands"""
    pass


@batch.command()
@click.option("--input-file", type=click.Path(exists=True), required=True, 
              help="CSV file with device data")
@click.option("--output-file", type=click.Path(), default="batch_results.csv",
              help="Output CSV file for results")
@click.option("--format", type=click.Choice(["csv", "json"]), default="csv",
              help="Output format")
def analyze(input_file, output_file, format):
    """Batch analyze multiple devices from CSV"""
    try:
        calculator = RiskCalculator()
        results = []
        
        # Read input CSV
        with open(input_file, 'r') as f:
            reader = csv.DictReader(f)
            devices = list(reader)
        
        if not devices:
            click.secho("[ERROR] No devices found in input file", fg="red")
            return
        
        click.echo(f"Analyzing {len(devices)} devices...")
        
        with click.progressbar(devices, label="Processing") as bar:
            for device_row in bar:
                try:
                    device_id = device_row.get("device_id", "unknown")
                    
                    risk_assessment = calculator.calculate_risk(
                        device_id=device_id,
                        device_metrics={
                            "login_failures": int(device_row.get("login_failures", 0)),
                            "total_login_attempts": int(device_row.get("total_logins", 100)),
                            "tpm_status": device_row.get("tpm_status", "healthy"),
                            "cpu_usage": float(device_row.get("cpu_usage", 25.0)),
                        }
                    )
                    
                    risk_category = calculator.get_risk_category(risk_assessment.overall_risk_score)
                    
                    results.append({
                        "device_id": device_id,
                        "risk_score": f"{risk_assessment.overall_risk_score:.2%}",
                        "risk_category": risk_category,
                        "confidence": f"{risk_assessment.confidence_score:.2%}",
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as e:
                    results.append({
                        "device_id": device_row.get("device_id", "unknown"),
                        "error": str(e)
                    })
        
        # Write output
        if format == "json":
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
        else:
            if results:
                with open(output_file, 'w', newline='') as f:
                    fieldnames = results[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(results)
        
        click.secho("[OK] Batch analysis complete", fg="green")
        click.echo(f"  Results saved to: {output_file}")
        click.echo(f"  Devices processed: {len(results)}")
    except Exception as e:
        click.secho(f"[ERROR] Error in batch analysis: {str(e)}", fg="red")
        raise click.Abort()


@batch.command()
@click.option("--input-file", type=click.Path(exists=True), required=True,
              help="CSV file with device data")
@click.option("--output-file", type=click.Path(), default="batch_quotes.csv",
              help="Output CSV file for quotes")
@click.option("--coverage", type=click.Choice(["basic", "standard", "premium"]),
              default="standard", help="Coverage level")
def quote_batch(input_file, output_file, coverage):
    """Generate premium quotes for multiple devices from CSV"""
    try:
        calculator = RiskCalculator()
        engine = PremiumEngine()
        results = []
        
        # Read input CSV
        with open(input_file, 'r') as f:
            reader = csv.DictReader(f)
            devices = list(reader)
        
        if not devices:
            click.secho("[ERROR] No devices found in input file", fg="red")
            return
        
        click.echo(f"Generating quotes for {len(devices)} devices...")
        
        with click.progressbar(devices, label="Processing") as bar:
            for device_row in bar:
                try:
                    device_id = device_row.get("device_id", "unknown")
                    
                    risk_assessment = calculator.calculate_risk(
                        device_id=device_id,
                        device_metrics={
                            "login_failures": int(device_row.get("login_failures", 0)),
                            "total_login_attempts": int(device_row.get("total_logins", 100)),
                            "tpm_status": device_row.get("tpm_status", "healthy"),
                            "cpu_usage": float(device_row.get("cpu_usage", 25.0)),
                        }
                    )
                    
                    quote = engine.generate_quote(
                        device_id=device_id,
                        risk_assessment=risk_assessment,
                        coverage_level=coverage
                    )
                    
                    results.append({
                        "device_id": device_id,
                        "coverage": coverage,
                        "annual_premium": f"${quote.annual_premium_usd:.2f}",
                        "monthly_premium": f"${quote.monthly_premium_usd:.2f}",
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as e:
                    results.append({
                        "device_id": device_row.get("device_id", "unknown"),
                        "error": str(e)
                    })
        
        # Write output
        if results:
            with open(output_file, 'w', newline='') as f:
                fieldnames = results[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
        
        click.secho(f"[OK] Batch quote generation complete", fg="green")
        click.echo(f"  Quotes saved to: {output_file}")
        click.echo(f"  Devices processed: {len(results)}")
    except Exception as e:
        click.secho(f"[ERROR] Error in batch quote generation: {str(e)}", fg="red")
        raise click.Abort()


# ========================
# Network Statistics
# ========================

@cli.group()
def network():
    """Network statistics and management commands"""
    pass


@network.command()
@click.option("--network-id", required=True, help="Network ID")
@click.option("--json-output", is_flag=True, help="Output as JSON")
def stats(network_id, json_output):
    """Get reputation network statistics"""
    try:
        rep_network = ReputationNetwork(network_id=network_id)
        
        # Get network statistics
        total_devices = len(rep_network.reputation_db)
        avg_reputation = (
            sum(record.reputation_score for record in rep_network.reputation_db.values()) / total_devices
            if total_devices > 0 else 0
        )
        high_risk_count = sum(
            1 for record in rep_network.reputation_db.values() if record.reputation_score > 0.7
        )
        
        if json_output:
            click.echo(json.dumps({
                "network_id": network_id,
                "total_devices": total_devices,
                "average_reputation": avg_reputation,
                "high_risk_devices": high_risk_count,
                "timestamp": datetime.now().isoformat()
            }, indent=2))
        else:
            click.echo(f"\nNetwork Statistics - {network_id}")
            click.echo("-" * 50)
            click.echo(f"Total Devices: {total_devices}")
            click.echo(f"Average Reputation: {avg_reputation:.2%}")
            click.secho(f"High Risk Devices: {high_risk_count}", fg="red" if high_risk_count > 0 else "green")
            click.echo(f"Retrieved: {datetime.now().isoformat()}")
    except Exception as e:
        click.secho(f"[ERROR] Error retrieving network stats: {str(e)}", fg="red")
        raise click.Abort()


@network.command()
@click.option("--network-id", required=True, help="Network ID")
@click.option("--device-id", required=True, help="Device ID")
@click.option("--reputation-score", type=float, required=True, help="Reputation score (0-1)")
@click.option("--threat-level", type=click.Choice(["low", "medium", "high"]), 
              default="low", help="Threat level")
@click.option("--json-output", is_flag=True, help="Output as JSON")
def report(network_id, device_id, reputation_score, threat_level, json_output):
    """Report device reputation to network"""
    try:
        rep_network = ReputationNetwork(network_id=network_id)
        
        rep_network.submit_reputation(
            device_id=device_id,
            reputation_score=reputation_score,
            metadata={"threat_level": threat_level}
        )
        
        if json_output:
            click.echo(json.dumps({
                "network_id": network_id,
                "device_id": device_id,
                "status": "reported",
                "reputation": reputation_score,
                "threat_level": threat_level,
                "timestamp": datetime.now().isoformat()
            }, indent=2))
        else:
            click.secho("[OK] Reputation reported to network", fg="green")
            click.echo(f"  Network ID: {network_id}")
            click.echo(f"  Device ID: {device_id}")
            click.echo(f"  Reputation Score: {reputation_score:.2%}")
            click.echo(f"  Threat Level: {threat_level}")
    except Exception as e:
        click.secho(f"[ERROR] Error reporting reputation: {str(e)}", fg="red")
        raise click.Abort()


@network.command()
@click.option("--network-id", required=True, help="Network ID")
@click.option("--limit", type=int, default=10, help="Number of devices to show")
@click.option("--sort-by", type=click.Choice(["reputation", "device_id"]), 
              default="reputation", help="Sort by field")
@click.option("--json-output", is_flag=True, help="Output as JSON")
def top_devices(network_id, limit, sort_by, json_output):
    """Show top devices by reputation in network"""
    try:
        rep_network = ReputationNetwork(network_id=network_id)
        
        # Get and sort device reputations
        devices = [
            (record.device_id, record.reputation_score) 
            for record in rep_network.reputation_db.values()
        ]
        
        if sort_by == "reputation":
            devices.sort(key=lambda x: x[1], reverse=True)
        else:
            devices.sort(key=lambda x: x[0])
        
        devices = devices[:limit]
        
        if json_output:
            click.echo(json.dumps({
                "network_id": network_id,
                "devices": [
                    {"device_id": d[0], "reputation": d[1]}
                    for d in devices
                ],
                "timestamp": datetime.now().isoformat()
            }, indent=2))
        else:
            click.echo(f"\nTop {limit} Devices by Reputation - {network_id}")
            click.echo("-" * 50)
            
            table_data = []
            for idx, (device_id, reputation) in enumerate(devices, 1):
                status = "[OK]" if reputation < 0.3 else "[WARN]" if reputation < 0.7 else "[HIGH]"
                table_data.append([idx, device_id, f"{reputation:.2%}", status])
            
            headers = ["#", "Device ID", "Reputation", "Status"]
            click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))
    except Exception as e:
        click.secho(f"[ERROR] Error retrieving top devices: {str(e)}", fg="red")
        raise click.Abort()


# ========================
# Help and Info
# ========================

@cli.command()
def info():
    """Display system information"""
    click.echo("\n" + "=" * 60)
    click.echo("SECUREPREMIUM - Device Risk Assessment System")
    click.echo("=" * 60)
    click.echo("\nVersion: 0.1.0")
    click.echo("Purpose: Enterprise-grade device risk quantification")
    click.echo("\nKey Features:")
    click.echo("  • Device registration and profiling")
    click.echo("  • Risk assessment with ML-based scoring")
    click.echo("  • Insurance premium calculation")
    click.echo("  • Decentralized threat intelligence")
    click.echo("  • Batch processing capabilities")
    click.echo("\nCommand Groups:")
    click.echo("  device     - Device management operations")
    click.echo("  risk       - Risk assessment operations")
    click.echo("  quote      - Premium quote generation")
    click.echo("  batch      - Batch processing operations")
    click.echo("  network    - Network statistics and reporting")
    click.echo("\nUse 'securepremium <group> --help' for more information")
    click.echo("=" * 60 + "\n")


if __name__ == "__main__":
    cli()
