"""
JSON file-based feature flag source.
"""

import json
from pathlib import Path
from typing import Dict

from aflags.core import FeatureFlag, FeatureFlagSource


class JsonSource(FeatureFlagSource):
    """Feature flag source that reads from a JSON file."""
    
    def __init__(self, file_path: str):
        """Initialize the JSON source.
        
        Args:
            file_path: Path to the JSON file containing feature flags.
        """
        self._file_path = file_path
    
    def get_flags(self) -> Dict[str, FeatureFlag]:
        """Get all feature flags from the JSON file.
        
        Returns:
            Dict[str, FeatureFlag]: Dictionary of feature flags.
        
        Raises:
            ValueError: If the JSON file contains invalid feature flag configuration.
            json.JSONDecodeError: If the JSON file is invalid.
        """
        if not Path(self._file_path).exists():
            return {}
        
        with open(self._file_path, "r") as f:
            data = json.load(f)
        
        flags = {}
        for name, config in data.items():
            if not isinstance(config, dict):
                continue
            
            if "type" not in config:
                raise ValueError(f"Missing 'type' for feature flag '{name}'")
            
            if "value" not in config:
                raise ValueError(f"Missing 'value' for feature flag '{name}'")
            
            flags[name] = FeatureFlag(
                name=name,
                type=config["type"],
                value=config["value"],
                description=config.get("description")
            )
        
        return flags 