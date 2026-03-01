import sys
from pathlib import Path
from sqlalchemy import text

# Add root to path
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

from ca_desktop.backend.src.dependencies import get_password_hash  # noqa: E402


def bootstrap():
    print("Bootstrapping Local Environment...")

    # Initialize tables using the app's database configuration
    from ca_desktop.backend.src import database

    database.init_db()

    # Use the shared engine for queries to ensure we hit the same DB
    engine = database.engine

    # Create default user
    hashed_pass = get_password_hash("admin123")
    with engine.connect() as conn:
        # Check if exists
        res = conn.execute(
            text("SELECT id FROM users WHERE username = 'admin'")
        ).fetchone()
        if not res:
            conn.execute(
                text(
                    "INSERT INTO users (username, email, password_hash, created_at) VALUES (:u, :e, :p, CURRENT_TIMESTAMP)"
                ),
                {"u": "admin", "e": "admin@example.com", "p": hashed_pass},
            )
            conn.commit()
            print("✅ Default CA User created: admin / admin123")
        else:
            print("ℹ️ Default CA User 'admin' already exists.")

    print("✅ Bootstrap Complete.")


if __name__ == "__main__":
    bootstrap()
