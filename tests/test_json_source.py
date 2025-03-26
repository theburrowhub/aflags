"""
Tests for JSON feature flag source.
"""

import json
import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile

from aflags.sources.json import JsonSource


def test_valid_json_source():
    """Test loading valid JSON feature flags."""
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
    
    with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f)
        temp_path = f.name
    
    try:
        source = JsonSource(temp_path)
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
    
    with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f)
        temp_path = f.name
    
    try:
        source = JsonSource(temp_path)
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
    
    with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f)
        temp_path = f.name
    
    try:
        source = JsonSource(temp_path)
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
    
    with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f)
        temp_path = f.name
    
    try:
        source = JsonSource(temp_path)
        with pytest.raises(ValueError) as exc_info:
            source.get_flags()
        assert "Value for" in str(exc_info.value)
    finally:
        Path(temp_path).unlink()


def test_nonexistent_file():
    """Test handling of nonexistent file."""
    source = JsonSource("nonexistent.json")
    assert source.get_flags() == {} 