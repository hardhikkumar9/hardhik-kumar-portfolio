"""Prepare a Google Flow export for the matte pipeline.

Run:  python tools/prep_hero.py "Man_walking_in_black_suit_20260920004633.mp4"
Out:  assets_src/v1.mp4

Flow's export is close to what matte.py wants - a dark suit on a bright
cyclorama - but it arrives with two things the original studio plate did not
have, and both survive keying as visible ghosts on the site:

1  A sparkle watermark burned into the bottom right of every frame. It sits on
   bare backdrop and twinkles, so a median over time will not find it; it is
   painted out with ffmpeg's delogo, which interpolates it away from the
   surrounding flat backdrop.

2  Shadows. Flow lights him hard enough to throw a shadow onto the cyclorama
   wall beside him and another under his shoes. Both are darker than the
   backdrop, and "darker than the backdrop" is exactly what the v1 key reads as
   subject - so the wall shadow composites as a white outline down his left
   side and the contact shadow as white puddles at his feet.

   The wall shadow cannot be fixed downstream, and that is worth recording so
   nobody spends the afternoon rediscovering it. It is not a soft edge case:
   the band sits as far from the backdrop in Lab as his own rim pixels do, so
   the alpha ramp (lo/hi) cannot separate them. It is not a stray component
   either - it touches him at the shoulder, so neither largest_component on the
   seed mask nor an island filter on the finished alpha will drop it. And the
   seed threshold that does exclude it (fg_thr ~170) is past the point where
   his face stops keying as foreground and his head falls off.

   What separates shadow from subject is not colour and not connectivity - it
   is that the shadow lies OUTSIDE his silhouette. That is a fact only the
   source frame knows, so it is acted on here: his silhouette is found from the
   one thing the footage is unambiguous about (he is very dark, the backdrop is
   not), and everything outside it is replaced with a clean estimate of what
   the backdrop would look like with nothing casting on it.

The rewrite only ever touches pixels that end up fully transparent, so it
cannot change a single visible pixel of the composite.
"""

import os
import subprocess
import sys

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets_src", "v1.mp4")

# the sparkle, located by a top-hat scan across every frame, plus margin
DELOGO = dict(x=850, y=1685, w=110, h=115)

SUBJ_L = 130       # at or below this a pixel is certainly him, not backdrop
SUBJ_C = 6         # ...and so is anything this far off the backdrop's neutral
GUARD = 8          # px kept around the silhouette, so his soft edge survives
BG_WIN = 81        # local-max window for the clean-backdrop estimate


def subject_mask(frame):
    """His silhouette, generously closed and filled.

    TWO tests, and the second one is not optional. Dark pixels give the suit,
    hair and shoes. But his SKIN is brighter than any dark threshold, and where
    lit skin touches the backdrop directly - the edge of a jaw, the outside of a
    hand - it is not enclosed by anything dark, so hole-filling cannot recover
    it either. Masked on luminance alone, those pixels fall outside the mask,
    get overwritten with backdrop, and the matte then keys them away: a
    straight-edged bite out of his jaw, and fingers eaten down to stumps.

    What separates skin from the shadows this function exists to remove is
    COLOUR, not brightness. A shadow on a neutral cyclorama stays neutral;
    skin does not. Measured on this plate: bare backdrop 0.0 and the cast wall
    shadow 1.0 chroma units off neutral, against 12.3 for his beard, 15.5 for
    his cheek and 13.2 for the cup he is holding. At a threshold of 6 that
    keeps 82% of skin and 0% of either shadow or backdrop.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB).astype(np.float32)
    h, w = gray.shape

    # the backdrop's own neutral, from the bright part of the border ring
    ring = np.zeros((h, w), bool)
    ring[:14, :] = ring[-14:, :] = True
    ring[:, :14] = ring[:, -14:] = True
    lit = ring & (lab[:, :, 0] > 150)
    aR = float(np.median(lab[:, :, 1][lit])) if lit.any() else 128.0
    bR = float(np.median(lab[:, :, 2][lit])) if lit.any() else 128.0
    dC = np.sqrt((lab[:, :, 1] - aR) ** 2 + (lab[:, :, 2] - bR) ** 2)

    m = ((gray < SUBJ_L) | (dC > SUBJ_C)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE,
                         cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
    n, lab, stats, _c = cv2.connectedComponentsWithStats(m, 8)
    if n > 1:
        m = (lab == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)

    # flood the inverse from the border; whatever it cannot reach is enclosed
    h, w = m.shape
    inv = (1 - m).astype(np.uint8)
    ff = inv.copy()
    cv2.floodFill(ff, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 2)
    m = (m.astype(bool) | ((inv == 1) & (ff != 2))).astype(np.uint8)

    return cv2.dilate(m, cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (GUARD * 2 + 1, GUARD * 2 + 1)))


def clean_backdrop(frame):
    """Replace everything outside him with an unshadowed backdrop estimate."""
    keep = subject_mask(frame)

    # A grayscale dilation is a local maximum, so it fills every shadow with
    # the brightest backdrop near it while still following the cyclorama's own
    # falloff - which a flat fill would flatten and a blur would smear the
    # shadow back into. He is the darkest thing in frame, so he never wins a
    # maximum and never bleeds outward.
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (BG_WIN, BG_WIN))
    est = cv2.GaussianBlur(cv2.dilate(frame, k), (0, 0), 12.0)

    out = np.where(keep[..., None].astype(bool), frame, est)
    return out.astype(np.uint8)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else None
    if not src or not os.path.exists(src):
        sys.exit("usage: python tools/prep_hero.py <flow-export.mp4>")

    tmp = os.path.join(ROOT, "_prep_delogo.mp4")
    print("1/2  painting out the Flow sparkle ...", flush=True)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", src,
         "-vf", "delogo=x=%(x)d:y=%(y)d:w=%(w)d:h=%(h)d" % DELOGO,
         "-c:v", "libx264", "-preset", "slow", "-crf", "12",
         "-pix_fmt", "yuv420p", "-an", tmp], check=True)

    print("2/2  clearing the shadows off the backdrop ...", flush=True)
    cap = cv2.VideoCapture(tmp)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    proc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y",
         "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "%dx%d" % (w, h),
         "-r", str(fps), "-i", "-", "-an",
         "-c:v", "libx264", "-preset", "slow", "-crf", "12",
         "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)

    n = 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        proc.stdin.write(clean_backdrop(fr).tobytes())
        n += 1
    cap.release()
    proc.stdin.close()
    proc.wait()
    os.remove(tmp)
    print("wrote %s  (%d frames, %dx%d)" % (OUT, n, w, h))
    print("next: python tools/build_media.py && python tools/track.py")


if __name__ == "__main__":
    main()
