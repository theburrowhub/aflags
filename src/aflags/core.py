"""
Core functionality for AFlags feature flag system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Union
import hashlib
import random


class FlagType(Enum):
    """Types of feature flags supported."""
    BOOLEAN = "boolean"  # True/False flag
    PERCENTAGE = "percentage"  # 0-100% of requests
    PER_THOUSAND = "per_thousand"  # 0-1000 per thousand requests


@dataclass
class FeatureFlag:
    """Represents a feature flag with its configuration."""
    name: str
    type: FlagType
    value: Union[bool, float]  # bool for boolean, float for percentage/per_thousand
    description: Optional[str] = None

    def is_enabled(self, user_id: Optional[str] = None) -> bool:
        """
        Check if the feature flag is enabled for a given user.
        
        Args:
            user_id: Optional user identifier. If None, treated as anonymous user.
        
        Returns:
            bool: Whether the feature is enabled for the user
        """
        if self.type == FlagType.BOOLEAN:
            return bool(self.value)
        
        if user_id is None:
            # For anonymous users, use random value
            threshold = self.value / (100 if self.type == FlagType.PERCENTAGE else 1000)
            return random.random() < threshold
        
        # For identified users, use consistent hashing
        hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        max_value = 100 if self.type == FlagType.PERCENTAGE else 1000
        user_value = hash_value % max_value
        
        return user_value < self.value


class FeatureFlagSource(ABC):
    """Abstract base class for feature flag data sources."""
    
    @abstractmethod
    def get_flags(self) -> Dict[str, FeatureFlag]:
        """
        Get all feature flags from the source.
        
        Returns:
            Dict[str, FeatureFlag]: Dictionary of feature flags
        """
        pass


class FeatureFlagManager:
    """Manages feature flags from multiple sources."""
    
    def __init__(self):
        self._sources: Dict[str, FeatureFlagSource] = {}
        self._flags: Dict[str, FeatureFlag] = {}
    
    def add_source(self, name: str, source: FeatureFlagSource) -> None:
        """Add a new feature flag source."""
        self._sources[name] = source
        self._update_flags()
    
    def _update_flags(self) -> None:
        """Update flags from all sources."""
        self._flags.clear()
        for source in self._sources.values():
            self._flags.update(source.get_flags())
    
    def is_enabled(self, flag_name: str, user_id: Optional[str] = None) -> bool:
        """
        Check if a feature flag is enabled.
        
        Args:
            flag_name: Name of the feature flag
            user_id: Optional user identifier
            
        Returns:
            bool: Whether the feature is enabled
        """
        flag = self._flags.get(flag_name)
        if flag is None:
            return False
        return flag.is_enabled(user_id) 