# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

PROJECT_ROOT = Path.cwd().resolve()

# ── 手动数据文件 ──────────────────────────────────────────────
datas = [
    (str(PROJECT_ROOT / "assets" / "eyebreak.ico"), "assets"),
]

# ── Block cipher (from PyInstaller template) ──────────────────
block_cipher = None

a = Analysis(
    [str(PROJECT_ROOT / "main.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # ── 新架构 ──
        "app.core",
        "app.core.events",
        "app.core.event_bus",
        "app.core.state_machine",
        "app.core.timer_engine",
        "app.platform",
        "app.platform.protocols",
        "app.platform.adapters",
        "app.ui",
        "app.ui.bridge",
        "app.infra",
        # ── 旧模块（主入口直接或间接使用） ──
        "app.config",
        "app.state",
        "app.idle",
        "app.fullscreen",
        "app.autostart",
        "app.paths",
        "app.icons",
        "app.tray",
        "app.floating_countdown",
        "app.reminder_window",
        "app.settings_window",
        # ── 第三方依赖 ──
        "pystray",
        "PIL",
        "PIL._tkinter_finder",
        "winreg",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter.test",
        "unittest",
        "pytest",
    ],
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
    name="EyeBreak",
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
    icon=str(PROJECT_ROOT / "assets" / "eyebreak.ico"),
)