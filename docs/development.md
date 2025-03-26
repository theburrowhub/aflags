# Development Guide

This guide will help you set up your development environment and contribute to AFlags.

## Development Setup

1. **Clone the Repository**

```bash
git clone https://github.com/yourusername/aflags.git
cd aflags
```

2. **Set Up Virtual Environment**

We recommend using `uv` for dependency management:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Project Structure

```
aflags/
├── src/
│   └── aflags/
│       ├── __init__.py
│       ├── core.py           # Core functionality
│       └── sources/          # Feature flag sources
│           ├── __init__.py
│           ├── json.py
│           ├── yaml.py
│           └── env.py
├── tests/
│   ├── fixtures/            # Test data files
│   ├── test_core.py
│   ├── test_json_source.py
│   ├── test_yaml_source.py
│   └── test_env_source.py
├── docs/                    # Documentation
├── pyproject.toml          # Project configuration
└── README.md
```

## Development Commands

- `make setup`: Set up development environment
- `make test`: Run tests
- `make lint`: Run linting checks
- `make format`: Format code
- `make clean`: Clean build artifacts
- `make dist`: Build distribution package

## Testing

We use pytest for testing. Run the test suite with:

```bash
make test
```

### Writing Tests

1. Place tests in the `tests/` directory
2. Use descriptive test names
3. Include both positive and negative test cases
4. Use fixtures for test data
5. Aim for 100% code coverage

Example test:

```python
def test_boolean_flag():
    """Test boolean feature flag functionality."""
    flag = FeatureFlag(
        name="test_flag",
        type=FlagType.BOOLEAN,
        value=True
    )
    assert flag.is_enabled() is True
```

## Code Style

We follow PEP 8 with some modifications:

- Line length: 88 characters (Black default)
- Use type hints
- Use docstrings for all public functions and classes
- Sort imports using isort

## Documentation

- Update API documentation when adding new features
- Include docstrings for all public interfaces
- Add examples for new functionality
- Keep README.md up to date

## Pull Request Process

1. Create a new branch for your feature/fix
2. Write tests for new functionality
3. Ensure all tests pass
4. Update documentation
5. Submit a pull request

### PR Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code formatted
- [ ] Type hints added
- [ ] Changelog updated

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release commit
4. Tag release
5. Build and publish to PyPI

```bash
# Update version
edit pyproject.toml

# Create release commit
git commit -am "Release v1.0.0"
git tag v1.0.0

# Build and publish
make dist
uv pip publish dist/*
```

## Debugging Tips

### Common Issues

1. **Import Errors**
   - Check virtual environment activation
   - Verify package installation
   - Check Python path

2. **Test Failures**
   - Use pytest -v for verbose output
   - Check test fixtures
   - Verify test environment

3. **Type Checking**
   - Run mypy for type checking
   - Check type hint imports
   - Verify stub files

### Debugging Tools

1. **pytest**
   ```bash
   pytest -v                 # Verbose output
   pytest -k "test_name"    # Run specific test
   pytest --pdb             # Debug on failure
   ```

2. **Coverage**
   ```bash
   pytest --cov=aflags      # Check coverage
   pytest --cov-report=html # Generate coverage report
   ```

3. **Linting**
   ```bash
   make lint               # Run all linting checks
   ruff check .           # Run Ruff linter
   black --check .        # Check formatting
   ```

## Performance Considerations

1. **Flag Evaluation**
   - Cache flag values when possible
   - Minimize file I/O operations
   - Use efficient data structures

2. **Memory Usage**
   - Avoid unnecessary object creation
   - Clean up resources properly
   - Monitor memory usage

3. **Testing**
   - Include performance tests
   - Test with large configurations
   - Profile critical paths

## Security

1. **Input Validation**
   - Validate all configuration input
   - Sanitize user IDs
   - Check file permissions

2. **Error Handling**
   - Never expose internal errors
   - Log security-relevant events
   - Handle all edge cases

3. **Best Practices**
   - Keep dependencies updated
   - Follow security guidelines
   - Regular security reviews 