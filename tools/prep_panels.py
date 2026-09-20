"""Build the twelve work panels, and the room plate behind them.

Run:  python tools/prep_panels.py                 # typographic panels
  or: python tools/prep_panels.py <art_dir>       # wearing supplied artwork
Out:  public/projects/p01_*.png .. p12_*.png
      public/projects/plate.jpg

WHY THE PERSPECTIVE IS NOT YOURS TO DRAW. Each card in the reference sits at
its own angle in the amphitheatre, and `public/projects/layout4.json` records
the four (or more) corners it occupies as a QUAD, alongside the axis-aligned
`box` the DOM element is positioned with. The sprite is a rectangle whose
*contents* are already warped into that quad - that is what makes a flat DOM
element read as a screen standing in a room.

So supplied art never needs to be drawn in perspective: hand over flat,
straight-on panels and this warps each one into its own quad with
`getPerspectiveTransform`. The measured geometry is reused untouched, which is
the whole point - re-measuring twelve quads against newly generated art is the
expensive, error-prone path.

With no art directory, panels are generated typographically: a dark glass
screen carrying the project's real title and where the link goes. That is not a
placeholder in the throwaway sense - it is legible, it is on-brand, and it says
what every card actually is, which the reference's own artwork never did.
"""

import json
import os
import re
import sys

import cv2
import numpy as np
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "public", "projects")
FRAME = (1600, 900)

# warm screen tints, cycled so neighbours differ - matches the reference's mix
TINTS = [(74, 96, 196), (52, 74, 172), (60, 132, 214), (44, 92, 188),
         (86, 142, 206), (66, 88, 178)]
GLOW = 26          # px of rim bloom around each panel
# The sprite must be EXACTLY the `box` the DOM element is sized to: boot4 sets
# the element's width from box[2] and the <img> fills it, so a padded sprite
# would sit inset and undersized inside its own card. The reference's own
# extractor cropped each card on its outline PLUS its glow, so the box already
# carries the room the bloom needs - it is drawn inside, not around.
PAD = 0
# Sprites are emitted at SS times their box. boot4 sizes the element from
# box[2] and the <img> fills it, so the card lands at exactly the same place -
# but with SS times the pixels behind it. Without this a 384px box renders at
# 384 CSS px, which is 768 device pixels on any HiDPI screen, from a 384px
# source: soft art and mushy type. This is the whole reason the panels looked
# blurred.
SS = 2


def ttf(name, px):
    src = os.path.join(ROOT, "public", "fonts", name + ".woff2")
    dst = os.path.join(os.environ.get("TEMP", ROOT), "_" + name + ".ttf")
    if not os.path.exists(dst):
        f = TTFont(src)
        f.flavor = None
        f.save(dst)
    return ImageFont.truetype(dst, px)


def cards():
    with open(os.path.join(OUT, "layout4.json"), encoding="utf-8") as f:
        meta = json.load(f)["cards"]
    src = open(os.path.join(ROOT, "src", "scene4", "layout4.js"),
               encoding="utf-8").read()
    info = {}
    for m in re.finditer(r"id: '(p\d\d)_(\w+)', title: '([^']*)'.*?host: '(\w+)'",
                         src, re.S):
        info[m.group(2)] = (m.group(1) + "_" + m.group(2), m.group(3), m.group(4))
    out = []
    for c in meta:
        if c["name"] in info:
            cid, title, host = info[c["name"]]
            out.append((cid, title, host, c["box"], c["quad"]))
    return out


def label(img, title, host, shrink=1.0):
    """Set the project's name and its destination onto a straight-on screen.

    Supplied artwork is deliberately textless - a generator cannot draw legible
    type - so the naming happens here, in the site's own faces, over a scrim so
    it stays readable whatever the panel behind it is doing. Without this the
    deck is twelve anonymous dashboards and the section stops being a portfolio.
    """
    h, w = img.shape[:2]
    band = int(h * 0.34)
    sc = np.linspace(0.0, 0.82, band, dtype=np.float32)[:, None, None]
    img[h - band:] = img[h - band:] * (1.0 - sc)

    pil = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)[:, :, ::-1])
    d = ImageDraw.Draw(pil)

    # Size the type against the FINAL card, not this working image. A small
    # card is drawn from the same 900px face as a large one and then shrunk
    # hard, so a height-relative size renders as a few illegible pixels on the
    # page. `shrink` is how much this face is about to be reduced by.
    size = max(15, int(16.0 * shrink))    # ~16 CSS px on the card
    f = ttf("bodonimoda-400", size)
    words, lines, cur = title.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=f) > w * 0.70 and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = t
    lines.append(cur)
    lines = lines[:3]

    fs = max(9, int(9.5 * shrink))        # ~9.5 CSS px
    fu = ttf("oswald-500", fs)
    y = h - int(h * 0.075) - len(lines) * int(size * 1.18)
    for ln in lines:
        d.text((int(w * 0.055), y), ln, font=f, fill=(242, 236, 230))
        y += int(size * 1.18)
    d.text((int(w * 0.055), y + int(size * 0.18)), host.upper(), font=fu,
           fill=(206, 158, 110))
    return np.array(pil)[:, :, ::-1].astype(np.float32)


def face(w, h, title, host, tint):
    """A straight-on screen: dark glass, a warm chart glow, the real title."""
    img = np.zeros((h, w, 3), np.float32)
    img[:] = (18, 16, 15)

    # a soft interior glow so the panel reads as lit rather than printed
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    g = np.exp(-(((xx - w * 0.62) / (w * 0.55)) ** 2
                 + ((yy - h * 0.58) / (h * 0.5)) ** 2))
    img += np.float32(tint)[None, None, :] * g[..., None] * 0.20

    return np.clip(img, 0, 255)


def sprite(cid, title, host, box, quad, art=None, i=0):
    bx, by, bw, bh = box
    q = np.array(quad, np.float32)
    # the quad is in FRAME coords; move it into the sprite's own space, then
    # scale both it and the canvas by SS
    q = (q - np.float32([bx - PAD, by - PAD])) * SS
    W, H = (bw + PAD * 2) * SS, (bh + PAD * 2) * SS

    # a straight-on face, then warped onto the quad's four extreme corners
    fw = max(900, W)
    fh = int(fw * bh / bw)
    if art is not None:
        src = cv2.resize(art, (fw, fh), interpolation=cv2.INTER_AREA).astype(np.float32)
    else:
        src = face(fw, fh, title, host, TINTS[i % len(TINTS)])
    # shrink = source-face width / FINAL CARD width in CSS px. The sprite is
    # SS times the card, but the type is specified in CSS px, so SS must NOT
    # appear here - dividing by it again halves every title.
    src = label(src, title, host, shrink=fw / float(bw))

    s = np.float32([[0, 0], [fw, 0], [fw, fh], [0, fh]])
    # pick the quad's extreme corners in the same order, so a 5- or 6-point
    # outline still maps correctly
    c = np.float32([q[np.argmin(q[:, 0] + q[:, 1])],
                    q[np.argmax(q[:, 0] - q[:, 1])],
                    q[np.argmax(q[:, 0] + q[:, 1])],
                    q[np.argmin(q[:, 0] - q[:, 1])]])
    M = cv2.getPerspectiveTransform(s, c)
    warped = cv2.warpPerspective(src, M, (W, H), flags=cv2.INTER_CUBIC,
                                 borderValue=(0, 0, 0))
    mask = cv2.warpPerspective(np.full((fh, fw), 255, np.uint8), M, (W, H),
                               flags=cv2.INTER_NEAREST)

    # rim bloom: the panel lights the air around its own edge
    edge = cv2.dilate(mask, np.ones((3, 3), np.uint8)) - cv2.erode(mask, np.ones((3, 3), np.uint8))
    bloom = cv2.GaussianBlur(edge.astype(np.float32), (0, 0), GLOW * 0.45 * SS)
    bloom /= max(bloom.max(), 1e-6)
    tint = np.float32(TINTS[i % len(TINTS)])
    rgb = warped + tint[None, None, :] * bloom[..., None] * 0.50
    alpha = np.clip(mask.astype(np.float32) + bloom * 130.0, 0, 255)

    rgba = np.dstack([np.clip(rgb, 0, 255), alpha]).astype(np.uint8)
    cv2.imwrite(os.path.join(OUT, cid + ".png"), rgba)
    return W, H


# the generator's sparkle, same fixed spot on every 2752x1536 export
MARK = (2495, 1285, 2675, 1460)


def plate():
    """The room the deck stands in.

    Prefers a purpose-generated empty amphitheatre in assets_src/. Falling back
    to a defocused frame of the work film works, but it is soft and the panels
    baked into that footage survive as bokeh competing with the twelve real
    ones placed on top - so a real empty plate is always the better input.
    """
    gen = os.path.join(ROOT, "assets_src", "room_plate.jpeg")
    if os.path.exists(gen):
        fr = cv2.imdecode(np.fromfile(gen, np.uint8), cv2.IMREAD_COLOR)
        h, w = fr.shape[:2]
        m = np.zeros((h, w), np.uint8)
        x0, y0, x1, y1 = MARK
        if x1 <= w and y1 <= h:
            m[y0:y1, x0:x1] = 255
            fr = cv2.inpaint(fr, m, 9, cv2.INPAINT_TELEA)
        fr = cv2.resize(fr, FRAME, interpolation=cv2.INTER_AREA).astype(np.float32)
        # the deck sits over the upper half, so take that down a little and let
        # the floor keep its glow: the panels must out-read the room behind them
        yy = np.linspace(0.62, 1.0, FRAME[1], dtype=np.float32)[:, None, None]
        fr *= yy
        cv2.imwrite(os.path.join(OUT, "plate.jpg"),
                    np.clip(fr, 0, 255).astype(np.uint8),
                    [cv2.IMWRITE_JPEG_QUALITY, 92])
        return "generated empty room"

    src = os.path.join(ROOT, "public", "media", "gallery.mp4")
    cap = cv2.VideoCapture(src)
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) * 0.72))
    ok, fr = cap.read()
    cap.release()
    if not ok:
        return False
    fr = cv2.resize(fr, FRAME, interpolation=cv2.INTER_AREA).astype(np.float32)
    fr = cv2.GaussianBlur(fr, (0, 0), 16.0) * 0.46
    # keep the floor's warmth but sink the upper half, where the deck sits
    yy = np.linspace(1.0, 0.55, FRAME[1], dtype=np.float32)[::-1][:, None, None]
    fr *= yy
    cv2.imwrite(os.path.join(OUT, "plate.jpg"),
                np.clip(fr, 0, 255).astype(np.uint8),
                [cv2.IMWRITE_JPEG_QUALITY, 92])
    return "defocused frame of the work film"


def main():
    art_dir = sys.argv[1] if len(sys.argv) > 1 else None
    print("plate:", plate() or "FAILED")
    for i, (cid, title, host, box, quad) in enumerate(cards()):
        art = None
        if art_dir:
            n = cid.split("_")[0]          # "p07"
            for stem in (n, n[1:], str(int(n[1:]))):   # p07 / 07 / 7
                for ext in (".png", ".jpg", ".jpeg", ".webp"):
                    q = os.path.join(art_dir, stem + ext)
                    if os.path.exists(q):
                        art = cv2.imdecode(np.fromfile(q, np.uint8), cv2.IMREAD_COLOR)
                        break
                if art is not None:
                    break
        w, h = sprite(cid, title, host, box, quad, art, i)
        print("  %-18s sprite %4dx%-4d  card %3dx%-3d  %-9s %s"
              % (cid, w, h, w // SS, h // SS, host,
                 "supplied art" if art is not None else title))


if __name__ == "__main__":
    main()
