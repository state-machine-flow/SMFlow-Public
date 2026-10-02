#!/usr/bin/env python3
"""Generate placeholder screenshots for the Fundamentals labs.

Reads shots.json and writes a placeholder PNG for every shot that does not yet
have a real screenshot. Backfilling is a one-step operation: overwrite the PNG
with the real capture. Nothing in the lab markdown changes.

Placeholders are tagged with a PNG metadata key, so a regeneration run will
never overwrite a real screenshot you have already dropped in.

    python make-placeholders.py            # fill in what is missing
    python make-placeholders.py --status   # report what is done and what isn't
    python make-placeholders.py --force    # regenerate placeholders (not real shots)
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, PngImagePlugin
except ImportError:
    sys.exit("Pillow is required:  pip install pillow")

HERE = Path(__file__).resolve().parent
TRAINING = HERE.parent
MANIFEST = HERE / "shots.json"

# Marker written into the PNG's text chunk. Its presence means "this is still a
# placeholder and may be regenerated"; its absence means a human put a real
# screenshot here and the script must leave it alone.
MARKER_KEY = "smflow-placeholder"

WIDTH, HEIGHT = 1600, 900

BG = (248, 249, 251)
PANEL = (255, 255, 255)
BORDER = (203, 210, 222)
ACCENT = (209, 74, 44)
INK = (31, 41, 55)
MUTED = (107, 114, 128)
FAINT = (229, 233, 240)


def load_font(names: list[str], size: int):
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


BOLD = ["seguisb.ttf", "SegoeUI-Semibold.ttf", "DejaVuSans-Bold.ttf", "Arial Bold.ttf", "arialbd.ttf"]
REG = ["segoeui.ttf", "DejaVuSans.ttf", "Arial.ttf", "arial.ttf"]
MONO = ["consola.ttf", "DejaVuSansMono.ttf", "Courier New.ttf", "cour.ttf"]


def is_placeholder(path: Path) -> bool:
    """True if the file is absent or is one of our generated placeholders."""
    if not path.exists():
        return True
    try:
        with Image.open(path) as im:
            return MARKER_KEY in (im.info or {})
    except Exception:
        # Unreadable or not a PNG — treat as real and leave it alone.
        return False


def draw_placeholder(shot: dict, lab: str, dest: Path) -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    d = ImageDraw.Draw(img)

    f_id = load_font(BOLD, 64)
    f_title = load_font(BOLD, 40)
    f_body = load_font(REG, 27)
    f_label = load_font(BOLD, 20)
    f_mono = load_font(MONO, 24)
    f_foot = load_font(REG, 21)

    # Card
    m = 54
    d.rounded_rectangle([m, m, WIDTH - m, HEIGHT - m], radius=18, fill=PANEL, outline=BORDER, width=3)

    # Accent bar
    d.rounded_rectangle([m, m, m + 12, HEIGHT - m], radius=6, fill=ACCENT)

    x = m + 60
    y = m + 52
    right = WIDTH - m - 60
    wrap_px = right - x

    def wrap(text: str, font, width_px: int) -> list[str]:
        words, lines, cur = text.split(), [], ""
        for w in words:
            trial = f"{cur} {w}".strip()
            if d.textlength(trial, font=font) <= width_px:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    # Banner
    d.text((x, y), "SCREENSHOT PLACEHOLDER", font=f_label, fill=ACCENT)
    y += 42

    # Shot id
    d.text((x, y), f"SHOT {shot['id']}", font=f_id, fill=INK)
    y += 84

    # Title
    for line in wrap(shot["title"], f_title, wrap_px):
        d.text((x, y), line, font=f_title, fill=INK)
        y += 50
    y += 18

    # Divider
    d.line([x, y, right, y], fill=FAINT, width=2)
    y += 30

    # Spec
    for line in wrap(shot["spec"], f_body, wrap_px):
        d.text((x, y), line, font=f_body, fill=INK)
        y += 38

    y += 16
    if shot.get("frame"):
        for line in wrap(f"Frame:  {shot['frame']}", f_body, wrap_px):
            d.text((x, y), line, font=f_body, fill=MUTED)
            y += 36

    # Footer
    fy = HEIGHT - m - 78
    d.line([x, fy, right, fy], fill=FAINT, width=2)
    d.text((x, fy + 20), f"{lab}/images/{shot['file']}", font=f_mono, fill=MUTED)
    note = "Replace this file with the real capture — no markdown changes needed."
    d.text((right - d.textlength(note, font=f_foot), fy + 24), note, font=f_foot, fill=MUTED)

    meta = PngImagePlugin.PngInfo()
    meta.add_text(MARKER_KEY, "1")
    meta.add_text("smflow-shot-id", shot["id"])
    meta.add_text("smflow-lab", lab)

    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "PNG", pnginfo=meta, optimize=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true", help="report progress, write nothing")
    ap.add_argument("--force", action="store_true", help="regenerate existing placeholders")
    ap.add_argument("--lab", help="limit to one lab directory name")
    args = ap.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    labs = {k: v for k, v in manifest.items() if not k.startswith("_")}
    if args.lab:
        labs = {k: v for k, v in labs.items() if k == args.lab}
        if not labs:
            return print(f"no such lab in shots.json: {args.lab}") or 1

    total = done = written = 0

    for lab, shots in labs.items():
        real = 0
        for shot in shots:
            total += 1
            dest = TRAINING / lab / "images" / shot["file"]
            placeholder = is_placeholder(dest)
            if not placeholder:
                real += 1
                done += 1
                continue
            if args.status:
                continue
            if dest.exists() and not args.force:
                continue
            draw_placeholder(shot, lab, dest)
            written += 1
        print(f"{lab}: {real}/{len(shots)} real screenshots")

    if args.status:
        pending = total - done
        print(f"\n{done}/{total} captured, {pending} pending")
    else:
        print(f"\nwrote {written} placeholder(s); {done}/{total} shots are real captures")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
