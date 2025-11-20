#!/bin/bash
# Run all examples using uv

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed."
    echo "Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "Virtual environment not found. Creating it..."
    cd "$PROJECT_ROOT"
    uv venv
    uv sync
fi

# Run all examples
cd "$SCRIPT_DIR"
echo "Running all examples..."
echo ""

for example in *.py; do
    if [ "$example" != "__init__.py" ]; then
        echo "=========================================="
        echo "Running $example..."
        echo "=========================================="
        cd "$PROJECT_ROOT"
        uv run python "examples/$example"
        echo ""
    fi
done

echo "All examples completed!"


