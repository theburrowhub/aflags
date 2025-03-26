"""
YAML file-based feature flag source.
"""

import yaml
from pathlib import Path
from typing import Dict

from aflags.core import FeatureFlag, FeatureFlagSource


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

        with open(self._file_path, "r") as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise yaml.YAMLError(f"Invalid YAML file: {str(e)}")

        if not data:
            return {}

        flags = {}
        for name, config in data.items():
            if not isinstance(config, dict):
                continue

            # Skip entries that don't look like feature flags
            if "type" not in config and "value" not in config:
                continue

            if "type" not in config:
                raise ValueError(f"Missing 'type' for feature flag '{name}'")

            if "value" not in config:
                raise ValueError(f"Missing 'value' for feature flag '{name}'")

            try:
                flags[name] = FeatureFlag(
                    name=name,
                    type=config["type"],
                    value=config["value"],
                    description=config.get("description"),
                )
            except ValueError as e:
                raise ValueError(
                    f"Invalid configuration for feature flag '{name}': {str(e)}"
                )

        return flags
