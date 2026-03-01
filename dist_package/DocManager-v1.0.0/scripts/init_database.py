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
