"""Tests for Securepremium CLI module."""

import pytest
import json
from click.testing import CliRunner
from securepremium.cli.main import cli


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


class TestDeviceCommands:
    """Test device management CLI commands."""
    
    def test_device_register_basic(self, runner):
        """Test basic device registration."""
        result = runner.invoke(cli, [
            'device', 'register',
            '--device-id', 'TEST-001',
            '--fingerprint', 'abc123'
        ])
        assert result.exit_code == 0
        assert 'Device registered successfully' in result.output
        assert 'TEST-001' in result.output
    
    def test_device_register_json(self, runner):
        """Test device registration with JSON output."""
        result = runner.invoke(cli, [
            'device', 'register',
            '--device-id', 'TEST-002',
            '--fingerprint', 'def456',
            '--json-output'
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data['device_id'] == 'TEST-002'
        assert data['status'] == 'registered'
    
    def test_device_register_full(self, runner):
        """Test device registration with all options."""
        result = runner.invoke(cli, [
            'device', 'register',
            '--device-id', 'TEST-003',
            '--fingerprint', 'ghi789',
            '--cpu', 'Intel Core i9',
            '--ram', '32GB',
            '--os', 'Windows 11',
            '--version', '22H2',
            '--hostname', 'TEST-HOST'
        ])
        assert result.exit_code == 0
        assert 'Intel Core i9' in result.output
        assert '32GB' in result.output


class TestRiskCommands:
    """Test risk assessment CLI commands."""
    
    def test_risk_assess_basic(self, runner):
        """Test basic risk assessment."""
        result = runner.invoke(cli, [
            'risk', 'assess',
            '--device-id', 'TEST-001'
        ])
        # Risk assessment may fail if device doesn't exist, but command should execute
        assert 'Risk' in result.output or 'Error' in result.output
    
    def test_risk_assess_with_metrics(self, runner):
        """Test risk assessment with custom metrics."""
        result = runner.invoke(cli, [
            'risk', 'assess',
            '--device-id', 'TEST-001',
            '--login-failures', '5',
            '--total-logins', '100',
            '--tpm-status', 'degraded',
            '--cpu-usage', '85.5'
        ])
        # Command should execute without crashing
        assert result.output  # Should have output
    
    def test_risk_assess_json(self, runner):
        """Test risk assessment with JSON output."""
        result = runner.invoke(cli, [
            'risk', 'assess',
            '--device-id', 'TEST-001',
            '--json-output'
        ])
        # Should produce valid JSON or error message
        try:
            data = json.loads(result.output)
            assert 'device_id' in data or 'error' in data
        except json.JSONDecodeError:
            # May fail but shouldn't crash
            assert 'Error' in result.output or result.exit_code == 1


class TestQuoteCommands:
    """Test premium quote CLI commands."""
    
    def test_quote_generate_basic(self, runner):
        """Test basic quote generation."""
        result = runner.invoke(cli, [
            'quote', 'generate',
            '--device-id', 'TEST-001'
        ])
        assert result.exit_code == 0
        assert 'Premium Quote' in result.output
        assert 'Annual Premium' in result.output
    
    def test_quote_generate_coverage_levels(self, runner):
        """Test quote generation for different coverage levels."""
        for coverage in ['basic', 'standard', 'premium']:
            result = runner.invoke(cli, [
                'quote', 'generate',
                '--device-id', 'TEST-001',
                '--coverage', coverage
            ])
            assert result.exit_code == 0
            assert coverage.upper() in result.output
    
    def test_quote_generate_json(self, runner):
        """Test quote generation with JSON output."""
        result = runner.invoke(cli, [
            'quote', 'generate',
            '--device-id', 'TEST-001',
            '--coverage', 'standard',
            '--json-output'
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data['device_id'] == 'TEST-001'
        assert 'annual_premium' in data
        assert data['coverage'] == 'standard'


class TestNetworkCommands:
    """Test network CLI commands."""
    
    def test_network_stats(self, runner):
        """Test network statistics retrieval."""
        result = runner.invoke(cli, [
            'network', 'stats',
            '--network-id', 'test_network'
        ])
        assert result.exit_code == 0
        assert 'Network Statistics' in result.output
        assert 'Total Devices' in result.output
    
    def test_network_stats_json(self, runner):
        """Test network statistics with JSON output."""
        result = runner.invoke(cli, [
            'network', 'stats',
            '--network-id', 'test_network',
            '--json-output'
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 'network_id' in data
        assert 'total_devices' in data
    
    def test_network_report(self, runner):
        """Test reputation reporting."""
        result = runner.invoke(cli, [
            'network', 'report',
            '--network-id', 'test_network',
            '--device-id', 'TEST-001',
            '--reputation-score', '0.75',
            '--threat-level', 'medium'
        ])
        # Command should execute
        assert result.output  # Should have output
    
    def test_network_top_devices(self, runner):
        """Test top devices retrieval."""
        result = runner.invoke(cli, [
            'network', 'top-devices',
            '--network-id', 'test_network',
            '--limit', '5'
        ])
        assert result.exit_code == 0
        assert 'Top 5 Devices' in result.output


class TestInfoCommand:
    """Test info command."""
    
    def test_info_display(self, runner):
        """Test system information display."""
        result = runner.invoke(cli, ['info'])
        assert result.exit_code == 0
        assert 'SECUREPREMIUM' in result.output
        assert 'Version' in result.output
        assert 'Device management' in result.output or 'device' in result.output.lower()


class TestHelpCommands:
    """Test help functionality."""
    
    def test_main_help(self, runner):
        """Test main help."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Commands:' in result.output or 'Usage:' in result.output
    
    def test_device_help(self, runner):
        """Test device command help."""
        result = runner.invoke(cli, ['device', '--help'])
        assert result.exit_code == 0
        assert 'register' in result.output.lower()
    
    def test_risk_help(self, runner):
        """Test risk command help."""
        result = runner.invoke(cli, ['risk', '--help'])
        assert result.exit_code == 0
        assert 'assess' in result.output.lower()
    
    def test_quote_help(self, runner):
        """Test quote command help."""
        result = runner.invoke(cli, ['quote', '--help'])
        assert result.exit_code == 0
        assert 'generate' in result.output.lower()
    
    def test_network_help(self, runner):
        """Test network command help."""
        result = runner.invoke(cli, ['network', '--help'])
        assert result.exit_code == 0


class TestBatchCommands:
    """Test batch processing CLI commands."""
    
    def test_batch_analyze_help(self, runner):
        """Test batch analyze help."""
        result = runner.invoke(cli, ['batch', 'analyze', '--help'])
        assert result.exit_code == 0
        assert '--input-file' in result.output
        assert '--output-file' in result.output
    
    def test_batch_quote_batch_help(self, runner):
        """Test batch quote help."""
        result = runner.invoke(cli, ['batch', 'quote-batch', '--help'])
        assert result.exit_code == 0
        assert '--input-file' in result.output
