# -*- mode: python ; coding: utf-8 -*-

from kivy_deps import sdl2, glew
from kivymd import hooks_path as kivymd_hooks_path

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('kv', 'kv'),               # вся папка kv
        ('assets', 'assets'),       # вся папка assets
        ('data', 'data'),           # вся папка data (БД)
    ],
    hiddenimports=[
        'kivy',
        'kivymd',
        'kivymd.icon_definitions',
        'kivymd.font_definitions',
        'win32timezone',   # <-- решает ошибку FileChooser
        'win32file',
        'win32api',
        'win32con',
        'pywintypes',
        'pythoncom',
        'PIL',             # на всякий случай для изображений
        'PIL.Image',
    ],
    hookspath=[kivymd_hooks_path],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    name='CPlay',
    debug=False,
    console=False,      # скрыть консоль
    icon='assets/icon.ico',  # убедитесь, что файл существует
    upx=True,
)