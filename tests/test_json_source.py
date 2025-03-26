"""
Tests for JSON file-based feature flag source.
"""

import json
import pytest
from pathlib import Path

from aflags.sources.json import JsonSource

# Constants for percentage and per-thousand values
MAX_PERCENTAGE = 100
MAX_PER_THOUSAND = 1000

def test_valid_json_source(tmp_path):
    """Test loading feature flags from a valid JSON file."""
    fixture_path = Path(__file__).parent / "fixtures" / "valid_flags.json"
    source = JsonSource(str(fixture_path))
    flags = source.get_flags()

    assert len(flags) == 3
    assert flags["feature1"].type.value == "boolean"
    assert flags["feature1"].value is True
    assert flags["feature2"].type.value == "percentage"
    assert flags["feature2"].value == 50
    assert flags["feature3"].type.value == "per_thousand"
    assert flags["feature3"].value == 500


def test_missing_type():
    """Test error handling for missing type field."""
    fixture_path = Path(__file__).parent / "fixtures" / "missing_type.json"
    source = JsonSource(str(fixture_path))
    with pytest.raises(ValueError) as exc_info:
        source.get_flags()
    assert "Missing 'type' for feature flag" in str(exc_info.value)


def test_invalid_boolean_value():
    """Test error handling for invalid boolean value."""
    fixture_path = Path(__file__).parent / "fixtures" / "invalid_boolean.json"
    source = JsonSource(str(fixture_path))
    with pytest.raises(ValueError) as exc_info:
        source.get_flags()
    assert "Boolean flag must have a boolean value" in str(exc_info.value)


def test_invalid_percentage_value():
    """Test error handling for invalid percentage value."""
    fixture_path = Path(__file__).parent / "fixtures" / "invalid_percentage.json"
    source = JsonSource(str(fixture_path))
    with pytest.raises(ValueError) as exc_info:
        source.get_flags()
    assert "Percentage flag must have a numeric value" in str(exc_info.value)


def test_nonexistent_file():
    """Test handling of nonexistent JSON file."""
    source = JsonSource("nonexistent.json")
    flags = source.get_flags()
    assert len(flags) == 0


def test_invalid_json():
    """Test error handling for invalid JSON data."""
    fixture_path = Path(__file__).parent / "fixtures" / "invalid.json"
    source = JsonSource(str(fixture_path))
    with pytest.raises(json.JSONDecodeError):
        source.get_flags()


def test_valid_json():
    """Test valid JSON configuration."""
    config = {
        "feature1": {
            "type": "boolean",
            "value": True,
            "description": "Test flag 1",
        },
        "feature2": {
            "type": "percentage",
            "value": MAX_PERCENTAGE / 2,
            "description": "Test flag 2",
        },
        "feature3": {
            "type": "per_thousand",
            "value": MAX_PER_THOUSAND / 2,
            "description": "Test flag 3",
        },
    }

    with open("test_flags.json", "w") as f:
        json.dump(config, f)

    source = JsonSource("test_flags.json")
    flags = source.get_flags()

    assert len(flags) == 3
    assert flags["feature1"].type.value == "boolean"
    assert flags["feature1"].value is True
    assert flags["feature2"].type.value == "percentage"
    assert flags["feature2"].value == MAX_PERCENTAGE / 2
    assert flags["feature3"].type.value == "per_thousand"
    assert flags["feature3"].value == MAX_PER_THOUSAND / 2
