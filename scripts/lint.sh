#!/bin/bash

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🧹 Running Code Quality Checks..."

source venv/bin/activate

# 1. Python Linting (Ruff)
echo "🐍 Running Ruff (Linting)..."
ruff check .
RUFF_EXIT=$?

if [ $RUFF_EXIT -ne 0 ]; then
    echo "❌ Ruff found issues."
else
    echo "✅ Ruff passed."
fi

# 2. Python Formatting (Black)
echo "⚫ Running Black (Formatting)..."
black --check .
BLACK_EXIT=$?

if [ $BLACK_EXIT -ne 0 ]; then
    echo "❌ Black found formatting issues."
else
    echo "✅ Black passed."
fi

# 3. Python Type Checking (MyPy)
echo "typing Running MyPy (Type Checking)..."
# Set python path to project root to find modules
export PYTHONPATH=$PROJECT_ROOT
mypy --config-file ca_desktop/backend/pyproject.toml ca_desktop/backend/src
MYPY_EXIT=$?

if [ $MYPY_EXIT -ne 0 ]; then
    echo "❌ MyPy found type errors."
else
    echo "✅ MyPy passed."
fi

# 4. Frontend Linting
echo "⚛️  Running Frontend Lint..."
cd ca_desktop/frontend
npm run lint
FRONTEND_EXIT=$?

if [ $FRONTEND_EXIT -ne 0 ]; then
    echo "❌ Frontend linting failed."
else
    echo "✅ Frontend lint passed."
fi

# Summary
if [ $RUFF_EXIT -eq 0 ] && [ $BLACK_EXIT -eq 0 ] && [ $MYPY_EXIT -eq 0 ] && [ $FRONTEND_EXIT -eq 0 ]; then
    echo "✨ All code quality checks passed!"
    exit 0
else
    echo "⚠️  Some checks failed. Please review output above."
    exit 1
fi
