import sys
import os
import math
import re
from PySide6 import QtCore, QtGui, QtWidgets, QtSvg

# =====================================================================
# Design System (Dark Glass Modern - Fidelidade Absoluta ao Mockup)
# =====================================================================
BG_COLOR = "#0D0E12"
CARD_BG = "#191B22"
CARD_HOVER = "#22252F"
CARD_ACTIVE = "#2C303E"
BORDER_COLOR = "rgba(255, 255, 255, 0.08)"
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#94A3B8"
ACCENT_GREEN = "#4ADE80"
ACCENT_CYAN = "#38BDF8"
ACCENT_ORANGE = "#FB923C"
THUMB_COLOR = "#D4C5B9"
POWER_CREAM = "#D4D0C7"

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


def get_base_dir() -> str:
    """Retorna o diretório base da aplicação (local do executável ou script), onde o .env deve residir."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_resource_path(relative_path: str) -> str:
    """Retorna o caminho absoluto para recursos/assets, suportando tanto Python puro quanto PyInstaller (_MEIPASS)."""
    base = getattr(sys, '_MEIPASS', get_base_dir())
    return os.path.join(base, relative_path)


def load_user_svg(filename: str, width: int = 30, height: int = 30, padding: int = 1, color: str = "#FFFFFF") -> QtGui.QPixmap:
    """Carrega os arquivos SVG da pasta assets com cor branca pura (#FFFFFF) e dimensionamento proporcional"""
    path = get_resource_path(os.path.join("assets", filename))
    if not os.path.exists(path):
        pix = QtGui.QPixmap(width, height)
        pix.fill(QtCore.Qt.GlobalColor.transparent)
        return pix

    with open(path, "r", encoding="utf-8") as f:
        svg = f.read()

    # Garantir preenchimento branco puro em todos os caminhos
    if "fill=" not in svg:
        svg = svg.replace("<path", f'<path fill="{color}"')
    else:
        svg = re.sub(r'fill="[^"]*"', f'fill="{color}"', svg)

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


def create_stepper_icon(symbol_type: str, size: int = 38) -> QtGui.QIcon:
    """Gera ícone vetorial perfeitamente centralizado para os botões (+) e (-) do stepper"""
    pix = QtGui.QPixmap(size, size)
    pix.fill(QtCore.Qt.GlobalColor.transparent)
    p = QtGui.QPainter(pix)
    p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    pen = QtGui.QPen(QtGui.QColor("#FFFFFF"), 2.2)
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


def svg_to_pixmap(svg_text: str, width: int = 24, height: int = 24, color: str = "#FFFFFF") -> QtGui.QPixmap:
    """Renderiza SVG embutido com currentColor"""
    svg_colored = svg_text.replace("currentColor", color)
    renderer = QtSvg.QSvgRenderer(QtCore.QByteArray(svg_colored.encode('utf-8')))
    pix = QtGui.QPixmap(width, height)
    pix.fill(QtCore.Qt.GlobalColor.transparent)
    painter = QtGui.QPainter(pix)
    painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
    renderer.render(painter)
    painter.end()
    return pix


class AnimatedAirCurtainHero(QtWidgets.QWidget):
    """Widget Hero: Ar Condicionado Split com Cortina de Vento Alinhada e Fluida"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(185)
        self.is_powered_on = True
        self.current_mode = "Cool"
        self._phase = 0.0
        self._wind_alpha = 1.0

        img_path = get_resource_path(os.path.join("assets", "ac_unit_pure.png"))
        if not os.path.exists(img_path):
            img_path = get_resource_path(os.path.join("assets", "ac_unit_nobg.png"))

        self.ac_pixmap = QtGui.QPixmap(img_path)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._step)
        self.timer.setInterval(33)
        self.timer.start()

    def set_power(self, power: bool):
        self.is_powered_on = power
        if power:
            self._wind_alpha = 1.0
            if not self.timer.isActive():
                self.timer.start()
        else:
            self._wind_alpha = 0.0
            self.timer.stop()
        self.update()

    def set_mode(self, mode: str):
        self.current_mode = mode
        self.update()

    def showEvent(self, event):
        super().showEvent(event)
        if self.is_powered_on and not self.timer.isActive():
            self.timer.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.timer.stop()

    def _step(self):
        if not self.is_powered_on:
            self._wind_alpha = 0.0
            self.timer.stop()
            self.update()
            return

        self._phase += 0.035
        if self._phase > 2 * math.pi * 100:
            self._phase = 0.0

        self.update()

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)

        w = self.width()
        ac_w = 192
        if not self.ac_pixmap.isNull():
            ac_h = int(ac_w * (self.ac_pixmap.height() / self.ac_pixmap.width()))
        else:
            ac_h = 124

        ac_x = (w - ac_w) // 2
        ac_y = 6

        if self._wind_alpha > 0.005:
            self._draw_air_curtain(p, ac_x, ac_y, ac_w, ac_h)

        if not self.ac_pixmap.isNull():
            p.drawPixmap(ac_x, ac_y, ac_w, ac_h, self.ac_pixmap)

        p.end()

    def _draw_air_curtain(self, p: QtGui.QPainter, ac_x: int, ac_y: int, ac_w: int, ac_h: int):
        mode = self.current_mode.lower()
        if "heat" in mode:
            base_col = QtGui.QColor(251, 146, 60)
            accent_col = QtGui.QColor(254, 215, 170)
        elif "fan" in mode:
            base_col = QtGui.QColor(241, 245, 249)
            accent_col = QtGui.QColor(255, 255, 255)
        elif "dry" in mode:
            base_col = QtGui.QColor(45, 212, 191)
            accent_col = QtGui.QColor(153, 246, 228)
        else:
            base_col = QtGui.QColor(56, 189, 248)
            accent_col = QtGui.QColor(186, 230, 253)

        vent_x1 = ac_x + int(ac_w * 0.12)
        vent_x2 = ac_x + int(ac_w * 0.88)
        vent_y1 = ac_y + int(ac_h * 0.98)
        vent_y2 = ac_y + int(ac_h * 0.67)

        wind_img = QtGui.QImage(self.width(), self.height(), QtGui.QImage.Format.Format_ARGB32_Premultiplied)
        wind_img.fill(QtCore.Qt.GlobalColor.transparent)
        wp = QtGui.QPainter(wind_img)
        wp.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        # -----------------------------------------------------------------
        # Curvatura suave para cima: o ar desce da aleta e sobe para frente
        # -----------------------------------------------------------------

        # -----------------------------------------------------------------
        # Trajetória fiel ao desenho: sai de Y vertical e curva para X horizontal (+X direita)
        # -----------------------------------------------------------------

        # Camada 1: Glow difuso de fundo (Backlight Glow / Névoa)
        num_glows = 14
        for g in range(num_glows):
            tg = g / (num_glows - 1)
            gx = vent_x1 + tg * (vent_x2 - vent_x1)
            gy = vent_y1 + tg * (vent_y2 - vent_y1)

            drift_x = 32 + tg * 32

            c1x = gx + drift_x * 0.12
            c1y = gy + 20
            c2x = gx + drift_x * 0.68
            c2y = gy + 34
            g_ex = gx + drift_x
            g_ey = gy + 35

            g_path = QtGui.QPainterPath()
            g_path.moveTo(gx, gy)
            g_path.cubicTo(c1x, c1y, c2x, c2y, g_ex, g_ey)

            g_grad = QtGui.QLinearGradient(gx, gy, g_ex, g_ey)
            edge = math.sin(tg * math.pi)
            g_alpha = int(34 * self._wind_alpha * edge)

            cg_top = QtGui.QColor(base_col)
            cg_top.setAlpha(g_alpha)
            cg_bot = QtGui.QColor(base_col)
            cg_bot.setAlpha(0)

            g_grad.setColorAt(0.0, cg_top)
            g_grad.setColorAt(0.45, cg_top)
            g_grad.setColorAt(1.0, cg_bot)

            pen_g = QtGui.QPen(QtGui.QBrush(g_grad), 32.0)
            pen_g.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
            wp.setPen(pen_g)
            wp.drawPath(g_path)

        # Camada 2: Faixas Volumétricas Principais (Curvando de Y para X)
        num_streams = 22
        for i in range(num_streams):
            t = i / (num_streams - 1)
            sx = vent_x1 + t * (vent_x2 - vent_x1)
            sy = vent_y1 + t * (vent_y2 - vent_y1)

            wave_y = math.sin(self._phase + i * 0.35) * 5.0
            wave_x = math.cos(self._phase * 0.8 + i * 0.3) * 4.0

            drift_x = 34 + t * 34 + wave_x

            # Começa descendo verticalmente em Y
            c1x = sx + drift_x * 0.12
            c1y = sy + 18 + wave_y * 0.3

            # Curva fazendo a dobra em direção a X
            c2x = sx + drift_x * 0.70
            c2y = sy + 33 + wave_y * 0.7

            # Ponto final nivelado horizontalmente em X
            ex = sx + drift_x
            ey = sy + 35 + wave_y

            path = QtGui.QPainterPath()
            path.moveTo(sx, sy)
            path.cubicTo(c1x, c1y, c2x, c2y, ex, ey)

            grad = QtGui.QLinearGradient(sx, sy, ex, ey)
            edge_factor = math.sin(t * math.pi)
            pulse = 0.75 + 0.25 * math.sin(self._phase * 0.85 + i * 0.45)

            alpha_top = int(76 * self._wind_alpha * edge_factor * pulse)
            alpha_mid = int(42 * self._wind_alpha * edge_factor * pulse)

            c_top = QtGui.QColor(accent_col)
            c_top.setAlpha(alpha_top)
            c_mid = QtGui.QColor(base_col)
            c_mid.setAlpha(alpha_mid)
            c_bot = QtGui.QColor(base_col)
            c_bot.setAlpha(0)

            grad.setColorAt(0.0, c_top)
            grad.setColorAt(0.35, c_mid)
            grad.setColorAt(0.85, c_bot)
            grad.setColorAt(1.0, c_bot)

            pen_w = 20.0 + 5.0 * math.sin(self._phase * 0.5 + i)
            pen = QtGui.QPen(QtGui.QBrush(grad), pen_w)
            pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
            wp.setPen(pen)
            wp.drawPath(path)

        # Camada 3: Cristas Internas Suaves
        for j in range(10):
            t = (j + 0.5) / 10.0
            sx = vent_x1 + t * (vent_x2 - vent_x1)
            sy = vent_y1 + t * (vent_y2 - vent_y1)

            w_ph = self._phase * 1.35 + j * 0.55
            wave_w = math.sin(w_ph) * 6.0
            drift_x = 36 + t * 32 + wave_w

            c1x = sx + drift_x * 0.12
            c1y = sy + 19
            c2x = sx + drift_x * 0.70
            c2y = sy + 34 + wave_w * 0.7
            ex = sx + drift_x
            ey = sy + 36 + wave_w

            path = QtGui.QPainterPath()
            path.moveTo(sx, sy)
            path.cubicTo(c1x, c1y, c2x, c2y, ex, ey)

            w_grad = QtGui.QLinearGradient(sx, sy, ex, ey)
            edge_factor = math.sin(t * math.pi)
            pulse = 0.7 + 0.3 * math.sin(w_ph)
            alpha_top = int(62 * self._wind_alpha * edge_factor * pulse)

            c_w_top = QtGui.QColor(accent_col)
            c_w_top.setAlpha(alpha_top)
            c_w_bot = QtGui.QColor(base_col)
            c_w_bot.setAlpha(0)

            w_grad.setColorAt(0.0, c_w_top)
            w_grad.setColorAt(0.4, c_w_top)
            w_grad.setColorAt(0.9, c_w_bot)
            w_grad.setColorAt(1.0, c_w_bot)

            pen_w = 9.0 + 2.5 * math.sin(w_ph)
            pen = QtGui.QPen(QtGui.QBrush(w_grad), pen_w)
            pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
            wp.setPen(pen)
            wp.drawPath(path)

        wp.end()
        p.drawImage(0, 0, wind_img)


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

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        is_on = self.isChecked()
        bg_col = QtGui.QColor(THUMB_COLOR) if is_on else QtGui.QColor(42, 45, 54)
        p.setBrush(QtGui.QBrush(bg_col))
        p.setPen(QtCore.Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, self.width(), self.height(), 12, 12)

        thumb_col = QtGui.QColor(20, 22, 28) if is_on else QtGui.QColor(160, 166, 178)
        p.setBrush(QtGui.QBrush(thumb_col))
        p.drawEllipse(QtCore.QPointF(self._thumb_position + 9.0, 12.0), 9.0, 9.0)
        p.end()


class ModernTrackSlider(QtWidgets.QSlider):
    """Slider de trilha premium com gradiente contínuo e pill perfeitamente integrado"""
    def __init__(self, parent=None):
        super().__init__(QtCore.Qt.Orientation.Horizontal, parent)
        self._dragging = False
        self._hovered = False
        self._visual_ratio = 0.0

        self._anim = QtCore.QPropertyAnimation(self, b"visual_ratio", self)
        self._anim.setDuration(130)
        self._anim.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)

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
        pill_w = 40.0
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

        # 1. Base Track (Groove)
        p.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 14), 1.0))
        p.setBrush(QtGui.QBrush(QtGui.QColor("#181A22")))
        p.drawRoundedRect(track_rect, radius, radius)

        # 2. Pill Position
        pill_w = 40.0
        pill_h = 24.0
        pad = 2.0
        min_x = pad
        max_x = w - pill_w - pad
        pill_x = min_x + self._visual_ratio * (max_x - min_x)
        pill_y = (h - pill_h) / 2.0

        # 3. Active Gradient (Envelops the pill: ends slightly ahead of the pill)
        grad_end_x = min(w, pill_x + pill_w + 6.0)

        track_path = QtGui.QPainterPath()
        track_path.addRoundedRect(track_rect, radius, radius)
        p.save()
        p.setClipPath(track_path)

        grad = QtGui.QLinearGradient(0.0, 0.0, grad_end_x, 0.0)
        grad.setColorAt(0.0, QtGui.QColor("#242732"))
        grad.setColorAt(0.4, QtGui.QColor("#3A3734"))
        grad.setColorAt(0.85, QtGui.QColor("#544C44"))
        grad.setColorAt(1.0, QtGui.QColor("#60564C"))

        p.setPen(QtCore.Qt.PenStyle.NoPen)
        p.setBrush(QtGui.QBrush(grad))
        grad_rect = QtCore.QRectF(0.0, track_y, grad_end_x, track_h)
        p.drawRoundedRect(grad_rect, radius, radius)
        p.restore()

        # 4. Pill (Handle)
        pill_rect = QtCore.QRectF(pill_x, pill_y, pill_w, pill_h)
        pill_col = QtGui.QColor("#EDE4DC" if (self._hovered or self._dragging) else "#D4C5B9")
        p.setPen(QtCore.Qt.PenStyle.NoPen)
        p.setBrush(QtGui.QBrush(pill_col))
        p.drawRoundedRect(pill_rect, 12.0, 12.0)

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

    def _init_icons(self):
        if self.key == "mode":
            pix = load_user_svg("mode.svg", 30, 30, padding=1, color="#FFFFFF")
            self.icon_label.setPixmap(pix)

        elif self.key == "fan":
            # Fan speed: Rotação horária suave no hover ou quando o modo estiver selecionado
            self.fan_base_pixmap = load_user_svg("fan-speed.svg", 30, 30, padding=1, color="#FFFFFF")
            self.icon_label.setPixmap(self.fan_base_pixmap)
            self._fan_angle = 0.0
            self._fan_timer = QtCore.QTimer(self)
            self._fan_timer.setInterval(28)  # ~35 FPS para giro suave e macio
            self._fan_timer.timeout.connect(self._step_fan_rotation)

        elif self.key == "sleep":
            pix = load_user_svg("crescent-moon.svg", 30, 30, padding=1, color="#FFFFFF")
            self.icon_label.setPixmap(pix)

        elif self.key == "airflow":
            # Airflow: Ícone animado originado de air.json (28 frames fluidos)
            self.air_frames = []
            frames_dir = get_resource_path(os.path.join("assets", "air_frames"))
            if os.path.exists(frames_dir):
                for i in range(28):
                    fn = os.path.join(frames_dir, f"frame_{i:02d}.png")
                    if os.path.exists(fn):
                        pm = QtGui.QPixmap(fn).scaled(30, 30, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
                        self.air_frames.append(pm)

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
        if self.is_expanded:
            self.setStyleSheet(f"""
                QFrame#ControlCard {{
                    background-color: {CARD_ACTIVE};
                    border: 1px solid rgba(255, 255, 255, 0.28);
                    border-radius: 18px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame#ControlCard {{
                    background-color: {CARD_BG};
                    border: 1px solid {BORDER_COLOR};
                    border-radius: 18px;
                }}
                QFrame#ControlCard:hover {{
                    background-color: {CARD_HOVER};
                    border: 1px solid rgba(255, 255, 255, 0.16);
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
        self.setStyleSheet("""
            QFrame#OptionsDrawer {{
                background-color: #13151C;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 14px;
            }}
        """)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(6)

        self.setFixedHeight(0)
        self.setVisible(False)

        self.anim = QtCore.QPropertyAnimation(self, b"fixed_height_prop", self)
        self.anim.setDuration(180)
        self.anim.setEasingCurve(QtCore.QEasingCurve.Type.InOutCubic)

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

        for opt in options:
            btn = QtWidgets.QPushButton(opt)
            btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            is_active = (opt.lower() == selected_value.lower())

            bg = "#272B38" if is_active else "#181A22"
            col = "#38BDF8" if is_active else "#E2E8F0"
            border = "rgba(56, 189, 248, 0.5)" if is_active else "rgba(255, 255, 255, 0.08)"

            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    color: {col};
                    border: 1px solid {border};
                    border-radius: 10px;
                    padding: 8px 14px;
                    font-size: 12px;
                    font-weight: 600;
                    font-family: 'Segoe UI', sans-serif;
                }}
                QPushButton:hover {{
                    background-color: #2F3444;
                    color: #FFFFFF;
                }}
            """)
            btn.clicked.connect(lambda checked=False, o=opt, c=category: self._on_opt_click(c, o))
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


class ThinQWorker(QtCore.QThread):
    status_updated = QtCore.Signal(dict)

    def run(self):
        try:
            from dotenv import load_dotenv
            env_file = os.path.join(get_base_dir(), ".env")
            if os.path.exists(env_file):
                load_dotenv(env_file)
            else:
                load_dotenv()

            pat = os.getenv("THINQ_PAT")
            country = os.getenv("THINQ_COUNTRY", "BR")
            client_id = os.getenv("THINQ_CLIENT_ID", "windows_ac_tray_app")
            device_id = os.getenv("THINQ_DEVICE_ID", "947e6dea7dd7be07c5e1b7821664f80c1db9845fbf75d6d4f33c60d206d7ab3a")
            if not pat:
                return

            import asyncio
            from aiohttp import ClientSession
            from thinqconnect import ThinQApi

            async def _get():
                async with ClientSession() as session:
                    api = ThinQApi(session=session, access_token=pat, country_code=country, client_id=client_id)
                    res = await api.async_get_device_status(device_id)
                    return res.body if hasattr(res, "body") else res

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            data = loop.run_until_complete(_get())
            loop.close()
            if data and isinstance(data, dict):
                print(f"[ThinQ] Status atualizado com sucesso do aparelho.", flush=True)
                self.status_updated.emit(data)
        except Exception as e:
            print("[ThinQ Status Error]:", e, flush=True)


class ThinQCommandWorker(QtCore.QThread):
    command_finished = QtCore.Signal(bool, str)

    def __init__(self, payload: dict, parent=None):
        super().__init__(parent)
        self.payload = payload

    def run(self):
        try:
            from dotenv import load_dotenv
            env_file = os.path.join(get_base_dir(), ".env")
            if os.path.exists(env_file):
                load_dotenv(env_file)
            else:
                load_dotenv()

            pat = os.getenv("THINQ_PAT")
            country = os.getenv("THINQ_COUNTRY", "BR")
            client_id = os.getenv("THINQ_CLIENT_ID", "windows_ac_tray_app")
            device_id = os.getenv("THINQ_DEVICE_ID", "947e6dea7dd7be07c5e1b7821664f80c1db9845fbf75d6d4f33c60d206d7ab3a")
            if not pat:
                return

            import asyncio
            from aiohttp import ClientSession
            from thinqconnect import ThinQApi

            async def _send():
                async with ClientSession() as session:
                    api = ThinQApi(session=session, access_token=pat, country_code=country, client_id=client_id)
                    print(f"[ThinQ] >> Enviando comando: {self.payload}", flush=True)
                    res = await api.async_post_device_control(device_id, self.payload)
                    print(f"[ThinQ] << Comando executado com sucesso: {res}", flush=True)
                    return res

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            res = loop.run_until_complete(_send())
            loop.close()
            self.command_finished.emit(True, str(res))
        except Exception as e:
            print(f"[ThinQ Command Error]: {e} (Payload: {self.payload})", flush=True)
            self.command_finished.emit(False, str(e))



class ACPanelWidget(QtWidgets.QFrame):
    """Painel Principal Proporcional com Estética macOS / Windows 11 Flyout"""

    power_toggled = QtCore.Signal(bool)
    temp_changed = QtCore.Signal(float)
    eco_toggled = QtCore.Signal(bool)
    option_changed = QtCore.Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ACPanel")

        self.is_powered_on = False  # Começa seguro e sincroniza imediatamente com o estado real do aparelho
        self.room_temp = 22.5
        self.target_temp = 21.0
        self.eco_mode = False
        self.current_mode = "Cool"
        self.fan_speed = "Auto"
        self.sleep_state = "Off"
        self.airflow_state = "Vertical"
        self._active_workers = []

        self._temp_debounce_timer = QtCore.QTimer(self)
        self._temp_debounce_timer.setSingleShot(True)
        self._temp_debounce_timer.setInterval(400)
        self._temp_debounce_timer.timeout.connect(self._send_temp_command)

        self.setStyleSheet(f"""
            QFrame#ACPanel {{
                background-color: {BG_COLOR};
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 28px;
            }}
        """)

        self.setFixedWidth(450)
        self._build_ui()

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
        self.lbl_room_temp.setStyleSheet("color: #E2E8F0; font-size: 15px; font-family: 'Segoe UI', sans-serif;")
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
        self.ac_hero.set_power(self.is_powered_on)
        self.ac_hero.set_mode(self.current_mode)
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

        # Eco Mode: Card unificado com folha preenchida sólida e corte da nervura central (leaf.fill)
        eco_card = QtWidgets.QFrame()
        eco_card.setObjectName("EcoCard")
        eco_card.setStyleSheet(f"""
            QFrame#EcoCard {{
                background-color: #171920;
                border: 1px solid {BORDER_COLOR};
                border-radius: 20px;
            }}
        """)
        eco_layout = QtWidgets.QHBoxLayout(eco_card)
        eco_layout.setContentsMargins(14, 8, 14, 8)
        eco_layout.setSpacing(10)

        leaf_icon = QtWidgets.QLabel()
        leaf_icon.setFixedSize(24, 24)
        leaf_icon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        leaf_icon.setPixmap(load_user_icon("eco.png", 24, 24, color="#FFFFFF"))
        eco_layout.addWidget(leaf_icon)

        eco_lbl = QtWidgets.QLabel("Eco Mode")
        eco_lbl.setStyleSheet("color: #FFFFFF; font-size: 13px; font-weight: 600; font-family: 'Segoe UI', sans-serif;")
        eco_layout.addWidget(eco_lbl)

        self.toggle_eco = AnimatedToggle()
        self.toggle_eco.setChecked(self.eco_mode)
        self.toggle_eco.stateChanged.connect(self._eco_state_changed)
        eco_layout.addWidget(self.toggle_eco)

        temp_eco_row.addWidget(eco_card)
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
        lbl_min = QtWidgets.QLabel("18°")
        lbl_min.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 500;")
        limits_row.addWidget(lbl_min)
        limits_row.addStretch()
        lbl_max = QtWidgets.QLabel("30°")
        lbl_max.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 500;")
        limits_row.addWidget(lbl_max)
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
        status_box.setSpacing(6)

        shield_icon = QtWidgets.QLabel()
        shield_icon.setFixedSize(16, 16)
        shield_icon.setPixmap(svg_to_pixmap(SVG_SHIELD, 16, 16, ACCENT_GREEN))
        status_box.addWidget(shield_icon)

        lbl_conn = QtWidgets.QLabel("Connected")
        lbl_conn.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 500;")
        status_box.addWidget(lbl_conn)

        footer.addLayout(status_box)
        footer.addStretch()

        btn_settings = QtWidgets.QPushButton()
        btn_settings.setFixedSize(28, 28)
        btn_settings.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        btn_settings.setIcon(QtGui.QIcon(svg_to_pixmap(SVG_SLIDERS, 20, 20, "#94A3B8")))
        btn_settings.setIconSize(QtCore.QSize(20, 20))
        btn_settings.setToolTip("Sincronizar status com LG ThinQ")
        btn_settings.setStyleSheet("QPushButton { background: transparent; border: none; } QPushButton:hover { opacity: 0.8; }")
        btn_settings.clicked.connect(self.refresh_status_from_thinq)
        footer.addWidget(btn_settings)

        layout.addLayout(footer)
        self.set_power(self.is_powered_on)

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
        self.drawer.show_category(cat, opts, sel)

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
            self.current_mode = option
            self.card_mode.set_value(option)
            self.ac_hero.set_mode(option)
            mode_map = {"Cool": "COOL", "Heat": "HEAT", "Fan": "FAN", "Dry": "AIR_DRY"}
            if option in mode_map:
                self._send_thinq_command({"airConJobMode": {"currentJobMode": mode_map[option]}})
        elif category == "fan":
            self.fan_speed = option
            self.card_fan.set_value(option)
            fan_map = {"Auto": "AUTO", "Low": "LOW", "Mid": "MID", "High": "HIGH"}
            if option in fan_map:
                self._send_thinq_command({"airFlow": {"windStrength": fan_map[option]}})
        elif category == "sleep":
            self.sleep_state = option
            self.card_sleep.set_value(option)
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
            self.card_airflow.set_value(option)
            is_swing = (option.lower() == "swing")
            self._send_thinq_command({"windDirection": {"rotateUpDown": is_swing}})

        self.option_changed.emit(category, option)

    def refresh_status_from_thinq(self):
        """Consulta o status em tempo real do aparelho via nuvem LG ThinQ em segundo plano"""
        worker = ThinQWorker(self)
        worker.status_updated.connect(self._apply_thinq_status)
        self._active_workers.append(worker)
        worker.finished.connect(lambda: self._active_workers.remove(worker) if worker in self._active_workers else None)
        worker.start()

    def _send_thinq_command(self, payload: dict):
        """Dispara comando assíncrono para o ar condicionado em segundo plano"""
        worker = ThinQCommandWorker(payload, self)
        self._active_workers.append(worker)
        worker.finished.connect(lambda: self._active_workers.remove(worker) if worker in self._active_workers else None)
        worker.start()

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
            self.slider.blockSignals(True)
            self.slider.setValue(int(t))
            self.slider.blockSignals(False)
            self.lbl_target_num.setText(str(int(t)))

        if "currentTemperature" in temp:
            self.room_temp = float(temp["currentTemperature"])
            self.lbl_room_temp.setText(f"Room  <b>{int(round(self.room_temp))}°C</b>")

        mode = data.get("airConJobMode", {})
        job_mode = mode.get("currentJobMode")
        if job_mode:
            formatted = "Dry" if job_mode == "AIR_DRY" else job_mode.capitalize()
            self.current_mode = formatted
            self.card_mode.set_value(formatted)
            self.ac_hero.set_mode(formatted)

        flow = data.get("airFlow", {})
        wind = flow.get("windStrength")
        if wind:
            self.fan_speed = wind.capitalize()
            self.card_fan.set_value(self.fan_speed)

        swing = data.get("windDirection", {})
        if "rotateUpDown" in swing:
            is_swing = swing.get("rotateUpDown", False)
            self.airflow_state = "Swing" if is_swing else "Vertical"
            self.card_airflow.set_value(self.airflow_state)

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
                self.card_sleep.set_value(self.sleep_state)
        elif sleep.get("relativeStopTimer") == "UNSET":
            self.sleep_state = "Off"
            self.card_sleep.set_value("Off")

    def set_power(self, power: bool):
        """Define o estado de energia em todos os componentes visuais"""
        self.is_powered_on = power
        self._update_power_button()
        self.ac_hero.set_power(power)
        self.card_mode.set_power(power)
        self.card_fan.set_power(power)
        self.card_sleep.set_power(power)
        self.card_airflow.set_power(power)

    def _update_power_button(self):
        col = POWER_CREAM if self.is_powered_on else "#64748B"
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
        self.eco_mode = bool(state)
        self.eco_toggled.emit(self.eco_mode)
        # Modo Eco: desliga ou liga o visor do ar condicionado
        self._send_thinq_command({"display": {"light": "OFF" if self.eco_mode else "ON"}})

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
        for worker in list(self._active_workers):
            if worker.isRunning():
                worker.quit()
                worker.wait(400)


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

    def reposition_smart(self):
        screen = QtGui.QGuiApplication.primaryScreen()
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
            if not self.isActiveWindow():
                QtCore.QTimer.singleShot(140, self._check_hide)
        super().changeEvent(event)

    def _check_hide(self):
        if not self.isActiveWindow():
            self.hide()


def create_tray_icon_pixmap() -> QtGui.QPixmap:
    pixmap = QtGui.QPixmap(64, 64)
    pixmap.fill(QtCore.Qt.GlobalColor.transparent)
    painter = QtGui.QPainter(pixmap)
    painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

    painter.setBrush(QtGui.QBrush(QtGui.QColor(30, 32, 38)))
    painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 40), 2))
    painter.drawRoundedRect(4, 4, 56, 56, 16, 16)

    painter.setBrush(QtGui.QBrush(QtGui.QColor(240, 240, 245)))
    painter.setPen(QtCore.Qt.PenStyle.NoPen)
    painter.drawRoundedRect(12, 16, 40, 18, 4, 4)

    painter.setPen(QtGui.QPen(QtGui.QColor(180, 185, 195), 2))
    painter.drawLine(15, 30, 49, 30)

    pen_air = QtGui.QPen(QtGui.QColor(56, 189, 248), 2.5)
    pen_air.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_air)
    painter.drawLine(18, 38, 18, 46)
    painter.drawLine(28, 38, 28, 49)
    painter.drawLine(36, 38, 36, 49)
    painter.drawLine(46, 38, 46, 46)
    painter.end()
    return pixmap


class TrayApplication:
    def __init__(self):
        self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setFont(QtGui.QFont("Segoe UI", 9))

        self.window = FullTrayWindow()

        self.tray = QtWidgets.QSystemTrayIcon(QtGui.QIcon(create_tray_icon_pixmap()), self.app)
        self.tray.setToolTip("LG Dual Inverter - Ar Condicionado")

        menu = QtWidgets.QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #18181B;
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 4px;
                font-family: 'Segoe UI', sans-serif;
            }
            QMenu::item {
                padding: 6px 16px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #27272A;
            }
        """)
        m_open = menu.addAction("Abrir Painel")
        m_open.triggered.connect(self.toggle)
        menu.addSeparator()
        m_quit = menu.addAction("Sair")
        m_quit.triggered.connect(self.quit)
        self.tray.setContextMenu(menu)

        self.tray.activated.connect(self.on_activated)
        self.tray.show()

    def on_activated(self, reason):
        if reason in (QtWidgets.QSystemTrayIcon.ActivationReason.Trigger, QtWidgets.QSystemTrayIcon.ActivationReason.DoubleClick):
            self.toggle()

    def toggle(self):
        if self.window.isVisible():
            self.window.hide()
        else:
            self.window.show_popup()

    def quit(self):
        try:
            self.window.panel.cleanup()
        except Exception:
            pass
        self.tray.hide()
        self.app.quit()

    def run(self):
        return self.app.exec()


if __name__ == "__main__":
    app_instance = TrayApplication()
    QtCore.QTimer.singleShot(350, app_instance.window.show_popup)
    sys.exit(app_instance.run())
