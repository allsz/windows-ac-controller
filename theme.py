"""
theme.py - Fonte unica de temas (paletas) e resolucao de tema para o painel e o dialogo de credenciais.

Cada paleta contem as chaves usadas pelo painel e pelo dialogo (campos, acentos, botoes secundarios).
Para ajustar uma cor, edite apenas este arquivo.
"""

from typing import Optional

from PySide6 import QtCore

from common import is_windows_dark_mode

THEME_MODES = ("system", "light", "dark", "black")

PALETTES = {
    "dark": {
        "bg_color": "#0D0E12",
        "card_bg": "#191B22",
        "card_hover": "#22252F",
        "card_active": "#2C303E",
        "border_color": "rgba(255, 255, 255, 0.08)",
        "border_hover": "rgba(255, 255, 255, 0.16)",
        "border_active": "rgba(255, 255, 255, 0.28)",
        "panel_border": "rgba(255, 255, 255, 0.12)",
        "text_primary": "#FFFFFF",
        "text_secondary": "#94A3B8",
        "text_muted": "#64748B",
        "icon_color": "#FFFFFF",
        "power_color": "#D4D0C7",
        "power_off_color": "#64748B",
        "power_bg": "rgba(255, 255, 255, 0.08)",
        "power_hover": "rgba(255, 255, 255, 0.14)",
        "power_pressed": "rgba(255, 255, 255, 0.04)",
        "stepper_color": "#FFFFFF",
        "slider_groove": "#181A22",
        "slider_groove_border": "rgba(255, 255, 255, 0.06)",
        "drawer_bg": "#13151C",
        "drawer_border": "rgba(255, 255, 255, 0.08)",
        "opt_bg": "#181A22",
        "opt_bg_active": "#272B38",
        "opt_bg_hover": "#2F3444",
        "opt_color": "#E2E8F0",
        "opt_color_active": "#38BDF8",
        "opt_border": "rgba(255, 255, 255, 0.08)",
        "opt_border_active": "rgba(56, 189, 248, 0.5)",
        "menu_bg": "#181920",
        "menu_color": "#FFFFFF",
        "menu_border": "rgba(255, 255, 255, 0.12)",
        "menu_item_hover_bg": "#272A36",
        "menu_item_hover_color": "#38BDF8",
        "menu_separator": "rgba(255, 255, 255, 0.08)",
        "settings_btn_hover": "#22252F",
        # --- Chaves do dialogo de credenciais ---
        "input_bg": "#111218",
        "input_border": "rgba(255, 255, 255, 0.12)",
        "input_border_focus": "#38BDF8",
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
        "border_color": "rgba(255, 255, 255, 0.10)",
        "border_hover": "rgba(255, 255, 255, 0.20)",
        "border_active": "rgba(255, 255, 255, 0.32)",
        "panel_border": "rgba(255, 255, 255, 0.14)",
        "text_primary": "#FFFFFF",
        "text_secondary": "#9E9EAF",
        "text_muted": "#6E6E82",
        "icon_color": "#FFFFFF",
        "power_color": "#D4D0C7",
        "power_off_color": "#6E6E82",
        "power_bg": "rgba(255, 255, 255, 0.10)",
        "power_hover": "rgba(255, 255, 255, 0.16)",
        "power_pressed": "rgba(255, 255, 255, 0.06)",
        "stepper_color": "#FFFFFF",
        "slider_groove": "#0C0D12",
        "slider_groove_border": "rgba(255, 255, 255, 0.08)",
        "drawer_bg": "#0A0B0E",
        "drawer_border": "rgba(255, 255, 255, 0.10)",
        "opt_bg": "#111218",
        "opt_bg_active": "#222533",
        "opt_bg_hover": "#2A2D3D",
        "opt_color": "#E2E8F0",
        "opt_color_active": "#38BDF8",
        "opt_border": "rgba(255, 255, 255, 0.10)",
        "opt_border_active": "rgba(56, 189, 248, 0.55)",
        "menu_bg": "#101014",
        "menu_color": "#FFFFFF",
        "menu_border": "rgba(255, 255, 255, 0.14)",
        "menu_item_hover_bg": "#222533",
        "menu_item_hover_color": "#38BDF8",
        "menu_separator": "rgba(255, 255, 255, 0.10)",
        "settings_btn_hover": "#17171E",
        # --- Chaves do dialogo de credenciais ---
        "input_bg": "#0A0B0E",
        "input_border": "rgba(255, 255, 255, 0.14)",
        "input_border_focus": "#38BDF8",
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
        "card_hover": "#F1F3F5",
        "card_active": "#E9ECEF",
        "border_color": "rgba(0, 0, 0, 0.08)",
        "border_hover": "rgba(0, 0, 0, 0.16)",
        "border_active": "rgba(0, 0, 0, 0.28)",
        "panel_border": "rgba(0, 0, 0, 0.12)",
        "text_primary": "#0F172A",
        "text_secondary": "#475569",
        "text_muted": "#64748B",
        "icon_color": "#0F172A",
        "power_color": "#D97706",
        "power_off_color": "#94A3B8",
        "power_bg": "rgba(0, 0, 0, 0.06)",
        "power_hover": "rgba(0, 0, 0, 0.10)",
        "power_pressed": "rgba(0, 0, 0, 0.04)",
        "stepper_color": "#0F172A",
        "slider_groove": "#E2E8F0",
        "slider_groove_border": "rgba(0, 0, 0, 0.06)",
        "drawer_bg": "#F1F5F9",
        "drawer_border": "rgba(0, 0, 0, 0.08)",
        "opt_bg": "#FFFFFF",
        "opt_bg_active": "#E0F2FE",
        "opt_bg_hover": "#F8FAFC",
        "opt_color": "#1E293B",
        "opt_color_active": "#0284C7",
        "opt_border": "rgba(0, 0, 0, 0.08)",
        "opt_border_active": "rgba(2, 132, 199, 0.6)",
        "menu_bg": "#FFFFFF",
        "menu_color": "#0F172A",
        "menu_border": "rgba(0, 0, 0, 0.12)",
        "menu_item_hover_bg": "#F1F5F9",
        "menu_item_hover_color": "#0284C7",
        "menu_separator": "rgba(0, 0, 0, 0.08)",
        "settings_btn_hover": "#E2E8F0",
        # --- Chaves do dialogo de credenciais ---
        "input_bg": "#FFFFFF",
        "input_border": "rgba(0, 0, 0, 0.15)",
        "input_border_focus": "#0284C7",
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


def normalize_mode(mode: Optional[str]) -> str:
    """Valida o modo de tema ('system', 'light', 'dark', 'black'); invalido vira 'system'."""
    return mode if mode in THEME_MODES else "system"


def resolve_theme_name(mode: Optional[str]) -> str:
    """Converte o modo configurado em um tema concreto: 'light', 'dark' ou 'black'."""
    mode = normalize_mode(mode)
    if mode == "system":
        return "dark" if is_windows_dark_mode() else "light"
    return mode


def get_palette(name: str) -> dict:
    return PALETTES.get(name, PALETTES["dark"])


def resolve_theme_palette(mode: Optional[str] = None) -> tuple[str, dict]:
    """Retorna (tema concreto, copia da paleta). Sem 'mode', le a preferencia salva."""
    if mode is None:
        mode = str(QtCore.QSettings("WTC LG", "Preferences").value("theme", "system"))
    name = resolve_theme_name(mode)
    return name, dict(get_palette(name))
