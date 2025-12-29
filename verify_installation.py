#!/usr/bin/env python3
"""
Installation verification script for n8n-flow-manager.
Run this after installation to ensure everything is set up correctly.
"""

import sys
from pathlib import Path


def check_python_version():
    """Check Python version."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (requires 3.9+)")
        return False


def check_imports():
    """Check if all required packages can be imported."""
    print("\nChecking package imports...")

    packages = {
        "httpx": "httpx",
        "pydantic": "pydantic",
        "typer": "typer",
        "jinja2": "jinja2",
        "dotenv": "python-dotenv",
        "rich": "rich",
    }

    all_ok = True
    for import_name, package_name in packages.items():
        try:
            __import__(import_name)
            print(f"  ✓ {package_name}")
        except ImportError:
            print(f"  ✗ {package_name} (not installed)")
            all_ok = False

    return all_ok


def check_n8n_manager():
    """Check if n8n_manager package can be imported."""
    print("\nChecking n8n_manager package...")

    try:
        import n8n_manager

        print(f"  ✓ n8n_manager {n8n_manager.__version__}")

        # Check main components
        from n8n_manager import N8NClient
        from n8n_manager.models.execution import Execution
        from n8n_manager.models.workflow import Workflow

        print("  ✓ Core components")

        return True
    except ImportError as e:
        print(f"  ✗ n8n_manager (error: {e})")
        return False


def check_env_file():
    """Check if .env file exists."""
    print("\nChecking configuration...")

    env_file = Path(".env")
    if env_file.exists():
        print("  ✓ .env file exists")

        # Check if it contains required keys
        content = env_file.read_text()
        has_key = "N8N_API_KEY" in content
        has_url = "N8N_BASE_URL" in content

        if has_key and has_url:
            # Check if they're configured (not default values)
            if "your_api_key_here" not in content:
                print("  ✓ API key configured")
            else:
                print("  ⚠ API key not configured (still has default value)")

            if "n8n.example.com" not in content:
                print("  ✓ Base URL configured")
            else:
                print("  ⚠ Base URL not configured (still has default value)")
        else:
            print("  ⚠ .env file missing required keys")
    else:
        print("  ✗ .env file not found")
        print("     Create one using: cp .env.example .env")

    return env_file.exists()


def check_tests():
    """Check if tests can be run."""
    print("\nChecking test environment...")

    try:
        import importlib.util

        has_pytest = importlib.util.find_spec("pytest") is not None
        if has_pytest:
            print("  ✓ pytest installed")
        else:
            print("  ✗ pytest not installed")
            return False

        # Check if test files exist
        tests_dir = Path("tests")
        if tests_dir.exists():
            test_files = list(tests_dir.glob("test_*.py"))
            print(f"  ✓ Found {len(test_files)} test files")
        else:
            print("  ✗ tests directory not found")
            return False

        return True
    except ImportError:
        print("  ✗ pytest not installed")
        return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("n8n-flow-manager Installation Verification")
    print("=" * 60)

    checks = [
        ("Python Version", check_python_version),
        ("Package Imports", check_imports),
        ("n8n_manager Package", check_n8n_manager),
        ("Configuration", check_env_file),
        ("Test Environment", check_tests),
    ]

    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} {name}")
        if not result:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n✨ Installation verified successfully!")
        print("\nNext steps:")
        print("1. Configure your .env file with n8n credentials")
        print("2. Test connection: poetry run n8n-py health")
        print("3. Try: poetry run n8n-py list-workflows")
        print("\nRead QUICKSTART.md for more information.")
        return 0
    else:
        print("\n⚠ Some checks failed. Please review the issues above.")
        print("\nTroubleshooting:")
        print("- Ensure you've run: poetry install --with dev")
        print("- Check that you're in the project directory")
        print("- Verify Python 3.9+ is installed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
