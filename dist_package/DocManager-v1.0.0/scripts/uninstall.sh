#!/bin/bash
echo "⚠️  This will remove all DocManager data!"
read -p "Are you sure? (yes/no): " confirm
if [ "$confirm" = "yes" ]; then
    cd "$(dirname "$0")/.."
    rm -rf data/
    rm -rf backend/
    rm -rf frontend/
    echo "✅ DocManager uninstalled"
else
    echo "❌ Uninstall cancelled"
fi
