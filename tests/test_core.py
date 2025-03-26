"""
Tests for core feature flag functionality.
"""

import pytest

from aflags.core import FeatureFlag, FeatureFlagManager, FeatureFlagSource, FlagType
from aflags.sources.env import EnvSource
from aflags.sources.json import JsonSource
from aflags.sources.yaml import YamlSource

# Constants for percentage and per-thousand values
MAX_PERCENTAGE = 100
MAX_PER_THOUSAND = 1000


def test_boolean_flag():
    """Test boolean feature flag."""
    flag = FeatureFlag(
        name="test_flag", type=FlagType.BOOLEAN, value=True, description="Test flag"
    )

    assert flag.name == "test_flag"
    assert flag.type == FlagType.BOOLEAN
    assert flag.value is True
    assert flag.description == "Test flag"


def test_percentage_flag():
    """Test percentage feature flag."""
    flag = FeatureFlag(
        name="test_flag",
        type=FlagType.PERCENTAGE,
        value=MAX_PERCENTAGE / 2,
        description="Test flag",
    )

    assert flag.name == "test_flag"
    assert flag.type == FlagType.PERCENTAGE
    assert flag.value == MAX_PERCENTAGE / 2
    assert flag.description == "Test flag"


def test_per_thousand_flag():
    """Test per-thousand feature flag."""
    flag = FeatureFlag(
        name="test_flag",
        type=FlagType.PER_THOUSAND,
        value=MAX_PER_THOUSAND / 2,
        description="Test flag",
    )

    assert flag.name == "test_flag"
    assert flag.type == FlagType.PER_THOUSAND
    assert flag.value == MAX_PER_THOUSAND / 2
    assert flag.description == "Test flag"


def test_anonymous_user():
    """Test feature flag evaluation for anonymous user."""
    flag = FeatureFlag(name="test_flag", type=FlagType.BOOLEAN, value=True)

    # Both calls should work the same for anonymous users
    assert flag.is_enabled() is True
    assert flag.is_enabled(user_id=None) is True


def test_consistent_user_assignment():
    """Test consistent user assignment for percentage/per-thousand flags."""
    flag = FeatureFlag(
        name="test_flag", type=FlagType.PERCENTAGE, value=MAX_PERCENTAGE / 2
    )

    # Same user should get consistent results
    user_id = "test_user"
    result1 = flag.is_enabled(user_id=user_id)
    result2 = flag.is_enabled(user_id=user_id)
    assert result1 == result2

    # Different users should get different results
    other_user = "other_user"
    result3 = flag.is_enabled(user_id=other_user)
    assert result1 != result3


def test_invalid_flag_type():
    """Test error handling for invalid flag type."""
    with pytest.raises(ValueError) as exc_info:
        FeatureFlag(
            name="test_flag",
            type="invalid_type",  # type: ignore
            value=True,
        )
    assert "Invalid flag type" in str(exc_info.value)


def test_invalid_boolean_value():
    """Test error handling for invalid boolean value."""
    with pytest.raises(ValueError) as exc_info:
        FeatureFlag(
            name="test_flag",
            type=FlagType.BOOLEAN,
            value="not_a_boolean",  # type: ignore
        )
    assert "Boolean flag must have a boolean value" in str(exc_info.value)


def test_invalid_percentage_value():
    """Test error handling for invalid percentage value."""
    with pytest.raises(ValueError) as exc_info:
        FeatureFlag(
            name="test_flag",
            type=FlagType.PERCENTAGE,
            value="not_a_number",  # type: ignore
        )
    assert "Percentage flag must have a numeric value" in str(exc_info.value)


def test_invalid_percentage_range():
    """Test error handling for percentage value out of range."""
    with pytest.raises(ValueError) as exc_info:
        FeatureFlag(
            name="test_flag",
            type=FlagType.PERCENTAGE,
            value=150,  # Value above 100
        )
    assert "Percentage value must be between 0 and 100" in str(exc_info.value)


def test_invalid_per_thousand_value():
    """Test error handling for invalid per-thousand value."""
    with pytest.raises(ValueError) as exc_info:
        FeatureFlag(
            name="test_flag",
            type=FlagType.PER_THOUSAND,
            value="not_a_number",  # type: ignore
        )
    assert "Per-thousand flag must have a numeric value" in str(exc_info.value)


def test_invalid_per_thousand_range():
    """Test error handling for per-thousand value out of range."""
    with pytest.raises(ValueError) as exc_info:
        FeatureFlag(
            name="test_flag",
            type=FlagType.PER_THOUSAND,
            value=1500,  # Value above 1000
        )
    assert "Per-thousand value must be between 0 and 1000" in str(exc_info.value)


def test_feature_flag_manager():
    """Test feature flag manager functionality."""

    class MockSource(FeatureFlagSource):
        def get_flags(self):
            return {
                "test_flag": FeatureFlag(
                    name="test_flag", type=FlagType.BOOLEAN, value=True
                )
            }

    manager = FeatureFlagManager(MockSource())
    # Test with and without user_id
    assert manager.is_enabled("test_flag") is True
    assert manager.is_enabled("test_flag", user_id="test_user") is True
    assert manager.is_enabled("nonexistent_flag") is False
    assert manager.is_enabled("nonexistent_flag", user_id="test_user") is False


def test_feature_flag_manager_reload():
    """Test feature flag manager reload functionality."""

    class MockSource(FeatureFlagSource):
        def __init__(self):
            self.value = True

        def get_flags(self):
            return {
                "test_flag": FeatureFlag(
                    name="test_flag", type=FlagType.BOOLEAN, value=self.value
                )
            }

    source = MockSource()
    manager = FeatureFlagManager(source)
    assert manager.is_enabled("test_flag") is True

    # Change the flag value
    source.value = False
    manager.reload()
    assert manager.is_enabled("test_flag") is False


def test_feature_flag_manager_constructors():
    """Test semantic constructors for feature flag manager."""
    # Test JSON constructor
    json_manager = FeatureFlagManager.from_json("flags.json")
    assert isinstance(json_manager._source, JsonSource)
    assert json_manager._source._file_path == "flags.json"

    # Test YAML constructor
    yaml_manager = FeatureFlagManager.from_yaml("flags.yaml")
    assert isinstance(yaml_manager._source, YamlSource)
    assert yaml_manager._source._file_path == "flags.yaml"

    # Test environment constructor with default prefix
    env_manager = FeatureFlagManager.from_env()
    assert isinstance(env_manager._source, EnvSource)
    assert env_manager._source.prefix == "AFLAG_"

    # Test environment constructor with custom prefix
    custom_env_manager = FeatureFlagManager.from_env(prefix="CUSTOM_")
    assert isinstance(custom_env_manager._source, EnvSource)
    assert custom_env_manager._source.prefix == "CUSTOM_"
