"""Ludizm logo: 本 (ben, root / origin / foundation), with the top of the vertical stroke as a green bud.

Run inside logo/:  python3 make_logo.py .
Writes one folder per version, each with the .svg and two .png (2048 and 512 px, transparent).
"""
import sys
from pathlib import Path

out = Path(sys.argv[1])
BLUE, WHITE, BLACK = "#3498DB", "#FFFFFF", "#000000"
BUD_ON_BLUE, BUD_ON_WHITE = "#9BE36B", "#4CAF50"


def ben(stroke, bud):
    """本 in a 100 x 100 box. Strokes 8.5 wide, round ends."""
    return f'''<g fill="none" stroke-linecap="round" stroke-width="8.5">
    <path d="M50 14 V38" stroke="{bud}"/>
    <path d="M50 38 V87" stroke="{stroke}"/>
    <path d="M18 38 H82" stroke="{stroke}"/>
    <path d="M47 42 L21 71" stroke="{stroke}"/>
    <path d="M53 42 L79 71" stroke="{stroke}"/>
    <path d="M36 72 H64" stroke="{stroke}"/>
  </g>'''


def word(color):
    """LUDIZM as strokes, same round ends as 本. Drawn at cap height 200, scaled to 42."""
    return f'''<g transform="translate(118 29) scale(0.21)" fill="none" stroke="{color}" stroke-width="40" stroke-linecap="round" stroke-linejoin="round">
    <path d="M0 0 V200 H115"/>
    <path d="M195 0 V130 A65 65 0 0 0 325 130 V0"/>
    <path d="M405 0 H455 A100 100 0 0 1 455 200 H405 Z"/>
    <path d="M635 0 V200"/>
    <path d="M715 0 H845 L715 200 H845"/>
    <path d="M925 200 V0 L1005 125 L1085 0 V200"/>
  </g>'''


def svg(vb, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="Ludizm">\n'
            f'  <title>Ludizm</title>\n  {body}\n</svg>\n')


# One folder per version: <folder>/<name>.svg + <name>_2048.png + <name>_512.png
VERSIONS = {
    "01_icon_black": ("ludizm_icon_black", svg("0 0 100 100",
        f'<rect width="100" height="100" rx="22" fill="{BLACK}"/>\n  ' + ben(WHITE, BUD_ON_BLUE))),
    "02_horizontal_light-bg": ("ludizm_horizontal_light-bg", svg("12 8 344 85",
        ben(BLUE, BUD_ON_WHITE) + "\n  " + word(BLUE))),
    "03_horizontal_black": ("ludizm_horizontal_black", svg("0 0 370 100",
        f'<rect width="370" height="100" rx="22" fill="{BLACK}"/>\n  ' + ben(WHITE, BUD_ON_BLUE) + "\n  " + word(WHITE))),
    "04_horizontal_dark-bg": ("ludizm_horizontal_dark-bg", svg("12 8 344 85",
        ben(WHITE, BUD_ON_BLUE) + "\n  " + word(WHITE))),
    "05_mark_light-bg": ("ludizm_mark_light-bg", svg("12 8 76 85", ben(BLUE, BUD_ON_WHITE))),
    "06_mark_dark-bg": ("ludizm_mark_dark-bg", svg("12 8 76 85", ben(WHITE, BUD_ON_BLUE))),
}

if __name__ == "__main__":
    import subprocess
    for folder, (name, s) in VERSIONS.items():
        d = out / folder
        d.mkdir(exist_ok=True)
        src = d / f"{name}.svg"
        src.write_text(s, encoding="utf-8")
        for px in (2048, 512):
            # macOS sips keeps the transparent background
            subprocess.run(["sips", "-s", "format", "png", "-Z", str(px), str(src),
                            "--out", str(d / f"{name}_{px}.png")], check=True, capture_output=True)
        print(f"{folder}/  {name}.svg  {name}_2048.png  {name}_512.png")
