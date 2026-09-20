# Scene 3 — step by step

## The thing worth knowing first

Scene 3 is **not** a picture. The warm black room, the reflective floor, the
turning ring mechanism, the giant clock and its two hanging hands, the curved
timeline rail, the glowing year nodes and the red beam — all of it is drawn live
in WebGL every frame from measured geometry in `src/scene3/layout3.js`. The year
numbers, the headings and the body lines are live HTML, already written from
your CV.

Only **two** things ever came out of `section 3 image.jpg`:

1. six small photographs, one per year;
2. the figure's silhouette.

**Number 2 is already done** — I cut it from your walking clip, so the man
standing in front of your timeline is now actually you, in the suit, with the
laptop. `public/years/figure.png`.

So scene 3 needs six photographs. That is the whole job.

---

## Step 1 — generate six images

In Flow, use the **image** step (or ImageFX / Whisk — any Imagen surface).

- **Aspect: 4:3 landscape.** The card crops to 4:3, so anything else loses edges.
- **Any resolution.** I resize them.
- **No text anywhere in the frame.** The year, the heading and the three lines
  are live text on the card already. A date baked into the photo will collide
  with it.
- **No recognisable faces**, except 2026 where the figure is you from behind.

Paste this **style line at the end of every one of the six**, so they read as a
set and sit inside the scene's grade:

> Cinematic still, dark and warm, amber and deep red light, everything else
> near-black. Heavy film grain, strong vignette, shallow depth of field,
> desaturated except for the warm light. No text, no numbers, no labels, no logos,
> no watermarks. Nobody looking at camera.

### The six

**2021 · Foundations** — B.Tech IT, Delhi
> A university computer lab at night, long rows of desks with dark monitors
> receding into shadow, one screen glowing warm amber with lines of code, empty
> chairs, light falling from a single overhead strip.

**2022 · First delivery** — AICTE E-Governance, Android support app
> A cluttered desk at night lit only by its screens: an Android phone propped
> upright showing a simple app interface, a laptop behind it with code, a
> notebook and a cold cup of tea, warm lamplight raking across from the left.

**2023 · Into industry** — joined Nexgen Techtronics
> A small software team's office after hours, three or four dark monitors on a
> shared bench, a glass whiteboard behind them covered in faint diagrams, a
> warm desk lamp at one end, nobody in shot.

**2024 · The analyst turn** — requirements, specs, stakeholders
> A wall of sticky notes and index cards connected by drawn arrows into a
> process flow, photographed at a slight angle in warm low light, one hand at
> the edge of frame reaching to move a note, the rest of the room dark.

**2025 · Birmingham** — MSc Business Analytics, BCS Agile BA
> A university lecture theatre seen from the back, steeply raked empty seats in
> shadow, the lit screen at the front far away and small, cold grey daylight
> from high windows warmed by amber interior light.

**2026 · Evidence at scale** — the capstone
> A young South Asian man in a dark jacket seen from behind in silhouette,
> standing at a wide window at sunset looking out over a city skyline, warm
> orange light flooding past him, his face not visible.

---

## Step 2 — drop them in

Save them into the project root as `2021.jpg`, `2022.jpg` … `2026.jpg`
(or hand me the files under any names — I will sort it).

## Step 3 — install them

```bash
python tools/prep_years.py
```

That resizes each to the card's 264px width at 4:3, applies the same warm
grade-and-sharpen the original extractor used so they match the room, writes
them to `public/years/`, and updates `public/years/meta.json`.

## Step 4 — look at it

```bash
python tools/serve.py 5173
```

Scroll to the timeline and move the mouse across it. The clock hand should
sweep, and whichever year it points at should light up and take the stage.

---

## What you do NOT need to do

You do not need to regenerate `section 3 image.jpg` as a whole poster. It is
still in the project and `tools/extract_s3.py` still works, but its six crop
boxes are **hardcoded pixel coordinates measured off the original artwork** —
a newly generated poster would put the cards somewhere else and the extractor
would cut six rectangles of empty floor. Supplying the six photos directly
skips that problem entirely and gives you better images, because each one gets
a whole frame of Flow's attention instead of being a 120px-wide detail inside a
crowded poster.
