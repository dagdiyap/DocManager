"""Production entry point for packaged DocManager application.

This is the main entry point when running as a packaged Windows executable.
Optimized for low resource usage and fast startup.
"""

import sys
import os
from pathlib import Path

# Setup paths for both development and packaged environments
if getattr(sys, 'frozen', False):
    # Running as packaged executable
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller temp directory
        base_dir = Path(sys._MEIPASS)
    else:
        base_dir = Path(sys.executable).parent
    
    # Add to path
    sys.path.insert(0, str(base_dir))
    sys.path.insert(0, str(base_dir / 'ca_desktop' / 'backend'))
else:
    # Running in development
    base_dir = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(base_dir))


def main():
    """Start the production server."""
    import uvicorn
    
    # Import configuration
    try:
        from ca_desktop.backend.src.config_prod import get_production_settings
    except ImportError:
        try:
            from src.config_prod import get_production_settings
        except ImportError:
            # Last resort - direct import
            import importlib.util
            config_path = Path(__file__).parent / 'src' / 'config_prod.py'
            spec = importlib.util.spec_from_file_location("config_prod", config_path)
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            get_production_settings = config_module.get_production_settings
    
    # Import and create app directly
    try:
        from ca_desktop.backend.src.main import app
    except ImportError:
        try:
            from src.main import app
        except ImportError:
            # Create app directly by importing main module
            import importlib.util
            main_path = Path(__file__).parent / 'src' / 'main.py'
            spec = importlib.util.spec_from_file_location("main", main_path)
            main_module = importlib.util.module_from_spec(spec)
            sys.modules['main'] = main_module
            spec.loader.exec_module(main_module)
            app = main_module.app
    
    settings = get_production_settings()
    
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📁 Data directory: {Path(settings.database_url.replace('sqlite:///', '/')).parent}")
    print(f"🌐 Server: http://{settings.host}:{settings.port}")
    print(f"📊 API Docs: http://{settings.host}:{settings.port}/docs")
    print(f"🔒 Running in PRODUCTION mode")
    print()
    
    # Configure uvicorn for production
    config = uvicorn.Config(
        app,  # Pass app object directly instead of import string
        host=settings.host,
        port=settings.port,
        reload=False,  # No auto-reload
        workers=1,  # Single worker for desktop
        log_level=settings.log_level.lower(),
        access_log=False,  # Disable access logs for performance
        use_colors=True,
        loop="asyncio",  # Standard event loop
    )
    
    server = uvicorn.Server(config)
    
    try:
        server.run()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except OSError as e:
        # User-friendly messages for common errors on Windows and macOS
        if e.errno == 98 or e.errno == 10048:  # EADDRINUSE (Linux/Mac) / Windows
            print(f"\n❌ Port {settings.port} is already in use.")
            print("   Another copy of DocManager may be running.")
            print("   Close it first, or change the port in your .env file.")
        elif e.errno == 13 or e.errno == 10013:  # EACCES / Windows
            print(f"\n❌ Permission denied on port {settings.port}.")
            print("   Try running as Administrator, or use a port above 1024.")
        else:
            print(f"\n❌ Server error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        print("   If this keeps happening, please contact support.")
        sys.exit(1)


if __name__ == "__main__":
    main()
