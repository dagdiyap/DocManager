#!/bin/bash

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🧪 Running CA Desktop Test Suite..."

# 1. Backend Tests
echo "📦 Running Backend Tests..."
source venv/bin/activate
pytest tests/ -v
BACKEND_EXIT=$?

if [ $BACKEND_EXIT -ne 0 ]; then
    echo "❌ Backend tests failed!"
    exit $BACKEND_EXIT
fi

# 2. Frontend Tests
echo "💻 Running Frontend Tests..."
cd ca_desktop/frontend
npm test -- run
FRONTEND_EXIT=$?

if [ $FRONTEND_EXIT -ne 0 ]; then
    echo "❌ Frontend tests failed!"
    exit $FRONTEND_EXIT
fi

echo "✅ All tests passed successfully!"
exit 0
