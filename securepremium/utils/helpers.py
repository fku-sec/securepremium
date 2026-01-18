"""Utility functions and helpers"""

import logging
from typing import Dict, Any, List
import json
from datetime import datetime


def setup_logging(name: str, level: str = "INFO") -> logging.Logger:
    """
    Setup standard logging for module.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def safe_get(data: Dict, path: str, default: Any = None) -> Any:
    """
    Safely access nested dictionary values.

    Args:
        data: Dictionary to access
        path: Dot-separated path (e.g., "user.profile.name")
        default: Default value if path not found

    Returns:
        Value at path or default
    """
    keys = path.split(".")
    current = data

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default

    return current


def normalize_risk_score(score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """
    Normalize risk score to specified range.

    Args:
        score: Raw score value
        min_val: Minimum normalized value
        max_val: Maximum normalized value

    Returns:
        Normalized score
    """
    return max(min_val, min(max_val, float(score)))


def calculate_percentile(value: float, values: List[float]) -> float:
    """
    Calculate percentile rank of value within list.

    Args:
        value: Value to rank
        values: List of values

    Returns:
        Percentile rank 0-100
    """
    if not values:
        return 0.0

    sorted_values = sorted(values)
    rank = sum(1 for v in sorted_values if v <= value)
    percentile = (rank / len(sorted_values)) * 100

    return percentile


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format amount as currency string.

    Args:
        amount: Amount to format
        currency: Currency code (USD, EUR, etc.)

    Returns:
        Formatted currency string
    """
    if currency == "USD":
        return f"${amount:.2f}"
    elif currency == "EUR":
        return f"€{amount:.2f}"
    else:
        return f"{amount:.2f} {currency}"


def validate_device_id(device_id: str) -> bool:
    """
    Validate device ID format.

    Args:
        device_id: Device identifier to validate

    Returns:
        True if valid format
    """
    if not device_id or not isinstance(device_id, str):
        return False

    if len(device_id) < 8 or len(device_id) > 128:
        return False

    return True


def validate_risk_score(score: float) -> bool:
    """
    Validate risk score is in valid range.

    Args:
        score: Risk score to validate

    Returns:
        True if score valid
    """
    return isinstance(score, (int, float)) and 0.0 <= score <= 1.0


def validate_reputation_score(score: float) -> bool:
    """
    Validate reputation score is in valid range.

    Args:
        score: Reputation score to validate

    Returns:
        True if score valid
    """
    return isinstance(score, (int, float)) and 0.0 <= score <= 1.0


def iso_to_datetime(iso_string: str) -> datetime:
    """
    Convert ISO format string to datetime.

    Args:
        iso_string: ISO format timestamp string

    Returns:
        datetime object
    """
    try:
        return datetime.fromisoformat(iso_string)
    except (ValueError, TypeError):
        return datetime.utcnow()


def datetime_to_iso(dt: datetime) -> str:
    """
    Convert datetime to ISO format string.

    Args:
        dt: datetime object

    Returns:
        ISO format string
    """
    return dt.isoformat()


def serialize_report(report_dict: Dict) -> str:
    """
    Serialize report to JSON string.

    Args:
        report_dict: Report dictionary

    Returns:
        JSON string
    """
    return json.dumps(report_dict, indent=2, default=str)


def deserialize_report(json_string: str) -> Dict:
    """
    Deserialize JSON string to report dictionary.

    Args:
        json_string: JSON string

    Returns:
        Dictionary
    """
    return json.loads(json_string)
