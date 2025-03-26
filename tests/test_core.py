"""
Tests for core feature flag functionality.
"""

import pytest
from aflags.core import FeatureFlag, FlagType, FeatureFlagManager
from aflags.sources.json import JsonSource


def test_boolean_flag():
    """Test boolean feature flag behavior."""
    flag = FeatureFlag(
        name="test_flag",
        type=FlagType.BOOLEAN,
        value=True
    )
    assert flag.is_enabled() is True
    assert flag.is_enabled("user123") is True
    
    flag = FeatureFlag(
        name="test_flag",
        type=FlagType.BOOLEAN,
        value=False
    )
    assert flag.is_enabled() is False
    assert flag.is_enabled("user123") is False


def test_percentage_flag():
    """Test percentage-based feature flag behavior."""
    flag = FeatureFlag(
        name="test_flag",
        type=FlagType.PERCENTAGE,
        value=100
    )
    assert flag.is_enabled("user123") is True
    
    flag = FeatureFlag(
        name="test_flag",
        type=FlagType.PERCENTAGE,
        value=0
    )
    assert flag.is_enabled("user123") is False


def test_per_thousand_flag():
    """Test per-thousand feature flag behavior."""
    flag = FeatureFlag(
        name="test_flag",
        type=FlagType.PER_THOUSAND,
        value=1000
    )
    assert flag.is_enabled("user123") is True
    
    flag = FeatureFlag(
        name="test_flag",
        type=FlagType.PER_THOUSAND,
        value=0
    )
    assert flag.is_enabled("user123") is False


def test_anonymous_user():
    """Test feature flag behavior for anonymous users."""
    flag = FeatureFlag(
        name="test_flag",
        type=FlagType.PERCENTAGE,
        value=50
    )
    # For anonymous users, we expect random behavior
    # Run multiple times to ensure we get both True and False
    results = [flag.is_enabled() for _ in range(100)]
    assert any(results)  # At least one True
    assert not all(results)  # Not all True


def test_consistent_user_assignment():
    """Test that feature flag assignment is consistent for the same user."""
    flag = FeatureFlag(
        name="test_flag",
        type=FlagType.PERCENTAGE,
        value=50
    )
    user_id = "test_user"
    
    # Same user should get same result multiple times
    results = [flag.is_enabled(user_id) for _ in range(10)]
    assert all(results) == any(results)  # All results should be the same 