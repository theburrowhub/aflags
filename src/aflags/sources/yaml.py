"""
YAML file-based feature flag source.
"""

from pathlib import Path
from typing import Dict

import yaml

from aflags.core import FeatureFlag, FeatureFlagSource

# Constants for percentage and per-thousand values
MAX_PERCENTAGE = 100
MAX_PER_THOUSAND = 1000


class YamlSource(FeatureFlagSource):
    """Feature flag source that reads from a YAML file."""

    def __init__(self, file_path: str):
        """Initialize the YAML source.

        Args:
            file_path: Path to the YAML file containing feature flags.
        """
        self._file_path = file_path

    def get_flags(self) -> Dict[str, FeatureFlag]:
        """Get all feature flags from the YAML file.

        Returns:
            Dict[str, FeatureFlag]: Dictionary of feature flags.

        Raises:
            ValueError: If the YAML file contains invalid feature flag configuration.
            yaml.YAMLError: If the YAML file is invalid.
        """
        if not Path(self._file_path).exists():
            return {}

        try:
            with open(self._file_path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as err:
            raise yaml.YAMLError(f"Invalid YAML file: {err!s}") from err

        if not data:
            return {}

        flags = {}
        for name, config in data.items():
            if not isinstance(config, dict):
                raise ValueError(f"Invalid configuration for feature flag '{name}'")

            try:
                flag_type = config.get("type", "boolean")
                value = config.get("value")
                description = config.get("description")

                if flag_type == "boolean":
                    if not isinstance(value, bool):
                        raise ValueError("Boolean flag must have a boolean value")
                elif flag_type == "percentage":
                    if not isinstance(value, (int, float)):
                        raise ValueError("Percentage flag must have a numeric value")
                    if not 0 <= value <= MAX_PERCENTAGE:
                        raise ValueError(
                            f"Percentage value must be between 0 and {MAX_PERCENTAGE}"
                        )
                elif flag_type == "per_thousand":
                    if not isinstance(value, (int, float)):
                        raise ValueError("Per-thousand flag must have a numeric value")
                    if not 0 <= value <= MAX_PER_THOUSAND:
                        raise ValueError(
                            f"Per-thousand value must be between 0 and {MAX_PER_THOUSAND}"
                        )
                else:
                    raise ValueError(f"Invalid flag type: {flag_type}")

                flags[name] = FeatureFlag(name, flag_type, value, description)
            except ValueError as err:
                raise ValueError(
                    f"Invalid configuration for feature flag '{name}': {err!s}"
                ) from err

        return flags
