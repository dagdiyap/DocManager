# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for DocManager CA Desktop
Optimized for production Windows deployment
"""

import sys
from pathlib import Path

# Get the base directory
base_dir = Path(SPECPATH)

# Analysis: Discover all imports and dependencies
a = Analysis(
    ['main_prod.py'],
    pathex=[str(base_dir)],
    binaries=[],
    datas=[
        # Include source code
        ('src', 'src'),
        # Include shared utilities
        ('../../shared', 'shared'),
    ],
    hiddenimports=[
        # FastAPI and dependencies
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
        
        # SQLAlchemy
        'sqlalchemy',
        'sqlalchemy.ext',
        'sqlalchemy.ext.declarative',
        'sqlalchemy.orm',
        'sqlalchemy.pool',
        'sqlalchemy.dialects.sqlite',
        
        # Pydantic
        'pydantic',
        'pydantic.fields',
        'pydantic_settings',
        
        # Authentication
        'jose',
        'jose.jwt',
        'passlib',
        'passlib.handlers',
        'passlib.handlers.bcrypt',
        'bcrypt',
        
        # Email
        'resend',
        
        # Other dependencies
        'aiofiles',
        'python_multipart',
        'qrcode',
        'PIL',
        'slugify',
        'openpyxl',
        'pandas',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude test frameworks
        'pytest',
        'pytest_asyncio',
        'pytest_cov',
        'httpx',
        
        # Exclude development tools
        'black',
        'isort',
        'mypy',
        'pylint',
        
        # Exclude unnecessary modules
        'tkinter',
        'matplotlib',
        'IPython',
        'notebook',
        'jupyter',
        
        # Exclude large unused libraries
        'scipy',
        'numpy.distutils',
        'numpy.f2py',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate binaries
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create executable
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
    upx=True,  # Enable UPX compression
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Show console for logs
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # TODO: Add icon file
)

# Optional: Create a COLLECT for folder distribution (uncomment if needed)
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='DocManager',
# )
