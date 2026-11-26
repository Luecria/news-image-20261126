#!/usr/bin/env python3
"""Render the 26 Nov 2026 world-news front page (1024x1024 PNG, <=1 MiB).

Deterministic: same stories.json -> identical bytes. No network, no clock,
no randomness at run time. Run twice and compare sha256 to verify.
"""
import glob
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "stories.json").read_text(encoding="utf-8"))
OUT = ROOT / "entry.png"

W, H = 1024, 1024
MARGIN = 30
FRAME = 14
PAPER = (251, 248, 241)
INK = (17, 17, 17)
RED = (185, 28, 28)
GRAY = (107, 114, 128)
RULE = (17, 17, 17)
LIGHT = (205, 200, 188)

COL_GAP = 22
COL_W = (W - 2 * MARGIN - 2 * COL_GAP) // 3
FOOTER_H = 30


def find_font(patterns):
    for pat in patterns:
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[0]
    raise FileNotFoundError(patterns)


SERIF_B = find_font(["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"])
SANS = find_font(["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"])
SANS_B = find_font(["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"])


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_center(draw, y, text, fnt, fill=INK):
    w = draw.textlength(text, font=fnt)
    draw.text(((W - w) / 2, y), text, font=fnt, fill=fill)


def section_stories(name):
    for sec in DATA["sections"]:
        if sec["name"] == name:
            return sec["stories"]
    return []


COLUMNS = [
    ["NORTH AMERICA", "EUROPE"],
    ["MIDDLE EAST", "AFRICA"],
    ["LATIN AMERICA", "ASIA-PACIFIC", "WORLD"],
]

LEAD_H = 154  # measured: kicker 16 + claim 18 + headline 3x23 + deck 2x16 + source 14


def story_block_h(draw, st, fnt, lh):
    """Pixel height of one story block, exactly as draw_story renders it."""
    prefix = "[CLAIM] " if st["claim"] else ""
    lines = wrap(draw, prefix + st["headline"], fnt, COL_W)[:2]
    h = len(lines) * lh
    src_txt = "— " + st["source"]
    last_w = draw.textlength(lines[-1], font=fnt) if lines else 0
    sw = draw.textlength(src_txt, font=F(SANS, 10))
    if last_w + 6 + sw > COL_W:
        h += int(10 * 1.3)
    return h + 4


def columns_height(draw, story_size):
    fnt = F(SANS_B, story_size)
    lh = int(story_size * 1.26)
    heights = []
    for col in COLUMNS:
        h = 0
        for name in col:
            h += 24  # section header (16 text + 8 gap)
            for st in section_stories(name):
                h += story_block_h(draw, st, fnt, lh)
            h += 6  # gap after section
        heights.append(h)
    return max(heights)


def draw_story(draw, x, y, st, fnt, lh):
    prefix = "[CLAIM] " if st["claim"] else ""
    lines = wrap(draw, prefix + st["headline"], fnt, COL_W)[:2]
    for li, line in enumerate(lines):
        if li == 0 and st["claim"]:
            tw = draw.textlength(prefix, font=fnt)
            draw.text((x, y), prefix, font=fnt, fill=RED)
            draw.text((x + tw, y), line[len(prefix):], font=fnt, fill=INK)
        else:
            draw.text((x, y), line, font=fnt, fill=INK)
        y += lh
    src_txt = "— " + st["source"]
    last_w = draw.textlength(lines[-1], font=fnt) if lines else 0
    sw = draw.textlength(src_txt, font=F(SANS, 10))
    if last_w + 6 + sw <= COL_W:
        draw.text((x + last_w + 6, y - lh + 2), src_txt, font=F(SANS, 10), fill=GRAY)
    else:
        draw.text((x, y), src_txt, font=F(SANS, 10), fill=GRAY)
        y += int(10 * 1.3)
    return y + 4


def render(story_size):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([FRAME, FRAME, W - FRAME - 1, H - FRAME - 1], outline=INK, width=2)

    y = MARGIN + 4
    draw_center(d, y, DATA["title"], F(SERIF_B, 62))
    y += 74
    draw_center(d, y, "THURSDAY  ·  26 NOVEMBER 2026", F(SANS_B, 15))
    y += 24
    n_stories = sum(len(s["stories"]) for s in DATA["sections"]) + len(DATA["leads"])
    draw_center(
        d, y,
        f"ONE DAY IN WORLD NEWS  —  {n_stories} STORIES  ·  7 REGIONS  ·  ALL SOURCED",
        F(SANS, 11), fill=GRAY,
    )
    y += 22
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=RULE, width=3)
    y += 12

    # Lead block
    d.text((MARGIN, y), "TOP STORIES", font=F(SANS_B, 12), fill=RED)
    y += 20
    lead_top = y
    lead_h = 0
    # Measure lead heights first so dividers use the final height.
    kick = F(SANS_B, 11)
    head = F(SERIF_B, 19)
    deck = F(SANS, 12)
    src = F(SANS, 10)
    lead_heights = []
    for lead in DATA["leads"]:
        lh = 16
        if lead["claim"]:
            lh += 18
        lh += len(wrap(d, lead["headline"], head, COL_W)[:3]) * int(19 * 1.25)
        lh += 3
        lh += len(wrap(d, lead["deck"], deck, COL_W)[:2]) * int(12 * 1.35)
        lh += 2 + 14
        lead_heights.append(lh)
    lead_h = max(lead_heights)
    for i, lead in enumerate(DATA["leads"]):
        x = MARGIN + i * (COL_W + COL_GAP)
        ly = lead_top
        d.text((x, ly), lead["kicker"], font=kick, fill=RED)
        ly += 16
        if lead["claim"]:
            tag = "  CLAIM  "
            tw = d.textlength(tag, font=F(SANS_B, 10))
            d.rectangle([x, ly + 2, x + tw, ly + 14], fill=RED)
            d.text((x, ly + 2), tag, font=F(SANS_B, 10), fill=(255, 255, 255))
            ly += 18
        for line in wrap(d, lead["headline"], head, COL_W)[:3]:
            d.text((x, ly), line, font=head, fill=INK)
            ly += int(19 * 1.25)
        ly += 3
        for line in wrap(d, lead["deck"], deck, COL_W)[:2]:
            d.text((x, ly), line, font=deck, fill=INK)
            ly += int(12 * 1.35)
        ly += 2
        d.text((x, ly), "Source: " + lead["source"], font=src, fill=GRAY)
        if i < 2:
            d.line(
                [(x + COL_W + COL_GAP // 2, lead_top),
                 (x + COL_W + COL_GAP // 2, lead_top + lead_h)],
                fill=LIGHT, width=1,
            )
    y = lead_top + lead_h + 10
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=RULE, width=1)
    y += 12

    # Region columns
    region_top = y
    sfnt = F(SANS_B, story_size)
    slh = int(story_size * 1.26)
    sec_f = F(SANS_B, 12)
    for ci, col in enumerate(COLUMNS):
        x = MARGIN + ci * (COL_W + COL_GAP)
        cy = region_top
        for name in col:
            d.text((x, cy), name, font=sec_f, fill=RED)
            cnt = str(len(section_stories(name)))
            cw = d.textlength(cnt, font=sec_f)
            d.text((x + COL_W - cw, cy), cnt, font=sec_f, fill=GRAY)
            cy += 16
            d.line([(x, cy), (x + COL_W, cy)], fill=RULE, width=1)
            cy += 8
            for st in section_stories(name):
                cy = draw_story(d, x, cy, st, sfnt, slh)
            cy += 6
    y = region_top + columns_height(d, story_size) + 4

    # Footer
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=RULE, width=1)
    y += 8
    draw_center(
        d, y,
        "All stories dated 26 November 2026  ·  Unconfirmed reports are labelled CLAIM  ·  Image generated by code — no AI imagery",
        F(SANS, 10), fill=GRAY,
    )
    return img


def main():
    probe = Image.new("RGB", (W, H), PAPER)
    pd = ImageDraw.Draw(probe)
    fixed = MARGIN + 4 + 74 + 24 + 22 + 12 + 20 + LEAD_H + 10 + 1 + 12
    avail = H - FRAME - FOOTER_H - fixed
    chosen = None
    for size in (13, 12.5, 12, 11.5, 11):
        need = columns_height(pd, size)
        if need <= avail:
            chosen = size
            break
    if chosen is None:
        print(f"LAYOUT DOES NOT FIT even at 11pt (need={columns_height(pd, 11)} avail={avail})",
              file=sys.stderr)
        sys.exit(1)
    img = render(chosen)
    img.save(OUT, format="PNG", optimize=True)
    data = OUT.read_bytes()
    print(f"wrote {OUT}")
    print(f"size_bytes={len(data)} limit=1048576 ok={len(data) <= 1048576}")
    print(f"dimensions={img.size}")
    print(f"story_font={chosen}")
    print(f"sha256={hashlib.sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
