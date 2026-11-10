import sys
import os
import math
import re
from PySide6 import QtCore, QtGui, QtWidgets, QtSvg, QtNetwork

from theme import PALETTES, THEME_MODES, get_palette, resolve_theme_name
import updater

__version__ = "1.0.0"
__app_name__ = "WTC LG"

# =====================================================================
# Design System & Dynamic Background Themes
# =====================================================================
ACCENT_GREEN = "#4ADE80"
ACCENT_CYAN = "#38BDF8"
ACCENT_ORANGE = "#FB923C"
THUMB_COLOR = "#D4C5B9"
POWER_CREAM = "#D4D0C7"


# Aliases de compatibilidade para código que utilize as constantes diretamente
BG_COLOR = PALETTES["dark"]["bg_color"]
CARD_BG = PALETTES["dark"]["card_bg"]
CARD_HOVER = PALETTES["dark"]["card_hover"]
CARD_ACTIVE = PALETTES["dark"]["card_active"]
BORDER_COLOR = PALETTES["dark"]["border_color"]
TEXT_PRIMARY = PALETTES["dark"]["text_primary"]
TEXT_SECONDARY = PALETTES["dark"]["text_secondary"]

# SVGs de sistema mantidos
SVG_LEAF_FILL = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <path fill="currentColor" fill-rule="evenodd" d="
    M 20.8 3.2 
    C 11.5 3.8 3.5 10.5 3.5 19.5 
    C 4.0 19.5 4.5 19.5 5.0 19.5 
    C 14.0 19.5 20.2 12.5 20.8 3.2 Z
    M 5.8 17.5
    C 9.2 14.5 13.5 10.5 17.5 6.8
    C 17.2 6.5 16.8 6.2 16.5 6.5
    C 12.5 10.0 8.5 13.8 5.2 17.0
    Z" />
</svg>"""

SVG_POWER = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  <path d="M 7.05 6.05 A 8.5 8.5 0 1 0 16.95 6.05" />
  <line x1="12" y1="2.5" x2="12" y2="11.5" />
</svg>"""

SVG_SHIELD = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  <path d="M 12 3 C 8 3 4.5 4.5 4.5 7.5 C 4.5 13.5 8 18.5 12 21 C 16 18.5 19.5 13.5 19.5 7.5 C 19.5 4.5 16 3 12 3 Z" />
  <polyline points="8.5 11.5 11 14 16 8.5" />
</svg>"""

SVG_SLIDERS = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  <line x1="3" y1="6" x2="21" y2="6" />
  <circle cx="16" cy="6" r="2.5" fill="#0D0E12" stroke="currentColor" stroke-width="1.8" />
  <line x1="3" y1="12" x2="21" y2="12" />
  <circle cx="8" cy="12" r="2.5" fill="#0D0E12" stroke="currentColor" stroke-width="1.8" />
  <line x1="3" y1="18" x2="21" y2="18" />
  <circle cx="17" cy="18" r="2.5" fill="#0D0E12" stroke="currentColor" stroke-width="1.8" />
</svg>"""

TRANSLATIONS = {
    "en": {
        "room": "Room",
        "mode": "Mode",
        "fan_speed": "Fan speed",
        "sleep": "Sleep",
        "airflow": "Airflow",
        "connected": "Connected",
        "syncing": "Syncing...",
        "disconnected": "Disconnected",
        "Cool": "Cool",
        "Heat": "Heat",
        "Fan": "Fan",
        "Dry": "Dry",
        "Auto": "Auto",
        "Low": "Low",
        "Mid": "Mid",
        "High": "High",
        "Off": "Off",
        "Vertical": "Vertical",
        "Swing": "Swing",
        "settings": "Settings",
        "temp_unit": "Temperature Unit",
        "celsius": "Celsius (°C)",
        "fahrenheit": "Fahrenheit (°F)",
        "language": "Language",
        "sync_thinq": "Sync with LG ThinQ",
        "autostart": "Start with Windows",
        "open_panel": "Open Panel",
        "quit": "Quit",
        "theme": "Background Theme",
        "theme_system": "System",
        "theme_light": "Light (Off-white)",
        "theme_dark": "Dark",
        "theme_black": "True Black",
        "ac_color": "AC Unit Style",
        "ac_color_white": "Classic White",
        "ac_color_black": "Artcool Black",
        "clear_data": "Clear Credentials & Data...",
        "clear_data_title": "Reset Application Data",
        "clear_data_confirm": "Are you sure you want to permanently disconnect and delete all your LG ThinQ credentials and local settings from this computer?\n\nThis action cannot be undone.",
        "clear_data_success": "All credentials, vault files, and saved preferences have been permanently removed from this computer.",
        "update_check": "Check for updates...",
        "update_auto": "Check for updates automatically",
        "update_title": "WTC LG Update",
        "update_available": "Version {v} is available. Download and install now? The app will close and reopen.",
        "update_available_portable": "Version {v} is available. This is the portable build, so it cannot update itself. Open the download page?",
        "update_notify": "Version {v} is available. Click here to update.",
        "update_none": "You are on the latest version ({v}).",
        "update_error": "Could not update: {e}",
        "update_downloading": "Downloading the update...",
        "command_failed_title": "Command not sent",
        "command_failed": "The AC did not respond. The panel was synced with the real device state.",
    },
    "pt": {
        "room": "Ambiente",
        "mode": "Modo",
        "fan_speed": "Velocidade",
        "sleep": "Timer",
        "airflow": "Direção",
        "connected": "Conectado",
        "syncing": "Sincronizando...",
        "disconnected": "Desconectado",
        "Cool": "Frio",
        "Heat": "Quente",
        "Fan": "Ventilar",
        "Dry": "Desumidificar",
        "Auto": "Auto",
        "Low": "Baixa",
        "Mid": "Média",
        "High": "Alta",
        "Off": "Desligado",
        "Vertical": "Fixo",
        "Swing": "Oscilar",
        "settings": "Configurações",
        "temp_unit": "Unidade de Temperatura",
        "celsius": "Celsius (°C)",
        "fahrenheit": "Fahrenheit (°F)",
        "language": "Idioma",
        "sync_thinq": "Sincronizar com LG ThinQ",
        "autostart": "Iniciar com o Windows",
        "open_panel": "Abrir Painel",
        "quit": "Sair",
        "theme": "Tema de Fundo",
        "theme_system": "Sistema",
        "theme_light": "Claro (Off-white)",
        "theme_dark": "Escuro",
        "theme_black": "Preto Puro (True Black)",
        "ac_color": "Cor do Ar-Condicionado",
        "ac_color_white": "Branco Clássico",
        "ac_color_black": "Preto Artcool",
        "clear_data": "Excluir Credenciais e Dados...",
        "clear_data_title": "Redefinir Dados do Aplicativo",
        "clear_data_confirm": "Tem certeza que deseja desconectar e apagar permanentemente todas as suas credenciais LG ThinQ e configurações locais deste computador?\n\nEsta ação não poderá ser desfeita.",
        "clear_data_success": "Todas as credenciais, arquivos do cofre e preferências salvas foram excluídos permanentemente deste computador.",
        "update_check": "Verificar atualizações...",
        "update_auto": "Buscar atualizações automaticamente",
        "update_title": "Atualização do WTC LG",
        "update_available": "A versão {v} está disponível. Baixar e instalar agora? O app será fechado e reaberto.",
        "update_available_portable": "A versão {v} está disponível. Esta é a versão portátil e não se atualiza sozinha. Abrir a página de download?",
        "update_notify": "A versão {v} está disponível. Clique aqui para atualizar.",
        "update_none": "Você já está na versão mais recente ({v}).",
        "update_error": "Não foi possível atualizar: {e}",
        "update_downloading": "Baixando a atualização...",
        "command_failed_title": "Comando não enviado",
        "command_failed": "O ar-condicionado não respondeu. O painel foi sincronizado com o estado real do aparelho.",
    },
    "es": {
        "room": "Ambiente",
        "mode": "Modo",
        "fan_speed": "Velocidad",
        "sleep": "Temporizador",
        "airflow": "Dirección",
        "connected": "Conectado",
        "syncing": "Sincronizando...",
        "disconnected": "Desconectado",
        "Cool": "Frío",
        "Heat": "Calor",
        "Fan": "Ventilador",
        "Dry": "Deshumidificar",
        "Auto": "Auto",
        "Low": "Baja",
        "Mid": "Media",
        "High": "Alta",
        "Off": "Apagado",
        "Vertical": "Fijo",
        "Swing": "Oscilar",
        "settings": "Configuraciones",
        "temp_unit": "Unidad de Temperatura",
        "celsius": "Celsius (°C)",
        "fahrenheit": "Fahrenheit (°F)",
        "language": "Idioma",
        "sync_thinq": "Sincronizar com LG ThinQ",
        "autostart": "Iniciar con Windows",
        "open_panel": "Abrir Panel",
        "quit": "Salir",
        "theme": "Tema de Fondo",
        "theme_system": "Sistema",
        "theme_light": "Claro (Off-white)",
        "theme_dark": "Oscuro",
        "theme_black": "Negro Puro (True Black)",
        "ac_color": "Color del Aire Acondicionado",
        "ac_color_white": "Blanco Clásico",
        "ac_color_black": "Negro Artcool",
        "clear_data": "Eliminar Credenciales y Datos...",
        "clear_data_title": "Restablecer Datos de la Aplicación",
        "clear_data_confirm": "¿Está seguro de que desea desconectar y eliminar permanentemente todas sus credenciales de LG ThinQ y configuraciones locales de esta computadora?\n\nEsta acción no se puede deshacer.",
        "clear_data_success": "Todas las credenciales, archivos de la bóveda y preferencias guardadas se han eliminado permanentemente de esta computadora.",
        "update_check": "Buscar actualizaciones...",
        "update_auto": "Buscar actualizaciones automáticamente",
        "update_title": "Actualización de WTC LG",
        "update_available": "La versión {v} está disponible. ¿Descargar e instalar ahora? La aplicación se cerrará y se reabrirá.",
        "update_available_portable": "La versión {v} está disponible. Esta es la versión portátil y no se actualiza sola. ¿Abrir la página de descarga?",
        "update_notify": "La versión {v} está disponible. Haz clic aquí para actualizar.",
        "update_none": "Ya tienes la versión más reciente ({v}).",
        "update_error": "No se pudo actualizar: {e}",
        "update_downloading": "Descargando la actualización...",
        "command_failed_title": "Comando no enviado",
        "command_failed": "El aire acondicionado no respondió. El panel se sincronizó con el estado real del equipo.",
    }
}


# Design vetorial do ar condicionado (modulo local, analisado pelo PyInstaller)
from ac_unit import render_ac_svg
from common import (
    FONT_STACK, get_base_dir, get_resource_path, init_app_fonts,
    is_windows_dark_mode, svg_to_pixmap,
)
from thinq_client import ThinQClient


def auto_update_enabled() -> bool:
    return QtCore.QSettings("WTC LG", "Preferences").value("auto_update", False, type=bool)


def set_auto_update_enabled(enabled: bool) -> None:
    QtCore.QSettings("WTC LG", "Preferences").setValue("auto_update", bool(enabled))


def is_autostart_enabled(app_name: str = "WTC LG") -> bool:
    """Verifica se o aplicativo está configurado para inicializar com o Windows no Registro (HKCU)."""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
        try:
            val, _ = winreg.QueryValueEx(key, app_name)
            winreg.CloseKey(key)
            return bool(val)
        except FileNotFoundError:
            try:
                val, _ = winreg.QueryValueEx(key, "LGAirConditioner")
                winreg.CloseKey(key)
                return bool(val)
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
    except Exception:
        return False


def set_autostart_enabled(enabled: bool, app_name: str = "WTC LG") -> bool:
    """Adiciona ou remove a inicialização com o Windows no Registro (HKCU, sem exigir admin)."""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        if enabled:
            if getattr(sys, 'frozen', False):
                cmd = f'"{sys.executable}" --silent'
            else:
                script_path = os.path.abspath(__file__)
                cmd = f'"{sys.executable}" "{script_path}" --silent'
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, cmd)
            try:
                winreg.DeleteValue(key, "LGAirConditioner")
            except Exception:
                pass
        else:
            try:
                winreg.DeleteValue(key, app_name)
            except Exception:
                pass
            try:
                winreg.DeleteValue(key, "LGAirConditioner")
            except Exception:
                pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"[Autostart Error]: {e}", flush=True)
        return False


def load_user_svg(filename: str, width: int = 30, height: int = 30, padding: float = 1.0, color: str = "#FFFFFF", stroke_width: float = 0.0) -> QtGui.QPixmap:
    """Carrega os arquivos SVG da pasta assets com cor branca pura (#FFFFFF) e dimensionamento proporcional"""
    path = get_resource_path(os.path.join("assets", filename))
    if not os.path.exists(path):
        pix = QtGui.QPixmap(width, height)
        pix.fill(QtCore.Qt.GlobalColor.transparent)
        return pix

    with open(path, "r", encoding="utf-8") as f:
        svg = f.read()

    # Garantir preenchimento branco puro e traço encorpado se solicitado
    stroke_attr = f' stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"' if stroke_width > 0 else ""
    if "fill=" not in svg:
        svg = svg.replace("<path", f'<path fill="{color}"{stroke_attr}')
    else:
        svg = re.sub(r'fill="[^"]*"', f'fill="{color}"{stroke_attr}', svg)

    renderer = QtSvg.QSvgRenderer(QtCore.QByteArray(svg.encode("utf-8")))
    pix = QtGui.QPixmap(width, height)
    pix.fill(QtCore.Qt.GlobalColor.transparent)
    p = QtGui.QPainter(pix)
    p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)

    target_rect = QtCore.QRectF(padding, padding, width - 2 * padding, height - 2 * padding)
    renderer.render(p, target_rect)
    p.end()
    return pix


def load_user_icon(filename: str, width: int = 24, height: int = 24, color: str = "#FFFFFF") -> QtGui.QPixmap:
    """Carrega ícone (PNG ou SVG) da pasta assets e aplica a cor desejada (branco puro por padrão)"""
    assets_dir = get_resource_path("assets")
    path = os.path.join(assets_dir, filename)

    # Suporta fallback automático entre extensões se necessário
    if not os.path.exists(path):
        base, _ = os.path.splitext(filename)
        for ext in [".png", ".svg"]:
            candidate = os.path.join(assets_dir, base + ext)
            if os.path.exists(candidate):
                path = candidate
                break

    if not os.path.exists(path):
        pix = QtGui.QPixmap(width, height)
        pix.fill(QtCore.Qt.GlobalColor.transparent)
        return pix

    if path.lower().endswith(".svg"):
        return load_user_svg(os.path.basename(path), width, height, padding=0, color=color)

    # Para PNG (como eco.png): redimensiona suavemente e tinge os pixels preservando a transparência
    orig = QtGui.QPixmap(path)
    scaled = orig.scaled(width, height, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
    result = QtGui.QPixmap(scaled.size())
    result.fill(QtCore.Qt.GlobalColor.transparent)
    p = QtGui.QPainter(result)
    p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
    p.drawPixmap(0, 0, scaled)
    p.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_SourceIn)
    p.fillRect(result.rect(), QtGui.QColor(color))
    p.end()
    return result


def create_stepper_icon(symbol_type: str, size: int = 38, color: str = "#FFFFFF") -> QtGui.QIcon:
    """Gera ícone vetorial perfeitamente centralizado para os botões (+) e (-) do stepper"""
    pix = QtGui.QPixmap(size, size)
    pix.fill(QtCore.Qt.GlobalColor.transparent)
    p = QtGui.QPainter(pix)
    p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    pen = QtGui.QPen(QtGui.QColor(color), 2.2)
    pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
    p.setPen(pen)

    cx, cy = size / 2.0, size / 2.0
    half_len = 6.5

    # Linha horizontal perfeitamente centralizada
    p.drawLine(QtCore.QPointF(cx - half_len, cy), QtCore.QPointF(cx + half_len, cy))

    # Linha vertical (apenas para o botão '+')
    if symbol_type == "plus":
        p.drawLine(QtCore.QPointF(cx, cy - half_len), QtCore.QPointF(cx, cy + half_len))

    p.end()
    return QtGui.QIcon(pix)


def create_dot_pixmap(diameter: int = 6, color_hex: str = ACCENT_GREEN) -> QtGui.QPixmap:
    """Gera um círculo antialiasing nítido para o indicador de status de conexão"""
    scale = 3
    size = diameter * scale
    pix = QtGui.QPixmap(size, size)
    pix.fill(QtCore.Qt.GlobalColor.transparent)
    p = QtGui.QPainter(pix)
    p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    p.setPen(QtCore.Qt.PenStyle.NoPen)
    p.setBrush(QtGui.QBrush(QtGui.QColor(color_hex)))
    p.drawEllipse(0, 0, size, size)
    p.end()
    return pix.scaled(
        diameter, diameter,
        QtCore.Qt.AspectRatioMode.KeepAspectRatio,
        QtCore.Qt.TransformationMode.SmoothTransformation
    )


class AnimatedAirCurtainHero(QtWidgets.QWidget):
    """Widget Hero: Ar Condicionado Split com o novo design vetorial moderno"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(168)
        self.is_powered_on = False
        self.current_mode = "Cool"
        self.fan_speed = "Auto"
        self.target_temp = 21
        self.airflow_state = "Vertical"
        self.ac_color = "white"
        self._louver_angle = 0.0
        self._flow_progress = 0.0
        self._phase = 0.0
        self._renderer = QtSvg.QSvgRenderer()

        self._louver_anim = QtCore.QPropertyAnimation(self, b"louver_angle", self)
        self._louver_anim.setDuration(550)
        self._louver_anim.setEasingCurve(QtCore.QEasingCurve.Type.InOutCubic)

        self._flow_anim = QtCore.QPropertyAnimation(self, b"flow_progress", self)
        self._flow_anim.setDuration(600)
        self._flow_anim.setEasingCurve(QtCore.QEasingCurve.Type.InOutCubic)
        self._flow_anim.finished.connect(self._on_flow_anim_finished)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._step)
        self.timer.setInterval(33)

    def _get_louver_angle(self):
        return self._louver_angle

    def _set_louver_angle(self, angle: float):
        self._louver_angle = angle
        self.update()

    louver_angle = QtCore.Property(float, _get_louver_angle, _set_louver_angle)

    def _get_flow_progress(self):
        return self._flow_progress

    def _set_flow_progress(self, val: float):
        self._flow_progress = val
        self.update()

    flow_progress = QtCore.Property(float, _get_flow_progress, _set_flow_progress)

    def _on_flow_anim_finished(self):
        if not self.is_powered_on and self._flow_progress <= 0.01:
            if self.timer.isActive():
                self.timer.stop()
            self.update()

    def set_power(self, power: bool):
        self.is_powered_on = power
        target_angle = 70.0 if power else 0.0
        self._louver_anim.stop()
        self._louver_anim.setStartValue(self._louver_angle)
        self._louver_anim.setEndValue(target_angle)
        self._louver_anim.start()

        self._flow_anim.stop()
        self._flow_anim.setStartValue(self._flow_progress)
        self._flow_anim.setEndValue(1.0 if power else 0.0)
        self._flow_anim.start()

        if power or self._flow_progress > 0.01:
            if not self.timer.isActive():
                self.timer.start()
        self.update()

    def set_mode(self, mode: str):
        self.current_mode = mode
        self.update()

    def set_fan(self, fan: str):
        self.fan_speed = fan
        self.update()

    def set_temp(self, temp):
        try:
            self.target_temp = int(round(float(temp)))
        except (ValueError, TypeError):
            self.target_temp = 21
        self.update()

    def set_ac_color(self, color: str):
        if color in ["white", "black"] and self.ac_color != color:
            self.ac_color = color
            self.update()

    def set_airflow(self, airflow: str):
        self.airflow_state = airflow
        self.update()

    def showEvent(self, event):
        super().showEvent(event)
        if self.is_powered_on and not self.timer.isActive():
            self.timer.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.timer.stop()

    def _step(self):
        if not self.is_powered_on and self._flow_progress <= 0.01 and self._louver_angle <= 0.01:
            self.timer.stop()
            self.update()
            return

        fan_speed_factor = {"low": 0.025, "mid": 0.040, "high": 0.065, "auto": 0.040}
        delta = fan_speed_factor.get(self.fan_speed.lower(), 0.040)
        self._phase += delta
        if self._phase > 2 * math.pi * 100:
            self._phase = 0.0

        self.update()

    def paintEvent(self, event):
        w = self.width()
        h = self.height()
        # Escala reduzida em 10% para melhor equilíbrio visual do mockup e da cortina de ar
        scale = min(w / 400.0, 185.0 / 210.0) * 0.90
        target_w = 400.0 * scale
        target_h = 250.0 * scale
        target_x = (w - target_w) / 2.0
        target_y = 2.0
        target_rect = QtCore.QRectF(target_x, target_y, target_w, target_h)

        if render_ac_svg is not None:
            is_swing = (self.airflow_state.lower() == "swing")
            show_display_temp = (
                self.is_powered_on
                and self.current_mode.lower() not in ("fan", "ventilação", "ventilacao")
                and self.target_temp is not None
            )
            svg_data = render_ac_svg(
                on=self.is_powered_on,
                mode=self.current_mode,
                fan=self.fan_speed,
                louver=self._louver_angle,
                swing=is_swing,
                temp=self.target_temp if show_display_temp else None,
                phase=self._phase if (self.is_powered_on or self._flow_progress > 0.01) else None,
                uid="ac_hero",
                ac_color=self.ac_color,
                flow_progress=self._flow_progress,
            )
            self._renderer.load(QtCore.QByteArray(svg_data.encode('utf-8')))

            # Renderiza primeiro em buffer para aplicar gradiente suave de transparência no fluxo de ar
            buf = QtGui.QImage(w, h, QtGui.QImage.Format.Format_ARGB32_Premultiplied)
            buf.fill(QtCore.Qt.GlobalColor.transparent)
            bp = QtGui.QPainter(buf)
            bp.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            bp.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
            self._renderer.render(bp, target_rect)

            # Transição suave (fade out) para transparência no término da cortina de ar
            if self.is_powered_on or self._flow_progress > 0.01:
                bp.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_DestinationIn)
                fade_grad = QtGui.QLinearGradient(0, 0, 0, h)
                fade_grad.setColorAt(0.0, QtGui.QColor(0, 0, 0, 255))
                fade_grad.setColorAt(0.52, QtGui.QColor(0, 0, 0, 255))
                fade_grad.setColorAt(0.75, QtGui.QColor(0, 0, 0, 210))
                fade_grad.setColorAt(0.90, QtGui.QColor(0, 0, 0, 90))
                fade_grad.setColorAt(1.0, QtGui.QColor(0, 0, 0, 0))
                bp.fillRect(0, 0, w, h, QtGui.QBrush(fade_grad))

            bp.end()

            p = QtGui.QPainter(self)
            p.drawImage(0, 0, buf)
            p.end()


class AnimatedToggle(QtWidgets.QCheckBox):
    """Switch pílula estilo iOS com polegar em cor creme / champagne"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(46, 24)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self._thumb_position = 3.0

        self._anim = QtCore.QPropertyAnimation(self, b"thumb_position", self)
        self._anim.setDuration(160)
        self._anim.setEasingCurve(QtCore.QEasingCurve.Type.InOutQuad)
        self.stateChanged.connect(self._start_animation)

    def _get_thumb_position(self):
        return self._thumb_position

    def _set_thumb_position(self, pos):
        self._thumb_position = pos
        self.update()

    thumb_position = QtCore.Property(float, _get_thumb_position, _set_thumb_position)

    def _start_animation(self, state):
        self._anim.stop()
        self._anim.setEndValue(25.0 if state else 3.0)
        self._anim.start()

    def setChecked(self, checked: bool):
        super().setChecked(checked)
        if self.signalsBlocked():
            self._anim.stop()
            self._thumb_position = 25.0 if checked else 3.0
            self.update()

    def hitButton(self, pos: QtCore.QPoint) -> bool:
        """Garante que 100% da área do switch receba cliques do mouse"""
        return self.contentsRect().contains(pos)

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        is_light = getattr(self, "_is_light", False)
        is_on = self.isChecked()
        bg_col = QtGui.QColor(THUMB_COLOR) if is_on else (QtGui.QColor(210, 215, 224) if is_light else QtGui.QColor(42, 45, 54))
        p.setBrush(QtGui.QBrush(bg_col))
        p.setPen(QtCore.Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, self.width(), self.height(), 12, 12)

        thumb_col = QtGui.QColor(20, 22, 28) if is_on else (QtGui.QColor(100, 110, 125) if is_light else QtGui.QColor(160, 166, 178))
        p.setBrush(QtGui.QBrush(thumb_col))
        p.drawEllipse(QtCore.QPointF(self._thumb_position + 9.0, 12.0), 9.0, 9.0)
        p.end()

    def set_light_mode(self, is_light: bool):
        self._is_light = is_light
        self.update()


class EcoCard(QtWidgets.QFrame):
    """Card pílula interativo para o Modo Eco"""
    clicked = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("EcoCard")
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.clicked.emit()
            event.accept()
            return
        super().mousePressEvent(event)


def lerp_color(c1, c2, t: float) -> QtGui.QColor:
    """Interpola linearmente entre duas cores."""
    col1 = QtGui.QColor(c1) if not isinstance(c1, QtGui.QColor) else c1
    col2 = QtGui.QColor(c2) if not isinstance(c2, QtGui.QColor) else c2
    factor = max(0.0, min(1.0, float(t)))
    r = int(col1.red() + (col2.red() - col1.red()) * factor)
    g = int(col1.green() + (col2.green() - col1.green()) * factor)
    b = int(col1.blue() + (col2.blue() - col1.blue()) * factor)
    a = int(col1.alpha() + (col2.alpha() - col1.alpha()) * factor)
    return QtGui.QColor(r, g, b, a)


SLIDER_MODE_THEMES = {
    "cool": {
        "thumb": "#38BDF8",
        "thumb_hover": "#7DD3FC",
        "track_stops": [
            (0.0, "#16202E"),
            (0.4, "#1E354F"),
            (0.85, "#0E5A8A"),
            (1.0, "#0284C7"),
        ],
    },
    "heat": {
        "thumb": "#FB923C",
        "thumb_hover": "#FDBA74",
        "track_stops": [
            (0.0, "#241B1F"),
            (0.4, "#42241C"),
            (0.85, "#7C3416"),
            (1.0, "#C2410C"),
        ],
    },
    "dry": {
        "thumb": "#2DD4BF",
        "thumb_hover": "#5EEAD4",
        "track_stops": [
            (0.0, "#152424"),
            (0.4, "#16423D"),
            (0.85, "#11695F"),
            (1.0, "#0F766E"),
        ],
    },
    "fan": {
        "thumb": "#CBD5E1",
        "thumb_hover": "#F1F5F9",
        "track_stops": [
            (0.0, "#1E222A"),
            (0.4, "#2B3342"),
            (0.85, "#475569"),
            (1.0, "#64748B"),
        ],
    },
    "auto": {
        "thumb": "#818CF8",
        "thumb_hover": "#A5B4FC",
        "track_stops": [
            (0.0, "#1E1F30"),
            (0.4, "#2E3052"),
            (0.85, "#4338CA"),
            (1.0, "#6366F1"),
        ],
    },
}


def get_slider_theme(mode: str) -> dict:
    if not mode:
        return SLIDER_MODE_THEMES["cool"]
    key = str(mode).lower().strip()
    if key in ["heat", "quente", "calor"]:
        return SLIDER_MODE_THEMES["heat"]
    elif key in ["cool", "frio", "frío"]:
        return SLIDER_MODE_THEMES["cool"]
    elif key in ["dry", "desumidificar", "deshumidificar"]:
        return SLIDER_MODE_THEMES["dry"]
    elif key in ["fan", "ventilar", "ventilador"]:
        return SLIDER_MODE_THEMES["fan"]
    elif key in ["auto", "automático", "automatico"]:
        return SLIDER_MODE_THEMES["auto"]
    return SLIDER_MODE_THEMES.get(key, SLIDER_MODE_THEMES["cool"])


class ModernTrackSlider(QtWidgets.QSlider):
    """Slider de trilha premium com gradiente contínuo e pill perfeitamente integrado à paleta do modo"""
    def __init__(self, parent=None):
        super().__init__(QtCore.Qt.Orientation.Horizontal, parent)
        self._dragging = False
        self._hovered = False
        self._visual_ratio = 0.0
        self._current_mode = "cool"

        self._anim = QtCore.QPropertyAnimation(self, b"visual_ratio", self)
        self._anim.setDuration(130)
        self._anim.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)

        self._color_ratio = 1.0
        self._prev_theme = get_slider_theme("cool")
        self._curr_theme = get_slider_theme("cool")
        self._color_anim = QtCore.QPropertyAnimation(self, b"color_ratio", self)
        self._color_anim.setDuration(180)
        self._color_anim.setEasingCurve(QtCore.QEasingCurve.Type.InOutCubic)

        self.setFixedHeight(38)
        self.setMinimum(18)
        self.setMaximum(30)
        self.setValue(22)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)

    def _calc_ratio(self, val):
        span = self.maximum() - self.minimum()
        return (val - self.minimum()) / float(span) if span > 0 else 0.0

    def _get_visual_ratio(self):
        return self._visual_ratio

    def _set_visual_ratio(self, r):
        self._visual_ratio = r
        self.update()

    visual_ratio = QtCore.Property(float, _get_visual_ratio, _set_visual_ratio)

    def _get_color_ratio(self):
        return self._color_ratio

    def _set_color_ratio(self, r):
        self._color_ratio = r
        self.update()

    color_ratio = QtCore.Property(float, _get_color_ratio, _set_color_ratio)

    def _get_interpolated_theme(self, t: float) -> dict:
        if t >= 1.0:
            return self._curr_theme
        if t <= 0.0:
            return self._prev_theme

        thumb = lerp_color(self._prev_theme["thumb"], self._curr_theme["thumb"], t).name()
        thumb_hover = lerp_color(self._prev_theme["thumb_hover"], self._curr_theme["thumb_hover"], t).name()

        stops = []
        for (p1, c1_hex), (p2, c2_hex) in zip(self._prev_theme["track_stops"], self._curr_theme["track_stops"]):
            col = lerp_color(c1_hex, c2_hex, t).name()
            stops.append((p1, col))

        return {
            "thumb": thumb,
            "thumb_hover": thumb_hover,
            "track_stops": stops,
        }

    def set_mode(self, mode: str):
        if not mode:
            return
        theme = get_slider_theme(mode)
        norm_key = "cool"
        k = str(mode).lower().strip()
        if k in ["heat", "quente", "calor"]:
            norm_key = "heat"
        elif k in ["dry", "desumidificar", "deshumidificar"]:
            norm_key = "dry"
        elif k in ["fan", "ventilar", "ventilador"]:
            norm_key = "fan"
        elif k in ["auto", "automático", "automatico"]:
            norm_key = "auto"

        if norm_key == self._current_mode and self._color_ratio >= 1.0:
            return

        self._current_mode = norm_key
        if not self.isVisible():
            self._color_anim.stop()
            self._prev_theme = theme
            self._curr_theme = theme
            self._color_ratio = 1.0
            self.update()
        else:
            self._prev_theme = self._get_interpolated_theme(self._color_ratio)
            self._curr_theme = theme
            self._color_anim.stop()
            self._color_ratio = 0.0
            self._color_anim.setStartValue(0.0)
            self._color_anim.setEndValue(1.0)
            self._color_anim.start()

    def setValue(self, val):
        clamped = max(self.minimum(), min(self.maximum(), int(val)))
        super().setValue(clamped)
        target_r = self._calc_ratio(clamped)
        if self._dragging or not self.isVisible():
            self._anim.stop()
            self._visual_ratio = target_r
            self.update()
        else:
            self._anim.stop()
            self._anim.setStartValue(self._visual_ratio)
            self._anim.setEndValue(target_r)
            self._anim.start()

    def setMinimum(self, val):
        super().setMinimum(val)
        self._visual_ratio = self._calc_ratio(self.value())
        self.update()

    def setMaximum(self, val):
        super().setMaximum(val)
        self._visual_ratio = self._calc_ratio(self.value())
        self.update()

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._dragging = True
            self._anim.stop()
            self._update_from_x(event.position().x())
            event.accept()

    def mouseMoveEvent(self, event):
        if self._dragging:
            self._update_from_x(event.position().x())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._dragging = False
            self.update()
            event.accept()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.setValue(self.value() + 1)
        elif delta < 0:
            self.setValue(self.value() - 1)
        event.accept()

    def _update_from_x(self, x):
        w = float(self.width())
        pill_w = 24.0
        pad = 2.0
        min_x = pad
        max_x = w - pill_w - pad
        if max_x <= min_x:
            return
        ratio = max(0.0, min(1.0, (x - pill_w / 2.0 - min_x) / (max_x - min_x)))
        self._visual_ratio = ratio
        val = self.minimum() + round(ratio * (self.maximum() - self.minimum()))
        if val != self.value():
            super().setValue(int(val))
        self.update()

    def set_theme_colors(self, groove_color: str, groove_border: str):
        self._groove_color = groove_color
        self._groove_border = groove_border
        self.update()

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)

        w = float(self.width())
        h = float(self.height())
        track_h = 28.0
        track_y = (h - track_h) / 2.0
        track_rect = QtCore.QRectF(0.0, track_y, w, track_h)
        radius = 14.0

        groove_col = QtGui.QColor(getattr(self, "_groove_color", "#181A22"))
        groove_border = QtGui.QColor(getattr(self, "_groove_border", "rgba(255, 255, 255, 14)"))

        # 1. Base Track (Groove)
        p.setPen(QtGui.QPen(groove_border, 1.0))
        p.setBrush(QtGui.QBrush(groove_col))
        p.drawRoundedRect(track_rect, radius, radius)

        # 2. Pill Position (Circle: 24x24)
        pill_w = 24.0
        pill_h = 24.0
        pad = 2.0
        min_x = pad
        max_x = w - pill_w - pad
        pill_x = min_x + self._visual_ratio * (max_x - min_x)
        pill_y = (h - pill_h) / 2.0

        # 3. Active Gradient (Concentric with pill: ends exactly pad px ahead of pill)
        grad_end_x = min(w, pill_x + pill_w + pad)

        track_path = QtGui.QPainterPath()
        track_path.addRoundedRect(track_rect, radius, radius)
        p.save()
        p.setClipPath(track_path)

        active_theme = self._get_interpolated_theme(self._color_ratio)

        grad = QtGui.QLinearGradient(0.0, 0.0, grad_end_x, 0.0)
        for pos, col_hex in active_theme["track_stops"]:
            grad.setColorAt(pos, QtGui.QColor(col_hex))

        p.setPen(QtCore.Qt.PenStyle.NoPen)
        p.setBrush(QtGui.QBrush(grad))
        grad_rect = QtCore.QRectF(0.0, track_y, grad_end_x, track_h)
        p.drawRoundedRect(grad_rect, radius, radius)
        p.restore()

        # 4. Pill (Handle: Circle)
        pill_rect = QtCore.QRectF(pill_x, pill_y, pill_w, pill_h)
        pill_col = QtGui.QColor(active_theme["thumb_hover"] if (self._hovered or self._dragging) else active_theme["thumb"])
        p.setPen(QtCore.Qt.PenStyle.NoPen)
        p.setBrush(QtGui.QBrush(pill_col))
        p.drawEllipse(pill_rect)

        p.end()


class ControlCard(QtWidgets.QFrame):
    """Card inferior espaçoso com ícones brancos, animação no fan-speed e airflow animado"""
    clicked = QtCore.Signal()

    def __init__(self, key: str, title: str, initial_value: str, is_sleep: bool = False, parent=None):
        super().__init__(parent)
        self.key = key
        self.title_text = title
        self.value_text = initial_value
        self.is_sleep = is_sleep
        self.is_expanded = False
        self._is_hovered = False
        self.is_powered_on = True

        self.setObjectName("ControlCard")
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        # Altura de 94px para proporcionar respiro generoso e proporção idêntica à referência
        self.setFixedHeight(94)
        self._apply_style()

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(0)

        # Linha superior: Ícone (30x30) + Indicador (Chevron ou Ponto)
        top_row = QtWidgets.QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(0)

        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedSize(30, 30)
        top_row.addWidget(self.icon_label)

        top_row.addStretch()

        if self.is_sleep:
            self.arrow = QtWidgets.QLabel("●")
            self.arrow.setStyleSheet("color: #64748B; font-size: 8px; padding-top: 4px;")
        else:
            self.arrow = QtWidgets.QLabel("⌵")
            self.arrow.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; font-weight: bold;")

        top_row.addWidget(self.arrow)
        layout.addLayout(top_row)

        # Espaçamento explícito de 10px entre a linha do ícone e o título
        layout.addSpacing(10)

        self.title_label = QtWidgets.QLabel(title)
        self.title_label.setFixedHeight(14)
        self.title_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; font-weight: 500;")
        layout.addWidget(self.title_label)

        layout.addSpacing(2)

        self.value_label = QtWidgets.QLabel(initial_value)
        self.value_label.setFixedHeight(18)
        self.value_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 14px; font-weight: 600;")
        layout.addWidget(self.value_label)

        layout.addStretch()

        # Configurar recursos específicos por card
        self._init_icons()

    def update_palette(self, palette: dict):
        self._palette = palette
        self._apply_style()
        self.title_label.setStyleSheet(f"color: {palette['text_secondary']}; font-size: 11px; font-weight: 500;")
        self.value_label.setStyleSheet(f"color: {palette['text_primary']}; font-size: 14px; font-weight: 600;")
        if not self.is_sleep:
            self.arrow.setStyleSheet(f"color: {palette['text_secondary']}; font-size: 13px; font-weight: bold;")
        self._init_icons()

    def _init_icons(self):
        palette = getattr(self, "_palette", None)
        icon_col = palette["icon_color"] if palette else "#FFFFFF"

        if self.key == "mode":
            # Padding 2.5 para harmonizar a escala do floco com a altura de 24px dos demais ícones
            pix = load_user_svg("mode.svg", 30, 30, padding=2.5, color=icon_col)
            self.icon_label.setPixmap(pix)

        elif self.key == "fan":
            # Fan speed: Traço encorpado (stroke_width=1.4) e rotação suave
            self.fan_base_pixmap = load_user_svg("fan-speed.svg", 30, 30, padding=1.0, color=icon_col, stroke_width=1.4)
            self.icon_label.setPixmap(self.fan_base_pixmap)
            if not hasattr(self, "_fan_timer"):
                self._fan_angle = 0.0
                self._fan_timer = QtCore.QTimer(self)
                self._fan_timer.setInterval(28)  # ~35 FPS para giro suave e macio
                self._fan_timer.timeout.connect(self._step_fan_rotation)

        elif self.key == "sleep":
            pix = load_user_svg("crescent-moon.svg", 30, 30, padding=1, color=icon_col)
            self.icon_label.setPixmap(pix)

        elif self.key == "airflow":
            # Airflow: Ícone animado originado de air.json (28 frames fluidos)
            self.air_frames = []
            frames_dir = get_resource_path(os.path.join("assets", "air_frames"))
            if os.path.exists(frames_dir):
                for i in range(28):
                    fn = os.path.join(frames_dir, f"frame_{i:02d}.png")
                    if os.path.exists(fn):
                        orig_pm = QtGui.QPixmap(fn).scaled(30, 30, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
                        if icon_col != "#FFFFFF":
                            tinted = QtGui.QPixmap(orig_pm.size())
                            tinted.fill(QtCore.Qt.GlobalColor.transparent)
                            tp = QtGui.QPainter(tinted)
                            tp.drawPixmap(0, 0, orig_pm)
                            tp.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_SourceIn)
                            tp.fillRect(tinted.rect(), QtGui.QColor(icon_col))
                            tp.end()
                            self.air_frames.append(tinted)
                        else:
                            self.air_frames.append(orig_pm)

            if not hasattr(self, "_air_timer"):
                self._air_frame_idx = 0
                self._air_timer = QtCore.QTimer(self)
                self._air_timer.setInterval(42)  # 24 FPS padrão de animação
                self._air_timer.timeout.connect(self._step_air_frame)

            if self.air_frames:
                self.icon_label.setPixmap(self.air_frames[0])

    def _step_air_frame(self):
        if self.air_frames:
            self._air_frame_idx = (self._air_frame_idx + 1) % len(self.air_frames)
            self.icon_label.setPixmap(self.air_frames[self._air_frame_idx])

    def _step_fan_rotation(self):
        # Rotação horária suave (+6 graus a cada ~28ms)
        self._fan_angle = (self._fan_angle + 6.0) % 360.0
        size = self.fan_base_pixmap.size()
        rotated = QtGui.QPixmap(size)
        rotated.fill(QtCore.Qt.GlobalColor.transparent)
        p = QtGui.QPainter(rotated)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
        p.translate(size.width() / 2.0, size.height() / 2.0)
        p.rotate(self._fan_angle)
        p.translate(-size.width() / 2.0, -size.height() / 2.0)
        p.drawPixmap(0, 0, self.fan_base_pixmap)
        p.end()
        self.icon_label.setPixmap(rotated)

    def _check_fan_rotation(self):
        if self.key == "fan":
            should_rotate = self.is_powered_on and (self._is_hovered or self.is_expanded)
            if should_rotate:
                if not self._fan_timer.isActive():
                    self._fan_timer.start()
            else:
                if self._fan_timer.isActive():
                    self._fan_timer.stop()

    def _check_airflow_animation(self):
        if self.key == "airflow" and hasattr(self, "air_frames") and self.air_frames:
            should_animate = self.is_powered_on and (self._is_hovered or self.is_expanded)
            if should_animate:
                if not self._air_timer.isActive():
                    self._air_timer.start()
            else:
                if self._air_timer.isActive():
                    self._air_timer.stop()
                self._air_frame_idx = 0
                self.icon_label.setPixmap(self.air_frames[0])

    def set_power(self, power: bool):
        self.is_powered_on = power
        self._check_fan_rotation()
        self._check_airflow_animation()

    def enterEvent(self, event):
        self._is_hovered = True
        self._check_fan_rotation()
        self._check_airflow_animation()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._is_hovered = False
        self._check_fan_rotation()
        self._check_airflow_animation()
        super().leaveEvent(event)

    def set_title(self, new_title: str):
        self.title_text = new_title
        self.title_label.setText(new_title)

    def set_value(self, new_val: str):
        self.value_text = new_val
        self.value_label.setText(new_val)

    def set_expanded(self, expanded: bool):
        self.is_expanded = expanded
        if not self.is_sleep:
            self.arrow.setText("⌃" if expanded else "⌵")
        self._apply_style()
        self._check_fan_rotation()
        self._check_airflow_animation()

    def _apply_style(self):
        palette = getattr(self, "_palette", None)
        if palette:
            card_active = palette["card_active"]
            border_active = palette["border_active"]
            card_bg = palette["card_bg"]
            border_color = palette["border_color"]
            card_hover = palette["card_hover"]
            border_hover = palette["border_hover"]
        else:
            card_active = CARD_ACTIVE
            border_active = "rgba(255, 255, 255, 0.28)"
            card_bg = CARD_BG
            border_color = BORDER_COLOR
            card_hover = CARD_HOVER
            border_hover = "rgba(255, 255, 255, 0.16)"

        if self.is_expanded:
            self.setStyleSheet(f"""
                QFrame#ControlCard {{
                    background-color: {card_active};
                    border: 1px solid {border_active};
                    border-radius: 18px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame#ControlCard {{
                    background-color: {card_bg};
                    border: 1px solid {border_color};
                    border-radius: 18px;
                }}
                QFrame#ControlCard:hover {{
                    background-color: {card_hover};
                    border: 1px solid {border_hover};
                }}
            """)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class OptionsDrawer(QtWidgets.QFrame):
    """Gaveta animada que se expande abaixo dos 4 cards"""
    option_selected = QtCore.Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_category = None
        self.setObjectName("OptionsDrawer")
        self.palette = PALETTES["dark"]
        self._apply_style()

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(6)

        self.setFixedHeight(0)
        self.setVisible(False)

        self.anim = QtCore.QPropertyAnimation(self, b"fixed_height_prop", self)
        self.anim.setDuration(180)
        self.anim.setEasingCurve(QtCore.QEasingCurve.Type.InOutCubic)

    def update_palette(self, palette: dict):
        self.palette = palette
        self._apply_style()

    def _apply_style(self):
        bg = self.palette.get("drawer_bg", "#13151C")
        border = self.palette.get("border_color", "rgba(255, 255, 255, 0.08)")
        self.setStyleSheet(f"""
            QFrame#OptionsDrawer {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 14px;
            }}
        """)

    def _get_fixed_height(self):
        return self.height()

    def _set_fixed_height(self, h):
        self.setFixedHeight(int(h))

    fixed_height_prop = QtCore.Property(int, _get_fixed_height, _set_fixed_height)

    def show_category(self, category: str, options: list, selected_value: str):
        self.current_category = category
        while self.layout.count():
            item = self.layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        btn_bg = self.palette.get("card_bg", "#181A22")
        btn_hover = self.palette.get("card_hover", "#2F3444")
        btn_active = self.palette.get("card_active", "#272B38")
        text_primary = self.palette.get("text_primary", "#E2E8F0")
        border_color = self.palette.get("border_color", "rgba(255, 255, 255, 0.08)")

        for item in options:
            if isinstance(item, tuple):
                canonical_key, label = item
            else:
                canonical_key = label = item

            btn = QtWidgets.QPushButton(label)
            btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            is_active = (canonical_key.lower() == selected_value.lower())

            bg = btn_active if is_active else btn_bg
            col = "#38BDF8" if is_active else text_primary
            border = "rgba(56, 189, 248, 0.6)" if is_active else border_color

            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    color: {col};
                    border: 1px solid {border};
                    border-radius: 10px;
                    padding: 8px 14px;
                    font-size: 12px;
                    font-weight: 600;
                    font-family: {FONT_STACK};
                }}
                QPushButton:hover {{
                    background-color: {btn_hover};
                    color: {"#38BDF8" if is_active else ("#000000" if self.palette.get("is_light") else "#FFFFFF")};
                }}
            """)
            btn.clicked.connect(lambda checked=False, k=canonical_key, c=category: self._on_opt_click(c, k))
            self.layout.addWidget(btn)

        self.setVisible(True)
        self.anim.stop()
        self.anim.setStartValue(self.height())
        self.anim.setEndValue(50)
        self.anim.start()

    def collapse(self):
        self.current_category = None
        self.anim.stop()
        self.anim.setStartValue(self.height())
        self.anim.setEndValue(0)
        self.anim.finished.connect(self._on_collapse_finished)
        self.anim.start()

    def _on_collapse_finished(self):
        try:
            self.anim.finished.disconnect(self._on_collapse_finished)
        except Exception:
            pass
        if self.height() == 0:
            self.setVisible(False)

    def _on_opt_click(self, category: str, option: str):
        self.option_selected.emit(category, option)
        self.collapse()


class ACPanelWidget(QtWidgets.QFrame):
    """Painel Principal Proporcional com Estetica macOS / Windows 11 Flyout"""

    power_toggled = QtCore.Signal(bool)
    temp_changed = QtCore.Signal(float)
    eco_toggled = QtCore.Signal(bool)
    option_changed = QtCore.Signal(str, str)
    language_changed = QtCore.Signal(str)
    command_failed = QtCore.Signal()
    check_updates_requested = QtCore.Signal()
    temp_unit_changed = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ACPanel")

        prefs = QtCore.QSettings("WTC LG", "Preferences")
        self.language = str(prefs.value("language", "en"))
        if self.language not in TRANSLATIONS:
            self.language = "en"
        self.temp_unit = str(prefs.value("temp_unit", "C"))
        if self.temp_unit not in ["C", "F"]:
            self.temp_unit = "C"
        self.theme_mode = str(prefs.value("theme", "system"))
        if self.theme_mode not in THEME_MODES:
            self.theme_mode = "system"
        self.ac_color = str(prefs.value("ac_color", "white"))
        if self.ac_color not in ["white", "black"]:
            self.ac_color = "white"

        self._menu_open = False
        self.connection_status = "connected"

        self.is_powered_on = False  # Comeca seguro e sincroniza imediatamente com o estado real do aparelho
        self.room_temp = 22.5
        self.target_temp = 21.0
        self.eco_mode = False
        self.current_mode = "Cool"
        self.fan_speed = "Auto"
        self.sleep_state = "Off"
        self.airflow_state = "Vertical"
        self._client = ThinQClient(get_base_dir(), self)
        self._client.status_updated.connect(self._apply_thinq_status)
        self._client.status_failed.connect(self._on_sync_failed)
        self._client.status_stale.connect(self._on_status_stale)
        self._client.command_finished.connect(self._on_command_finished)
        self._resync_scheduled = False

        self._temp_debounce_timer = QtCore.QTimer(self)
        self._temp_debounce_timer.setSingleShot(True)
        self._temp_debounce_timer.setInterval(400)
        self._temp_debounce_timer.timeout.connect(self._send_temp_command)

        self.setFixedWidth(450)
        self._build_ui()
        self.apply_theme()

    def _resolve_theme(self) -> str:
        """Resolve o modo de tema atual ('system', 'light', 'dark', 'black') para um tema concreto ('light', 'dark', 'black')."""
        return resolve_theme_name(self.theme_mode)

    def set_theme_mode(self, mode: str):
        if mode not in THEME_MODES or (self.theme_mode == mode and hasattr(self, '_current_resolved_theme')):
            return
        self.theme_mode = mode
        prefs = QtCore.QSettings("WTC LG", "Preferences")
        prefs.setValue("theme", mode)
        self.apply_theme()

    def set_ac_color(self, color: str):
        if color not in ["white", "black"] or self.ac_color == color:
            return
        self.ac_color = color
        prefs = QtCore.QSettings("WTC LG", "Preferences")
        prefs.setValue("ac_color", color)
        if hasattr(self, 'ac_hero'):
            self.ac_hero.set_ac_color(color)

    def apply_theme(self):
        resolved = self._resolve_theme()
        self._current_resolved_theme = resolved
        palette = get_palette(resolved)

        # 1. Painel principal
        self.setStyleSheet(f"""
            QFrame#ACPanel {{
                background-color: {palette["bg_color"]};
                border: 1px solid {palette["panel_border"]};
                border-radius: 28px;
            }}
        """)

        # 2. Header
        if hasattr(self, 'lbl_room_temp'):
            self.lbl_room_temp.setStyleSheet(f"color: {palette['text_primary']}; font-size: 15px; font-family: {FONT_STACK};")
        if hasattr(self, 'therm_icon'):
            self.therm_icon.setPixmap(load_user_svg("thermometer.svg", 22, 22, padding=0, color=palette["icon_color"]))
        if hasattr(self, 'btn_power'):
            self.btn_power.setStyleSheet(f"""
                QPushButton#PowerButton {{
                    background-color: {palette["power_bg"]};
                    border: 1px solid {palette["border_color"]};
                    border-radius: 22px;
                }}
                QPushButton#PowerButton:hover {{
                    background-color: {palette["power_hover"]};
                    border: 1px solid {palette["border_hover"]};
                }}
                QPushButton#PowerButton:pressed {{
                    background-color: {palette["power_pressed"]};
                }}
            """)
            self._update_power_button()

        # 3. Target temp row & Eco mode card
        if hasattr(self, 'lbl_target_num'):
            self.lbl_target_num.setStyleSheet(f"color: {palette['text_primary']}; font-size: 50px; font-weight: 700; line-height: 1;")
        if hasattr(self, 'lbl_target_unit'):
            self.lbl_target_unit.setStyleSheet(f"color: {palette['text_secondary']}; font-size: 22px; font-weight: 500; margin-bottom: 8px;")

        if hasattr(self, 'eco_card'):
            self.eco_card.setStyleSheet(f"""
                QFrame#EcoCard {{
                    background-color: {palette["card_bg"]};
                    border: 1px solid {palette["border_color"]};
                    border-radius: 17px;
                }}
                QFrame#EcoCard:hover {{
                    background-color: {palette["card_hover"]};
                    border: 1px solid {palette["border_hover"]};
                }}
            """)
        if hasattr(self, 'eco_icon'):
            self.eco_icon.setPixmap(load_user_icon("eco_mode.png", 24, 24, color=palette["icon_color"]))
        if hasattr(self, 'toggle_eco'):
            self.toggle_eco.set_light_mode(resolved == "light")

        # 4. Stepper buttons & Slider
        if hasattr(self, 'btn_minus'):
            self.btn_minus.setIcon(create_stepper_icon("minus", 38, color=palette["stepper_color"]))
            self.btn_minus.setStyleSheet(f"""
                QPushButton {{
                    background-color: {palette["card_bg"]};
                    border: 1px solid {palette["border_color"]};
                    border-radius: 19px;
                }}
                QPushButton:hover {{
                    background-color: {palette["card_hover"]};
                    border: 1px solid {palette["border_hover"]};
                }}
                QPushButton:disabled {{
                    background-color: {palette["card_bg"]};
                    border: 1px solid {palette["border_color"]};
                    opacity: 0.35;
                }}
            """)
        if hasattr(self, 'btn_plus'):
            self.btn_plus.setIcon(create_stepper_icon("plus", 38, color=palette["stepper_color"]))
            self.btn_plus.setStyleSheet(f"""
                QPushButton {{
                    background-color: {palette["card_bg"]};
                    border: 1px solid {palette["border_color"]};
                    border-radius: 19px;
                }}
                QPushButton:hover {{
                    background-color: {palette["card_hover"]};
                    border: 1px solid {palette["border_hover"]};
                }}
                QPushButton:disabled {{
                    background-color: {palette["card_bg"]};
                    border: 1px solid {palette["border_color"]};
                    opacity: 0.35;
                }}
            """)
        if hasattr(self, 'slider'):
            self.slider.set_theme_colors(palette["slider_groove"], palette["slider_groove_border"])
        if hasattr(self, 'lbl_slider_min'):
            self.lbl_slider_min.setStyleSheet(f"color: {palette['text_muted']}; font-size: 11px; font-weight: 500;")
        if hasattr(self, 'lbl_slider_max'):
            self.lbl_slider_max.setStyleSheet(f"color: {palette['text_muted']}; font-size: 11px; font-weight: 500;")

        # 5. 4 Control Cards
        for c in [getattr(self, 'card_mode', None), getattr(self, 'card_fan', None), getattr(self, 'card_sleep', None), getattr(self, 'card_airflow', None)]:
            if c:
                c.update_palette(palette)

        # 6. Drawer
        if hasattr(self, 'drawer'):
            self.drawer.update_palette(palette)

        # 7. Footer
        if hasattr(self, 'lbl_conn'):
            self.lbl_conn.setStyleSheet(f"color: {palette['text_secondary']}; font-size: 12px; font-weight: 500;")
        if hasattr(self, 'btn_settings'):
            self.btn_settings.setIcon(QtGui.QIcon(svg_to_pixmap(SVG_SLIDERS, 20, 20, palette["text_secondary"])))

    def tr_text(self, key: str) -> str:
        lang_dict = TRANSLATIONS.get(self.language, TRANSLATIONS["en"])
        return lang_dict.get(key, TRANSLATIONS["en"].get(key, key))

    def set_connection_status(self, status: str):
        """Atualiza a cor do círculo indicador (6px) e o texto de conexão"""
        self.connection_status = status
        color_map = {
            "connected": ACCENT_GREEN,
            "syncing": ACCENT_ORANGE,
            "disconnected": "#F87171"
        }
        col = color_map.get(status, ACCENT_GREEN)
        if hasattr(self, 'status_dot'):
            self.status_dot.setPixmap(create_dot_pixmap(6, col))
        if hasattr(self, 'lbl_conn'):
            self.lbl_conn.setText(self.tr_text(status))

    def set_temp_unit(self, unit: str):
        if unit not in ["C", "F"] or self.temp_unit == unit:
            return
        self.temp_unit = unit
        prefs = QtCore.QSettings("WTC LG", "Preferences")
        prefs.setValue("temp_unit", unit)
        self.temp_unit_changed.emit(unit)
        self.update_ui_texts()

    def set_language(self, lang: str):
        if lang not in TRANSLATIONS or self.language == lang:
            return
        self.language = lang
        prefs = QtCore.QSettings("WTC LG", "Preferences")
        prefs.setValue("language", lang)
        self.language_changed.emit(lang)
        self.update_ui_texts()

    def update_ui_texts(self):
        # 1. Room temp
        if self.temp_unit == "F":
            f_room = int(round(self.room_temp * 1.8 + 32))
            self.lbl_room_temp.setText(f"{self.tr_text('room')}  <b>{f_room}°F</b>")
        else:
            self.lbl_room_temp.setText(f"{self.tr_text('room')}  <b>{int(round(self.room_temp))}°C</b>")

        # 2. Target temp & unit
        if self.temp_unit == "F":
            f_target = int(round(self.target_temp * 1.8 + 32))
            self.lbl_target_num.setText(str(f_target))
            self.lbl_target_unit.setText("°F")
            self.lbl_slider_min.setText(f"{int(round(18 * 1.8 + 32))}°")
            self.lbl_slider_max.setText(f"{int(round(30 * 1.8 + 32))}°")
        else:
            self.lbl_target_num.setText(str(int(self.target_temp)))
            self.lbl_target_unit.setText("°C")
            self.lbl_slider_min.setText("18°")
            self.lbl_slider_max.setText("30°")

        # 3. Cards
        self.card_mode.set_title(self.tr_text("mode"))
        self.card_mode.set_value(self.tr_text(self.current_mode))

        self.card_fan.set_title(self.tr_text("fan_speed"))
        self.card_fan.set_value(self.tr_text(self.fan_speed))

        self.card_sleep.set_title(self.tr_text("sleep"))
        self.card_sleep.set_value(self.tr_text(self.sleep_state))

        self.card_airflow.set_title(self.tr_text("airflow"))
        self.card_airflow.set_value(self.tr_text(self.airflow_state))

        # 4. Footer & Tooltip
        self.set_connection_status(getattr(self, 'connection_status', 'connected'))
        self.btn_settings.setToolTip(self.tr_text("settings"))

        # 5. Refresh drawer if active
        if self.drawer.isVisible() and self.drawer.current_category:
            cat = self.drawer.current_category
            options_map = {
                "mode": (["Cool", "Heat", "Fan", "Dry"], self.current_mode),
                "fan": (["Auto", "Low", "Mid", "High"], self.fan_speed),
                "sleep": (["Off", "1h", "2h", "4h", "8h"], self.sleep_state),
                "airflow": (["Vertical", "Swing"], self.airflow_state)
            }
            opts, sel = options_map.get(cat, ([], ""))
            translated_opts = [(opt, self.tr_text(opt)) for opt in opts]
            self.drawer.show_category(cat, translated_opts, sel)

    def _open_settings_menu(self):
        self._menu_open = True
        resolved = self._resolve_theme()
        pal = get_palette(resolved)

        menu = QtWidgets.QMenu(self)
        menu_css = f"""
            QMenu {{
                background-color: {pal["menu_bg"]};
                color: {pal["menu_color"]};
                border: 1px solid {pal["menu_border"]};
                border-radius: 12px;
                padding: 6px;
                font-family: {FONT_STACK};
                font-size: 13px;
            }}
            QMenu::item {{
                padding: 7px 24px 7px 14px;
                border-radius: 6px;
            }}
            QMenu::item:selected {{
                background-color: {pal["menu_item_hover_bg"]};
                color: {pal["menu_item_hover_color"]};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {pal["menu_separator"]};
                margin: 4px 6px;
            }}
        """
        menu.setStyleSheet(menu_css)

        # 1. Background / Theme
        menu_theme = menu.addMenu(self.tr_text("theme"))
        menu_theme.setStyleSheet(menu_css)

        act_system = menu_theme.addAction(self.tr_text("theme_system"))
        act_system.setCheckable(True)
        act_system.setChecked(self.theme_mode == "system")
        act_system.triggered.connect(lambda: self.set_theme_mode("system"))

        act_light = menu_theme.addAction(self.tr_text("theme_light"))
        act_light.setCheckable(True)
        act_light.setChecked(self.theme_mode == "light")
        act_light.triggered.connect(lambda: self.set_theme_mode("light"))

        act_dark = menu_theme.addAction(self.tr_text("theme_dark"))
        act_dark.setCheckable(True)
        act_dark.setChecked(self.theme_mode == "dark")
        act_dark.triggered.connect(lambda: self.set_theme_mode("dark"))

        act_black = menu_theme.addAction(self.tr_text("theme_black"))
        act_black.setCheckable(True)
        act_black.setChecked(self.theme_mode == "black")
        act_black.triggered.connect(lambda: self.set_theme_mode("black"))

        # 2. Cor do Ar-Condicionado (Mockup)
        menu_ac = menu.addMenu(self.tr_text("ac_color"))
        menu_ac.setStyleSheet(menu_css)

        act_white = menu_ac.addAction(self.tr_text("ac_color_white"))
        act_white.setCheckable(True)
        act_white.setChecked(self.ac_color == "white")
        act_white.triggered.connect(lambda: self.set_ac_color("white"))

        act_ac_black = menu_ac.addAction(self.tr_text("ac_color_black"))
        act_ac_black.setCheckable(True)
        act_ac_black.setChecked(self.ac_color == "black")
        act_ac_black.triggered.connect(lambda: self.set_ac_color("black"))

        # 3. Unidade de Temperatura
        menu_unit = menu.addMenu(self.tr_text("temp_unit"))
        menu_unit.setStyleSheet(menu_css)
        act_c = menu_unit.addAction(self.tr_text("celsius"))
        act_c.setCheckable(True)
        act_c.setChecked(self.temp_unit == "C")
        act_c.triggered.connect(lambda: self.set_temp_unit("C"))

        act_f = menu_unit.addAction(self.tr_text("fahrenheit"))
        act_f.setCheckable(True)
        act_f.setChecked(self.temp_unit == "F")
        act_f.triggered.connect(lambda: self.set_temp_unit("F"))

        # 3. Idioma / Language
        menu_lang = menu.addMenu(self.tr_text("language"))
        menu_lang.setStyleSheet(menu_css)
        act_en = menu_lang.addAction("English")
        act_en.setCheckable(True)
        act_en.setChecked(self.language == "en")
        act_en.triggered.connect(lambda: self.set_language("en"))

        act_pt = menu_lang.addAction("Português (Brasil)")
        act_pt.setCheckable(True)
        act_pt.setChecked(self.language == "pt")
        act_pt.triggered.connect(lambda: self.set_language("pt"))

        act_es = menu_lang.addAction("Español")
        act_es.setCheckable(True)
        act_es.setChecked(self.language == "es")
        act_es.triggered.connect(lambda: self.set_language("es"))

        menu.addSeparator()

        # 4. Sincronizar com ThinQ
        act_sync = menu.addAction(self.tr_text("sync_thinq"))
        act_sync.triggered.connect(self.refresh_status_from_thinq)

        menu.addSeparator()

        # 5. Iniciar com o Windows
        act_autostart = menu.addAction(self.tr_text("autostart"))
        act_autostart.setCheckable(True)
        act_autostart.setChecked(is_autostart_enabled())
        act_autostart.triggered.connect(lambda: set_autostart_enabled(act_autostart.isChecked()))

        menu.addSeparator()

        # 5b. Atualizacoes (manual e busca automatica)
        act_update = menu.addAction(self.tr_text("update_check"))
        act_update.triggered.connect(self.check_updates_requested.emit)

        act_auto_update = menu.addAction(self.tr_text("update_auto"))
        act_auto_update.setCheckable(True)
        act_auto_update.setChecked(auto_update_enabled())
        act_auto_update.triggered.connect(lambda: set_auto_update_enabled(act_auto_update.isChecked()))

        menu.addSeparator()

        # 6. Excluir permanentemente dados e credenciais
        act_clear_data = menu.addAction(self.tr_text("clear_data"))
        act_clear_data.triggered.connect(self._prompt_clear_data)

        btn_pos = self.btn_settings.mapToGlobal(QtCore.QPoint(0, 0))
        size_hint = menu.sizeHint()
        popup_x = btn_pos.x() + self.btn_settings.width() - size_hint.width()
        popup_y = btn_pos.y() - size_hint.height() - 6
        menu.exec(QtCore.QPoint(max(10, popup_x), max(10, popup_y)))
        self._menu_open = False
        if self.window():
            self.window().activateWindow()

    def _prompt_clear_data(self):
        """Exibe confirmação e realiza a purga completa das credenciais e preferências deste computador."""
        win = self.window()
        was_visible = False
        if isinstance(win, FullTrayWindow) and win.isVisible():
            was_visible = True
            win.hide()

        resolved = self._resolve_theme()
        pal = get_palette(resolved)

        box = QtWidgets.QMessageBox(None)
        box.setWindowFlags(
            QtCore.Qt.WindowType.Dialog
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        box.setWindowTitle(self.tr_text("clear_data_title"))
        box.setText(self.tr_text("clear_data_confirm"))
        box.setIcon(QtWidgets.QMessageBox.Icon.Warning)

        # Estilização consistente com o tema e cantos elegantes
        box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {pal["bg_color"]};
                font-family: {FONT_STACK};
            }}
            QLabel {{
                color: {pal["text_primary"]};
                font-size: 13px;
                font-family: {FONT_STACK};
                line-height: 1.4;
            }}
            QPushButton {{
                background-color: {pal["card_bg"]};
                color: {pal["text_primary"]};
                border: 1px solid {pal["border_color"]};
                border-radius: 8px;
                padding: 7px 18px;
                font-size: 13px;
                font-weight: 600;
                font-family: {FONT_STACK};
                min-width: 90px;
            }}
            QPushButton:hover {{
                background-color: {pal["card_hover"]};
                border: 1px solid {pal["border_hover"]};
            }}
        """)

        btn_delete = box.addButton(
            "Excluir Permanentemente" if self.language == "pt" else ("Delete Permanently" if self.language == "en" else "Eliminar Permanentemente"),
            QtWidgets.QMessageBox.ButtonRole.DestructiveRole
        )
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #DC2626;
                color: #FFFFFF;
                border: 1px solid #B91C1C;
            }
            QPushButton:hover {
                background-color: #EF4444;
            }
        """)

        btn_cancel = box.addButton(
            "Cancelar" if self.language in ["pt", "es"] else "Cancel",
            QtWidgets.QMessageBox.ButtonRole.RejectRole
        )
        box.setDefaultButton(btn_cancel)

        box.raise_()
        box.activateWindow()
        box.exec()

        if box.clickedButton() == btn_delete:
            import credentials_backend
            credentials_backend.purge_all_app_data()

            info_box = QtWidgets.QMessageBox(None)
            info_box.setWindowFlags(
                QtCore.Qt.WindowType.Dialog
                | QtCore.Qt.WindowType.WindowStaysOnTopHint
            )
            info_box.setWindowTitle(self.tr_text("clear_data_title"))
            info_box.setText(self.tr_text("clear_data_success"))
            info_box.setIcon(QtWidgets.QMessageBox.Icon.Information)
            info_box.setStyleSheet(box.styleSheet())
            info_box.raise_()
            info_box.activateWindow()
            info_box.exec()

            # Encerra o aplicativo de forma limpa
            app = QtWidgets.QApplication.instance()
            if app:
                app.quit()
        else:
            # Se cancelou e o painel estava aberto, reexibe o painel
            if was_visible and isinstance(win, FullTrayWindow):
                win.show_popup()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(12)

        # -------------------------------------------------------------
        # 1. HEADER: Room 23°C (com termômetro branco puro) + Botão Power Redondo Translúcido
        # -------------------------------------------------------------
        header = QtWidgets.QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)

        room_box = QtWidgets.QHBoxLayout()
        room_box.setSpacing(6)

        # Room Temp: thermometer.svg da pasta assets em branco puro (#FFFFFF) com tamanho ampliado
        self.therm_icon = QtWidgets.QLabel()
        self.therm_icon.setFixedSize(22, 22)
        self.therm_icon.setPixmap(load_user_svg("thermometer.svg", 22, 22, padding=0, color="#FFFFFF"))
        room_box.addWidget(self.therm_icon)

        self.lbl_room_temp = QtWidgets.QLabel(f"Room  <b>{int(round(self.room_temp))}°C</b>")
        self.lbl_room_temp.setStyleSheet(f"color: #E2E8F0; font-size: 15px; font-family: {FONT_STACK};")
        room_box.addWidget(self.lbl_room_temp)

        header.addLayout(room_box)
        header.addStretch()

        # Power Button: Circular escuro translúcido com o ícone Power centralizado na cor bege/creme (#d4d0c7)
        self.btn_power = QtWidgets.QPushButton()
        self.btn_power.setObjectName("PowerButton")
        self.btn_power.setFixedSize(44, 44)
        self.btn_power.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btn_power.setStyleSheet("""
            QPushButton#PowerButton {
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 22px;
            }
            QPushButton#PowerButton:hover {
                background-color: rgba(255, 255, 255, 0.14);
                border: 1px solid rgba(255, 255, 255, 0.16);
            }
            QPushButton#PowerButton:pressed {
                background-color: rgba(255, 255, 255, 0.04);
            }
        """)
        self._update_power_button()
        self.btn_power.clicked.connect(self._toggle_power_clicked)
        header.addWidget(self.btn_power)

        layout.addLayout(header)

        # -------------------------------------------------------------
        # 2. HERO: Ar Condicionado Split com Cortina de Ar Ondulante
        # -------------------------------------------------------------
        self.ac_hero = AnimatedAirCurtainHero(self)
        self.ac_hero.set_ac_color(getattr(self, 'ac_color', 'white'))
        self.ac_hero.set_power(self.is_powered_on)
        self.ac_hero.set_mode(self.current_mode)
        self.ac_hero.set_fan(self.fan_speed)
        self.ac_hero.set_temp(self.target_temp)
        self.ac_hero.set_airflow(self.airflow_state)
        layout.addWidget(self.ac_hero)

        # -------------------------------------------------------------
        # 3. LINHA: 21 °C + Card Unificado Eco Mode
        # -------------------------------------------------------------
        temp_eco_row = QtWidgets.QHBoxLayout()
        temp_eco_row.setContentsMargins(0, 0, 0, 0)

        temp_box = QtWidgets.QHBoxLayout()
        temp_box.setSpacing(4)
        temp_box.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom)

        self.lbl_target_num = QtWidgets.QLabel(f"{int(self.target_temp)}")
        self.lbl_target_num.setStyleSheet("color: #FFFFFF; font-size: 50px; font-weight: 700; line-height: 1;")
        temp_box.addWidget(self.lbl_target_num)

        self.lbl_target_unit = QtWidgets.QLabel("°C")
        self.lbl_target_unit.setStyleSheet("color: #94A3B8; font-size: 22px; font-weight: 500; margin-bottom: 8px;")
        temp_box.addWidget(self.lbl_target_unit)

        temp_eco_row.addLayout(temp_box)
        temp_eco_row.addStretch()

        # Eco Mode: Card compacto com asset eco_mode.png e switch animado
        self.eco_card = EcoCard()
        self.eco_card.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.eco_card.setStyleSheet(f"""
            QFrame#EcoCard {{
                background-color: #171920;
                border: 1px solid {BORDER_COLOR};
                border-radius: 17px;
            }}
            QFrame#EcoCard:hover {{
                background-color: #1F222B;
                border: 1px solid rgba(255, 255, 255, 0.22);
            }}
        """)
        eco_layout = QtWidgets.QHBoxLayout(self.eco_card)
        eco_layout.setContentsMargins(10, 5, 10, 5)
        eco_layout.setSpacing(8)

        self.eco_icon = QtWidgets.QLabel()
        self.eco_icon.setFixedSize(24, 24)
        self.eco_icon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.eco_icon.setPixmap(load_user_icon("eco_mode.png", 24, 24, color="#FFFFFF"))
        eco_layout.addWidget(self.eco_icon)

        self.toggle_eco = AnimatedToggle()
        self.toggle_eco.setChecked(self.eco_mode)
        self.toggle_eco.stateChanged.connect(self._eco_state_changed)
        eco_layout.addWidget(self.toggle_eco)

        # Clicar em qualquer lugar do card pílula aciona o toggle
        self.eco_card.clicked.connect(self.toggle_eco.toggle)

        temp_eco_row.addWidget(self.eco_card, 0, QtCore.Qt.AlignmentFlag.AlignVCenter)
        layout.addLayout(temp_eco_row)

        # -------------------------------------------------------------
        # 4. SLIDER LARGO COM BOTÕES (-) E (+)
        # -------------------------------------------------------------
        slider_container = QtWidgets.QVBoxLayout()
        slider_container.setSpacing(4)

        slider_row = QtWidgets.QHBoxLayout()
        slider_row.setSpacing(12)

        self.btn_minus = QtWidgets.QPushButton()
        self.btn_minus.setFixedSize(38, 38)
        self.btn_minus.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btn_minus.setIcon(create_stepper_icon("minus", 38))
        self.btn_minus.setIconSize(QtCore.QSize(38, 38))
        self.btn_minus.setStyleSheet(f"""
            QPushButton {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 19px;
            }}
            QPushButton:hover {{
                background-color: {CARD_HOVER};
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
        """)
        self.btn_minus.clicked.connect(self._step_down_temp)
        slider_row.addWidget(self.btn_minus)

        self.slider = ModernTrackSlider(self)
        self.slider.setMinimum(18)
        self.slider.setMaximum(30)
        self.slider.setValue(int(self.target_temp))
        self.slider.set_mode(self.current_mode)
        self.slider.valueChanged.connect(self._slider_changed)
        slider_row.addWidget(self.slider)

        self.btn_plus = QtWidgets.QPushButton()
        self.btn_plus.setFixedSize(38, 38)
        self.btn_plus.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btn_plus.setIcon(create_stepper_icon("plus", 38))
        self.btn_plus.setIconSize(QtCore.QSize(38, 38))
        self.btn_plus.setStyleSheet(f"""
            QPushButton {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 19px;
            }}
            QPushButton:hover {{
                background-color: {CARD_HOVER};
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
        """)
        self.btn_plus.clicked.connect(self._step_up_temp)
        slider_row.addWidget(self.btn_plus)

        slider_container.addLayout(slider_row)

        limits_row = QtWidgets.QHBoxLayout()
        limits_row.setContentsMargins(50, 0, 50, 0)
        self.lbl_slider_min = QtWidgets.QLabel("18°")
        self.lbl_slider_min.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 500;")
        limits_row.addWidget(self.lbl_slider_min)
        limits_row.addStretch()
        self.lbl_slider_max = QtWidgets.QLabel("30°")
        self.lbl_slider_max.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 500;")
        limits_row.addWidget(self.lbl_slider_max)
        slider_container.addLayout(limits_row)

        layout.addLayout(slider_container)

        # -------------------------------------------------------------
        # 5. GRADE DE 4 CARDS COM ÍCONES DA PASTA ASSETS
        # -------------------------------------------------------------
        grid_row = QtWidgets.QHBoxLayout()
        grid_row.setSpacing(10)

        # Modo: assets/mode.svg em branco puro
        self.card_mode = ControlCard("mode", "Mode", self.current_mode)
        self.card_mode.clicked.connect(lambda: self._toggle_category("mode"))
        grid_row.addWidget(self.card_mode)

        # Fan speed: assets/fan-speed.svg em branco puro com rotação horária no hover/seleção
        self.card_fan = ControlCard("fan", "Fan speed", self.fan_speed)
        self.card_fan.clicked.connect(lambda: self._toggle_category("fan"))
        grid_row.addWidget(self.card_fan)

        # Sleep: assets/crescent-moon.svg em branco puro + ponto indicador (dot) cinza à direita
        self.card_sleep = ControlCard("sleep", "Sleep", self.sleep_state, is_sleep=True)
        self.card_sleep.clicked.connect(lambda: self._toggle_category("sleep"))
        grid_row.addWidget(self.card_sleep)

        # Airflow: assets/air.json convertido para animação fluida de 28 frames
        self.card_airflow = ControlCard("airflow", "Airflow", self.airflow_state)
        self.card_airflow.clicked.connect(lambda: self._toggle_category("airflow"))
        grid_row.addWidget(self.card_airflow)

        layout.addLayout(grid_row)

        # GAVETA ANIMADA DE SUB-OPÇÕES
        self.drawer = OptionsDrawer(self)
        self.drawer.option_selected.connect(self._on_sub_option_selected)
        layout.addWidget(self.drawer)

        # -------------------------------------------------------------
        # 6. FOOTER: Connected + Sliders Icon
        # -------------------------------------------------------------
        footer = QtWidgets.QHBoxLayout()
        footer.setContentsMargins(2, 4, 2, 0)

        status_box = QtWidgets.QHBoxLayout()
        status_box.setSpacing(7)

        self.status_dot = QtWidgets.QLabel()
        self.status_dot.setFixedSize(6, 6)
        self.status_dot.setPixmap(create_dot_pixmap(6, ACCENT_GREEN))
        status_box.addWidget(self.status_dot, 0, QtCore.Qt.AlignmentFlag.AlignVCenter)

        self.lbl_conn = QtWidgets.QLabel("Connected")
        self.lbl_conn.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 500;")
        status_box.addWidget(self.lbl_conn, 0, QtCore.Qt.AlignmentFlag.AlignVCenter)

        footer.addLayout(status_box)
        footer.addStretch()

        self.btn_settings = QtWidgets.QPushButton()
        self.btn_settings.setFixedSize(28, 28)
        self.btn_settings.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btn_settings.setIcon(QtGui.QIcon(svg_to_pixmap(SVG_SLIDERS, 20, 20, "#94A3B8")))
        self.btn_settings.setIconSize(QtCore.QSize(20, 20))
        self.btn_settings.setToolTip("Settings")
        self.btn_settings.setStyleSheet("QPushButton { background: transparent; border: none; } QPushButton:hover { opacity: 0.8; }")
        self.btn_settings.clicked.connect(self._open_settings_menu)
        footer.addWidget(self.btn_settings)

        layout.addLayout(footer)
        self.set_power(self.is_powered_on)
        self.update_ui_texts()

    def _toggle_category(self, cat: str):
        if self.drawer.current_category == cat:
            self.drawer.collapse()
            self._set_card_expanded(cat, False)
            return

        for c in ["mode", "fan", "sleep", "airflow"]:
            self._set_card_expanded(c, (c == cat))

        options_map = {
            "mode": (["Cool", "Heat", "Fan", "Dry"], self.current_mode),
            "fan": (["Auto", "Low", "Mid", "High"], self.fan_speed),
            "sleep": (["Off", "1h", "2h", "4h", "8h"], self.sleep_state),
            "airflow": (["Vertical", "Swing"], self.airflow_state)
        }

        opts, sel = options_map.get(cat, ([], ""))
        translated_opts = [(opt, self.tr_text(opt)) for opt in opts]
        self.drawer.show_category(cat, translated_opts, sel)

    def _set_card_expanded(self, cat: str, expanded: bool):
        card_map = {
            "mode": self.card_mode,
            "fan": self.card_fan,
            "sleep": self.card_sleep,
            "airflow": self.card_airflow
        }
        card = card_map.get(cat)
        if card:
            card.set_expanded(expanded)

    def _on_sub_option_selected(self, category: str, option: str):
        self._set_card_expanded(category, False)
        if category == "mode":
            self.set_mode(option)
            mode_map = {"Cool": "COOL", "Heat": "HEAT", "Fan": "FAN", "Dry": "AIR_DRY"}
            if option in mode_map:
                self._send_thinq_command({"airConJobMode": {"currentJobMode": mode_map[option]}})
        elif category == "fan":
            self.fan_speed = option
            self.card_fan.set_value(self.tr_text(option))
            self.ac_hero.set_fan(option)
            fan_map = {"Auto": "AUTO", "Low": "LOW", "Mid": "MID", "High": "HIGH"}
            if option in fan_map:
                self._send_thinq_command({"airFlow": {"windStrength": fan_map[option]}})
        elif category == "sleep":
            self.sleep_state = option
            self.card_sleep.set_value(self.tr_text(option))
            if option == "Off":
                self._send_thinq_command({"sleepTimer": {"relativeStopTimer": "UNSET"}})
            else:
                try:
                    hrs = int(option.replace("h", ""))
                    self._send_thinq_command({"sleepTimer": {"relativeHourToStop": hrs, "relativeMinuteToStop": 0}})
                except Exception as e:
                    print("[Sleep Timer Error]:", e)
        elif category == "airflow":
            self.airflow_state = option
            self.card_airflow.set_value(self.tr_text(option))
            self.ac_hero.set_airflow(option)
            is_swing = (option.lower() == "swing")
            self._send_thinq_command({"windDirection": {"rotateUpDown": is_swing}})

        self.option_changed.emit(category, option)

    def refresh_status_from_thinq(self):
        """Consulta o status em tempo real do aparelho via nuvem LG ThinQ em segundo plano"""
        self.set_connection_status("syncing")
        self._client.get_status()

    def _on_sync_failed(self):
        self.set_connection_status("disconnected")

    def _on_status_stale(self):
        # Um comando mais novo tornou este status obsoleto; a UI ja reflete a intencao do usuario
        self.set_connection_status("connected")

    def _on_command_finished(self, ok: bool, message: str):
        """Comando falhou: avisa o usuario e ressincroniza a UI com o estado real do aparelho."""
        if ok:
            return
        self.command_failed.emit()
        if not self._resync_scheduled:
            self._resync_scheduled = True
            QtCore.QTimer.singleShot(500, self._resync_after_failure)

    def _resync_after_failure(self):
        self._resync_scheduled = False
        self.refresh_status_from_thinq()

    def _send_thinq_command(self, payload: dict):
        """Dispara comando assincrono para o ar condicionado em segundo plano"""
        self._client.send_command(payload)

    def _apply_thinq_status(self, data: dict):
        """Aplica os valores reais retornados pela API LG ThinQ na interface"""
        op = data.get("operation", {})
        power_str = op.get("airConOperationMode", "")
        if power_str:
            is_on = (power_str == "POWER_ON")
            self.set_power(is_on)

        temp = data.get("temperature", {})
        if "targetTemperature" in temp:
            t = float(temp["targetTemperature"])
            self.target_temp = t
            self.ac_hero.set_temp(t)
            self.slider.blockSignals(True)
            self.slider.setValue(int(t))
            self.slider.blockSignals(False)
            if self.temp_unit == "F":
                self.lbl_target_num.setText(str(int(round(t * 1.8 + 32))))
            else:
                self.lbl_target_num.setText(str(int(t)))

        if "currentTemperature" in temp:
            self.room_temp = float(temp["currentTemperature"])
            if self.temp_unit == "F":
                f_room = int(round(self.room_temp * 1.8 + 32))
                self.lbl_room_temp.setText(f"{self.tr_text('room')}  <b>{f_room}°F</b>")
            else:
                self.lbl_room_temp.setText(f"{self.tr_text('room')}  <b>{int(round(self.room_temp))}°C</b>")

        mode = data.get("airConJobMode", {})
        job_mode = mode.get("currentJobMode")
        if job_mode:
            formatted = "Dry" if job_mode == "AIR_DRY" else job_mode.capitalize()
            self.set_mode(formatted)

        flow = data.get("airFlow", {})
        wind = flow.get("windStrength")
        if wind:
            self.fan_speed = wind.capitalize()
            self.card_fan.set_value(self.tr_text(self.fan_speed))
            self.ac_hero.set_fan(self.fan_speed)

        swing = data.get("windDirection", {})
        if "rotateUpDown" in swing:
            is_swing = swing.get("rotateUpDown", False)
            self.airflow_state = "Swing" if is_swing else "Vertical"
            self.card_airflow.set_value(self.tr_text(self.airflow_state))
            self.ac_hero.set_airflow(self.airflow_state)

        disp = data.get("display", {})
        if "light" in disp:
            is_light_off = (disp.get("light") == "OFF")
            self.eco_mode = is_light_off
            self.toggle_eco.blockSignals(True)
            self.toggle_eco.setChecked(is_light_off)
            self.toggle_eco.blockSignals(False)

        sleep = data.get("sleepTimer", {})
        if sleep.get("relativeStopTimer") == "SET":
            hrs = sleep.get("relativeHourToStop", 0)
            if hrs > 0:
                self.sleep_state = f"{hrs}h"
                self.card_sleep.set_value(self.tr_text(self.sleep_state))
        elif sleep.get("relativeStopTimer") == "UNSET":
            self.sleep_state = "Off"
            self.card_sleep.set_value(self.tr_text("Off"))

        self.set_connection_status("connected")

    def set_power(self, power: bool):
        """Define o estado de energia em todos os componentes visuais"""
        self.is_powered_on = power
        self._update_power_button()
        self.ac_hero.set_power(power)
        self.card_mode.set_power(power)
        self.card_fan.set_power(power)
        self.card_sleep.set_power(power)
        self.card_airflow.set_power(power)

    def set_mode(self, mode: str):
        """Define o modo de operação do ar condicionado e sincroniza os componentes visuais"""
        self.current_mode = mode
        if hasattr(self, 'card_mode'):
            self.card_mode.set_value(self.tr_text(mode))
        if hasattr(self, 'ac_hero'):
            self.ac_hero.set_mode(mode)
        if hasattr(self, 'slider'):
            self.slider.set_mode(mode)
        self._sync_mode_controls()

    def _sync_mode_controls(self):
        """No modo Fan (Ventilação), desativa e oculta a temperatura, pois só a ventoinha opera"""
        is_fan = self.current_mode.lower() in ("fan", "ventilação", "ventilacao")
        if hasattr(self, 'btn_minus'):
            self.btn_minus.setEnabled(not is_fan)
        if hasattr(self, 'btn_plus'):
            self.btn_plus.setEnabled(not is_fan)
        if hasattr(self, 'lbl_target_num'):
            self.lbl_target_num.setText("--" if is_fan else (
                str(int(round(self.target_temp * 1.8 + 32))) if self.temp_unit == "F" else str(int(self.target_temp))
            ))
        if hasattr(self, 'lbl_target_unit'):
            self.lbl_target_unit.setText("" if is_fan else ("°F" if self.temp_unit == "F" else "°C"))
        if hasattr(self, 'slider'):
            self.slider.setEnabled(not is_fan)

    def _update_power_button(self):
        resolved = self._resolve_theme()
        pal = get_palette(resolved)
        col = pal.get("power_color", POWER_CREAM) if self.is_powered_on else pal.get("power_off_color", "#64748B")
        pix = svg_to_pixmap(SVG_POWER, 22, 22, col)
        self.btn_power.setIcon(QtGui.QIcon(pix))
        self.btn_power.setIconSize(QtCore.QSize(22, 22))

    def _toggle_power_clicked(self):
        new_state = not self.is_powered_on
        self.set_power(new_state)
        self.power_toggled.emit(new_state)
        self._send_thinq_command({"operation": {"airConOperationMode": "POWER_ON" if new_state else "POWER_OFF"}})

    def _slider_changed(self, val):
        self.target_temp = float(val)
        self.ac_hero.set_temp(self.target_temp)
        if self.temp_unit == "F":
            self.lbl_target_num.setText(str(int(round(self.target_temp * 1.8 + 32))))
        else:
            self.lbl_target_num.setText(str(val))
        self.temp_changed.emit(self.target_temp)
        self._temp_debounce_timer.start()

    def _send_temp_command(self):
        self._send_thinq_command({"temperature": {"targetTemperature": self.target_temp}})

    def _step_down_temp(self):
        if self.slider.value() > self.slider.minimum():
            self.slider.setValue(self.slider.value() - 1)

    def _step_up_temp(self):
        if self.slider.value() < self.slider.maximum():
            self.slider.setValue(self.slider.value() + 1)

    def _eco_state_changed(self, state):
        self.eco_mode = self.toggle_eco.isChecked()
        self.eco_toggled.emit(self.eco_mode)
        # Modo Eco: desliga ou liga o visor do ar condicionado
        self._send_thinq_command({"display": {"light": "OFF" if self.eco_mode else "ON"}})

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            win = self.window()
            if isinstance(win, FullTrayWindow):
                win._start_drag(event.globalPosition().toPoint())
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        win = self.window()
        if isinstance(win, FullTrayWindow) and getattr(win, '_is_dragging', False):
            if event.buttons() & QtCore.Qt.MouseButton.LeftButton:
                win._do_drag(event.globalPosition().toPoint())
                event.accept()
                return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        win = self.window()
        if isinstance(win, FullTrayWindow) and getattr(win, '_is_dragging', False):
            win._end_drag()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def cleanup(self):
        """Encerra timers e threads ativas para fechamento limpo da aplicacao"""
        if hasattr(self, '_temp_debounce_timer'):
            self._temp_debounce_timer.stop()
        if hasattr(self, 'ac_hero') and hasattr(self.ac_hero, 'timer'):
            self.ac_hero.timer.stop()
        for card in [getattr(self, 'card_mode', None), getattr(self, 'card_fan', None), getattr(self, 'card_sleep', None), getattr(self, 'card_airflow', None)]:
            if card:
                if hasattr(card, '_fan_timer'):
                    card._fan_timer.stop()
                if hasattr(card, '_air_timer'):
                    card._air_timer.stop()
        self._client.close()


class FullTrayWindow(QtWidgets.QWidget):
    """Janela Flutuante com Sombra, Cantos Arredondados e Auto-hide no Blur"""
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.Tool
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._is_dragging = False
        self._drag_start_cursor = QtCore.QPoint()
        self._drag_start_win = QtCore.QPoint()

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)

        self.panel = ACPanelWidget(self)

        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(36)
        shadow.setColor(QtGui.QColor(0, 0, 0, 210))
        shadow.setOffset(0, 10)
        self.panel.setGraphicsEffect(shadow)

        main_layout.addWidget(self.panel)
        self.adjustSize()

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._start_drag(event.globalPosition().toPoint())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self._is_dragging and (event.buttons() & QtCore.Qt.MouseButton.LeftButton):
            self._do_drag(event.globalPosition().toPoint())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        if self._is_dragging:
            self._end_drag()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _start_drag(self, global_pos: QtCore.QPoint):
        self._is_dragging = True
        if hasattr(self, 'panel'):
            self.panel._is_dragging = True
        self._drag_start_cursor = global_pos
        self._drag_start_win = self.pos()

    def _do_drag(self, global_pos: QtCore.QPoint):
        delta = global_pos - self._drag_start_cursor
        target_pos = self._drag_start_win + delta

        # Limitar o arraste para impedir que o aplicativo suma para fora do espaço de telas
        screens = QtGui.QGuiApplication.screens()
        if screens:
            union_rect = screens[0].availableGeometry()
            for s in screens[1:]:
                union_rect = union_rect.united(s.availableGeometry())
            w = self.width()
            h = self.height()
            # O topo não pode subir além do topo visível e deve sobrar área mínima para agarrar
            clamped_x = max(union_rect.left() - w + 80, min(target_pos.x(), union_rect.right() - 80))
            clamped_y = max(union_rect.top(), min(target_pos.y(), union_rect.bottom() - 80))
            self.move(clamped_x, clamped_y)
        else:
            self.move(target_pos)

    def _end_drag(self):
        self._is_dragging = False
        if hasattr(self, 'panel'):
            self.panel._is_dragging = False

        # Snap de segurança ao soltar: detecta em qual monitor o app foi largado e ajusta para ficar 100% visível
        win_rect = self.frameGeometry()
        best_screen = None
        best_area = 0
        for s in QtGui.QGuiApplication.screens():
            inter = s.availableGeometry().intersected(win_rect)
            area = inter.width() * inter.height()
            if area > best_area:
                best_area = area
                best_screen = s

        if not best_screen:
            best_screen = QtGui.QGuiApplication.screenAt(QtGui.QCursor.pos()) or QtGui.QGuiApplication.primaryScreen()

        if best_screen:
            avail = best_screen.availableGeometry()
            margin = 8
            w = self.width()
            h = self.height()
            safe_x = max(avail.left() + margin, min(win_rect.x(), avail.right() - w - margin))
            safe_y = max(avail.top() + margin, min(win_rect.y(), avail.bottom() - h - margin))
            self.move(safe_x, safe_y)

    def reposition_smart(self):
        screen = QtGui.QGuiApplication.screenAt(QtGui.QCursor.pos()) or QtGui.QGuiApplication.primaryScreen()
        avail = screen.availableGeometry()
        cursor = QtGui.QCursor.pos()

        w = self.width()
        h = self.height()
        margin = 12

        if cursor.y() > (avail.bottom() - 100):
            x = cursor.x() - (w // 2)
        else:
            x = avail.right() - w - margin

        x = max(avail.left() + margin, min(x, avail.right() - w - margin))
        y = avail.bottom() - h - margin
        self.move(x, y)

    def show_popup(self):
        self.reposition_smart()
        self.show()
        self.raise_()
        self.activateWindow()
        self.panel.refresh_status_from_thinq()

    def changeEvent(self, event: QtCore.QEvent):
        if event.type() == QtCore.QEvent.Type.ActivationChange:
            if not self.isActiveWindow() and not getattr(self.panel, '_menu_open', False) and not self._is_dragging:
                QtCore.QTimer.singleShot(140, self._check_hide)
        super().changeEvent(event)

    def _check_hide(self):
        if not self.isActiveWindow() and not getattr(self.panel, '_menu_open', False) and not self._is_dragging:
            self.hide()


def is_windows_taskbar_light() -> bool:
    """Verifica no registro do Windows se a barra de tarefas está no modo claro (1) ou escuro (0)."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            0,
            winreg.KEY_READ
        )
        val, _ = winreg.QueryValueEx(key, "SystemUsesLightTheme")
        winreg.CloseKey(key)
        return bool(val == 1)
    except Exception:
        return False


def create_tray_icon() -> QtGui.QIcon:
    """Cria o ícone da bandeja a partir de assets/miniature.png reagindo dinamicamente à cor da barra de tarefas."""
    is_light = is_windows_taskbar_light()
    color = QtGui.QColor("#18181B") if is_light else QtGui.QColor("#FFFFFF")

    orig_path = get_resource_path(os.path.join("assets", "miniature.png"))
    if not os.path.exists(orig_path):
        ico_path = get_resource_path(os.path.join("assets", "app_icon.ico"))
        if os.path.exists(ico_path):
            return QtGui.QIcon(ico_path)
        return QtGui.QIcon(load_user_icon("eco.png", 24, 24, color="#FFFFFF"))

    orig = QtGui.QPixmap(orig_path)
    result = QtGui.QPixmap(orig.size())
    result.fill(QtCore.Qt.GlobalColor.transparent)

    p = QtGui.QPainter(result)
    p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
    p.drawPixmap(0, 0, orig)
    p.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_SourceIn)
    p.fillRect(result.rect(), color)
    p.end()

    icon = QtGui.QIcon()
    for size in [16, 20, 24, 32, 48]:
        scaled = result.scaled(
            size, size,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation
        )
        icon.addPixmap(scaled)

    return icon


class TrayApplication:
    def __init__(self):
        # Configura ID explícito de modelo de aplicativo no Windows para agrupar corretamente o ícone na barra de tarefas
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Windows Tray Controller")
        except Exception:
            pass

        self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        self.app.setApplicationName("Windows Tray Controller")
        self.app.setApplicationDisplayName("Windows Tray Controller")
        self.app.setQuitOnLastWindowClosed(False)

        # Instancia unica: se ja existe uma rodando, pede para ela abrir o painel e encerra
        if not self._claim_single_instance():
            sys.exit(0)

        init_app_fonts()
        app_font = QtGui.QFont("Inter", 10)
        app_font.setStyleHint(QtGui.QFont.StyleHint.SansSerif)
        self.app.setFont(app_font)

        # Aplica o novo ícone oficial do aplicativo
        app_ico_path = get_resource_path(os.path.join("assets", "app_icon.ico"))
        if os.path.exists(app_ico_path):
            self.app_icon = QtGui.QIcon(app_ico_path)
            self.app.setWindowIcon(self.app_icon)

        self.window = FullTrayWindow()
        if hasattr(self, 'app_icon'):
            self.window.setWindowIcon(self.app_icon)

        self.tray = QtWidgets.QSystemTrayIcon(create_tray_icon(), self.app)
        self.tray.setToolTip("WTC LG - Windows Tray Controller")

        self._current_theme_is_light = is_windows_taskbar_light()
        self._current_apps_dark = is_windows_dark_mode()
        self._theme_timer = QtCore.QTimer(self.app)
        self._theme_timer.setInterval(3000)
        self._theme_timer.timeout.connect(self._check_taskbar_theme)
        self._theme_timer.start()

        menu = QtWidgets.QMenu()
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: #18181B;
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 4px;
                font-family: {FONT_STACK};
            }}
            QMenu::item {{
                padding: 6px 16px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: #27272A;
            }}
        """)
        self.m_open = menu.addAction(self.window.panel.tr_text("open_panel"))
        self.m_open.triggered.connect(self.toggle)
        menu.addSeparator()

        self.action_autostart = menu.addAction(self.window.panel.tr_text("autostart"))
        self.action_autostart.setCheckable(True)
        self.action_autostart.setChecked(is_autostart_enabled())
        self.action_autostart.triggered.connect(self._toggle_autostart)

        self.action_creds = menu.addAction("Configurar Credenciais LG...")
        self.action_creds.triggered.connect(self._open_credentials_dialog)

        self.action_update = menu.addAction(self.window.panel.tr_text("update_check"))
        self.action_update.triggered.connect(lambda: self._check_updates(manual=True))

        self.action_clear_data = menu.addAction(self.window.panel.tr_text("clear_data"))
        self.action_clear_data.triggered.connect(self.window.panel._prompt_clear_data)

        menu.addSeparator()
        self.m_quit = menu.addAction(self.window.panel.tr_text("quit"))
        self.m_quit.triggered.connect(self.quit)
        self.tray.setContextMenu(menu)

        self.window.panel.language_changed.connect(self._update_tray_texts)
        self.window.panel.command_failed.connect(self._on_command_failed)
        self.window.panel.check_updates_requested.connect(lambda: self._check_updates(manual=True))
        self._init_updater()

        self.tray.activated.connect(self.on_activated)
        self.tray.messageClicked.connect(self._on_tray_message_clicked)
        self.tray.show()

    SINGLE_INSTANCE_KEY = "WTC-LG-single-instance"

    def _claim_single_instance(self) -> bool:
        """Retorna True se esta e a primeira instancia. Caso contrario avisa a existente e retorna False."""
        socket = QtNetwork.QLocalSocket()
        socket.connectToServer(self.SINGLE_INSTANCE_KEY)
        if socket.waitForConnected(500):
            # --silent (autostart) nao deve abrir o painel da instancia existente
            if "--silent" not in sys.argv and "--minimized" not in sys.argv:
                socket.write(b"show")
                socket.waitForBytesWritten(500)
            socket.disconnectFromServer()
            return False

        # Remove socket orfao de uma execucao anterior que caiu e cria o servidor
        QtNetwork.QLocalServer.removeServer(self.SINGLE_INSTANCE_KEY)
        self._instance_server = QtNetwork.QLocalServer(self.app)
        self._instance_server.newConnection.connect(self._on_instance_message)
        self._instance_server.listen(self.SINGLE_INSTANCE_KEY)
        return True

    def _on_instance_message(self):
        """Outra instancia tentou abrir: mostra o painel (ou a configuracao, se nao ha credenciais)."""
        conn = self._instance_server.nextPendingConnection()
        if conn is not None:
            conn.waitForReadyRead(200)
            conn.disconnectFromServer()
        if not self.window.isVisible():
            self.toggle()

    def has_configured_credentials(self) -> bool:
        """Verifica se há credenciais válidas configuradas (PAT presente)."""
        import credentials_backend
        creds = credentials_backend.load_credentials()
        return bool(creds and creds.get("pat"))

    def _on_tray_message_clicked(self):
        """Ao clicar na notificação da bandeja: oferece a atualização pendente ou reabre as credenciais."""
        if self._pending_update is not None:
            info, self._pending_update = self._pending_update, None
            self._prompt_update(info)
        elif not self.has_configured_credentials():
            self._open_credentials_dialog()

    # ------------------------------------------------------------------
    # Atualizacoes
    # ------------------------------------------------------------------
    UPDATE_CHECK_INTERVAL_SECONDS = 24 * 3600

    def _init_updater(self):
        self._updater = updater.Updater(__version__, self)
        self._updater.check_finished.connect(self._on_update_check)
        self._updater.download_finished.connect(self._on_update_downloaded)
        self._pending_update = None
        self._update_manual = False
        self._update_busy = False
        if auto_update_enabled():
            prefs = QtCore.QSettings("WTC LG", "Preferences")
            last = prefs.value("last_update_check", 0.0, type=float)
            import time
            if time.time() - last >= self.UPDATE_CHECK_INTERVAL_SECONDS:
                QtCore.QTimer.singleShot(15000, lambda: self._check_updates(manual=False))

    def _check_updates(self, manual: bool):
        if self._update_busy:
            return
        import time
        self._update_busy = True
        self._update_manual = manual
        QtCore.QSettings("WTC LG", "Preferences").setValue("last_update_check", time.time())
        self._updater.check()

    def _update_message(self, kind: str, text: str):
        panel = self.window.panel
        box = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Icon.Warning if kind == "error" else QtWidgets.QMessageBox.Icon.Information,
            panel.tr_text("update_title"), text)
        box.setWindowIcon(self.tray.icon())
        box.exec()

    def _on_update_check(self, info, error: str):
        self._update_busy = False
        panel = self.window.panel
        if error:
            if self._update_manual:
                self._update_message("error", panel.tr_text("update_error").format(e=error))
        elif info is None:
            if self._update_manual:
                self._update_message("info", panel.tr_text("update_none").format(v=__version__))
        elif self._update_manual:
            self._prompt_update(info)
        else:
            # Busca automatica nunca interrompe com janela: avisa na bandeja e espera o clique
            self._pending_update = info
            self.tray.showMessage(panel.tr_text("update_title"),
                                  panel.tr_text("update_notify").format(v=info["version"]),
                                  QtWidgets.QSystemTrayIcon.MessageIcon.Information, 8000)

    def _prompt_update(self, info: dict):
        panel = self.window.panel
        can_install = updater.is_installed_build() and info.get("setup_url") and info.get("sums_url")
        key = "update_available" if can_install else "update_available_portable"
        answer = QtWidgets.QMessageBox.question(
            None, panel.tr_text("update_title"), panel.tr_text(key).format(v=info["version"]))
        if answer != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        if can_install:
            self._update_busy = True
            self.tray.showMessage(panel.tr_text("update_title"), panel.tr_text("update_downloading"),
                                  QtWidgets.QSystemTrayIcon.MessageIcon.Information, 4000)
            self._updater.download(info)
        else:
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(info.get("page") or updater.RELEASES_PAGE))

    def _on_update_downloaded(self, path: str, error: str):
        self._update_busy = False
        if error:
            self._update_message("error", self.window.panel.tr_text("update_error").format(e=error))
            return
        try:
            updater.launch_installer(path)
        except OSError as e:
            self._update_message("error", self.window.panel.tr_text("update_error").format(e=e))
            return
        self.quit()

    def _on_command_failed(self):
        panel = self.window.panel
        self.tray.showMessage(
            panel.tr_text("command_failed_title"),
            panel.tr_text("command_failed"),
            QtWidgets.QSystemTrayIcon.MessageIcon.Warning,
            5000
        )

    def _update_tray_texts(self, lang: str):
        self.m_open.setText(self.window.panel.tr_text("open_panel"))
        self.action_autostart.setText(self.window.panel.tr_text("autostart"))
        self.action_update.setText(self.window.panel.tr_text("update_check"))
        if hasattr(self, "action_clear_data"):
            self.action_clear_data.setText(self.window.panel.tr_text("clear_data"))
        self.m_quit.setText(self.window.panel.tr_text("quit"))

    def _check_taskbar_theme(self):
        is_light = is_windows_taskbar_light()
        if is_light != self._current_theme_is_light:
            self._current_theme_is_light = is_light
            self.tray.setIcon(create_tray_icon())

        apps_dark = is_windows_dark_mode()
        if apps_dark != self._current_apps_dark:
            self._current_apps_dark = apps_dark
            if getattr(self.window.panel, "theme_mode", "system") == "system":
                self.window.panel.apply_theme()

    def _toggle_autostart(self):
        new_state = self.action_autostart.isChecked()
        success = set_autostart_enabled(new_state)
        if not success:
            self.action_autostart.setChecked(not new_state)

    def _open_credentials_dialog(self):
        from credentials_dialog import CredentialsDialog
        theme_mode = getattr(self.window.panel, "theme_mode", "system")
        dlg = CredentialsDialog(theme_mode=theme_mode)
        if dlg.exec():
            # O botão do diálogo diz "Concluir e Abrir Painel": abre o painel (show_popup também
            # sincroniza o status). O atraso deixa o diálogo terminar de fechar antes de o painel
            # pedir o foco, senão o auto-ocultar pode escondê-lo na hora.
            QtCore.QTimer.singleShot(100, self.window.show_popup)
            return True
        return False

    def on_activated(self, reason):
        if reason in (QtWidgets.QSystemTrayIcon.ActivationReason.Trigger, QtWidgets.QSystemTrayIcon.ActivationReason.DoubleClick):
            self.toggle()

    def toggle(self):
        # Se não houver credenciais configuradas, notifica o usuário na bandeja e oferece para tentar novamente
        if not self.has_configured_credentials():
            self.tray.showMessage(
                "LG ThinQ - Configuração Pendente",
                "Você precisa conectar sua conta LG ThinQ para usar o painel. Clique aqui para configurar suas credenciais e tentar novamente.",
                QtWidgets.QSystemTrayIcon.MessageIcon.Information,
                6000
            )
            QtCore.QTimer.singleShot(250, self._open_credentials_dialog)
            return

        if self.window.isVisible():
            self.window.hide()
        else:
            self.window.show_popup()

    def quit(self):
        try:
            if hasattr(self, '_theme_timer'):
                self._theme_timer.stop()
            self.window.panel.cleanup()
        except Exception:
            pass
        self.tray.hide()
        self.app.quit()

    def run(self):
        return self.app.exec()


if __name__ == "__main__":
    import credentials_backend
    app_instance = TrayApplication()

    # Se não houver credenciais configuradas nem .env, abre automaticamente a tela de onboarding
    existing_creds = credentials_backend.load_credentials()
    if not existing_creds or not existing_creds.get("pat"):
        QtCore.QTimer.singleShot(150, app_instance._open_credentials_dialog)
    elif "--silent" not in sys.argv and "--minimized" not in sys.argv:
        QtCore.QTimer.singleShot(350, app_instance.window.show_popup)

    sys.exit(app_instance.run())
