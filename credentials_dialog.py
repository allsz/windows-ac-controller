"""
credentials_dialog.py - Telas de Configuração e Validação de Credenciais LG ThinQ

Projetado com princípios do Impeccable:
- Tipografia inspirada no Notion (família Inter, ritmo vertical, proporções confortáveis e hierarquia clara).
- Suporte nativo completo aos 3 temas do app: Dark Glass, True Black e Light Mode.
- Resolução automática do tema do sistema operacional Windows por padrão.
- Alternância de visibilidade do token PAT (Mostrar/Ocultar com ícones SVG).
- Atalho direto para o portal oficial LG ThinQ Developer (Connect).
- Estados explícitos de validação com micro-animação, cartão de dispositivo encontrado e recuperação de erros.
- Integração transparente e segura com Windows DPAPI.
"""

import sys
import os
import asyncio
from typing import Optional, List, Dict, Any
from PySide6 import QtCore, QtGui, QtWidgets, QtSvg
from aiohttp import ClientSession
from thinqconnect import ThinQApi

import credentials_backend

# ---------------------------------------------------------------------
# Tipografia e Pilha de Fontes (Notion Style: Inter)
# ---------------------------------------------------------------------
FONT_STACK = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"

def init_fonts():
    """Garante que a fonte Inter (estilo Notion) seja registrada no QFontDatabase."""
    if not QtGui.QFontDatabase.hasFamily("Inter"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(base_dir, "assets", "fonts", "Inter-Variable.ttf")
        if os.path.exists(font_path):
            QtGui.QFontDatabase.addApplicationFont(font_path)

# ---------------------------------------------------------------------
# Paletas de Cores Sincronizadas com o ui_panel (Dark, Black, Light)
# ---------------------------------------------------------------------
FALLBACK_PALETTES = {
    "dark": {
        "bg_color": "#0D0E12",
        "card_bg": "#161820",
        "card_hover": "#1E202B",
        "card_active": "#272A36",
        "input_bg": "#111218",
        "input_border": "rgba(255, 255, 255, 0.12)",
        "input_border_focus": "#38BDF8",
        "border_color": "rgba(255, 255, 255, 0.08)",
        "panel_border": "rgba(255, 255, 255, 0.12)",
        "text_primary": "#FFFFFF",
        "text_secondary": "#94A3B8",
        "text_muted": "#64748B",
        "accent_primary": "#38BDF8",
        "accent_primary_text": "#000000",
        "accent_hover": "#60A5FA",
        "accent_green": "#4ADE80",
        "accent_red": "#F87171",
        "btn_sec_bg": "rgba(255, 255, 255, 0.06)",
        "btn_sec_hover": "rgba(255, 255, 255, 0.12)",
        "btn_sec_text": "#E2E8F0",
        "is_light": False,
    },
    "black": {
        "bg_color": "#000000",
        "card_bg": "#0D0D11",
        "card_hover": "#17171E",
        "card_active": "#21212B",
        "input_bg": "#0A0B0E",
        "input_border": "rgba(255, 255, 255, 0.14)",
        "input_border_focus": "#38BDF8",
        "border_color": "rgba(255, 255, 255, 0.10)",
        "panel_border": "rgba(255, 255, 255, 0.14)",
        "text_primary": "#FFFFFF",
        "text_secondary": "#9E9EAF",
        "text_muted": "#6E6E82",
        "accent_primary": "#38BDF8",
        "accent_primary_text": "#000000",
        "accent_hover": "#60A5FA",
        "accent_green": "#4ADE80",
        "accent_red": "#F87171",
        "btn_sec_bg": "rgba(255, 255, 255, 0.08)",
        "btn_sec_hover": "rgba(255, 255, 255, 0.15)",
        "btn_sec_text": "#E2E8F0",
        "is_light": False,
    },
    "light": {
        "bg_color": "#F8F9FA",
        "card_bg": "#FFFFFF",
        "card_hover": "#F1F5F9",
        "card_active": "#E2E8F0",
        "input_bg": "#FFFFFF",
        "input_border": "rgba(0, 0, 0, 0.15)",
        "input_border_focus": "#0284C7",
        "border_color": "rgba(0, 0, 0, 0.08)",
        "panel_border": "rgba(0, 0, 0, 0.14)",
        "text_primary": "#0F172A",
        "text_secondary": "#475569",
        "text_muted": "#64748B",
        "accent_primary": "#0284C7",
        "accent_primary_text": "#FFFFFF",
        "accent_hover": "#0369A1",
        "accent_green": "#16A34A",
        "accent_red": "#DC2626",
        "btn_sec_bg": "rgba(0, 0, 0, 0.05)",
        "btn_sec_hover": "rgba(0, 0, 0, 0.10)",
        "btn_sec_text": "#1E293B",
        "is_light": True,
    },
}

def is_windows_dark_mode() -> bool:
    """Verifica no registro do Windows se o tema de aplicativos é escuro (0) ou claro (1)."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            0,
            winreg.KEY_READ
        )
        val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return bool(val == 0)
    except Exception:
        return True

def resolve_theme_palette(theme_mode: Optional[str] = None) -> tuple[str, dict]:
    """Retorna o tema concreto ('dark', 'black', 'light') e o dicionário de cores."""
    if theme_mode is None:
        prefs = QtCore.QSettings("WTC LG", "Preferences")
        theme_mode = str(prefs.value("theme", "system"))

    if theme_mode not in ["system", "light", "dark", "black"]:
        theme_mode = "system"

    if theme_mode == "system":
        resolved = "dark" if is_windows_dark_mode() else "light"
    else:
        resolved = theme_mode

    pal = dict(FALLBACK_PALETTES.get(resolved, FALLBACK_PALETTES["dark"]))
    return resolved, pal

# ---------------------------------------------------------------------
# Ícones Minimalistas Vetoriais (SVG puros)
# ---------------------------------------------------------------------
SVG_KEY = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>"""

SVG_SHIELD = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>"""

SVG_CHECK_CIRCLE = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>"""

SVG_ALERT_CIRCLE = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>"""

SVG_REFRESH = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>"""

SVG_CLOSE = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>"""

SVG_EYE = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>"""

SVG_EYE_OFF = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>"""

SVG_AC = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="12" rx="2"/><line x1="6" y1="12" x2="18" y2="12"/><line x1="6" y1="18" x2="6" y2="20"/><line x1="12" y1="18" x2="12" y2="20"/><line x1="18" y1="18" x2="18" y2="20"/></svg>"""

def svg_to_pixmap(svg_template: str, width: int, height: int, color: str = "#FFFFFF") -> QtGui.QPixmap:
    svg_str = svg_template.format(color=color)
    renderer = QtSvg.QSvgRenderer(QtCore.QByteArray(svg_str.encode("utf-8")))
    pix = QtGui.QPixmap(width, height)
    pix.fill(QtCore.Qt.GlobalColor.transparent)
    p = QtGui.QPainter(pix)
    p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
    renderer.render(p)
    p.end()
    return pix

# ---------------------------------------------------------------------
# Worker Assíncrono de Validação com a LG ThinQ API
# ---------------------------------------------------------------------
class ValidationWorker(QtCore.QThread):
    finished_success = QtCore.Signal(list)
    finished_error = QtCore.Signal(str)

    def __init__(self, pat: str, country: str, client_id: str):
        super().__init__()
        self.pat = pat
        self.country = country
        self.client_id = client_id

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._validate())
        except Exception as e:
            self.finished_error.emit(f"Erro inesperado: {str(e)}")
        finally:
            loop.close()

    async def _validate(self):
        try:
            async with ClientSession() as session:
                api = ThinQApi(
                    session=session,
                    access_token=self.pat,
                    country_code=self.country,
                    client_id=self.client_id
                )
                resp = await api.async_get_device_list()
                devices = resp if isinstance(resp, list) else getattr(resp, "body", [])

                if not devices and not isinstance(resp, (list, dict)):
                    self.finished_error.emit("Não foi possível conectar aos servidores da LG. Verifique se o token PAT é válido.")
                    return

                ac_list = []
                for d in devices:
                    info = d.get("deviceInfo", {})
                    d_type = str(info.get("deviceType", d.get("deviceType", ""))).upper()
                    if "AIR_CONDITIONER" in d_type or "AC" in d_type:
                        ac_list.append({
                            "deviceId": d.get("deviceId"),
                            "alias": info.get("alias", d.get("alias", "Ar Condicionado LG")),
                            "model": info.get("modelName", d.get("modelName", "Dual Inverter Voice"))
                        })

                if not ac_list:
                    if devices:
                        first = devices[0]
                        info = first.get("deviceInfo", {})
                        ac_list.append({
                            "deviceId": first.get("deviceId"),
                            "alias": info.get("alias", "Dispositivo LG"),
                            "model": info.get("modelName", "Modelo ThinQ")
                        })
                    else:
                        self.finished_error.emit("Nenhum ar-condicionado encontrado na sua conta LG ThinQ.")
                        return

                self.finished_success.emit(ac_list)

        except Exception as e:
            err_str = str(e)
            if "401" in err_str or "unauthorized" in err_str.lower():
                self.finished_error.emit("Token de Acesso (PAT) inválido ou expirado. Gere um novo token no portal ThinQ Connect.")
            elif "403" in err_str or "forbidden" in err_str.lower():
                self.finished_error.emit("Acesso negado. Verifique se o código do país (ex: BR) corresponde à região da sua conta.")
            elif "timeout" in err_str.lower() or "connection" in err_str.lower():
                self.finished_error.emit("Tempo limite esgotado ao contatar os servidores da LG. Verifique sua conexão com a internet.")
            else:
                self.finished_error.emit(f"Falha na comunicação com a API LG: {err_str}")

# ---------------------------------------------------------------------
# Diálogo Principal de Credenciais
# ---------------------------------------------------------------------
class CredentialsDialog(QtWidgets.QDialog):
    credentials_saved = QtCore.Signal(dict)

    def __init__(self, parent=None, theme_mode: Optional[str] = None):
        super().__init__(parent)
        init_fonts()

        self.setWindowTitle("Configuração LG ThinQ")
        self.setFixedSize(550, 640)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        app_ico_path = os.path.join(base_dir, "assets", "app_icon.ico")
        if os.path.exists(app_ico_path):
            self.setWindowIcon(QtGui.QIcon(app_ico_path))

        default_font = QtGui.QFont("Inter", 10)
        default_font.setStyleHint(QtGui.QFont.StyleHint.SansSerif)
        self.setFont(default_font)

        self._resolved_theme, self.palette = resolve_theme_palette(theme_mode)
        self._devices_found = []
        self._worker: Optional[ValidationWorker] = None
        self._drag_pos = None
        self._pat_visible = False
        self._spin_angle = 0

        # Timer de rotação suave do spinner de validação
        self._spin_timer = QtCore.QTimer(self)
        self._spin_timer.setInterval(40)
        self._spin_timer.timeout.connect(self._step_spin)

        self._setup_ui()
        self._apply_theme()
        self._load_initial_values()

    def _setup_ui(self):
        root_layout = QtWidgets.QVBoxLayout(self)
        root_layout.setContentsMargins(14, 14, 14, 14)

        # Container Principal
        self.container = QtWidgets.QFrame(self)
        self.container.setObjectName("CredsContainer")

        # Sombra suave com profundidade
        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 10)
        shadow.setColor(QtGui.QColor(0, 0, 0, 120 if not self.palette["is_light"] else 50))
        self.container.setGraphicsEffect(shadow)
        root_layout.addWidget(self.container)

        container_layout = QtWidgets.QVBoxLayout(self.container)
        container_layout.setContentsMargins(28, 26, 28, 28)
        container_layout.setSpacing(18)

        # 1. Header (Ícone Badge + Título + Fechar)
        header_row = QtWidgets.QHBoxLayout()
        header_row.setSpacing(16)

        self.icon_badge = QtWidgets.QLabel()
        self.icon_badge.setFixedSize(42, 42)
        self.icon_badge.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        header_row.addWidget(self.icon_badge)

        title_box = QtWidgets.QVBoxLayout()
        title_box.setSpacing(4)
        self.lbl_title = QtWidgets.QLabel("Conectar LG ThinQ")
        self.lbl_subtitle = QtWidgets.QLabel("Controle direto do seu ar-condicionado pelo Windows")
        
        title_box.addWidget(self.lbl_title)
        title_box.addWidget(self.lbl_subtitle)
        header_row.addLayout(title_box)

        header_row.addStretch()

        self.btn_close = QtWidgets.QPushButton()
        self.btn_close.setFixedSize(32, 32)
        self.btn_close.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(self.reject)
        header_row.addWidget(self.btn_close)

        container_layout.addLayout(header_row)

        # Linha divisória sutil
        self.sep = QtWidgets.QFrame()
        self.sep.setFixedHeight(1)
        container_layout.addWidget(self.sep)

        # 2. Stacked Widget: Página 0 (Formulário) | Página 1 (Status / Validação)
        self.stack = QtWidgets.QStackedWidget()
        self.stack.setStyleSheet("background: transparent; border: none;")
        container_layout.addWidget(self.stack)

        # ---- Página 0: Formulário de Credenciais ----
        page_form = QtWidgets.QWidget()
        form_layout = QtWidgets.QVBoxLayout(page_form)
        form_layout.setContentsMargins(0, 4, 0, 0)
        form_layout.setSpacing(16)

        # PAT: Header da label + Badge
        pat_header = QtWidgets.QHBoxLayout()
        pat_header.setSpacing(8)
        self.lbl_pat = QtWidgets.QLabel("Personal Access Token (PAT)")
        pat_header.addWidget(self.lbl_pat)

        self.badge_required = QtWidgets.QLabel("Obrigatório")
        pat_header.addWidget(self.badge_required)
        pat_header.addStretch()

        self.btn_pat_portal = QtWidgets.QPushButton("Obter Token ↗")
        self.btn_pat_portal.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btn_pat_portal.clicked.connect(self._open_thinq_portal)
        pat_header.addWidget(self.btn_pat_portal)

        form_layout.addLayout(pat_header)

        # Input PAT com botão de visibilidade embutido
        pat_box = QtWidgets.QHBoxLayout()
        pat_box.setSpacing(8)

        self.input_pat = QtWidgets.QLineEdit()
        self.input_pat.setPlaceholderText("Cole o token PAT gerado no portal ThinQ...")
        self.input_pat.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.input_pat.setFixedHeight(42)
        self.input_pat.returnPressed.connect(self._start_validation)
        pat_box.addWidget(self.input_pat)

        self.btn_toggle_pat = QtWidgets.QPushButton()
        self.btn_toggle_pat.setFixedSize(42, 42)
        self.btn_toggle_pat.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_pat.setToolTip("Mostrar/Ocultar Token")
        self.btn_toggle_pat.clicked.connect(self._toggle_pat_visibility)
        pat_box.addWidget(self.btn_toggle_pat)

        form_layout.addLayout(pat_box)

        # Linha dupla: País + Client ID
        row_fields = QtWidgets.QHBoxLayout()
        row_fields.setSpacing(14)

        # Coluna País
        col_country = QtWidgets.QVBoxLayout()
        col_country.setSpacing(6)
        self.lbl_country = QtWidgets.QLabel("País da Conta")
        col_country.addWidget(self.lbl_country)

        self.input_country = QtWidgets.QLineEdit()
        self.input_country.setText("BR")
        self.input_country.setMaxLength(3)
        self.input_country.setFixedHeight(42)
        self.input_country.returnPressed.connect(self._start_validation)
        col_country.addWidget(self.input_country)

        self.lbl_country_help = QtWidgets.QLabel("Código de 2 ou 3 letras (ex: BR, US, PT)")
        col_country.addWidget(self.lbl_country_help)
        row_fields.addLayout(col_country, 1)

        # Coluna Client ID
        col_client = QtWidgets.QVBoxLayout()
        col_client.setSpacing(6)
        self.lbl_client = QtWidgets.QLabel("Client ID")
        col_client.addWidget(self.lbl_client)

        self.input_client_id = QtWidgets.QLineEdit()
        self.input_client_id.setText("windows_ac_tray_app")
        self.input_client_id.setFixedHeight(42)
        self.input_client_id.returnPressed.connect(self._start_validation)
        col_client.addWidget(self.input_client_id)

        self.lbl_client_help = QtWidgets.QLabel("Identificador do aplicativo no ThinQ")
        col_client.addWidget(self.lbl_client_help)
        row_fields.addLayout(col_client, 2)

        form_layout.addLayout(row_fields)

        # Card informativo sobre segurança e privacidade
        self.privacy_card = QtWidgets.QFrame()
        self.privacy_card.setObjectName("PrivacyCard")
        priv_layout = QtWidgets.QHBoxLayout(self.privacy_card)
        priv_layout.setContentsMargins(16, 14, 16, 14)
        priv_layout.setSpacing(14)

        self.shield_icon = QtWidgets.QLabel()
        self.shield_icon.setFixedSize(26, 26)
        priv_layout.addWidget(self.shield_icon)

        priv_text_box = QtWidgets.QVBoxLayout()
        priv_text_box.setSpacing(3)
        self.lbl_priv_title = QtWidgets.QLabel("Criptografia Local (Windows DPAPI)")
        self.lbl_priv_desc = QtWidgets.QLabel("Suas credenciais são protegidas com a chave da sua conta do Windows e salvas exclusivamente nesta máquina. Nenhuma informação é enviada a terceiros.")
        self.lbl_priv_desc.setWordWrap(True)
        priv_text_box.addWidget(self.lbl_priv_title)
        priv_text_box.addWidget(self.lbl_priv_desc)
        priv_layout.addLayout(priv_text_box)
        form_layout.addWidget(self.privacy_card)

        form_layout.addStretch()

        # Botões de Ação Inferiores (Cancelar + Testar e Salvar)
        btn_box = QtWidgets.QHBoxLayout()
        btn_box.setSpacing(12)

        self.btn_cancel = QtWidgets.QPushButton("Cancelar")
        self.btn_cancel.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setFixedHeight(44)
        self.btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(self.btn_cancel, 1)

        self.btn_validate = QtWidgets.QPushButton("Testar Conexão e Salvar")
        self.btn_validate.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btn_validate.setFixedHeight(44)
        self.btn_validate.clicked.connect(self._start_validation)
        btn_box.addWidget(self.btn_validate, 2)

        form_layout.addLayout(btn_box)
        self.stack.addWidget(page_form)

        # ---- Página 1: Status de Validação (Carregando / Sucesso / Erro) ----
        self.page_status = QtWidgets.QWidget()
        self.status_layout = QtWidgets.QVBoxLayout(self.page_status)
        self.status_layout.setContentsMargins(12, 20, 12, 12)
        self.status_layout.setSpacing(18)
        self.status_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.lbl_status_icon = QtWidgets.QLabel()
        self.lbl_status_icon.setFixedSize(60, 60)
        self.lbl_status_icon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.status_layout.addWidget(self.lbl_status_icon, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        self.lbl_status_title = QtWidgets.QLabel("Validando credenciais...")
        self.lbl_status_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.status_layout.addWidget(self.lbl_status_title)

        self.lbl_status_desc = QtWidgets.QLabel("Consultando a API oficial da LG ThinQ e listando seus dispositivos.")
        self.lbl_status_desc.setWordWrap(True)
        self.lbl_status_desc.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.status_layout.addWidget(self.lbl_status_desc)

        # Cartão de Aparelho Detectado
        self.device_card = QtWidgets.QFrame()
        self.device_card.setObjectName("DeviceCard")
        dev_layout = QtWidgets.QHBoxLayout(self.device_card)
        dev_layout.setContentsMargins(16, 14, 16, 14)
        dev_layout.setSpacing(14)

        self.ac_badge_icon = QtWidgets.QLabel()
        self.ac_badge_icon.setFixedSize(32, 32)
        dev_layout.addWidget(self.ac_badge_icon)

        dev_text_box = QtWidgets.QVBoxLayout()
        dev_text_box.setSpacing(3)
        self.lbl_device_alias = QtWidgets.QLabel("Ar Condicionado LG")
        self.lbl_device_model = QtWidgets.QLabel("Dual Inverter Voice")
        dev_text_box.addWidget(self.lbl_device_alias)
        dev_text_box.addWidget(self.lbl_device_model)
        dev_layout.addLayout(dev_text_box)
        dev_layout.addStretch()

        self.lbl_device_pill = QtWidgets.QLabel("Pronto")
        dev_layout.addWidget(self.lbl_device_pill)

        self.device_card.hide()
        self.status_layout.addWidget(self.device_card)

        # Seletor de dispositivo (se achar múltiplos aparelhos)
        self.device_combo = QtWidgets.QComboBox()
        self.device_combo.setFixedHeight(44)
        self.device_combo.hide()
        self.status_layout.addWidget(self.device_combo)

        self.status_layout.addStretch()

        # Botão de Ação do Status
        self.btn_status_action = QtWidgets.QPushButton("Continuar")
        self.btn_status_action.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btn_status_action.setFixedHeight(44)
        self.btn_status_action.hide()
        self.btn_status_action.clicked.connect(self._on_status_action_clicked)
        self.status_layout.addWidget(self.btn_status_action)

        self.stack.addWidget(self.page_status)

    def _apply_theme(self):
        """Aplica os estilos com tipografia no padrão Notion (Inter) e paleta ativa."""
        p = self.palette
        is_light = p["is_light"]

        # Container Principal
        self.container.setStyleSheet(f"""
            QFrame#CredsContainer {{
                background-color: {p["bg_color"]};
                border: 1px solid {p["panel_border"]};
                border-radius: 22px;
            }}
        """)

        # Header Badge
        badge_bg = "rgba(56, 189, 248, 0.12)" if not is_light else "rgba(2, 132, 199, 0.10)"
        self.icon_badge.setStyleSheet(f"background-color: {badge_bg}; border-radius: 12px;")
        self.icon_badge.setPixmap(svg_to_pixmap(SVG_KEY, 24, 24, p["accent_primary"]))

        # Textos do Header (Notion-grade scale)
        self.lbl_title.setStyleSheet(f"""
            color: {p['text_primary']};
            font-size: 20px;
            font-weight: 700;
            font-family: {FONT_STACK};
            letter-spacing: -0.02em;
            border: none;
        """)
        self.lbl_subtitle.setStyleSheet(f"""
            color: {p['text_secondary']};
            font-size: 13.5px;
            font-weight: 400;
            font-family: {FONT_STACK};
            border: none;
        """)

        # Botão Fechar
        self.btn_close.setIcon(QtGui.QIcon(svg_to_pixmap(SVG_CLOSE, 16, 16, p["text_secondary"])))
        self.btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 16px;
            }}
            QPushButton:hover {{
                background-color: {p["card_hover"]};
            }}
        """)

        # Separador
        self.sep.setStyleSheet(f"background-color: {p['border_color']}; border: none;")

        # Labels e Badges do Form
        self.lbl_pat.setStyleSheet(f"""
            color: {p['text_primary']};
            font-size: 13.5px;
            font-weight: 600;
            font-family: {FONT_STACK};
        """)
        self.badge_required.setStyleSheet(f"""
            color: {p['accent_primary']};
            background-color: {badge_bg};
            border: 1px solid {p['border_color']};
            font-size: 11px;
            font-weight: 600;
            font-family: {FONT_STACK};
            padding: 3px 8px;
            border-radius: 6px;
        """)

        self.btn_pat_portal.setStyleSheet(f"""
            QPushButton {{
                color: {p['accent_primary']};
                background: transparent;
                border: none;
                font-size: 12.5px;
                font-weight: 600;
                font-family: {FONT_STACK};
            }}
            QPushButton:hover {{
                text-decoration: underline;
                color: {p['accent_hover']};
            }}
        """)

        # Inputs Style (Notion-grade height & padding)
        input_css = f"""
            QLineEdit {{
                background-color: {p["input_bg"]};
                color: {p["text_primary"]};
                border: 1.2px solid {p["input_border"]};
                border-radius: 10px;
                padding: 10px 14px;
                font-size: 14px;
                font-family: {FONT_STACK};
                selection-background-color: {p["accent_primary"]};
                selection-color: {p["accent_primary_text"]};
            }}
            QLineEdit:focus {{
                border: 1.8px solid {p["input_border_focus"]};
            }}
            QLineEdit:hover:!focus {{
                border: 1.2px solid {p["card_active"]};
            }}
        """
        self.input_pat.setStyleSheet(input_css)
        self.input_country.setStyleSheet(input_css)
        self.input_client_id.setStyleSheet(input_css)

        # Botão de alternar visibilidade do PAT
        self._update_eye_icon()
        self.btn_toggle_pat.setStyleSheet(f"""
            QPushButton {{
                background-color: {p["card_bg"]};
                border: 1.2px solid {p["input_border"]};
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: {p["card_hover"]};
            }}
        """)

        # Labels de ajuda (legíveis, 12px+)
        self.lbl_country.setStyleSheet(f"""
            color: {p['text_primary']};
            font-size: 13.5px;
            font-weight: 600;
            font-family: {FONT_STACK};
        """)
        self.lbl_country_help.setStyleSheet(f"""
            color: {p['text_muted']};
            font-size: 12px;
            font-family: {FONT_STACK};
        """)
        self.lbl_client.setStyleSheet(f"""
            color: {p['text_primary']};
            font-size: 13.5px;
            font-weight: 600;
            font-family: {FONT_STACK};
        """)
        self.lbl_client_help.setStyleSheet(f"""
            color: {p['text_muted']};
            font-size: 12px;
            font-family: {FONT_STACK};
        """)

        # Card de Privacidade
        self.privacy_card.setStyleSheet(f"""
            QFrame#PrivacyCard {{
                background-color: {p["card_bg"]};
                border: 1px solid {p["border_color"]};
                border-radius: 14px;
            }}
        """)
        self.shield_icon.setPixmap(svg_to_pixmap(SVG_SHIELD, 24, 24, p["accent_green"]))
        self.lbl_priv_title.setStyleSheet(f"""
            color: {p['text_primary']};
            font-size: 13.5px;
            font-weight: 600;
            font-family: {FONT_STACK};
            border: none;
        """)
        self.lbl_priv_desc.setStyleSheet(f"""
            color: {p['text_secondary']};
            font-size: 12.5px;
            line-height: 1.45;
            font-family: {FONT_STACK};
            border: none;
        """)

        # Botão Cancelar
        self.btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: {p["btn_sec_bg"]};
                color: {p["btn_sec_text"]};
                font-size: 14px;
                font-weight: 600;
                font-family: {FONT_STACK};
                border-radius: 10px;
                border: 1px solid {p["border_color"]};
            }}
            QPushButton:hover {{
                background-color: {p["btn_sec_hover"]};
            }}
        """)

        # Botão Validar / Salvar (Primário)
        self.btn_validate.setStyleSheet(f"""
            QPushButton {{
                background-color: {p["accent_primary"]};
                color: {p["accent_primary_text"]};
                font-size: 14px;
                font-weight: 600;
                font-family: {FONT_STACK};
                letter-spacing: -0.01em;
                border-radius: 10px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {p["accent_hover"]};
            }}
            QPushButton:disabled {{
                background-color: {p["card_active"]};
                color: {p["text_muted"]};
            }}
        """)

        # Estilos da Página de Status
        self.lbl_status_title.setStyleSheet(f"""
            color: {p['text_primary']};
            font-size: 20px;
            font-weight: 700;
            font-family: {FONT_STACK};
            letter-spacing: -0.02em;
        """)
        self.lbl_status_desc.setStyleSheet(f"""
            color: {p['text_secondary']};
            font-size: 14px;
            line-height: 1.5;
            font-family: {FONT_STACK};
        """)

        self.device_card.setStyleSheet(f"""
            QFrame#DeviceCard {{
                background-color: {p["card_bg"]};
                border: 1px solid {p["border_color"]};
                border-radius: 14px;
            }}
        """)
        self.ac_badge_icon.setPixmap(svg_to_pixmap(SVG_AC, 26, 26, p["accent_primary"]))
        self.lbl_device_alias.setStyleSheet(f"""
            color: {p['text_primary']};
            font-size: 15px;
            font-weight: 700;
            font-family: {FONT_STACK};
            border: none;
        """)
        self.lbl_device_model.setStyleSheet(f"""
            color: {p['text_secondary']};
            font-size: 13px;
            font-family: {FONT_STACK};
            border: none;
        """)
        self.lbl_device_pill.setStyleSheet(f"""
            color: {p['accent_green']};
            background-color: rgba(74, 222, 128, 0.15);
            border: 1px solid rgba(74, 222, 128, 0.35);
            font-size: 12px;
            font-weight: 600;
            font-family: {FONT_STACK};
            padding: 4px 10px;
            border-radius: 10px;
        """)

        self.device_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {p["input_bg"]};
                color: {p["text_primary"]};
                border: 1.2px solid {p["input_border"]};
                border-radius: 10px;
                padding: 10px 14px;
                font-size: 13.5px;
                font-family: {FONT_STACK};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {p["bg_color"]};
                color: {p["text_primary"]};
                selection-background-color: {p["accent_primary"]};
                selection-color: {p["accent_primary_text"]};
                border: 1px solid {p["border_color"]};
            }}
        """)

        self.btn_status_action.setStyleSheet(self.btn_validate.styleSheet())

    def _update_eye_icon(self):
        svg = SVG_EYE if self._pat_visible else SVG_EYE_OFF
        self.btn_toggle_pat.setIcon(QtGui.QIcon(svg_to_pixmap(svg, 20, 20, self.palette["text_secondary"])))

    def _toggle_pat_visibility(self):
        self._pat_visible = not self._pat_visible
        mode = QtWidgets.QLineEdit.EchoMode.Normal if self._pat_visible else QtWidgets.QLineEdit.EchoMode.Password
        self.input_pat.setEchoMode(mode)
        self._update_eye_icon()

    def _open_thinq_portal(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://connect-pat.lgthinq.com/login"))

    def _load_initial_values(self):
        creds = credentials_backend.load_credentials()
        if creds:
            self.input_pat.setText(creds.get("pat", ""))
            self.input_country.setText(creds.get("country", "BR"))
            self.input_client_id.setText(creds.get("client_id", "windows_ac_tray_app"))

    def _step_spin(self):
        """Gera efeito de rotação no ícone de atualização durante o loading."""
        self._spin_angle = (self._spin_angle + 24) % 360
        base_pix = svg_to_pixmap(SVG_REFRESH, 52, 52, self.palette["accent_primary"])
        transform = QtGui.QTransform().rotate(self._spin_angle)
        rotated_pix = base_pix.transformed(transform, QtCore.Qt.TransformationMode.SmoothTransformation)
        self.lbl_status_icon.setPixmap(rotated_pix)

    def _start_validation(self):
        pat = self.input_pat.text().strip()
        country = self.input_country.text().strip().upper()
        client_id = self.input_client_id.text().strip()

        if not pat:
            self.input_pat.setStyleSheet(self.input_pat.styleSheet() + f"; border: 1.8px solid {self.palette['accent_red']};")
            self.input_pat.setFocus()
            return

        self.stack.setCurrentIndex(1)
        self.lbl_status_title.setText("Conectando à LG ThinQ...")
        self.lbl_status_desc.setText("Autenticando token e verificando comunicação com o ar-condicionado.")
        self.btn_status_action.hide()
        self.device_card.hide()
        self.device_combo.hide()

        self._spin_angle = 0
        self._step_spin()
        self._spin_timer.start()

        self._worker = ValidationWorker(pat, country, client_id)
        self._worker.finished_success.connect(self._on_validation_success)
        self._worker.finished_error.connect(self._on_validation_error)
        self._worker.start()

    def _on_validation_success(self, devices: list):
        self._spin_timer.stop()
        self._devices_found = devices
        self.lbl_status_icon.setPixmap(svg_to_pixmap(SVG_CHECK_CIRCLE, 56, 56, self.palette["accent_green"]))
        self.lbl_status_title.setText("Conexão Estabelecida!")

        count = len(devices)
        if count == 1:
            dev = devices[0]
            self.lbl_status_desc.setText("Aparelho identificado com sucesso e pronto para uso no painel.")
            self.lbl_device_alias.setText(dev["alias"])
            self.lbl_device_model.setText(f"Modelo: {dev['model']}")
            self.device_card.show()
            self.device_combo.hide()
        else:
            self.lbl_status_desc.setText(f"Encontramos {count} aparelhos LG na sua conta. Selecione qual controlar no painel:")
            self.device_combo.clear()
            for d in devices:
                self.device_combo.addItem(f"{d['alias']} ({d['model']})", d["deviceId"])
            self.device_combo.show()
            self.device_card.hide()

        self.btn_status_action.setText("Concluir e Abrir Painel")
        self.btn_status_action.show()

    def _on_validation_error(self, err_msg: str):
        self._spin_timer.stop()
        self.lbl_status_icon.setPixmap(svg_to_pixmap(SVG_ALERT_CIRCLE, 56, 56, self.palette["accent_red"]))
        self.lbl_status_title.setText("Falha na Autenticação")
        self.lbl_status_desc.setText(err_msg)
        self.device_card.hide()
        self.device_combo.hide()

        self.btn_status_action.setText("Voltar e Corrigir")
        self.btn_status_action.show()

    def _on_status_action_clicked(self):
        if self._devices_found:
            selected_device_id = self._devices_found[0]["deviceId"]
            if self.device_combo.isVisible() and self.device_combo.count() > 0:
                selected_device_id = self.device_combo.currentData()

            pat = self.input_pat.text().strip()
            country = self.input_country.text().strip().upper()
            client_id = self.input_client_id.text().strip()

            credentials_backend.save_credentials(
                pat=pat,
                country=country,
                client_id=client_id,
                device_id=selected_device_id
            )

            self.credentials_saved.emit({
                "pat": pat,
                "country": country,
                "client_id": client_id,
                "device_id": selected_device_id
            })
            self.accept()
        else:
            self.stack.setCurrentIndex(0)
            self.input_pat.setFocus()

    # Atalhos de Teclado
    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)

    # Permitir arrastar a janela sem borda
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self._drag_pos is not None and event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        self._drag_pos = None


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dlg = CredentialsDialog()
    dlg.show()
    sys.exit(app.exec())
