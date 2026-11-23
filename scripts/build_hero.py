"""Build assets/hero-{light,dark}.svg.

Text is converted to outlines (Pretendard, SIL OFL) so the image looks the same
on every machine. Usage: python scripts/build_hero.py <dir with Pretendard-*.otf>
Fonts: https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/public/static/
Needs: pip install fonttools
"""
import sys
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONT_DIR = Path(sys.argv[1])
OUT = Path(__file__).resolve().parent.parent / "assets"
_fonts = {}


def font(weight):
    if weight not in _fonts:
        f = TTFont(FONT_DIR / f"Pretendard-{weight}.otf")
        _fonts[weight] = (f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm)
    return _fonts[weight]


def text(s, weight, size, x=0.0, y=0.0, tracking=0.0):
    """Outline s with its baseline at (x, y). Returns (path d, ink bbox, advance)."""
    gs, cmap, upm = font(weight)
    k = size / upm
    pen, bpen = SVGPathPen(gs), BoundsPen(gs)
    cx = 0.0
    for ch in s:
        g = cmap[ord(ch)]
        t = (k, 0, 0, -k, x + cx * k, y)
        gs[g].draw(TransformPen(pen, t))
        gs[g].draw(TransformPen(bpen, t))
        cx += gs[g].width + tracking * upm
    cx -= tracking * upm
    return pen.getCommands(), bpen.bounds, cx * k


def place(s, weight, size, left, top, tracking=0.0):
    """Outline s so its ink box starts at (left, top)."""
    _, b, _ = text(s, weight, size, tracking=tracking)
    return text(s, weight, size, left - b[0], top - b[1], tracking)


THEMES = {
    "light": dict(canvas="#ECEEF2", dot="#C5CBD4", frame="#FFFFFF", ink="#15171C",
                  muted="#6A717D", sel="#0D99FF", red="#F0386B", sticky="#FFC7AE",
                  sticky_ink="#3A2018", label="#7A818C"),
    "dark": dict(canvas="#1C1D21", dot="#3A3D44", frame="#2A2C31", ink="#F2F3F5",
                 muted="#A0A6B0", sel="#3DA9FF", red="#FF5C8A", sticky="#F5B597",
                 sticky_ink="#3A2018", label="#8C929C"),
}

W = 1200
FX, FY, FW, PAD = 64, 92, 820, 64  # frame origin, width, inner padding

NAME = "Ethan"
LINE1 = "아이디어를 빠르게 동작하는 제품으로 만듭니다."
LINE2 = "풀스택 웹 개발자. 요구 정의부터 인프라 셋업까지 끝까지 완주합니다."


def build(c):
    # frame content, laid out top-down from ink boxes
    name_d, nb, _ = place(NAME, "ExtraBold", 172, FX + PAD, FY + PAD, tracking=-0.035)
    sub_d, sb, _ = place(LINE1, "SemiBold", 34, FX + PAD, nb[3] + 92)
    meta_d, mb, _ = place(LINE2, "Regular", 22, FX + PAD, sb[3] + 22)
    fh = mb[3] + PAD - FY
    H = round(FY + fh + 64)

    # frame name, as a design tool shows it above the frame
    lab_d, _, _ = text("socialofpeach.com/about", "Medium", 19, FX + 26, FY - 14)
    icon = (f'<path d="M{FX+3} {FY-29}v16M{FX+13} {FY-29}v16M{FX-1} {FY-25}h18M{FX-1} {FY-17}h18" '
            f'stroke="{c["label"]}" stroke-width="1.6" fill="none"/>')

    # selection box around the name
    m = 10
    sx0, sy0, sx1, sy1 = nb[0] - m, nb[1] - m, nb[2] + m, nb[3] + m
    handles = "".join(
        f'<rect x="{hx-5:.1f}" y="{hy-5:.1f}" width="10" height="10" fill="{c["frame"]}" '
        f'stroke="{c["sel"]}" stroke-width="2"/>'
        for hx, hy in ((sx0, sy0), (sx1, sy0), (sx0, sy1), (sx1, sy1)))
    dim = f"{round(nb[2]-nb[0])} × {round(nb[3]-nb[1])}"
    _, db, dw = text(dim, "SemiBold", 18)
    pw, ph = dw + 20, 28
    px, py = (sx0 + sx1) / 2 - pw / 2, sy1 + 9
    dim_d, _, _ = place(dim, "SemiBold", 18, px + 10, py + (ph - (db[3] - db[1])) / 2)

    # redlines: the name's left and top padding inside the frame
    def chip(val, cx, cy):
        _, b, w = text(val, "SemiBold", 17)
        d, _, _ = place(val, "SemiBold", 17, cx - w / 2, cy - (b[3] - b[1]) / 2)
        return (f'<rect x="{cx-w/2-7:.1f}" y="{cy-13:.1f}" width="{w+14:.1f}" height="26" rx="4" '
                f'fill="{c["red"]}"/><path d="{d}" fill="#fff"/>')

    midy = (nb[1] + nb[3]) / 2
    tx = nb[0] + 96
    red = (f'<path d="M{FX} {midy:.1f}H{nb[0]:.1f}M{FX} {midy-6:.1f}v12M{nb[0]:.1f} {midy-6:.1f}v12'
           f'M{tx:.1f} {FY}V{nb[1]:.1f}M{tx-6:.1f} {FY}h12M{tx-6:.1f} {nb[1]:.1f}h12" '
           f'stroke="{c["red"]}" stroke-width="1.5" fill="none"/>'
           + chip(str(round(nb[0] - FX)), (FX + nb[0]) / 2, midy - 26)
           + chip(str(round(nb[1] - FY)), tx + 30, (FY + nb[1]) / 2))

    # multiplayer cursor with a name tag; rests on the bottom-right handle
    tag_d, _, tw = text("Ethan", "SemiBold", 17, 28, 47)
    cur = (f'<path d="M0 0L0 26L7.5 19.5L12.5 31L17 29L12 17.8L22 17.8Z" fill="{c["sel"]}" '
           f'stroke="#fff" stroke-width="1.8" stroke-linejoin="round"/>'
           f'<rect x="16" y="29" width="{tw+24:.1f}" height="26" rx="13" fill="{c["sel"]}"/>'
           f'<path d="{tag_d}" fill="#fff"/>')

    # sticky note
    l1, _, _ = text("ethan", "Bold", 40, 30, 82)
    l2, _, _ = text("was right", "Bold", 40, 30, 130)
    l3, _, _ = text("블로그 소개 맨 아래에서", "Medium", 18, 30, 196)
    sticky = (f'<g transform="translate(934 {FY + fh / 2 - 125:.1f}) rotate(3)">'
              f'<rect width="220" height="230" fill="{c["sticky"]}"/>'
              f'<path d="{l1}{l2}" fill="{c["sticky_ink"]}"/>'
              f'<path d="{l3}" fill="{c["sticky_ink"]}" fill-opacity=".62"/></g>')

    # one motion moment: cursor flies to the top-left corner, then drags the selection open
    dx0, dy0 = sx0 - sx1, sy0 - sy1
    ease = "cubic-bezier(.3,.7,.3,1)"
    style = (
        "<style>"
        f".cur{{animation:cur 2s {ease} .2s both}}"
        f".sel{{transform-origin:{sx0:.1f}px {sy0:.1f}px;animation:sel 2s {ease} .2s both}}"
        ".late{animation:fade .35s ease-out 2.1s both}"
        ".later{animation:fade .35s ease-out 2.45s both}"
        "@keyframes cur{0%{transform:translate(300px,210px);opacity:0}12%{opacity:1}"
        f"45%,52%{{transform:translate({dx0:.1f}px,{dy0:.1f}px)}}100%{{transform:none}}}}"
        "@keyframes sel{0%,52%{transform:scale(0);opacity:0}53%{opacity:1}100%{transform:none}}"
        "@keyframes fade{from{opacity:0}}"
        "@media (prefers-reduced-motion:reduce){.cur,.sel,.late,.later{animation:none}}"
        "</style>")

    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="{NAME}. {LINE1}">',
        style,
        f'<defs><pattern id="g" width="24" height="24" patternUnits="userSpaceOnUse">'
        f'<circle cx="12" cy="12" r="1.3" fill="{c["dot"]}"/></pattern></defs>',
        f'<rect width="{W}" height="{H}" rx="14" fill="{c["canvas"]}"/>'
        f'<rect width="{W}" height="{H}" rx="14" fill="url(#g)"/>',
        icon + f'<path d="{lab_d}" fill="{c["label"]}"/>',
        f'<rect x="{FX}" y="{FY}" width="{FW}" height="{fh:.1f}" fill="{c["frame"]}"/>',
        f'<path d="{name_d}" fill="{c["ink"]}"/>',
        f'<path d="{sub_d}" fill="{c["ink"]}"/>',
        f'<path d="{meta_d}" fill="{c["muted"]}"/>',
        sticky,
        f'<g class="later">{red}</g>',
        f'<rect class="sel" x="{sx0:.1f}" y="{sy0:.1f}" width="{sx1-sx0:.1f}" height="{sy1-sy0:.1f}" '
        f'fill="none" stroke="{c["sel"]}" stroke-width="2"/>',
        f'<g class="late">{handles}<rect x="{px:.1f}" y="{py:.1f}" width="{pw:.1f}" height="{ph}" '
        f'rx="5" fill="{c["sel"]}"/><path d="{dim_d}" fill="#fff"/></g>',
        f'<g transform="translate({sx1:.1f} {sy1:.1f})"><g class="cur">{cur}</g></g>',
        "</svg>",
    ]), FY + fh


if __name__ == "__main__":
    for theme, colors in THEMES.items():
        svg, bottom = build(colors)
        (OUT / f"hero-{theme}.svg").write_text(svg, encoding="utf-8")
        print(theme, f"{len(svg) // 1024} KB, frame bottom {round(bottom)}")
