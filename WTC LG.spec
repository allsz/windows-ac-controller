# -*- mode: python ; coding: utf-8 -*-

# Módulos do Qt e do Python que o WTC LG não utiliza e podem ser excluídos com segurança
qt_excludes = [
    # Módulos pesados de Web e QML
    'PySide6.QtWebEngine',
    'PySide6.QtWebEngineCore',
    'PySide6.QtWebEngineWidgets',
    'PySide6.QtQml',
    'PySide6.QtQuick',
    'PySide6.QtQuickWidgets',
    'PySide6.QtQuick3D',
    'PySide6.QtQmlModels',

    # Multimídia, Áudio, Vídeo e 3D
    'PySide6.QtMultimedia',
    'PySide6.QtMultimediaWidgets',
    'PySide6.Qt3DCore',
    'PySide6.Qt3DRender',
    'PySide6.Qt3DInput',
    'PySide6.Qt3DLogic',
    'PySide6.Qt3DAnimation',
    'PySide6.Qt3DExtras',

    # PDF, Impressão e Gráficos avançados não usados
    'PySide6.QtPdf',
    'PySide6.QtPdfWidgets',
    'PySide6.QtCharts',
    'PySide6.QtDataVisualization',
    'PySide6.QtSpatialAudio',

    # Conectividade e Sensores não utilizados (o app usa aiohttp para a API ThinQ)
    'PySide6.QtBluetooth',
    'PySide6.QtNfc',
    'PySide6.QtPositioning',
    'PySide6.QtSensors',
    'PySide6.QtSerialPort',
    'PySide6.QtSerialBus',
    'PySide6.QtRemoteObjects',
    'PySide6.QtScxml',
    'PySide6.QtWebSockets',
    'PySide6.QtHttpServer',

    # Ferramentas de desenvolvimento e testes do Qt
    'PySide6.QtTest',
    'PySide6.QtDesigner',
    'PySide6.QtUiTools',
    'PySide6.QtHelp',
    'PySide6.QtSql',
    'PySide6.QtOpenGL',
    'PySide6.QtOpenGLWidgets',

    # Bibliotecas padrão do Python que não são utilizadas pelo app
    'tkinter',
    'unittest',
    'pydoc',
    'test',
]

a = Analysis(
    ['ui_panel.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'credentials_backend',
        'credentials_dialog',
        'thinqconnect',
        'aiohttp',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=qt_excludes,
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WTC LG',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/app_icon.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='WTC LG',
)
