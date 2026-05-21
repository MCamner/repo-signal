"""Generate terminal-style PNG screenshots for repo-signal docs."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "docs" / "screenshots"

BG = (13, 17, 23)
TEXT = (230, 237, 243)
PROMPT = (63, 185, 80)
ACCENT = (88, 166, 255)
MUTED = (139, 148, 158)
WIDTH = 860
PADDING = 32
TITLE_H = 28
LINE_H = 19
FONT_SIZE = 13

FONT_PATH = "/System/Library/Fonts/SFNSMono.ttf"
if not Path(FONT_PATH).exists():
    FONT_PATH = "/System/Library/Fonts/Supplemental/Andale Mono.ttf"


def _font(size: int = FONT_SIZE):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()


def _header(draw: ImageDraw.Draw, width: int, title: str, font) -> None:
    draw.rectangle([0, 0, width, TITLE_H], fill=(22, 27, 34))
    for i, color in enumerate([(255, 95, 86), (255, 190, 44), (39, 201, 63)]):
        draw.ellipse([10 + i * 18, 8, 22 + i * 18, 20], fill=color)
    draw.text((70, 6), title, font=font, fill=MUTED)


def render(filename: str, command: str, output: str, title: str = "repo-signal") -> None:
    font = _font()
    lines = [("$ ", PROMPT, command)] + [("", TEXT, l) for l in output.splitlines()]
    height = TITLE_H + PADDING + len(lines) * LINE_H + PADDING
    img = Image.new("RGB", (WIDTH, height), BG)
    draw = ImageDraw.Draw(img)
    _header(draw, WIDTH, title, _font(11))
    y = TITLE_H + PADDING
    for prefix, color, text in lines:
        x = PADDING
        if prefix:
            draw.text((x, y), prefix, font=font, fill=color)
            x += int(draw.textlength(prefix, font=font))
        draw.text((x, y), text, font=font, fill=color)
        y += LINE_H
    path = OUT_DIR / filename
    img.save(path)
    print(f"  {filename}")


def run(cmd: list[str]) -> str:
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False,
            cwd=str(REPO_ROOT), timeout=60,
        )
        return (result.stdout + result.stderr).strip()
    except Exception as exc:
        return str(exc)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Generating screenshots...")

    render(
        "inspect.png",
        "repo-signal inspect .",
        run(["repo-signal", "inspect", "."]),
        title="repo-signal inspect",
    )

    render(
        "publish-checklist.png",
        "repo-signal publish-checklist .",
        run(["repo-signal", "publish-checklist", "."]),
        title="repo-signal publish-checklist",
    )

    render(
        "inspect-json.png",
        "repo-signal inspect --json . | python3 -m json.tool",
        run(["repo-signal", "inspect", "--json", "."]),
        title="repo-signal inspect --json",
    )

    print("Done.")


if __name__ == "__main__":
    main()
