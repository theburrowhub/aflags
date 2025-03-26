"""
Tests for YAML feature flag source.
"""

import yaml
import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile

from aflags.sources.yaml import YamlSource


def test_valid_yaml_source():
    """Test loading valid YAML feature flags."""
    data = {
        "feature1": {
            "type": "boolean",
            "value": True,
            "description": "Test feature 1"
        },
        "feature2": {
            "type": "percentage",
            "value": 50,
            "description": "Test feature 2"
        },
        "feature3": {
            "type": "per_thousand",
            "value": 500,
            "description": "Test feature 3"
        }
    }
    
    with NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(data, f)
        temp_path = f.name
    
    try:
        source = YamlSource(temp_path)
        flags = source.get_flags()
        
        assert len(flags) == 3
        assert flags["feature1"].type.value == "boolean"
        assert flags["feature1"].value is True
        assert flags["feature2"].type.value == "percentage"
        assert flags["feature2"].value == 50
        assert flags["feature3"].type.value == "per_thousand"
        assert flags["feature3"].value == 500
    finally:
        Path(temp_path).unlink()


def test_missing_type():
    """Test error handling for missing type field."""
    data = {
        "feature1": {
            "value": True
        }
    }
    
    with NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(data, f)
        temp_path = f.name
    
    try:
        source = YamlSource(temp_path)
        with pytest.raises(ValueError) as exc_info:
            source.get_flags()
        assert "Missing 'type' for feature flag" in str(exc_info.value)
    finally:
        Path(temp_path).unlink()


def test_invalid_boolean_value():
    """Test error handling for invalid boolean value."""
    data = {
        "feature1": {
            "type": "boolean",
            "value": "not_a_boolean"
        }
    }
    
    with NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(data, f)
        temp_path = f.name
    
    try:
        source = YamlSource(temp_path)
        with pytest.raises(ValueError) as exc_info:
            source.get_flags()
        assert "Boolean flag" in str(exc_info.value)
    finally:
        Path(temp_path).unlink()


def test_invalid_percentage_value():
    """Test error handling for invalid percentage value."""
    data = {
        "feature1": {
            "type": "percentage",
            "value": 150
        }
    }
    
    with NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(data, f)
        temp_path = f.name
    
    try:
        source = YamlSource(temp_path)
        with pytest.raises(ValueError) as exc_info:
            source.get_flags()
        assert "Value for" in str(exc_info.value)
    finally:
        Path(temp_path).unlink()


def test_nonexistent_file():
    """Test handling of nonexistent file."""
    source = YamlSource("nonexistent.yaml")
    assert source.get_flags() == {}


def test_yaml_specific_features():
    """Test YAML-specific features like anchors and aliases."""
    yaml_data = """
    common_config: &common
      description: "Common description"
    
    feature1:
      <<: *common
      type: boolean
      value: true
    
    feature2:
      <<: *common
      type: percentage
      value: 50
    """
    
    with NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_data)
        temp_path = f.name
    
    try:
        source = YamlSource(temp_path)
        flags = source.get_flags()
        
        assert len(flags) == 2
        assert flags["feature1"].description == "Common description"
        assert flags["feature2"].description == "Common description"
    finally:
        Path(temp_path).unlink() 