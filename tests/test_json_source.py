"""
Tests for JSON file-based feature flag source.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from aflags.sources.json import JsonSource


def test_valid_json_source():
    """Test loading feature flags from a valid JSON file."""
    json_data = {
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
    
    mock_file = mock_open()
    mock_file.return_value.read.return_value = json.dumps(json_data)
    
    with patch("builtins.open", mock_file):
        with patch.object(Path, "exists", return_value=True):
            source = JsonSource("test.json")
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
    json_data = {
        "feature1": {
            "value": True
        }
    }
    
    mock_file = mock_open()
    mock_file.return_value.read.return_value = json.dumps(json_data)
    
    with patch("builtins.open", mock_file):
        with patch.object(Path, "exists", return_value=True):
            source = JsonSource("test.json")
            with pytest.raises(ValueError) as exc_info:
                source.get_flags()
            assert "Missing 'type' for feature flag" in str(exc_info.value)


def test_invalid_boolean_value():
    """Test error handling for invalid boolean value."""
    json_data = {
        "feature1": {
            "type": "boolean",
            "value": "not_a_boolean"
        }
    }
    
    mock_file = mock_open()
    mock_file.return_value.read.return_value = json.dumps(json_data)
    
    with patch("builtins.open", mock_file):
        with patch.object(Path, "exists", return_value=True):
            source = JsonSource("test.json")
            with pytest.raises(ValueError) as exc_info:
                source.get_flags()
            assert "Boolean flag must have a boolean value" in str(exc_info.value)


def test_invalid_percentage_value():
    """Test error handling for invalid percentage value."""
    json_data = {
        "feature1": {
            "type": "percentage",
            "value": "not_a_number"
        }
    }
    
    mock_file = mock_open()
    mock_file.return_value.read.return_value = json.dumps(json_data)
    
    with patch("builtins.open", mock_file):
        with patch.object(Path, "exists", return_value=True):
            source = JsonSource("test.json")
            with pytest.raises(ValueError) as exc_info:
                source.get_flags()
            assert "Percentage flag must have a numeric value" in str(exc_info.value)


def test_nonexistent_file():
    """Test handling of nonexistent JSON file."""
    with patch.object(Path, "exists", return_value=False):
        source = JsonSource("nonexistent.json")
        flags = source.get_flags()
        assert len(flags) == 0


def test_invalid_json():
    """Test error handling for invalid JSON data."""
    mock_file = mock_open()
    mock_file.return_value.read.return_value = "invalid json"
    
    with patch("builtins.open", mock_file):
        with patch.object(Path, "exists", return_value=True):
            source = JsonSource("test.json")
            with pytest.raises(json.JSONDecodeError):
                source.get_flags() 