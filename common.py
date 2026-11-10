"""
common.py - Utilitarios compartilhados entre o painel (ui_panel) e o dialogo de credenciais.
"""

import os
import sys

from PySide6 import QtCore, QtGui, QtSvg

FONT_STACK = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"


def get_base_dir() -> str:
    """Diretorio base da aplicacao (local do executavel ou do script), onde o .env pode residir."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_resource_path(relative_path: str) -> str:
    """Caminho absoluto para recursos/assets, em Python puro ou empacotado (PyInstaller _MEIPASS)."""
    base = getattr(sys, '_MEIPASS', get_base_dir())
    return os.path.join(base, relative_path)


def init_app_fonts() -> None:
    """Garante que a fonte Inter esteja registrada no QFontDatabase."""
    if not QtGui.QFontDatabase.hasFamily("Inter"):
        font_path = get_resource_path(os.path.join("assets", "fonts", "Inter-Variable.ttf"))
        if os.path.exists(font_path):
            QtGui.QFontDatabase.addApplicationFont(font_path)


def is_windows_dark_mode() -> bool:
    """Verifica no registro se o tema de aplicativos do Windows e escuro (True) ou claro (False)."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            0,
            winreg.KEY_READ,
        )
        val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return bool(val == 0)
    except Exception:
        return True


def svg_to_pixmap(svg_text: str, width: int = 24, height: int = 24, color: str = "#FFFFFF") -> QtGui.QPixmap:
    """Renderiza um SVG embutido, trocando 'currentColor' e '{color}' pela cor informada."""
    svg_colored = svg_text.replace("currentColor", color).replace("{color}", color)
    renderer = QtSvg.QSvgRenderer(QtCore.QByteArray(svg_colored.encode('utf-8')))
    pix = QtGui.QPixmap(width, height)
    pix.fill(QtCore.Qt.GlobalColor.transparent)
    painter = QtGui.QPainter(pix)
    painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
    renderer.render(painter)
    painter.end()
    return pix
