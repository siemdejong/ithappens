# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from glob import glob

def get_locales_data():
    locales_data = []
    for mo in glob("src/shithappens/locales/**/LC_MESSAGES/*.mo"):
        locales_data.append((mo, Path(*Path(mo).parent.parts[2:])))
    return locales_data

block_cipher = None


a = Analysis(
    ['src/shithappens/create_cards.py'],
    pathex=[],
    binaries=[],
    datas=get_locales_data() + [
        ('src/shithappens/images/*.png', Path('images')),
        ('src/shithappens/opensans/fonts/ttf/*.ttf', Path('opensans/fonts/ttf'))
    ],
    hiddenimports=["matplotlib.backends.backend_pdf"],
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
    [],
    exclude_binaries=True,
    name='shithappens',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='shithappens',
)
