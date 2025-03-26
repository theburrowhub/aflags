# AFlags API Documentation

## Core Components

### FeatureFlag

The `FeatureFlag` class represents a single feature flag with its configuration.

```python
from aflags.core import FeatureFlag, FlagType

flag = FeatureFlag(
    name="my_feature",
    type=FlagType.BOOLEAN,
    value=True,
    description="Optional description"
)
```

#### Parameters

- `name` (str): The unique identifier for the feature flag
- `type` (Union[FlagType, str]): The type of the feature flag (boolean, percentage, or per_thousand)
- `value` (Union[bool, int, float]): The value of the feature flag
- `description` (Optional[str]): Optional description of the feature flag

#### Methods

##### is_enabled() -> bool

Check if the feature flag is enabled for anonymous users.

```python
is_enabled = flag.is_enabled()
```

##### is_enabled_for_user(user_id: Optional[str]) -> bool

Check if the feature flag is enabled for a specific user.

```python
is_enabled = flag.is_enabled_for_user("user123")
```

### FlagType

An enumeration of supported feature flag types.

```python
from aflags.core import FlagType

FlagType.BOOLEAN       # True/False flag
FlagType.PERCENTAGE    # 0-100% of requests
FlagType.PER_THOUSAND  # 0-1000 per thousand requests
```

### FeatureFlagManager

The main class for managing feature flags from a source.

```python
from aflags.core import FeatureFlagManager
from aflags.sources.json import JsonSource

manager = FeatureFlagManager(JsonSource("flags.json"))
```

#### Methods

##### reload() -> None

Reload feature flags from the source.

```python
manager.reload()
```

##### is_enabled(flag_name: str) -> bool

Check if a feature flag is enabled for anonymous users.

```python
if manager.is_enabled("my_feature"):
    # Feature is enabled
    pass
```

##### is_enabled_for_user(flag_name: str, user_id: str) -> bool

Check if a feature flag is enabled for a specific user.

```python
if manager.is_enabled_for_user("my_feature", "user123"):
    # Feature is enabled for user123
    pass
```

## Sources

### JsonSource

Load feature flags from a JSON file.

```python
from aflags.sources.json import JsonSource

source = JsonSource("flags.json")
```

#### JSON Format

```json
{
    "feature_name": {
        "type": "boolean|percentage|per_thousand",
        "value": true|50|500,
        "description": "Optional description"
    }
}
```

### YamlSource

Load feature flags from a YAML file.

```python
from aflags.sources.yaml import YamlSource

source = YamlSource("flags.yaml")
```

#### YAML Format

```yaml
feature_name:
  type: boolean|percentage|per_thousand
  value: true|50|500
  description: Optional description
```

### EnvSource

Load feature flags from environment variables.

```python
from aflags.sources.env import EnvSource

source = EnvSource(prefix="FEATURE_")  # Default prefix
```

#### Environment Variable Format

- Boolean flags: `FEATURE_NAME=true|false`
- Percentage flags: `FEATURE_NAME=50%`
- Per-thousand flags: `FEATURE_NAME=500‰`

### Custom Sources

You can create custom sources by implementing the `FeatureFlagSource` abstract base class.

```python
from aflags.core import FeatureFlagSource, FeatureFlag
from typing import Dict

class CustomSource(FeatureFlagSource):
    def get_flags(self) -> Dict[str, FeatureFlag]:
        # Implement your logic to load and return feature flags
        return {}
```

## Value Ranges and Validation

### Boolean Flags
- Valid values: `True` or `False`
- Invalid values raise `ValueError`

### Percentage Flags
- Valid range: 0-100
- Must be numeric (int or float)
- Values outside range raise `ValueError`

### Per-Thousand Flags
- Valid range: 0-1000
- Must be numeric (int or float)
- Values outside range raise `ValueError`

## User Assignment

### Anonymous Users
- Random assignment on each check
- Not consistent between checks
- Based on flag value percentage

### Identified Users
- Consistent assignment based on user ID
- Same user gets same result for same flag
- Different users likely get different results
- Based on SHA-256 hash of flag name and user ID

## Error Handling

The library uses standard Python exceptions for error handling:

- `ValueError`: Invalid flag type, value, or configuration
- `FileNotFoundError`: Source file not found
- `json.JSONDecodeError`: Invalid JSON format
- `yaml.YAMLError`: Invalid YAML format

Example error handling:

```python
try:
    manager = FeatureFlagManager(JsonSource("flags.json"))
    is_enabled = manager.is_enabled("my_feature")
except ValueError as e:
    print(f"Invalid configuration: {e}")
except FileNotFoundError:
    print("Configuration file not found")
except json.JSONDecodeError:
    print("Invalid JSON format")
```

## Best Practices

1. **Configuration Management**
   - Keep flag configurations in version control
   - Use descriptive flag names
   - Include descriptions for flags
   - Regular cleanup of unused flags

2. **User Assignment**
   - Use consistent user IDs
   - Consider using anonymous mode for non-logged-in users
   - Test with both anonymous and identified users

3. **Performance**
   - Cache flag values when possible
   - Use `reload()` judiciously
   - Consider impact of source type on load times

4. **Testing**
   - Test both positive and negative cases
   - Verify user assignment consistency
   - Test all flag types
   - Include error cases in tests

5. **Monitoring**
   - Log flag evaluation results
   - Track flag usage
   - Monitor error rates
   - Regular configuration validation 