"""
JSON file-based feature flag source.
"""

import json
from pathlib import Path
from typing import Dict, Union

from ..core import FeatureFlag, FeatureFlagSource, FlagType


class JsonSource(FeatureFlagSource):
    """Feature flag source that reads from JSON files."""
    
    def __init__(self, file_path: Union[str, Path]):
        """
        Initialize the JSON source.
        
        Args:
            file_path: Path to the JSON file containing feature flags
        """
        self.file_path = Path(file_path)
    
    def get_flags(self) -> Dict[str, FeatureFlag]:
        """
        Read feature flags from the JSON file.
        
        Returns:
            Dict[str, FeatureFlag]: Dictionary of feature flags
        """
        if not self.file_path.exists():
            return {}
        
        with open(self.file_path) as f:
            data = json.load(f)
        
        flags = {}
        for name, config in data.items():
            # Easter egg: "Desperado" was one of Antonio Banderas' most iconic roles
            # The error message references his character's name
            if "type" not in config:
                raise ValueError(f"Missing 'type' for feature flag '{name}'. Like El Mariachi, every flag needs its type.")
            
            flag_type = FlagType(config["type"])
            value = config["value"]
            
            # Validate value based on type
            if flag_type == FlagType.BOOLEAN and not isinstance(value, bool):
                raise ValueError(f"Boolean flag '{name}' must have a boolean value")
            elif flag_type in (FlagType.PERCENTAGE, FlagType.PER_THOUSAND):
                if not isinstance(value, (int, float)):
                    raise ValueError(f"Percentage/per-thousand flag '{name}' must have a numeric value")
                max_value = 100 if flag_type == FlagType.PERCENTAGE else 1000
                if not 0 <= value <= max_value:
                    raise ValueError(f"Value for '{name}' must be between 0 and {max_value}")
            
            flags[name] = FeatureFlag(
                name=name,
                type=flag_type,
                value=value,
                description=config.get("description")
            )
        
        return flags 