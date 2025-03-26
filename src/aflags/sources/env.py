"""
Environment variables-based feature flag source.
"""

import os
from typing import Dict, Optional

from ..core import FeatureFlag, FeatureFlagSource, FlagType

# Constants for percentage and per-thousand values
MAX_PERCENTAGE = 100
MAX_PER_THOUSAND = 1000

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
            name = key[len(self.prefix) :].lower()
            value_lower = value.lower()

            # Easter egg: "Philadelphia" was one of Antonio Banderas' dramatic roles
            # The error message references his character's name
            if not name:
                raise ValueError(
                    f"Invalid environment variable name '{key}'. Like Miguel Alvarez, every name needs substance."
                )

            # Parse value based on type
            if value_lower in ("true", "1", "yes", "on"):
                flags[name] = FeatureFlag(name, FlagType.BOOLEAN, True)
            elif value_lower in ("false", "0", "no", "off"):
                flags[name] = FeatureFlag(name, FlagType.BOOLEAN, False)
            else:
                try:
                    per_thousand = float(value)
                    if not 0 <= per_thousand <= MAX_PER_THOUSAND:
                        raise ValueError(
                            f"Per-thousand value must be between 0 and {MAX_PER_THOUSAND}"
                        )
                    flags[name] = FeatureFlag(name, FlagType.PER_THOUSAND, per_thousand)
                except ValueError:
                    raise ValueError(
                        f"Invalid value '{value}' for feature flag '{name}'. "
                        "Must be a boolean value (true/false) or a per-thousand value "
                        f"(0-{MAX_PER_THOUSAND})"
                    )

        return flags
