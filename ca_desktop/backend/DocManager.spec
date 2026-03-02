# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for DocManager CA Desktop
Build on Windows: pyinstaller DocManager.spec
"""

import sys
from pathlib import Path

base_dir = Path(SPECPATH)
project_root = base_dir.parent.parent  # DocManager/

a = Analysis(
    ['main_prod.py'],
    pathex=[
        str(base_dir),
        str(project_root),
    ],
    binaries=[],
    datas=[
        # Backend source code
        ('src', 'src'),
        # Shared utilities (lives outside backend)
        (str(project_root / 'shared'), 'shared'),
        # Frontend dist (if built)
        *(
            [('../frontend/dist', 'frontend/dist')]
            if (base_dir / '..' / 'frontend' / 'dist' / 'index.html').resolve().exists()
            else []
        ),
        # WhatsApp server JS files (Node.js runs as subprocess)
        ('src/services/whatsapp/server.js', 'src/services/whatsapp'),
        ('src/services/whatsapp/client.js', 'src/services/whatsapp'),
        ('src/services/whatsapp/mock_server.js', 'src/services/whatsapp'),
        ('package.json', '.'),
        # Default env template
        ('.env.example', '.'),
    ],
    hiddenimports=[
        # --- FastAPI / Uvicorn ---
        'fastapi',
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'starlette',
        'starlette.responses',
        'starlette.staticfiles',

        # --- SQLAlchemy ---
        'sqlalchemy',
        'sqlalchemy.orm',
        'sqlalchemy.orm.decl_api',
        'sqlalchemy.pool',
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.ext.hybrid',

        # --- Pydantic ---
        'pydantic',
        'pydantic.fields',
        'pydantic_settings',

        # --- Auth / Security ---
        'jose',
        'jose.jwt',
        'jose.backends',
        'jose.backends.native_types',
        'bcrypt',

        # --- Email ---
        'resend',

        # --- Other deps ---
        'aiofiles',
        'python_multipart',
        'multipart',
        'qrcode',
        'PIL',
        'slugify',
        'openpyxl',
        'pandas',

        # --- Our own modules (PyInstaller misses dynamic imports) ---
        'src.main',
        'src.config',
        'src.database',
        'src.models',
        'src.schemas',
        'src.dependencies',
        'src.exceptions',
        'src.routers.auth',
        'src.routers.ca_profile',
        'src.routers.clients',
        'src.routers.compliance',
        'src.routers.documents',
        'src.routers.messaging',
        'src.routers.public',
        'src.routers.reminders',
        'src.routers.reminders_v2',
        'src.routers.tags',
        'src.routers.whatsapp',
        'src.middleware.rate_limit',
        'src.middleware.request_logging',
        'src.modules.documents.scanner',
        'src.modules.documents.tagger',
        'src.modules.files.streamer',
        'src.services.audit_service',
        'src.services.email_service',
        'src.services.reminder_service',
        'src.services.whatsapp.handler',
        'src.services.whatsapp.bot_state',
        'src.services.whatsapp.document_service',
        'src.services.whatsapp.templates',
        'shared',
        'shared.crypto',
        'shared.crypto.keys',
        'shared.crypto.tokens',
        'shared.crypto.signing',
        'shared.crypto.fingerprint',
        'shared.utils',
        'shared.utils.logging',
        'shared.utils.validators',
        'shared.utils.constants',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest', 'pytest_asyncio', 'pytest_cov', 'httpx',
        'black', 'isort', 'mypy', 'pylint', 'ruff',
        'tkinter', 'matplotlib', 'IPython', 'notebook', 'jupyter',
        'scipy', 'numpy.distutils', 'numpy.f2py',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# --- Single-file .exe (simple distribution) ---
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DocManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,   # Keep console visible so CA can see status
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # TODO: Add .ico file
)

# --- Folder distribution (faster startup, easier debugging) ---
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DocManager',
)
