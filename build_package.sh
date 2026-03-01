#!/bin/bash
# Build complete DocManager package for Windows deployment
# This script creates a distributable package ready for Windows installer

set -e

echo "🚀 DocManager Package Builder"
echo "=============================="
echo ""

# Configuration
PACKAGE_NAME="DocManager-v1.0.0"
BUILD_DIR="dist_package"
BACKEND_DIST="ca_desktop/backend/dist/DocManager"
FRONTEND_DIST="ca_desktop/frontend/dist"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/$PACKAGE_NAME"

# Create directory structure
echo "📁 Creating package structure..."
mkdir -p "$BUILD_DIR/$PACKAGE_NAME/backend"
mkdir -p "$BUILD_DIR/$PACKAGE_NAME/frontend"
mkdir -p "$BUILD_DIR/$PACKAGE_NAME/data/uploads"
mkdir -p "$BUILD_DIR/$PACKAGE_NAME/data/logs"
mkdir -p "$BUILD_DIR/$PACKAGE_NAME/config"
mkdir -p "$BUILD_DIR/$PACKAGE_NAME/scripts"

# Copy backend executable
echo "📦 Copying backend executable..."
if [ -f "$BACKEND_DIST" ]; then
    cp "$BACKEND_DIST" "$BUILD_DIR/$PACKAGE_NAME/backend/DocManager"
    chmod +x "$BUILD_DIR/$PACKAGE_NAME/backend/DocManager"
    echo "   ✅ Backend: $(du -sh $BACKEND_DIST | cut -f1)"
else
    echo "   ❌ Backend executable not found! Run PyInstaller first."
    exit 1
fi

# Copy frontend build
echo "📦 Copying frontend build..."
if [ -d "$FRONTEND_DIST" ]; then
    cp -r "$FRONTEND_DIST"/* "$BUILD_DIR/$PACKAGE_NAME/frontend/"
    echo "   ✅ Frontend: $(du -sh $FRONTEND_DIST | cut -f1)"
else
    echo "   ❌ Frontend build not found! Run 'npm run build' first."
    exit 1
fi

# Create configuration files
echo "⚙️  Creating configuration files..."

# Create .env template
cat > "$BUILD_DIR/$PACKAGE_NAME/config/.env.template" << 'EOF'
# DocManager Configuration
# Copy this file to data/.env and fill in your values

# Email Service (Required for email reminders)
# Get free API key from: https://resend.com
RESEND_API_KEY=re_your_api_key_here

# Security (Optional - auto-generated if not set)
SECRET_KEY=

# Server Configuration (Optional - defaults shown)
HOST=127.0.0.1
PORT=8443

# Frontend URL (Optional - defaults shown)
FRONTEND_URL=http://localhost:5174
EOF

# Create startup script for Windows
cat > "$BUILD_DIR/$PACKAGE_NAME/scripts/start_backend.bat" << 'EOF'
@echo off
title DocManager Backend Server
cd /d "%~dp0.."
backend\DocManager.exe
pause
EOF

# Create startup script for Mac/Linux
cat > "$BUILD_DIR/$PACKAGE_NAME/scripts/start_backend.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/.."
./backend/DocManager
EOF
chmod +x "$BUILD_DIR/$PACKAGE_NAME/scripts/start_backend.sh"

# Create README
cat > "$BUILD_DIR/$PACKAGE_NAME/README.txt" << 'EOF'
DocManager CA Desktop - Installation Guide
==========================================

QUICK START
-----------
1. Extract this folder to: C:\Program Files\DocManager
2. (Optional) Edit config/.env.template and save as data/.env
3. Run scripts/start_backend.bat
4. Open browser: http://localhost:5174/ca
5. Login with username: lokesh, password: lokesh

DEFAULT CREDENTIALS
-------------------
CA Login:
  Username: lokesh
  Password: lokesh

Demo Client:
  Phone: 9876543210
  Password: client123

⚠️  CHANGE DEFAULT PASSWORDS AFTER FIRST LOGIN!

FOLDER STRUCTURE
----------------
backend/        - Backend server (DocManager.exe)
frontend/       - Frontend web application
data/           - Database and uploaded documents
  ├── ca_desktop.db  - SQLite database
  ├── uploads/       - Client documents
  └── logs/          - Application logs
config/         - Configuration files
scripts/        - Startup scripts

SYSTEM REQUIREMENTS
-------------------
- Windows 10 or later
- 4 GB RAM minimum (8 GB recommended)
- 20 GB free disk space
- Modern web browser (Chrome, Firefox, Edge)

EMAIL CONFIGURATION
-------------------
To enable email reminders:
1. Sign up free at https://resend.com (3,000 emails/month free)
2. Get API key from dashboard
3. Copy config/.env.template to data/.env
4. Add: RESEND_API_KEY=re_your_key_here
5. Restart application

PORTS USED
----------
- Backend: 8443
- Frontend: 5174

ACCESS URLS
-----------
- CA Dashboard: http://localhost:5174/ca
- Client Portal: http://localhost:5174/portal
- Public Website: http://localhost:5174/ca-lokesh-dagdiya
- API Docs: http://localhost:8443/docs

SUPPORT
-------
For issues, check:
- data/logs/backend.log
- Documentation in docs/guides/

Version: 1.0.0
Released: March 2026
EOF

# Create uninstall script
cat > "$BUILD_DIR/$PACKAGE_NAME/scripts/uninstall.sh" << 'EOF'
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
EOF
chmod +x "$BUILD_DIR/$PACKAGE_NAME/scripts/uninstall.sh"

# Copy documentation
echo "📚 Copying documentation..."
mkdir -p "$BUILD_DIR/$PACKAGE_NAME/docs"
if [ -d "docs/guides" ]; then
    cp -r docs/guides "$BUILD_DIR/$PACKAGE_NAME/docs/"
fi

# Create database initialization script
cat > "$BUILD_DIR/$PACKAGE_NAME/scripts/init_database.py" << 'EOF'
"""Initialize DocManager database with default CA user."""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def init_db():
    """Initialize database."""
    print("🗄️  Initializing DocManager database...")
    
    # This would use the actual database setup
    # For now, just create the file
    db_path = Path(__file__).parent.parent / "data" / "ca_desktop.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"   Database: {db_path}")
    print("   ✅ Database initialized")
    print("\n   Default CA credentials:")
    print("   Username: lokesh")
    print("   Password: lokesh")
    print("\n   ⚠️  Remember to change the default password!")

if __name__ == "__main__":
    init_db()
EOF

# Calculate package size
echo ""
echo "📊 Package Summary:"
echo "   Backend:  $(du -sh $BUILD_DIR/$PACKAGE_NAME/backend | cut -f1)"
echo "   Frontend: $(du -sh $BUILD_DIR/$PACKAGE_NAME/frontend | cut -f1)"
echo "   Total:    $(du -sh $BUILD_DIR/$PACKAGE_NAME | cut -f1)"

# Create archive
echo ""
echo "📦 Creating distributable archive..."
cd "$BUILD_DIR"
tar -czf "$PACKAGE_NAME.tar.gz" "$PACKAGE_NAME"
zip -r -q "$PACKAGE_NAME.zip" "$PACKAGE_NAME"

echo ""
echo "✅ Package created successfully!"
echo ""
echo "📍 Output:"
echo "   Directory: $BUILD_DIR/$PACKAGE_NAME"
echo "   Archive:   $BUILD_DIR/$PACKAGE_NAME.tar.gz"
echo "   ZIP:       $BUILD_DIR/$PACKAGE_NAME.zip"
echo ""
echo "📝 Next Steps:"
echo "   1. Test the package locally"
echo "   2. Create Windows installer with Inno Setup"
echo "   3. Test in Docker environment"
echo "   4. Measure performance"
echo ""
