"""
Tests for YAML file-based feature flag source.
"""

import os

import pytest
import yaml

from aflags.sources.yaml import YamlSource

# Constants for percentage and per-thousand values
MAX_PERCENTAGE = 100
MAX_PER_THOUSAND = 1000


def get_fixture_path(filename: str) -> str:
    """Get the absolute path to a fixture file.

    Args:
        filename: Name of the fixture file.

    Returns:
        str: Absolute path to the fixture file.
    """
    return os.path.join(os.path.dirname(__file__), "fixtures", filename)


@pytest.mark.timeout(1)
def test_valid_yaml_source():
    """Test loading feature flags from a valid YAML file."""
    fixture_path = get_fixture_path("valid_flags.yaml")

    source = YamlSource(fixture_path)
    flags = source.get_flags()

    assert len(flags) == 3
    assert flags["feature1"].type.value == "boolean"
    assert flags["feature1"].value is True
    assert flags["feature2"].type.value == "percentage"
    assert flags["feature2"].value == 50
    assert flags["feature3"].type.value == "per_thousand"
    assert flags["feature3"].value == 500


@pytest.mark.timeout(1)
def test_missing_type():
    """Test error handling for missing type field."""
    fixture_path = get_fixture_path("missing_type.yaml")

    source = YamlSource(fixture_path)
    with pytest.raises(ValueError) as exc_info:
        source.get_flags()
    assert "Missing 'type' for feature flag" in str(exc_info.value)


@pytest.mark.timeout(1)
def test_invalid_boolean_value():
    """Test error handling for invalid boolean value."""
    fixture_path = get_fixture_path("invalid_boolean.yaml")

    source = YamlSource(fixture_path)
    with pytest.raises(ValueError) as exc_info:
        source.get_flags()
    assert "Boolean flag must have a boolean value" in str(exc_info.value)


@pytest.mark.timeout(1)
def test_invalid_percentage_value():
    """Test error handling for invalid percentage value."""
    fixture_path = get_fixture_path("invalid_percentage.yaml")

    source = YamlSource(fixture_path)
    with pytest.raises(ValueError) as exc_info:
        source.get_flags()
    assert "Percentage flag must have a numeric value" in str(exc_info.value)


@pytest.mark.timeout(1)
def test_nonexistent_file():
    """Test handling of nonexistent YAML file."""
    source = YamlSource("nonexistent.yaml")
    flags = source.get_flags()
    assert len(flags) == 0


@pytest.mark.timeout(1)
def test_yaml_specific_features():
    """Test YAML-specific features like anchors and aliases."""
    fixture_path = get_fixture_path("yaml_specific.yaml")

    source = YamlSource(fixture_path)
    flags = source.get_flags()

    assert len(flags) == 2
    assert flags["feature1"].type.value == "boolean"
    assert flags["feature1"].value is True
    assert flags["feature1"].description == "Common description"
    assert flags["feature2"].type.value == "percentage"
    assert flags["feature2"].value == 50
    assert flags["feature2"].description == "Common description"


@pytest.mark.timeout(1)
def test_invalid_yaml():
    """Test error handling for invalid YAML data."""
    fixture_path = get_fixture_path("invalid.yaml")

    source = YamlSource(fixture_path)
    with pytest.raises(yaml.YAMLError):
        source.get_flags()


@pytest.mark.timeout(1)
def test_non_dict_values():
    """Test handling of non-dictionary values in YAML."""
    fixture_path = get_fixture_path("non_dict_values.yaml")

    source = YamlSource(fixture_path)
    flags = source.get_flags()

    assert len(flags) == 1
    assert flags["feature4"].type.value == "boolean"
    assert flags["feature4"].value is True


def test_valid_yaml():
    """Test valid YAML configuration."""
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

    with open("test_flags.yaml", "w") as f:
        yaml.dump(config, f)

    source = YamlSource("test_flags.yaml")
    flags = source.get_flags()

    assert len(flags) == 3
    assert flags["feature1"].type.value == "boolean"
    assert flags["feature1"].value is True
    assert flags["feature2"].type.value == "percentage"
    assert flags["feature2"].value == MAX_PERCENTAGE / 2
    assert flags["feature3"].type.value == "per_thousand"
    assert flags["feature3"].value == MAX_PER_THOUSAND / 2


def test_common_description():
    """Test YAML configuration with common description."""
    config = {
        "description": "Common description",
        "feature1": {
            "type": "boolean",
            "value": True,
        },
        "feature2": {
            "type": "percentage",
            "value": MAX_PERCENTAGE / 2,
        },
    }

    with open("test_flags.yaml", "w") as f:
        yaml.dump(config, f)

    source = YamlSource("test_flags.yaml")
    flags = source.get_flags()

    assert len(flags) == 2
    assert flags["feature1"].type.value == "boolean"
    assert flags["feature1"].value is True
    assert flags["feature1"].description == "Common description"
    assert flags["feature2"].type.value == "percentage"
    assert flags["feature2"].value == MAX_PERCENTAGE / 2
    assert flags["feature2"].description == "Common description"
