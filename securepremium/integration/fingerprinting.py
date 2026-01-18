"""Thin adapter for hardware fingerprinting provider integration.

Provides a safe wrapper around an external production fingerprint generator
with a graceful fallback when the provider is unavailable. The adapter
exposes `get_fingerprint_hash()` and optional `get_metadata()`.
"""

from typing import Optional, Dict, Any
import hashlib
import json
import logging
import platform
import uuid

logger = logging.getLogger(__name__)


try:
    # External provider (if installed) offering production-grade fingerprints
    from device_fingerprinting.production_fingerprint import (
        ProductionFingerprintGenerator,
    )
except Exception:  # ImportError or other initialization errors
    ProductionFingerprintGenerator = None  # type: ignore


class DeviceFingerprintingService:
    """Adapter to obtain device fingerprints in a robust way.

    If an external provider is available, uses its production generator.
    Otherwise, falls back to a best-effort fingerprint derived from local
    system characteristics.
    """

    def __init__(self, generator: Optional[Any] = None) -> None:
        self._generator = generator
        if self._generator is None and ProductionFingerprintGenerator is not None:
            try:
                self._generator = ProductionFingerprintGenerator()
            except Exception as e:
                logger.warning(
                    "Failed to initialize ProductionFingerprintGenerator; using fallback: %s",
                    e,
                )
                self._generator = None

        self._using_fallback = self._generator is None
        if self._using_fallback:
            logger.info("External fingerprinting provider not available; using fallback")

    def get_fingerprint_hash(self) -> str:
        """Return a stable fingerprint hash string.

        - When the external generator is present, attempts multiple common
          method names to retrieve fingerprint data, then normalizes it to a
          SHA3-512 hex digest if needed.
        - When unavailable, computes a SHA3-512 digest from local system info.
        """
        if self._generator is not None:
            data = None
            try:
                if hasattr(self._generator, "generate_fingerprint"):
                    data = self._generator.generate_fingerprint()
                elif hasattr(self._generator, "generate"):
                    data = self._generator.generate()
                elif hasattr(self._generator, "get_fingerprint"):
                    data = self._generator.get_fingerprint()
                else:
                    logger.warning("Unknown generator API; coercing to string")
                    data = str(self._generator)
            except Exception as e:
                logger.warning("Error generating fingerprint; using fallback: %s", e)
                data = None

            # Normalize to a hex digest string
            if isinstance(data, str):
                return self._normalize_hash(data)
            elif isinstance(data, dict):
                for key in ("fingerprint_hash", "hash", "fingerprint"):
                    val = data.get(key)
                    if isinstance(val, str):
                        return self._normalize_hash(val)
                raw = json.dumps(data, sort_keys=True)
                return hashlib.sha3_512(raw.encode()).hexdigest()
            else:
                raw = json.dumps({"data": str(data)})
                return hashlib.sha3_512(raw.encode()).hexdigest()

        # Fallback path: derive a fingerprint from local system info
        info = {
            "node": platform.node(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "mac": uuid.getnode(),
        }
        raw = json.dumps(info, sort_keys=True)
        return hashlib.sha3_512(raw.encode()).hexdigest()

    def get_metadata(self) -> Dict[str, Any]:
        """Return optional metadata from the generator or fallback status."""
        if self._generator is not None:
            try:
                if hasattr(self._generator, "get_metadata"):
                    md = self._generator.get_metadata()
                    if isinstance(md, dict):
                        return md
            except Exception:
                pass
        return {"fallback": self._using_fallback}

    @staticmethod
    def _normalize_hash(value: str) -> str:
        """Normalize to a hex digest suitable for storage and comparisons."""
        s = value.strip().lower()
        if all(c in "0123456789abcdef" for c in s) and len(s) >= 64:
            return s
        return hashlib.sha3_512(s.encode()).hexdigest()
