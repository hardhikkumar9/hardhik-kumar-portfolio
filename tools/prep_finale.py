"""Assemble the closing shot from separately generated layers.

Run:  python tools/prep_finale.py <plate.jpg> <man.jpg> <frame2.jpg>
Out:  public/fin/plate.jpg   background + wordmark
      public/fin/man.png     the man, matted, with alpha
      public/fin/fin.json    his box
      footer 2nd image.jpg   the last cut

WHY THIS EXISTS INSTEAD OF tools/extract_fin.py. That script cuts one combined
poster into plate + man, and it does it with surgery written for one specific
photograph: a hardcoded 1600x900 assertion, a hardcoded box for the man, and
hand-placed GrabCut hints on his face, raised hand, cigarette, spine and hair.
It cannot survive a regenerated poster - the hints simply land on fog. Taking
the layers in already separated removes every one of those assumptions: the man
arrives on a white cyclorama and mattes with the same pipeline as the hero, and
the wordmark is set here in real type rather than recovered from pixels.

THE WORDMARK IS NOT THE HERO'S. src/scene/type.js solves for a 3.121
width:cap ratio, measured off the hero artwork. The footer sets the same seven
letters far more condensed - measured off the reference's own stems at
1016 x 739 in a 1600x900 frame, so 1.375. Using the hero's ratio here produces
a wordmark half the height the composition expects, with the man standing
against empty fog above it.

The letters are filled with the gradient sampled from the reference itself
(warm near-white at the cap, through red, to near-black at the baseline) and
multiplied by the site's own distress tile, so the footer's type is made of the
same material as the hero's.
"""

import json
import os
import sys

import cv2
import numpy as np
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matte import PRESETS, frame_alpha          # noqa: E402
from prep_hero import clean_backdrop            # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIN = os.path.join(ROOT, "public", "fin")
FRAME = (1600, 900)

# Flow burns its sparkle into a fixed spot of every 2752x1536 export, and
# sometimes a second, larger one just above and left of it. Both sit on empty
# background in these three plates, so inpainting removes them invisibly.
MARKS = [(2495, 1285, 2675, 1460)]

# measured off the reference's letter stems (see the module docstring)
WORD = "HARDHIK"
WORD_BOX = (292, 45, 1308, 784)      # x0, y0, x1, y1 of the ink, in FRAME

# sampled down a stem of the reference wordmark: (position, R, G, B)
STOPS = [(0.00, 250, 232, 224), (0.12, 233, 199, 185), (0.25, 215, 165, 148),
         (0.40, 178, 90, 72), (0.55, 123, 41, 29), (0.70, 89, 14, 10),
         (0.85, 97, 2, 4), (1.00, 66, 1, 2)]

# where the man stands, carried over from the reference composition
MAN_BOX = (580, 170, 450, 730)       # x, y, w, h - w is re-derived from aspect

# The sprite is emitted at MAN_SS times the box. finale.js maps his quad from
# the FRAME box in fin.json and samples the texture by UV, so its pixel size is
# independent of where he lands - which means the box can stay in frame
# coordinates while the texture carries more detail. It has to: the generated
# plate gives him 748x1426 px, and emitting at the box's 730 tall threw away
# half of that, then the page upscaled him 2x again on any HiDPI screen. He
# came out soft in the face, which is exactly what it looks like.
MAN_SS = 2


def read(path):
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        sys.exit("could not read %s" % path)
    return img


def clean(img):
    """Paint out the generator's watermarks."""
    h, w = img.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    for x0, y0, x1, y1 in MARKS:
        if x1 <= w and y1 <= h:
            mask[y0:y1, x0:x1] = 255
    if not mask.any():
        return img
    return cv2.inpaint(img, mask, 9, cv2.INPAINT_TELEA)


def anton(px):
    ttf = os.path.join(os.environ.get("TEMP", ROOT), "_anton.ttf")
    if not os.path.exists(ttf):
        f = TTFont(os.path.join(ROOT, "public", "fonts", "anton-400.woff2"))
        f.flavor = None
        f.save(ttf)
    return ImageFont.truetype(ttf, px)


def wordmark_mask(box):
    """The seven letters as a coverage mask, condensed to the measured ratio.

    Anton is naturally wider than the reference's face, so ONE horizontal scale
    is solved for and applied to the whole word - the same approach type.js
    takes for the hero. Per-letter fitting would squeeze the I into a hairline
    while leaving the H a slab, which is what makes set type look counterfeit.
    """
    x0, y0, x1, y1 = box
    want_w, cap = x1 - x0, y1 - y0

    font = anton(cap * 2)                       # oversample, then downscale
    probe = font.getbbox(WORD)
    nat_w = probe[2] - probe[0]
    nat_cap = probe[3] - probe[1]
    scale = cap * 2 / nat_cap                   # make the cap the right height
    font = anton(int(round(cap * 2 * scale)))
    probe = font.getbbox(WORD)

    pad = 40
    img = Image.new("L", (probe[2] - probe[0] + pad * 2,
                          probe[3] - probe[1] + pad * 2), 0)
    ImageDraw.Draw(img).text((pad - probe[0], pad - probe[1]), WORD,
                             font=font, fill=255)
    a = np.array(img)
    ys, xs = np.nonzero(a)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return cv2.resize(a, (want_w, cap), interpolation=cv2.INTER_AREA)


def fill(cap):
    """The reference's own vertical gradient, as a cap-tall colour ramp."""
    pos = np.array([s[0] for s in STOPS], np.float32)
    ramp = np.zeros((cap, 3), np.float32)
    t = np.linspace(0, 1, cap, dtype=np.float32)
    for c, idx in enumerate((3, 2, 1)):                 # BGR out of RGB stops
        ramp[:, c] = np.interp(t, pos, [s[idx] for s in STOPS])
    return ramp


def build_plate(src):
    plate = cv2.resize(clean(read(src)), FRAME, interpolation=cv2.INTER_AREA)
    x0, y0, x1, y1 = WORD_BOX
    cap = y1 - y0
    a = wordmark_mask(WORD_BOX).astype(np.float32) / 255.0

    ink = np.repeat(fill(cap)[:, None, :], x1 - x0, axis=1)

    # the site's own distress tile, so the footer's type wears the same surface
    tex = cv2.imread(os.path.join(ROOT, "public", "tex", "grunge.png"),
                     cv2.IMREAD_GRAYSCALE)
    if tex is not None:
        reps = (cap // tex.shape[0] + 2, (x1 - x0) // tex.shape[1] + 2)
        tile = np.tile(tex, reps)[:cap, :x1 - x0].astype(np.float32) / 255.0
        # same reasoning as the hero's wear: the tile is nearly all fine
        # noise, so a wide multiply speckles the wordmark rather than wearing it
        ink *= (0.90 + 0.20 * tile)[..., None]

    roi = plate[y0:y1, x0:x1].astype(np.float32)
    a3 = a[..., None]
    plate[y0:y1, x0:x1] = np.clip(roi * (1 - a3) + ink * a3, 0, 255).astype(np.uint8)

    os.makedirs(FIN, exist_ok=True)
    out = os.path.join(FIN, "plate.jpg")
    cv2.imwrite(out, plate, [cv2.IMWRITE_JPEG_QUALITY, 93])
    print("  plate.jpg   %dx%d, wordmark %dx%d at (%d,%d)"
          % (FRAME[0], FRAME[1], x1 - x0, cap, x0, y0))
    return plate


SAT_MIN = 2.5        # an object carries some colour; bare cyclorama does not
MAX_POCKET = 2000    # above this an enclosed gap is anatomy, not lost detail
ASPECT_RANGE = (0.55, 3.0)


def recover_objects(img, a, a_holes):
    """Re-solidify light OBJECTS the key mistook for backdrop.

    A white coffee cup is the same luminance as the cyclorama behind it, so the
    key drops it and the red plate shows straight through - the cup composites
    crimson. matte.py already has the switch for this (`hole_min`, the
    white-sneaker case), but turning it on costs two things it also fills: the
    triangle between his pocketed arm and his torso, and the gap between his
    legs. Both are genuinely enclosed, so neither area nor connectivity can
    tell them from a cup, and both land as solid white slabs.

    What tells them apart is what is INSIDE. Measured on this plate, the cup
    reads saturation 5.5 and is wider than it is tall; the arm and leg gaps
    read 0.1-0.2 and are tall, narrow slivers. They are bare backdrop, so they
    have no colour and no shape of their own. Both tests separate the three
    regions with room to spare, and both must pass.

    `a_holes` is the same matte run with hole_min on; only what IT added is
    considered, so nothing else about the alpha is disturbed.
    """
    gained = ((a_holes > 0.5) & (a <= 0.5)).astype(np.uint8)
    if not gained.any():
        return a

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1].astype(np.float32)

    n, lab, stats, _c = cv2.connectedComponentsWithStats(gained, 8)
    keep = np.zeros_like(gained)
    for i in range(1, n):
        bw, bh = stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_HEIGHT]
        if stats[i, cv2.CC_STAT_AREA] < 900 or bh == 0:
            continue
        m = lab == i
        if float(sat[m].mean()) < SAT_MIN:
            continue
        if not (ASPECT_RANGE[0] < bw / bh < ASPECT_RANGE[1]):
            continue
        keep[m] = 1
    if keep.any():
        a = np.where(keep.astype(bool), a_holes, a)
        print("  recovered %d object region(s) the key dropped as backdrop"
              % int(cv2.connectedComponents(keep)[0] - 1))
    return a


def harden_interior(a, inset=7):
    """Partial alpha belongs at the outline, nowhere else.

    Bright detail well inside the subject - a specular flash on a sunglass
    lens, the moulded lid of a cup, a sheen on a cuff - keys as partly
    transparent because it reads as backdrop-bright. At the edge that is
    correct and is what keeps hair soft; in the middle of a solid body it is
    simply wrong, and against this plate it shows up as red mottling where the
    fog comes through him.

    So everything further than `inset` inside the silhouette is forced opaque.
    The outline, and any genuinely open gap (the triangle beside a pocketed
    arm, the space between the legs) sits below the 0.5 threshold and is never
    part of the eroded core, so neither is touched.
    """
    core = cv2.erode((a > 0.5).astype(np.uint8),
                     cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                               (inset * 2 + 1,) * 2))

    # Small pockets fully enclosed by that core are detail the key lost - the
    # white flash inside a sunglass lens is the usual one. They are closed too.
    # The cap is what keeps the two big genuine gaps open: the triangle beside
    # his pocketed arm measures 3301px and the space between his legs 6472,
    # both far above it, while a lens flash is a few hundred.
    h, w = core.shape
    inv = (1 - core).astype(np.uint8)
    ff = inv.copy()
    cv2.floodFill(ff, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 2)
    pockets = ((inv == 1) & (ff != 2)).astype(np.uint8)
    if pockets.any():
        n, lab, stats, _c = cv2.connectedComponentsWithStats(pockets, 8)
        for i in range(1, n):
            if stats[i, cv2.CC_STAT_AREA] < MAX_POCKET:
                core[lab == i] = 1

    fixed = int(((core > 0) & (a < 0.99)).sum())
    if fixed:
        print("  hardened %d interior pixels that were letting the plate through"
              % fixed)
    return np.where(core.astype(bool), 1.0, a)


def build_man(src):
    img = clean_backdrop(clean(read(src)))
    a, _bg = frame_alpha(img, dict(PRESETS["v1"]))
    holes_cfg = dict(PRESETS["v1"])
    holes_cfg["hole_min"] = 2500
    a_holes, _bg2 = frame_alpha(img, holes_cfg)
    a = recover_objects(img, np.clip(a, 0, 1), np.clip(a_holes, 0, 1))
    a = harden_interior(a)

    ys, xs = np.nonzero(a > 0.05)
    if not len(ys):
        sys.exit("the man did not key - is the backdrop white and he in black?")
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    col = img[y0:y1, x0:x1]
    al = (a[y0:y1, x0:x1] * 255).astype(np.uint8)

    mx, my, _mw, mh = MAN_BOX
    scale = mh / col.shape[0]
    w = int(round(col.shape[1] * scale))          # his box, in frame px
    tw, th = w * MAN_SS, mh * MAN_SS              # the texture, oversampled
    col = cv2.resize(col, (tw, th), interpolation=cv2.INTER_LANCZOS4)
    al = cv2.resize(al, (tw, th), interpolation=cv2.INTER_LANCZOS4)

    rgba = np.dstack([col, al])
    cv2.imwrite(os.path.join(FIN, "man.png"), rgba)

    cx = MAN_BOX[0] + MAN_BOX[2] / 2.0            # keep the reference's centre
    box = [int(round(cx - w / 2.0)), my, w, mh]
    with open(os.path.join(FIN, "fin.json"), "w", encoding="utf-8") as f:
        json.dump({"man": box, "size": list(FRAME)}, f)
    print("  man.png     texture %dx%d for a %dx%d box  (opaque %.1f%%, soft %.1f%%)"
          % (tw, th, w, mh, (al > 242).mean() * 100,
             ((al > 12) & (al <= 242)).mean() * 100))


def build_frame2(src):
    img = cv2.resize(clean(read(src)), FRAME, interpolation=cv2.INTER_AREA)
    out = os.path.join(ROOT, "footer 2nd image.jpg")
    cv2.imwrite(out, img, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print("  footer 2nd image.jpg  %dx%d" % FRAME)


def main():
    if len(sys.argv) < 4:
        sys.exit("usage: python tools/prep_finale.py <plate> <man> <frame2>")
    print("assembling the finale ...")
    build_plate(sys.argv[1])
    build_man(sys.argv[2])
    build_frame2(sys.argv[3])
    print("done - reload the page")


if __name__ == "__main__":
    main()
