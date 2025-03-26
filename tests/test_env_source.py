"""
Tests for environment variables feature flag source.
"""

import os
import pytest
from unittest.mock import patch

from aflags.sources.env import EnvSource


def test_boolean_flags():
    """Test boolean feature flags from environment variables."""
    env_vars = {
        "AFLAG_FEATURE1": "true",
        "AFLAG_FEATURE2": "false",
        "AFLAG_FEATURE3": "yes",
        "AFLAG_FEATURE4": "no",
        "AFLAG_FEATURE5": "on",
        "AFLAG_FEATURE6": "off",
    }

    with patch.dict(os.environ, env_vars):
        source = EnvSource()
        flags = source.get_flags()

        assert len(flags) == 6
        assert flags["feature1"].type.value == "boolean"
        assert flags["feature1"].value is True
        assert flags["feature2"].type.value == "boolean"
        assert flags["feature2"].value is False
        assert flags["feature3"].type.value == "boolean"
        assert flags["feature3"].value is True
        assert flags["feature4"].type.value == "boolean"
        assert flags["feature4"].value is False
        assert flags["feature5"].type.value == "boolean"
        assert flags["feature5"].value is True
        assert flags["feature6"].type.value == "boolean"
        assert flags["feature6"].value is False


def test_per_thousand_flags():
    """Test per-thousand feature flags from environment variables."""
    env_vars = {
        "AFLAG_FEATURE1": "500",
        "AFLAG_FEATURE2": "0",
        "AFLAG_FEATURE3": "1000",
        "AFLAG_FEATURE4": "750.5",
        "AFLAG_FEATURE5": "1",
    }

    with patch.dict(os.environ, env_vars):
        source = EnvSource()
        flags = source.get_flags()

        assert len(flags) == 5
        assert flags["feature1"].type.value == "per_thousand"
        assert flags["feature1"].value == 500
        assert flags["feature2"].type.value == "per_thousand"
        assert flags["feature2"].value == 0
        assert flags["feature3"].type.value == "per_thousand"
        assert flags["feature3"].value == 1000
        assert flags["feature4"].type.value == "per_thousand"
        assert flags["feature4"].value == 750.5
        assert flags["feature5"].type.value == "per_thousand"
        assert flags["feature5"].value == 1


def test_invalid_per_thousand_value():
    """Test error handling for invalid per-thousand value."""
    env_vars = {
        "AFLAG_FEATURE1": "1500"  # Value above 1000
    }

    with patch.dict(os.environ, env_vars):
        source = EnvSource()
        with pytest.raises(ValueError) as exc_info:
            source.get_flags()
        assert "Per-thousand value must be between 0 and 1000" in str(exc_info.value)


def test_invalid_value():
    """Test error handling for invalid value."""
    env_vars = {"AFLAG_FEATURE1": "invalid"}

    with patch.dict(os.environ, env_vars):
        source = EnvSource()
        with pytest.raises(ValueError) as exc_info:
            source.get_flags()
        assert "Invalid value" in str(exc_info.value)


def test_empty_name():
    """Test error handling for empty feature name."""
    env_vars = {
        "AFLAG_": "true"  # Empty name after prefix
    }

    with patch.dict(os.environ, env_vars):
        source = EnvSource()
        with pytest.raises(ValueError) as exc_info:
            source.get_flags()
        assert "Invalid environment variable name" in str(exc_info.value)


def test_custom_prefix():
    """Test using a custom prefix for environment variables."""
    env_vars = {"CUSTOM_FEATURE1": "true", "CUSTOM_FEATURE2": "500"}

    with patch.dict(os.environ, env_vars):
        source = EnvSource(prefix="CUSTOM_")
        flags = source.get_flags()

        assert len(flags) == 2
        assert flags["feature1"].type.value == "boolean"
        assert flags["feature1"].value is True
        assert flags["feature2"].type.value == "per_thousand"
        assert flags["feature2"].value == 500


def test_no_flags():
    """Test when no feature flags are defined in environment."""
    with patch.dict(os.environ, {}, clear=True):
        source = EnvSource()
        flags = source.get_flags()
        assert len(flags) == 0
