#!/bin/bash

# n8n-flow-manager Installation Script
# This script helps set up the development environment

set -e

echo "🚀 n8n-flow-manager Setup"
echo "=========================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.9"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
    echo "❌ Python 3.9 or higher is required (found: $python_version)"
    exit 1
fi
echo "✓ Python $python_version"
echo ""

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry not found. Do you want to install it? (y/n)"
    read -r install_poetry

    if [ "$install_poetry" = "y" ]; then
        echo "Installing Poetry..."
        curl -sSL https://install.python-poetry.org | python3 -
        export PATH="$HOME/.local/bin:$PATH"
        echo "✓ Poetry installed"
    else
        echo "⚠️  Poetry is recommended but not required"
        echo "   You can install manually with: curl -sSL https://install.python-poetry.org | python3 -"
    fi
else
    echo "✓ Poetry $(poetry --version | awk '{print $3}')"
fi
echo ""

# Install dependencies
echo "Installing dependencies..."
if command -v poetry &> /dev/null; then
    poetry install --with dev
    echo "✓ Dependencies installed with Poetry"
else
    python3 -m pip install -e ".[dev]"
    echo "✓ Dependencies installed with pip"
fi
echo ""

# Setup .env file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
# n8n API Configuration
N8N_API_KEY=your_api_key_here
N8N_BASE_URL=https://n8n.example.com

# Optional: Request timeout in seconds
N8N_TIMEOUT=30

# Optional: Max retries for failed requests
N8N_MAX_RETRIES=3

# Optional: Polling interval for execution wait (seconds)
N8N_POLL_INTERVAL=2
EOF
    echo "✓ Created .env file (please update with your credentials)"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your n8n credentials:"
    echo "   - N8N_API_KEY: Get from n8n Settings > API"
    echo "   - N8N_BASE_URL: Your n8n instance URL"
else
    echo "✓ .env file already exists"
fi
echo ""

# Install pre-commit hooks
if command -v poetry &> /dev/null; then
    echo "Installing pre-commit hooks..."
    poetry run pre-commit install
    echo "✓ Pre-commit hooks installed"
    echo ""
fi

# Create necessary directories
echo "Creating project directories..."
mkdir -p backups
mkdir -p templates
echo "✓ Directories created"
echo ""

# Run tests to verify installation
echo "Running tests to verify installation..."
if command -v poetry &> /dev/null; then
    if poetry run pytest tests/ -v; then
        echo "✓ All tests passed"
    else
        echo "⚠️  Some tests failed (this might be expected without n8n connection)"
    fi
else
    if python3 -m pytest tests/ -v; then
        echo "✓ All tests passed"
    else
        echo "⚠️  Some tests failed (this might be expected without n8n connection)"
    fi
fi
echo ""

echo "=========================="
echo "✨ Setup Complete!"
echo "=========================="
echo ""
echo "Next steps:"
echo "1. Edit .env with your n8n credentials"
echo "2. Test connection: poetry run n8n-py health"
echo "3. Try: poetry run n8n-py list-workflows"
echo ""
echo "Documentation:"
echo "- Quick Start: QUICKSTART.md"
echo "- Full docs: README.md"
echo "- Examples: examples/"
echo ""
echo "Happy automating! 🚀"
