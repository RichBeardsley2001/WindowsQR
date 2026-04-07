# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for WindowsQR.
Build with:  python -m PyInstaller WindowsQR.spec --clean
"""
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

# accessible_output2 bundles the NVDA controller DLLs
ao2_datas = []
ao2_binaries = []
try:
    ao2_datas = collect_data_files("accessible_output2")
    ao2_binaries = collect_dynamic_libs("accessible_output2")
except Exception:
    pass

a = Analysis(
    ["src/main.py"],
    pathex=["src"],
    binaries=ao2_binaries,
    datas=[
        ("assets", "assets"),
        *ao2_datas,
    ],
    hiddenimports=[
        # pystray Windows backend
        "pystray._win32",
        # pynput Windows backend
        "pynput.keyboard._win32",
        "pynput.mouse._win32",
        # PIL
        "PIL._tkinter_finder",
        # accessible_output2 outputs
        "accessible_output2.outputs.auto",
        "accessible_output2.outputs.sapi5",
        "accessible_output2.outputs.nvda",
        "accessible_output2.outputs.jaws",
        # win32com
        "win32com.client",
        "win32com.shell",
        "pythoncom",
        "pywintypes",
        # opencv
        "cv2",
    ],
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
    name="WindowsQR",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,        # No console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/icon.ico",
    version_file=None,
    uac_admin=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="WindowsQR",
)
