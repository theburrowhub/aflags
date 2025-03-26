.PHONY: setup test lint clean format

# Development environment setup
setup:
	uv venv
	uv pip install -e ".[dev]"

# Run tests
test:
	pytest

# Run linting
lint:
	ruff check .
	ruff format --check .

# Format code
format:
	ruff format .

# Clean up
clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Install development dependencies
dev:
	uv pip install -e ".[dev]"

# Create distribution
dist:
	python -m build 