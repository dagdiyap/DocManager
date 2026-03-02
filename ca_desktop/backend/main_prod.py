"""Production entry point for packaged DocManager application.

Works in three modes:
1. PyInstaller frozen .exe on Windows
2. Direct `python main_prod.py` with virtualenv (portable zip distribution)
3. Development mode (`python main_prod.py` from repo root)

Non-technical CAs should never see raw Python tracebacks.
"""

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. PATH SETUP — must happen before any project imports
# ---------------------------------------------------------------------------
FROZEN = getattr(sys, "frozen", False)

if FROZEN:
    # PyInstaller: code extracted to _MEIPASS, exe lives in its own dir
    BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    APP_DIR = Path(sys.executable).parent  # writable directory next to .exe
else:
    # Script mode: main_prod.py sits in ca_desktop/backend/
    BUNDLE_DIR = Path(__file__).resolve().parent
    APP_DIR = BUNDLE_DIR

# Project root: parent of ca_desktop/  (two levels up from backend/)
PROJECT_ROOT = BUNDLE_DIR.parent.parent if not FROZEN else BUNDLE_DIR

# Ensure Python can find both `shared` and `ca_desktop.backend.src`
for p in [str(PROJECT_ROOT), str(BUNDLE_DIR), str(BUNDLE_DIR / "src")]:
    if p not in sys.path:
        sys.path.insert(0, p)

# On Windows frozen builds the shared package is bundled inside _MEIPASS
if FROZEN:
    sys.path.insert(0, str(BUNDLE_DIR / "shared"))


# ---------------------------------------------------------------------------
# 2. HELPERS
# ---------------------------------------------------------------------------
def _print_banner(host: str, port: int, data_dir: Path):
    """Print a friendly startup banner."""
    print()
    print("=" * 56)
    print("   DocManager CA Desktop  —  Starting...")
    print("=" * 56)
    print(f"   Server  : http://{host}:{port}")
    print(f"   API Docs: http://{host}:{port}/docs")
    print(f"   Data    : {data_dir}")
    print("=" * 56)
    print()


def _port_in_use(port: int) -> bool:
    """Check if a TCP port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return False
        except OSError:
            return True


def _ensure_data_dirs(base: Path):
    """Create all required data directories on first run."""
    for sub in ["documents", "shared_files", "logs", "keys"]:
        (base / sub).mkdir(parents=True, exist_ok=True)


def _ensure_env_file(base: Path):
    """Create a default .env if one doesn't exist yet (first-run)."""
    env_path = base / ".env"
    if env_path.exists():
        return
    import secrets

    env_path.write_text(
        f"# DocManager — auto-generated on first run\n"
        f"DATABASE_URL=sqlite:///{(base / 'ca_desktop.db').as_posix()}\n"
        f"SECRET_KEY={secrets.token_urlsafe(48)}\n"
        f"ENVIRONMENT=production\n"
        f"HOST=127.0.0.1\n"
        f"PORT=8443\n"
        f"LOG_LEVEL=INFO\n"
        f"LOG_FILE={( base / 'logs' / 'ca_desktop.log').as_posix()}\n"
        f"DOCUMENTS_ROOT={( base / 'documents').as_posix()}\n"
        f"SHARED_FILES_ROOT={( base / 'shared_files').as_posix()}\n"
        f"PUBLIC_KEY_PATH={( base / 'keys' / 'public_key.pem').as_posix()}\n",
        encoding="utf-8",
    )
    print(f"[Setup] Created default config: {env_path}")


def _start_whatsapp_server(backend_dir: Path):
    """Start the Node.js WhatsApp server as a managed subprocess."""
    server_js = backend_dir / "src" / "services" / "whatsapp" / "server.js"
    if not server_js.exists():
        print("[WhatsApp] server.js not found — skipping WhatsApp bot.")
        return None

    # Check if Node.js is available
    node_cmd = "node"
    try:
        subprocess.run(
            [node_cmd, "--version"],
            capture_output=True, timeout=5, check=True,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        print("[WhatsApp] Node.js not found — WhatsApp bot will not start.")
        print("           Install Node.js from https://nodejs.org/ to enable it.")
        return None

    # Check if node_modules exist
    if not (backend_dir / "node_modules" / "whatsapp-web.js").exists():
        print("[WhatsApp] Installing Node.js dependencies (first run)...")
        try:
            subprocess.run(
                ["npm", "install", "--production"],
                cwd=str(backend_dir),
                capture_output=True, timeout=120, check=True,
            )
            print("[WhatsApp] Dependencies installed.")
        except subprocess.SubprocessError as e:
            print(f"[WhatsApp] npm install failed: {e}")
            print("           WhatsApp bot will not start. Run 'npm install' manually.")
            return None

    if _port_in_use(3002):
        print("[WhatsApp] Port 3002 already in use — assuming server is running.")
        return None

    print("[WhatsApp] Starting WhatsApp server on port 3002...")
    env = os.environ.copy()
    env["BACKEND_URL"] = "http://127.0.0.1:8443"

    # On Windows, hide the Node console window
    kwargs = {}
    if sys.platform == "win32":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0  # SW_HIDE
        kwargs["startupinfo"] = si

    try:
        proc = subprocess.Popen(
            [node_cmd, "--max-old-space-size=256", str(server_js)],
            cwd=str(backend_dir),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            **kwargs,
        )
        # Wait briefly to see if it crashes immediately
        time.sleep(2)
        if proc.poll() is not None:
            print(f"[WhatsApp] Server exited immediately (code {proc.returncode}).")
            return None
        print("[WhatsApp] Server started (PID %d)." % proc.pid)
        return proc
    except Exception as e:
        print(f"[WhatsApp] Failed to start: {e}")
        return None


# ---------------------------------------------------------------------------
# 3. MAIN
# ---------------------------------------------------------------------------
def main():
    """Start the production server with full error handling."""

    # --- Data directory setup ---
    if FROZEN:
        data_dir = APP_DIR
    else:
        data_dir = APP_DIR  # in dev/portable mode, data lives next to the script

    _ensure_data_dirs(data_dir)
    _ensure_env_file(data_dir)

    # Point the .env search at our data directory so config picks it up
    os.environ.setdefault("CA_ENV_DIR", str(data_dir))

    # --- Import the app (after paths are set) ---
    try:
        from src.main import app  # noqa: F811
        from src.config import get_settings
    except ImportError:
        try:
            from ca_desktop.backend.src.main import app
            from ca_desktop.backend.src.config import get_settings
        except ImportError as exc:
            print(f"\nStartup Error: Cannot load application modules.\n  {exc}")
            print("Please ensure you're running from the correct directory.")
            _wait_and_exit(1)
            return

    settings = get_settings()
    host = str(getattr(settings, "host", "127.0.0.1"))
    port = int(getattr(settings, "port", 8443))

    # --- Pre-flight checks ---
    if _port_in_use(port):
        print(f"\nPort {port} is already in use.")
        print("Another copy of DocManager may be running.")
        print("Close it first, then try again.")
        _wait_and_exit(1)
        return

    _print_banner(host, port, data_dir)

    # --- Start WhatsApp server ---
    wa_proc = _start_whatsapp_server(BUNDLE_DIR if not FROZEN else APP_DIR)

    # --- Start backend ---
    import uvicorn

    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        reload=False,
        workers=1,
        log_level=str(getattr(settings, "log_level", "INFO")).lower(),
        access_log=False,
        loop="asyncio",
    )
    server = uvicorn.Server(config)

    exit_code = 0
    try:
        server.run()
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except OSError as e:
        if e.errno in (98, 10048):  # EADDRINUSE
            print(f"\nPort {port} is already in use.")
            print("Close the other application or change PORT in .env")
        elif e.errno in (13, 10013):  # EACCES
            print(f"\nPermission denied on port {port}.")
            print("Use a port above 1024, or run as Administrator.")
        else:
            print(f"\nServer error: {e}")
        exit_code = 1
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("If this keeps happening, please contact support.")
        exit_code = 1
    finally:
        # Clean up WhatsApp server
        if wa_proc and wa_proc.poll() is None:
            print("[WhatsApp] Stopping server...")
            wa_proc.terminate()
            try:
                wa_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                wa_proc.kill()

    if exit_code:
        _wait_and_exit(exit_code)


def _wait_and_exit(code: int):
    """On Windows, pause so the user can read the message before the console closes."""
    if sys.platform == "win32" or FROZEN:
        print("\nPress Enter to close...")
        try:
            input()
        except EOFError:
            pass
    sys.exit(code)


if __name__ == "__main__":
    main()
