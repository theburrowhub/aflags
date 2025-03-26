"""
Core functionality for AFlags feature flag system.
"""

import hashlib
import random
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Optional, Union

# Constants for percentage and per-thousand values
MAX_PERCENTAGE = 100
MAX_PER_THOUSAND = 1000


class FlagType(str, Enum):
    """Feature flag types."""

    BOOLEAN = "boolean"
    PERCENTAGE = "percentage"
    PER_THOUSAND = "per_thousand"


class FeatureFlag:
    """Represents a feature flag with its configuration."""

    def __init__(
        self,
        name: str,
        type: Union[str, FlagType],
        value: Union[bool, int, float],
        description: Optional[str] = None,
    ):
        """Initialize a feature flag.

        Args:
            name: Flag name
            type: Flag type (boolean, percentage, or per_thousand)
            value: Flag value
            description: Optional flag description
        """
        self.name = name
        try:
            self.type = type if isinstance(type, FlagType) else FlagType(type)
        except ValueError as err:
            raise ValueError("Invalid flag type") from err
        self.value = value
        self.description = description

        # Validate value based on type
        if self.type == FlagType.BOOLEAN:
            if not isinstance(self.value, bool):
                raise ValueError("Boolean flag must have a boolean value")
        elif self.type == FlagType.PERCENTAGE:
            if not isinstance(self.value, (int, float)):
                raise ValueError("Percentage flag must have a numeric value")
            if not 0 <= self.value <= MAX_PERCENTAGE:
                raise ValueError(
                    f"Percentage value must be between 0 and {MAX_PERCENTAGE}"
                )
        elif self.type == FlagType.PER_THOUSAND:
            if not isinstance(self.value, (int, float)):
                raise ValueError("Per-thousand flag must have a numeric value")
            if not 0 <= self.value <= MAX_PER_THOUSAND:
                raise ValueError(
                    f"Per-thousand value must be between 0 and {MAX_PER_THOUSAND}"
                )

    def is_enabled(self, user_id: Optional[str] = None) -> bool:
        """Check if the feature flag is enabled.

        Args:
            user_id: Optional ID of the user to check. If None, treats as anonymous.

        Returns:
            True if the feature flag is enabled for the user, False otherwise.
        """
        if self.type == FlagType.BOOLEAN:
            return bool(self.value)

        if user_id is None:
            # For anonymous users, use random value
            threshold = self.value / (100 if self.type == FlagType.PERCENTAGE else 1000)
            return random.random() < threshold

        # For identified users, use consistent hashing with better distribution
        # Use both name and user_id to ensure different flags get different distributions
        hash_input = f"{self.name}:{user_id}".encode()
        hash_bytes = hashlib.sha256(hash_input).digest()

        # Use the first 8 bytes as a seed for random number generation
        seed = int.from_bytes(hash_bytes[:8], byteorder="big")
        rng = random.Random(seed)

        # Get a random number between 0 and max_value
        max_value = 100 if self.type == FlagType.PERCENTAGE else 1000
        user_value = rng.randint(0, max_value - 1)

        return user_value < self.value


class FeatureFlagSource(ABC):
    """Abstract base class for feature flag data sources."""

    @abstractmethod
    def get_flags(self) -> Dict[str, FeatureFlag]:
        """Get all feature flags from the source.

        Returns:
            Dict[str, FeatureFlag]: Dictionary of feature flags
        """
        pass


class FeatureFlagManager:
    """Manages feature flags from a source."""

    def __init__(self, source: FeatureFlagSource):
        """Initialize the feature flag manager.

        Args:
            source: The source to load feature flags from.
        """
        self._source = source
        self._flags: Dict[str, FeatureFlag] = {}
        self.reload()

    @classmethod
    def from_json(cls, file_path: str) -> "FeatureFlagManager":
        """Create a feature flag manager from a JSON file.

        Args:
            file_path: Path to the JSON file containing feature flags.

        Returns:
            FeatureFlagManager: A new feature flag manager instance.
        """
        from .sources.json import JsonSource

        return cls(JsonSource(file_path))

    @classmethod
    def from_yaml(cls, file_path: str) -> "FeatureFlagManager":
        """Create a feature flag manager from a YAML file.

        Args:
            file_path: Path to the YAML file containing feature flags.

        Returns:
            FeatureFlagManager: A new feature flag manager instance.
        """
        from .sources.yaml import YamlSource

        return cls(YamlSource(file_path))

    @classmethod
    def from_env(cls, prefix: str = "AFLAG_") -> "FeatureFlagManager":
        """Create a feature flag manager from environment variables.

        Args:
            prefix: Prefix for environment variable names. Defaults to "AFLAG_".

        Returns:
            FeatureFlagManager: A new feature flag manager instance.
        """
        from .sources.env import EnvSource

        return cls(EnvSource(prefix))

    def reload(self) -> None:
        """Reload feature flags from the source."""
        self._flags = self._source.get_flags()

    def is_enabled(self, flag_name: str, user_id: Optional[str] = None) -> bool:
        """Check if a feature flag is enabled.

        Args:
            flag_name: The name of the feature flag to check.
            user_id: Optional ID of the user to check. If None, treats as anonymous.

        Returns:
            True if the feature flag is enabled for the user, False otherwise.
        """
        flag = self._flags.get(flag_name)
        return flag.is_enabled(user_id) if flag else False
