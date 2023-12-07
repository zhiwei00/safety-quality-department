# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    [r'I:\Project\safety-quality-department\3.2\main.py',
     r'I:\Project\safety-quality-department\3.2\src\__init__.py',
     r'I:\Project\safety-quality-department\3.2\src\application.py',
     r'I:\Project\safety-quality-department\3.2\src\cloud_disk.py',
     r'I:\Project\safety-quality-department\3.2\src\config.py',
     r'I:\Project\safety-quality-department\3.2\src\main_process.py',
     r'I:\Project\safety-quality-department\3.2\src\ui.py',
     r'I:\Project\safety-quality-department\3.2\src\verification_time.py'
     ],
    pathex=[r'I:\Project\safety-quality-department\venv\Lib\site-packages'],
    binaries=[],
    datas=[(r'I:\Project\safety-quality-department\3.2\js\*.js', 'js' )],
    hiddenimports=['typer', 'PyQt5.sip'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='rpa',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
    icon='I:\\Project\\invoice-check\\logo.png'
)
