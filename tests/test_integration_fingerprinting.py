from securepremium.integration.fingerprinting import DeviceFingerprintingService
from securepremium.models.device_scorer import DeviceScorer


def test_device_fingerprinting_service_initialization_and_hash():
    svc = DeviceFingerprintingService()
    fingerprint = svc.get_fingerprint_hash()
    assert isinstance(fingerprint, str)
    assert len(fingerprint) >= 64
    meta = svc.get_metadata()
    assert isinstance(meta, dict)


def test_register_device_with_adapter_without_explicit_hash():
    scorer = DeviceScorer()
    svc = DeviceFingerprintingService()
    profile = scorer.register_device(
        device_id="dev-001",
        fingerprint_hash=None,
        hardware_info={},
        system_info={},
        fingerprinting_service=svc,
    )
    assert isinstance(profile.fingerprint_hash, str)
    assert len(profile.fingerprint_hash) >= 64
