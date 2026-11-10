"""
ac_unit.py — AC split, vista frontal, inspirado em split de parede realista.

    from ac_unit import render_ac_svg
    svg = render_ac_svg(on=True, mode="cool", fan="auto", louver=35, swing=False, temp=21)

Parâmetros:
    on      bool   Ligado/desligado (desligado = aleta fechada, sem ar, display apagado)
    mode    str    "cool" | "heat" | "dry" | "fan" | "auto"  (cor do ar e dos tracinhos de status)
    fan     str    "auto" | "low" | "mid" | "high"           (velocidade da animação)
    louver  float  Abertura da aleta em graus, 0 (fechada) a 90 (aberta p/ baixo)
    swing   bool   Aleta oscilando continuamente
    temp    int    Temperatura no display do aparelho (None = esconde)
    phase   float  Fase de animação contínua (para renderização dinâmica em Qt / PySide6)
    uid     str    Prefixo de ids/classes (use um diferente para cada AC na mesma página)
"""

from __future__ import annotations
import math

MODE_COLORS = {
    "cool": "#7dd3fc",
    "heat": "#fb923c",
    "dry": "#5eead4",
    "fan": "#cbd5e1",
    "auto": "#a5b4fc",
}
FAN_PERIOD = {"low": 3.2, "mid": 2.2, "high": 1.4, "auto": 2.2}


# Cor dos números: versão um pouco mais escura de cada modo, para ler bem sobre o corpo branco.
DIGIT_COLORS = {
    "cool": "#4aa8d8",
    "heat": "#e8812f",
    "dry": "#2fb8a4",
    "fan": "#8e99aa",
    "auto": "#7c86d8",
}

# Segmentos de um display de 7 segmentos: a=topo, b=sup. dir., c=inf. dir., d=base, e=inf. esq., f=sup. esq., g=meio
_SEGS = {
    "0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc",
    "5": "afgcd", "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg",
}


def _digit(ch: str, x: float, y: float, w: float, h: float, t: float) -> str:
    """Um dígito de 7 segmentos arredondado, canto superior esquerdo em (x, y)."""
    mid = (h - t) / 2
    vh = mid - 0.4 * t
    r = t / 2
    geo = {
        "a": (0.6 * t, 0, w - 1.2 * t, t),
        "g": (0.6 * t, mid, w - 1.2 * t, t),
        "d": (0.6 * t, h - t, w - 1.2 * t, t),
        "f": (0, 0.7 * t, t, vh),
        "b": (w - t, 0.7 * t, t, vh),
        "e": (0, mid + 0.7 * t, t, vh),
        "c": (w - t, mid + 0.7 * t, t, vh),
    }
    return "".join(
        f'<rect x="{x + gx:.2f}" y="{y + gy:.2f}" width="{gw:.2f}" height="{gh:.2f}" rx="{r:.2f}"/>'
        for seg in _SEGS.get(ch, "")
        for gx, gy, gw, gh in [geo[seg]]
    )


def _temp_digits(temp: int, fill: str, uid: str, dark_body: bool = False) -> str:
    """Só o número (sem fundo), no canto superior direito, estilo display de 7 segmentos."""
    text = str(abs(temp))[-2:]
    w, h, t, gap = 10.5, 19, 2.5, 3.6
    total = len(text) * w + (len(text) - 1) * gap
    x_right = 360                      # borda direita do número
    x0 = x_right - total
    y0 = 39
    shapes = "".join(_digit(ch, x0 + i * (w + gap), y0, w, h, t) for i, ch in enumerate(text))
    ring = (f'<circle cx="{x_right + 4.6:.1f}" cy="{y0 + 2.6}" r="1.9" fill="none" '
            f'stroke="{{c}}" stroke-width="1.3"/>')
    sign = ""
    if temp < 0:
        sign = f'<rect x="{x0 - 6.5:.1f}" y="{y0 + (h - t) / 2:.1f}" width="4.5" height="{t}" rx="{t/2}"/>'
    glyph = shapes + sign
    
    if dark_body:
        # Relevo escuro com leve glow para modelo preto
        shadow_layer = f'<g fill="#000000" opacity=".75" transform="translate(.8 .9)">{glyph}{ring.format(c="#000000")}</g>'
    else:
        # Relevo branco para modelo branco
        shadow_layer = f'<g fill="#ffffff" opacity=".95" transform="translate(.8 .9)">{glyph}{ring.format(c="#ffffff")}</g>'

    return (
        f'<g transform="skewX(-5) translate({y0 * 0.0875:.2f} 0)">'
        f'{shadow_layer}'
        f'<g fill="{fill}" class="{uid}-num">{glyph}{ring.format(c=fill)}</g>'
        f'</g>'
    )


def render_ac_svg(
    on: bool = True,
    mode: str = "cool",
    fan: str = "auto",
    louver: float = 35,
    swing: bool = False,
    temp: int | None = 21,
    phase: float | None = None,
    uid: str = "ac",
    ac_color: str = "white",
    flow_progress: float = 1.0,
) -> str:
    mode_key = (mode or "cool").lower()
    color = MODE_COLORS.get(mode_key, MODE_COLORS["cool"])
    digit_color = DIGIT_COLORS.get(mode_key, DIGIT_COLORS["cool"])
    period = FAN_PERIOD.get((fan or "auto").lower(), FAN_PERIOD["auto"])
    is_black = (ac_color.lower() == "black")

    if phase is not None:
        if swing and on:
            current_louver = 15.0 + 65.0 * (0.5 + 0.5 * math.sin(phase * 1.5))
        else:
            current_louver = max(0.0, min(90.0, float(louver if on else 0)))
    else:
        current_louver = max(0.0, min(90.0, float(louver if on else 0)))

    progress = max(0.0, min(1.0, float(flow_progress)))
    flowing = progress > 0.01 and current_louver > 1
    base_reach = 62 + current_louver * 0.8
    reach = base_reach * progress
    spread = (0.05 + (90 - current_louver) / 90 * 0.32) * progress
    CX = 200

    rad = math.radians(current_louver)
    scale_y = max(0.12, math.cos(rad))
    flap_cy = 107.0

    # ---------------------------------------------------------------- ar
    air = ""
    if flowing:
        def veil_path(xl, xr):
            return (f"M{xl} 0 L{xr} 0 L{xr + (xr-CX)*spread:.1f} {reach:.1f} "
                    f"L{xl + (xl-CX)*spread:.1f} {reach:.1f} Z")

        n = 10
        x_a, x_b = 56, 344
        soft = []

        if phase is not None:
            flow_offset = (phase * 60) % 130
            breath = (0.65 + 0.35 * (0.5 + 0.5 * math.sin(phase * 2.0))) * progress
            sway_x = math.sin(phase * 1.5) * 4.0 if (swing and on) else 0.0
            for i in range(n):
                x0 = x_a + i * (x_b - x_a) / (n - 1)
                xe = x0 + (x0 - CX) * spread
                d = f"M{x0:.1f} 0 L{xe:.1f} {reach:.1f}"
                line_offset = -((i * 13) + flow_offset)
                op = (0.42 if (i % 2) else 0.28) * breath
                soft.append(
                    f'<path class="{uid}-soft" d="{d}" fill="none" stroke="{color}" stroke-width="12" '
                    f'stroke-linecap="round" stroke-dasharray="35 30" '
                    f'stroke-dashoffset="{line_offset:.1f}" opacity="{op:.2f}"/>'
                )
            air = f"""
<g class="{uid}-air" transform="translate({sway_x:.1f} 114)">
  <path class="{uid}-veil" d="{veil_path(48, CX-2)}" fill="url(#{uid}-veilg)" opacity="{breath:.2f}"/>
  <path class="{uid}-veil" d="{veil_path(CX+2, 352)}" fill="url(#{uid}-veilg)" opacity="{breath:.2f}"/>
  {''.join(soft)}
</g>"""
        else:
            for i in range(n):
                x0 = x_a + i * (x_b - x_a) / (n - 1)
                xe = x0 + (x0 - CX) * spread
                d = f"M{x0:.1f} 0 L{xe:.1f} {reach:.1f}"
                delay = -((i * 0.61) % period)
                alt = " alt" if i % 2 else ""
                soft.append(
                    f'<path class="{uid}-soft{alt}" d="{d}" fill="none" stroke="{color}" '
                    f'stroke-width="15" stroke-linecap="butt" stroke-dasharray="80 50" '
                    f'style="animation-delay:{delay:.2f}s"/>'
                )
            air = f"""
<g class="{uid}-air" transform="translate(0 114)">
  <path class="{uid}-veil" d="{veil_path(48, CX-2)}" fill="url(#{uid}-veilg)"/>
  <path class="{uid}-veil" d="{veil_path(CX+2, 352)}" fill="url(#{uid}-veilg)"/>
  {''.join(soft)}
</g>"""

    # -------------------------------------------------------- aparelho
    if phase is not None:
        tick_pulse = 0.5 + 0.5 * (0.5 + 0.5 * math.sin(phase * 2.5))
        default_tick = "#4B5563" if is_black else "#bfc5cf"
        tick_color = color if on else default_tick
        tick_op = f'opacity="{tick_pulse:.2f}"' if on else 'opacity="0.8"'
        ticks = "".join(
            f'<rect x="{x}" y="{y}" width="1.5" height="{h}" rx=".75" fill="{tick_color}" {tick_op} '
            f'transform="rotate({r} {x+.75} {y+h})"/>'
            for x, y, h, r in ((196.3, 83.5, 4.5, -22), (199.25, 82, 6, 0), (202.2, 83.5, 4.5, 22))
        )
    else:
        default_tick = "#4B5563" if is_black else "#bfc5cf"
        tick_color = color if on else default_tick
        tick_cls = f' class="{uid}-tick"' if on else ""
        ticks = "".join(
            f'<rect x="{x}" y="{y}" width="1.5" height="{h}" rx=".75" fill="{tick_color}"{tick_cls} '
            f'transform="rotate({r} {x+.75} {y+h})"/>'
            for x, y, h, r in ((196.3, 83.5, 4.5, -22), (199.25, 82, 6, 0), (202.2, 83.5, 4.5, 22))
        )

    screen = ""
    if on and temp is not None:
        screen = _temp_digits(int(temp), digit_color, uid, dark_body=is_black)

    seg_color = "#333946" if is_black else "#bcc2cc"
    seg_mid_color = "#1F232B" if is_black else "#aab1bd"
    seg = "".join(
        f'<rect x="{48 + k*(304/6):.1f}" y="103.5" width=".9" height="7" fill="{seg_color}"/>'
        for k in range(1, 6) if k != 3
    )
    seg += f'<rect x="{CX-.9}" y="103.5" width="1.8" height="7" fill="{seg_mid_color}"/>'

    swing_cls = f" {uid}-swing" if (swing and on and phase is None) else ""
    reduced = "@media (prefers-reduced-motion: reduce){.%s-soft,.%s-veil,.%s-flap,.%s-tick,.%s-air{animation:none!important}}" % ((uid,) * 5)

    css = f"""
.{uid}-root{{--louver:{current_louver:.0f}deg;--air:{color};--period:{period}s}}
.{uid}-flap{{transform-box:fill-box;transform-origin:50% 50%;
  transform:scaleY(max(.1,cos(var(--louver))));
  transition:transform .9s cubic-bezier(.4,0,.2,1)}}
.{uid}-flap.{uid}-swing{{animation:{uid}-sw 4.2s ease-in-out infinite alternate}}
@keyframes {uid}-sw{{from{{transform:scaleY(.94)}}to{{transform:scaleY(.14)}}}}
.{uid}-soft{{fill:none;stroke:{color};stroke-width:15;stroke-linecap:butt;
  stroke-dasharray:80 50;opacity:.30;animation:{uid}-flow calc(var(--period)*1.5) linear infinite}}
.{uid}-veil{{animation:{uid}-breath calc(var(--period)*2) ease-in-out infinite alternate}}
.{uid}-air{{{'animation:' + uid + '-swayx 4.2s ease-in-out infinite alternate' if (swing and phase is None) else ''}}}
.{uid}-tick{{animation:{uid}-pulse 2.6s ease-in-out infinite}}
.{uid}-soft.alt{{opacity:.46}}
@keyframes {uid}-flow{{to{{stroke-dashoffset:-130}}}}
@keyframes {uid}-breath{{from{{opacity:.5}}to{{opacity:1}}}}
@keyframes {uid}-swayx{{from{{transform:translate(-4px,114px)}}to{{transform:translate(4px,114px)}}}}
@keyframes {uid}-pulse{{50%{{opacity:.4}}}}
{reduced}
"""

    if phase is not None:
        flap_transform = f'transform="translate(0 {flap_cy * (1 - scale_y):.2f}) scale(1 {scale_y:.3f})"'
    else:
        flap_transform = ""

    # Gradientes dinâmicos conforme a cor do ar-condicionado (Branco vs Preto Artcool)
    if is_black:
        body_grad = f"""<stop offset="0" stop-color="#26282E"/><stop offset="1" stop-color="#18191E"/>"""
        lip_grad = f"""<stop offset="0" stop-color="#1E2026"/><stop offset="1" stop-color="#141518"/>"""
        line_grad = f"""<stop offset="0" stop-color="#3F434D" stop-opacity="0"/><stop offset=".5" stop-color="#3F434D"/><stop offset="1" stop-color="#3F434D" stop-opacity="0"/>"""
        flap_grad = f"""<stop offset="0" stop-color="#2D3038"/><stop offset="1" stop-color="#1A1C22"/>"""
        edge_stroke = "#3D414D"
        edge_opacity = ".5"
    else:
        body_grad = f"""<stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#eef0f4"/>"""
        lip_grad = f"""<stop offset="0" stop-color="#dfe2e8"/><stop offset="1" stop-color="#c9cdd6"/>"""
        line_grad = f"""<stop offset="0" stop-color="#cfd4dc" stop-opacity="0"/><stop offset=".5" stop-color="#cfd4dc"/><stop offset="1" stop-color="#cfd4dc" stop-opacity="0"/>"""
        flap_grad = f"""<stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#e1e4ea"/>"""
        edge_stroke = "#fff"
        edge_opacity = ".85"

    return f"""<svg class="{uid}-root" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 250"
 role="img" aria-label="Ar-condicionado {'ligado' if on else 'desligado'}">
<style>{css}</style>
<defs>
  <linearGradient id="{uid}-body" x1="0" y1="0" x2="0" y2="1">
    {body_grad}
  </linearGradient>
  <linearGradient id="{uid}-lip" x1="0" y1="0" x2="0" y2="1">
    {lip_grad}
  </linearGradient>
  <linearGradient id="{uid}-line" x1="0" y1="0" x2="1" y2="0">
    {line_grad}
  </linearGradient>
  <linearGradient id="{uid}-slot" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#07080B"/><stop offset="1" stop-color="#12141A"/>
  </linearGradient>
  <linearGradient id="{uid}-flapg" x1="0" y1="0" x2="0" y2="1">
    {flap_grad}
  </linearGradient>
  <linearGradient id="{uid}-veilg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{color}" stop-opacity=".32"/><stop offset="1" stop-color="{color}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="{uid}-shadow" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#000000" stop-opacity="0.30"/>
    <stop offset="1" stop-color="#000000" stop-opacity="0"/>
  </linearGradient>
</defs>

<!-- soft drop shadow -->
<rect x="22" y="24" width="356" height="96" rx="20" fill="url(#{uid}-shadow)"/>

<!-- corpo -->
<g>
  <path d="M30 94 H370 V104 Q370 116 358 116 H42 Q30 116 30 104 Z" fill="url(#{uid}-lip)"/>
  <rect x="20" y="14" width="360" height="86" rx="18" fill="url(#{uid}-body)"/>
</g>
<rect x="20.5" y="14.5" width="359" height="85" rx="17.5" fill="none" stroke="{edge_stroke}" stroke-opacity="{edge_opacity}"/>
<rect x="56" y="76.5" width="288" height="1.2" fill="url(#{uid}-line)"/>
{ticks}

<!-- saída de ar -->
<rect x="46" y="102" width="308" height="10" rx="5" fill="url(#{uid}-slot)"/>
<g class="{uid}-flap{swing_cls}" {flap_transform}>
  <rect x="48" y="103.5" width="304" height="7" rx="3.5" fill="url(#{uid}-flapg)"/>
  {seg}
</g>
{screen}
{air}
</svg>"""


if __name__ == "__main__":
    cards = [
        ("Cool · 35° · Auto", dict(mode="cool", louver=35, fan="auto", uid="a1", temp=21)),
        ("Heat · 75° · High", dict(mode="heat", louver=75, fan="high", uid="a2", temp=24)),
        ("Fan · swing · Low", dict(mode="fan", louver=50, fan="low", swing=True, uid="a3", temp=None)),
        ("Off", dict(on=False, uid="a4")),
    ]
    html = "<body style='margin:0;background:#0b0c10;color:#9aa1af;font:13px system-ui;display:grid;grid-template-columns:repeat(2,1fr);gap:8px;padding:16px'>"
    for label, kw in cards:
        html += f"<div style='background:#12141a;border-radius:16px;padding:12px;text-align:center'>{render_ac_svg(**kw)}<div>{label}</div></div>"
    with open("ac_preview.html", "w", encoding="utf-8") as f:
        f.write(html)
    with open("ac_cool.svg", "w", encoding="utf-8") as f:
        f.write(render_ac_svg(uid="ac"))
    print("ok")
