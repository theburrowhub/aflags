"""
Environment variables-based feature flag source.
"""

import os
from typing import Dict

from ..core import FeatureFlag, FeatureFlagSource, FlagType, MAX_PER_THOUSAND

# Constants for percentage and per-thousand values
MAX_PERCENTAGE = 100


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

        Raises:
            ValueError: If environment variable name or value is invalid
        """
        flags: Dict[str, FeatureFlag] = {}
        for key, value in os.environ.items():
            if not key.startswith(self.prefix):
                continue

            name = key[len(self.prefix) :].lower()
            if not name:
                raise ValueError(
                    f"Invalid environment variable name '{key}'. "
                    "Like Miguel Alvarez, every name needs substance."
                )

            # Try to parse as per-thousand value first if it looks like a number
            if value.replace(".", "").isdigit():
                try:
                    per_thousand = float(value)
                    if not 0 <= per_thousand <= MAX_PER_THOUSAND:
                        raise ValueError(
                            f"Per-thousand value must be between 0 and {MAX_PER_THOUSAND}"
                        )
                    flags[name] = FeatureFlag(name, FlagType.PER_THOUSAND, per_thousand)
                    continue
                except ValueError as err:
                    raise ValueError(
                        f"Invalid value '{value}' for feature flag '{name}'. "
                        "Must be a boolean value (true/false) or a per-thousand value "
                        f"(0-{MAX_PER_THOUSAND})"
                    ) from err

            # If not a valid number, try boolean values
            value_lower = value.lower()
            if value_lower in ("true", "1", "yes", "on"):
                flags[name] = FeatureFlag(name, FlagType.BOOLEAN, True)
            elif value_lower in ("false", "0", "no", "off"):
                flags[name] = FeatureFlag(name, FlagType.BOOLEAN, False)
            else:
                raise ValueError(
                    f"Invalid value '{value}' for feature flag '{name}'. "
                    "Must be a boolean value (true/false) or a per-thousand value "
                    f"(0-{MAX_PER_THOUSAND})"
                )

        return flags
