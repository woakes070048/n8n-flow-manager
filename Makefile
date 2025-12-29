.PHONY: help install install-dev test test-cov lint format type-check clean build publish docs

help:
	@echo "n8n-flow-manager Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install package in production mode"
	@echo "  make install-dev    Install package with dev dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make test           Run test suite"
	@echo "  make test-cov       Run tests with coverage report"
	@echo "  make lint           Run linter (ruff)"
	@echo "  make format         Format code with black"
	@echo "  make type-check     Run type checker (mypy)"
	@echo "  make check          Run all checks (lint + format + type)"
	@echo ""
	@echo "Package:"
	@echo "  make clean          Clean build artifacts"
	@echo "  make build          Build package"
	@echo "  make publish        Publish to PyPI"
	@echo ""
	@echo "Examples:"
	@echo "  make run-example    Run basic usage example"

install:
	poetry install

install-dev:
	poetry install --with dev
	poetry run pre-commit install

test:
	poetry run pytest

test-cov:
	poetry run pytest --cov=src/n8n_manager --cov-report=html --cov-report=term

lint:
	poetry run ruff check src/ tests/

format:
	poetry run black src/ tests/ examples/

type-check:
	poetry run mypy src/

check: lint format type-check
	@echo "✓ All checks passed!"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	poetry build

publish: build
	poetry publish

docs:
	@echo "Documentation available in README.md"
	@echo "API Reference: Check docstrings in source code"

run-example:
	@echo "Running basic usage example..."
	@echo "Make sure N8N_API_KEY and N8N_BASE_URL are set in .env"
	poetry run python examples/basic_usage.py

# Development shortcuts
dev: install-dev
	@echo "Development environment ready!"

.DEFAULT_GOAL := help
