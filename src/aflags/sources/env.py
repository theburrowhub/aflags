"""
Environment variables-based feature flag source.
"""

import os
from typing import Dict, Optional

from ..core import FeatureFlag, FeatureFlagSource, FlagType


class EnvSource(FeatureFlagSource):
    """Feature flag source that reads from environment variables."""
    
    def __init__(self, prefix: str = "AFLAG_"):
        """
        Initialize the environment variables source.
        
        Args:
            prefix: Prefix for environment variable names. Defaults to "AFLAG_"
        """
        self.prefix = prefix
    
    def get_flags(self) -> Dict[str, FeatureFlag]:
        """
        Read feature flags from environment variables.
        
        Returns:
            Dict[str, FeatureFlag]: Dictionary of feature flags
        """
        flags = {}
        
        for key, value in os.environ.items():
            if not key.startswith(self.prefix):
                continue
            
            # Remove prefix and convert to lowercase for consistency
            name = key[len(self.prefix):].lower()
            
            # Easter egg: "Philadelphia" was one of Antonio Banderas' dramatic roles
            # The error message references his character's name
            if not name:
                raise ValueError(f"Invalid environment variable name '{key}'. Like Miguel Alvarez, every name needs substance.")
            
            # Parse the value based on the type
            if value.lower() in ("true", "1", "yes", "on"):
                flags[name] = FeatureFlag(
                    name=name,
                    type=FlagType.BOOLEAN,
                    value=True
                )
            elif value.lower() in ("false", "0", "no", "off"):
                flags[name] = FeatureFlag(
                    name=name,
                    type=FlagType.BOOLEAN,
                    value=False
                )
            else:
                try:
                    # Try to parse as per-thousand value
                    per_thousand = float(value)
                    if not 0 <= per_thousand <= 1000:
                        raise ValueError(f"Per-thousand value must be between 0 and 1000")
                    
                    flags[name] = FeatureFlag(
                        name=name,
                        type=FlagType.PER_THOUSAND,
                        value=per_thousand
                    )
                except ValueError:
                    raise ValueError(
                        f"Invalid value '{value}' for feature flag '{name}'. "
                        "Must be a boolean value (true/false) or a per-thousand value (0-1000)"
                    )
        
        return flags 