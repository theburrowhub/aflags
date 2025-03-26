# AFlags: Feature Flag Management for Python

AFlags is a flexible and easy-to-use feature flag management library for Python applications. It supports multiple flag types and data sources, making it perfect for managing feature rollouts and A/B testing.

## Features

- Multiple flag types:
  - Boolean flags (on/off)
  - Percentage-based rollouts (0-100%)
  - Per-thousand rollouts (0-1000‰)
- Multiple configuration sources:
  - JSON files
  - YAML files
  - Environment variables
- Consistent user-based flag evaluation
- Anonymous user support
- Type validation and error handling
- Easy to extend with custom sources

## Installation

```bash
pip install aflags
```

## Quick Start

```python
from aflags.core import FeatureFlagManager
from aflags.sources.json import JsonSource

# Initialize with JSON source
manager = FeatureFlagManager(JsonSource("flags.json"))

# Check if a feature is enabled for anonymous user
if manager.is_enabled("my_feature"):
    # Feature is enabled
    pass

# Check if a feature is enabled for a specific user
if manager.is_enabled("my_feature", user_id="user123"):
    # Feature is enabled for user123
    pass
```

## Configuration Examples

### JSON Configuration

```json
{
    "dark_mode": {
        "type": "boolean",
        "value": true,
        "description": "Enable dark mode for all users"
    },
    "new_ui": {
        "type": "percentage",
        "value": 50,
        "description": "Roll out new UI to 50% of users"
    },
    "beta_feature": {
        "type": "per_thousand",
        "value": 100,
        "description": "Enable beta feature for 10% of users"
    }
}
```

### YAML Configuration

```yaml
dark_mode:
  type: boolean
  value: true
  description: Enable dark mode for all users

new_ui:
  type: percentage
  value: 50
  description: Roll out new UI to 50% of users

beta_feature:
  type: per_thousand
  value: 100
  description: Enable beta feature for 10% of users
```

### Environment Variables

```bash
FEATURE_DARK_MODE=true
FEATURE_NEW_UI=50%
FEATURE_BETA=100‰
```

## Usage Examples

### Basic Usage

```python
from aflags.core import FeatureFlagManager
from aflags.sources.json import JsonSource

# Initialize manager with JSON source
manager = FeatureFlagManager(JsonSource("flags.json"))

# Check boolean flag for anonymous user
if manager.is_enabled("dark_mode"):
    enable_dark_mode()

# Check percentage-based flag for a specific user
if manager.is_enabled("new_ui", user_id="user123"):
    show_new_ui()

# Check per-thousand flag for anonymous user
if manager.is_enabled("beta_feature"):
    enable_beta_features()
```

### Using Multiple Sources

```python
from aflags.core import FeatureFlagManager
from aflags.sources.yaml import YamlSource
from aflags.sources.env import EnvSource

# Use YAML for main configuration
manager = FeatureFlagManager(YamlSource("flags.yaml"))

# Or use environment variables
manager = FeatureFlagManager(EnvSource())

# Reload flags at runtime
manager.reload()
```

### Custom Source Implementation

```python
from aflags.core import FeatureFlagSource, FeatureFlag
from typing import Dict

class DatabaseSource(FeatureFlagSource):
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_flags(self) -> Dict[str, FeatureFlag]:
        flags = {}
        # Implement database fetching logic
        return flags

# Use custom source
manager = FeatureFlagManager(DatabaseSource(db_connection))
```

## Feature Types

### Boolean Flags

Simple on/off flags that are either enabled or disabled for all users.

```python
# Configuration
{
    "feature": {
        "type": "boolean",
        "value": true
    }
}

# Usage
is_enabled = manager.is_enabled("feature")
```

### Percentage Flags

Roll out features to a percentage of users (0-100%).

```python
# Configuration
{
    "feature": {
        "type": "percentage",
        "value": 50  # Enable for 50% of users
    }
}

# Usage
is_enabled = manager.is_enabled("feature", user_id="user123")
```

### Per-Thousand Flags

Fine-grained control with per-thousand precision (0-1000‰).

```python
# Configuration
{
    "feature": {
        "type": "per_thousand",
        "value": 100  # Enable for 10% of users (100‰)
    }
}

# Usage
is_enabled = manager.is_enabled("feature", user_id="user123")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 