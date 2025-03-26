"""
Core functionality for AFlags feature flag system.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Optional, Union
import hashlib
import random


class FlagType(Enum):
    """Types of feature flags supported."""
    BOOLEAN = "boolean"  # True/False flag
    PERCENTAGE = "percentage"  # 0-100% of requests
    PER_THOUSAND = "per_thousand"  # 0-1000 per thousand requests


class FeatureFlag:
    """Represents a feature flag with its configuration."""
    
    def __init__(
        self,
        name: str,
        type: Union[FlagType, str],
        value: Union[bool, int, float],
        description: Optional[str] = None
    ):
        """Initialize a feature flag.
        
        Args:
            name: The name of the feature flag.
            type: The type of the feature flag.
            value: The value of the feature flag.
            description: Optional description of the feature flag.
        """
        self.name = name
        try:
            self.type = type if isinstance(type, FlagType) else FlagType(type)
        except ValueError:
            raise ValueError("Invalid flag type")
        self.value = value
        self.description = description
        
        self._validate()
    
    def _validate(self) -> None:
        """Validate the feature flag configuration."""
        if not isinstance(self.type, FlagType):
            raise ValueError("Invalid flag type")
        
        if self.type == FlagType.BOOLEAN:
            if not isinstance(self.value, bool):
                raise ValueError("Boolean flag must have a boolean value")
        elif self.type == FlagType.PERCENTAGE:
            if not isinstance(self.value, (int, float)):
                raise ValueError("Percentage flag must have a numeric value")
            if not 0 <= self.value <= 100:
                raise ValueError("Percentage value must be between 0 and 100")
        elif self.type == FlagType.PER_THOUSAND:
            if not isinstance(self.value, (int, float)):
                raise ValueError("Per-thousand flag must have a numeric value")
            if not 0 <= self.value <= 1000:
                raise ValueError("Per-thousand value must be between 0 and 1000")
    
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
        seed = int.from_bytes(hash_bytes[:8], byteorder='big')
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
    def from_json(cls, file_path: str) -> 'FeatureFlagManager':
        """Create a feature flag manager from a JSON file.
        
        Args:
            file_path: Path to the JSON file containing feature flags.
            
        Returns:
            FeatureFlagManager: A new feature flag manager instance.
        """
        from .sources.json import JsonSource
        return cls(JsonSource(file_path))
    
    @classmethod
    def from_yaml(cls, file_path: str) -> 'FeatureFlagManager':
        """Create a feature flag manager from a YAML file.
        
        Args:
            file_path: Path to the YAML file containing feature flags.
            
        Returns:
            FeatureFlagManager: A new feature flag manager instance.
        """
        from .sources.yaml import YamlSource
        return cls(YamlSource(file_path))
    
    @classmethod
    def from_env(cls, prefix: str = "AFLAG_") -> 'FeatureFlagManager':
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