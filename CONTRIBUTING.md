# Contributing to n8n-flow-manager

Thank you for your interest in contributing to n8n-flow-manager! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/n8n-flow-manager.git
   cd n8n-flow-manager
   ```
3. **Add the upstream repository**:
   ```bash
   git remote add upstream https://github.com/original-owner/n8n-flow-manager.git
   ```

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Poetry (recommended) or pip
- Git

### Installation

1. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install dependencies**:
   ```bash
   poetry install --with dev
   ```

3. **Activate virtual environment**:
   ```bash
   poetry shell
   ```

4. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

### Environment Configuration

Create a `.env` file for testing:

```bash
N8N_API_KEY=your_test_api_key
N8N_BASE_URL=https://test.n8n.example.com
```

## Project Structure

```
n8n-flow-manager/
├── src/n8n_manager/     # Main package source code
│   ├── api/             # API resource modules
│   ├── models/          # Pydantic models
│   ├── cli/             # CLI application
│   └── utils/           # Utility functions
├── tests/               # Test suite
├── examples/            # Usage examples
└── docs/                # Documentation
```

## Coding Standards

### Python Style

We follow PEP 8 with some modifications:

- **Line length**: 100 characters (not 79)
- **Formatter**: Black
- **Linter**: Ruff
- **Type checker**: MyPy

### Code Quality Tools

Run before committing:

```bash
# Format code
poetry run black src/ tests/

# Lint code
poetry run ruff check src/ tests/

# Type check
poetry run mypy src/

# Run all checks
poetry run pre-commit run --all-files
```

### Type Hints

All functions must have type hints:

```python
def example_function(param: str, optional: Optional[int] = None) -> bool:
    """Docstring explaining the function."""
    return True
```

### Docstrings

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> Dict[str, Any]:
    """
    Brief description of the function.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When validation fails
    """
    pass
```

### Naming Conventions

- **Classes**: `PascalCase`
- **Functions/methods**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: `_leading_underscore`

## Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/n8n_manager --cov-report=html

# Run specific test file
poetry run pytest tests/test_client.py

# Run specific test
poetry run pytest tests/test_client.py::test_client_initialization
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files as `test_*.py`
- Name test functions as `test_*`
- Use pytest fixtures for common setup
- Mock external API calls with `unittest.mock`

Example:

```python
import pytest
from n8n_manager import N8NClient

@pytest.mark.asyncio
async def test_workflow_creation():
    """Test that workflows can be created."""
    client = N8NClient(api_key="test", base_url="https://test.com")
    # ... test implementation
```

### Test Coverage

- Aim for **80%+ test coverage**
- All new features must include tests
- Bug fixes should include regression tests

## Submitting Changes

### Branch Naming

Use descriptive branch names:

- `feature/add-webhook-support`
- `bugfix/fix-execution-polling`
- `docs/improve-readme`
- `refactor/simplify-client-init`

### Commit Messages

Follow the Conventional Commits specification:

```
type(scope): brief description

Longer explanation if needed

Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```
feat(cli): add backup command for workflows

Add new CLI command to backup all workflows to a local directory.
Supports filtering by active status.

Closes #45
```

```
fix(executions): correct polling timeout calculation

The timeout was being calculated incorrectly, causing premature
timeouts. Fixed by using monotonic time.

Fixes #67
```

### Pull Request Process

1. **Update your fork**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** following the coding standards

4. **Write/update tests** for your changes

5. **Run the test suite**:
   ```bash
   poetry run pytest
   poetry run black src/ tests/
   poetry run ruff check src/ tests/
   poetry run mypy src/
   ```

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request** on GitHub

### Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Include screenshots for UI changes
- Ensure all tests pass
- Request review from maintainers
- Be responsive to feedback

## Reporting Bugs

### Before Submitting

- Check if the bug has already been reported
- Verify you're using the latest version
- Test with a minimal reproduction case

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Initialize client with...
2. Call method...
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment:**
- OS: [e.g. Ubuntu 22.04]
- Python version: [e.g. 3.11.0]
- n8n-flow-manager version: [e.g. 0.1.0]
- n8n version: [e.g. 1.0.0]

**Additional context**
Any other relevant information.
```

## Feature Requests

We welcome feature requests! Please:

1. **Search existing issues** to avoid duplicates
2. **Describe the use case** clearly
3. **Explain the expected behavior**
4. **Provide examples** if possible
5. **Discuss implementation** approach

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Other approaches you've thought about.

**Additional context**
Any other relevant information.
```

## Development Tips

### Useful Commands

```bash
# Install package in editable mode
poetry install

# Add new dependency
poetry add httpx

# Add dev dependency
poetry add --group dev pytest

# Update dependencies
poetry update

# Build package
poetry build

# Publish to PyPI (maintainers only)
poetry publish
```

### Debugging

Use the built-in Python debugger:

```python
import pdb; pdb.set_trace()
```

Or with async code:

```python
import asyncio
import pdb
pdb.set_trace()
```

### IDE Setup

**VS Code**:
```json
{
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true
}
```

**PyCharm**:
- Enable Black formatter in Settings → Tools → Black
- Configure pytest as test runner
- Enable type checking inspections

## Questions?

If you have questions, feel free to:

- Open a [GitHub Discussion](https://github.com/original-owner/n8n-flow-manager/discussions)
- Ask in the [n8n Community Forum](https://community.n8n.io/)
- Check existing [documentation](https://github.com/original-owner/n8n-flow-manager/wiki)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to n8n-flow-manager! 🚀
