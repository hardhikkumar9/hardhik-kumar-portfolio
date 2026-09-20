"""Install the six timeline photographs.

Run:  python tools/prep_years.py <contact-sheet.jpg>   # a 3x2 sheet of all six
  or: python tools/prep_years.py [source_dir]          # 2021.jpg .. 2026.jpg
Out:  public/years/2021.jpg .. 2026.jpg   + meta.json

The card crops to 4:3 and is 264px wide, so that is what is emitted. The grade
is the one tools/extract_s3.py applied when these were cut out of the reference
poster: open the range, hold the warm cast, then put back a little local
contrast the resize takes off. Without it a photograph dropped in raw reads as
a bright rectangle stuck onto a warm black room - matching the grade is what
makes the six of them belong to the scene rather than sit on top of it.

SHEET MODE. An image generator asked for "six images by year" returns one
contact sheet, not six files, and it captions each tile with its year however
firmly the prompt says not to. Both are handled here:

  * the tile grid is DETECTED from the sheet's white gutters rather than
    assumed, so a regenerated sheet at another size still splits correctly;

  * the caption band is cropped off. Measured across all six tiles of the
    supplied sheet, the numerals occupy 83%-94% of tile height, so the bottom
    18% goes. That is also where Flow puts its sparkle watermark, so one crop
    removes both. The tile is then centre-cropped to 4:3 exactly as the card's
    `object-fit: cover` would, so what is written here is what the card shows.

The year, the heading and the three lines are live DOM text, written from the
CV in src/scene3/layout3.js - which is why a baked-in numeral has to go, or
every card would carry its year twice.
"""

import json
import os
import sys

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "public", "years")

YEARS = [2021, 2022, 2023, 2024, 2025, 2026]
OUT_W = 264
ASPECT = 4.0 / 3.0
CAPTION_KEEP = 0.82      # fraction of tile height kept above the caption band
GUTTER_L = 235           # a gutter pixel is at least this bright
GUTTER_FRAC = 0.85       # ...across at least this much of the row/column


def runs(mask, min_len=6):
    out, start = [], None
    for i, v in enumerate(mask):
        if v and start is None:
            start = i
        elif not v and start is not None:
            out.append((start, i - 1))
            start = None
    if start is not None:
        out.append((start, len(mask) - 1))
    return [r for r in out if r[1] - r[0] + 1 >= min_len]


def bands(gutters, extent):
    """Turn gutter runs into the content spans between them."""
    out, cur = [], 0
    for a, b in gutters:
        if a > cur:
            out.append((cur, a - 1))
        cur = b + 1
    if cur < extent:
        out.append((cur, extent - 1))
    return [s for s in out if s[1] - s[0] > extent * 0.08]


def split_sheet(img):
    """Detected tiles, in reading order."""
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    white = g > GUTTER_L
    cols = bands(runs(white.mean(axis=0) > GUTTER_FRAC), img.shape[1])
    rows = bands(runs(white.mean(axis=1) > GUTTER_FRAC), img.shape[0])
    return [img[y0:y1 + 1, x0:x1 + 1] for (y0, y1) in rows for (x0, x1) in cols]


def cover_crop(img, aspect):
    h, w = img.shape[:2]
    if w / h > aspect:                       # too wide - trim the sides
        nw = int(round(h * aspect))
        x = (w - nw) // 2
        return img[:, x:x + nw]
    nh = int(round(w / aspect))              # too tall - trim top and bottom
    y = (h - nh) // 2
    return img[y:y + nh, :]


def grade(c):
    """The extractor's grade, so a new photo sits in the same room."""
    c = c.astype(np.float32)
    lo, hi = np.percentile(c, [2, 99])
    c = np.clip((c - lo) / max(hi - lo, 1e-6), 0, 1)
    c = np.power(c, 0.86) * 255.0
    c = cv2.resize(c, (OUT_W, int(round(OUT_W / ASPECT))),
                   interpolation=cv2.INTER_LANCZOS4)
    c = cv2.bilateralFilter(np.clip(c, 0, 255).astype(np.uint8), 5, 30, 6)
    blur = cv2.GaussianBlur(c, (0, 0), 1.6)
    return np.clip(c.astype(np.float32) * 1.35 - blur.astype(np.float32) * 0.35,
                   0, 255).astype(np.uint8)


def write(year, tile, meta, note):
    out = grade(cover_crop(tile, ASPECT))
    cv2.imwrite(os.path.join(OUT, "%d.jpg" % year), out,
                [cv2.IMWRITE_JPEG_QUALITY, 88])
    meta[str(year)] = {"w": int(out.shape[1]), "h": int(out.shape[0])}
    print("  %d  <- %s" % (year, note))


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else ROOT
    meta_path = os.path.join(OUT, "meta.json")
    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)

    if os.path.isfile(arg):
        sheet = cv2.imread(arg)
        if sheet is None:
            sys.exit("could not read %s" % arg)
        tiles = split_sheet(sheet)
        if len(tiles) != len(YEARS):
            sys.exit("expected %d tiles, the gutter scan found %d - check the "
                     "sheet has clean white margins between the images"
                     % (len(YEARS), len(tiles)))
        print("sheet %dx%d -> %d tiles of %dx%d"
              % (sheet.shape[1], sheet.shape[0], len(tiles),
                 tiles[0].shape[1], tiles[0].shape[0]))
        for year, tile in zip(YEARS, tiles):
            keep = int(round(tile.shape[0] * CAPTION_KEEP))
            write(year, tile[:keep], meta, "sheet tile, caption cropped")
    else:
        missing = []
        for year in YEARS:
            src = next((p for p in
                        (os.path.join(arg, "%d%s" % (year, e))
                         for e in (".jpg", ".jpeg", ".png", ".webp"))
                        if os.path.exists(p)), None)
            img = cv2.imread(src) if src else None
            if img is None:
                missing.append(year)
                continue
            write(year, img, meta, os.path.basename(src))
        if missing:
            print("still missing: %s" % ", ".join(str(y) for y in missing))
            print("(years not supplied keep whatever is in public/years/)")

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)
    print("meta.json updated")


if __name__ == "__main__":
    main()
