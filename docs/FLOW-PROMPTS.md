# Google Flow prompts — Hardhik Kumar portfolio

Six assets carry this site. Two are **video**, four are **stills**. Flow makes
both (the still prompts go through Flow's image step, or ImageFX / Whisk — any
Imagen surface).

## Read this first — three things that will bite you

**1. Veo cannot draw a specific real face from text.** Every prompt below that
contains "the man" needs *you* in it. In Flow use **Ingredients to Video** and
attach 2–3 reference photos of yourself (front, 3/4, full body, same black
suit). Without that you get a stranger, and the four assets won't match each
other.

**2. Veo garbles text.** Anything with a word baked into the frame — the
`HARDHIK` wordmark, the tool logos, the twelve project-card headlines — will
come back as convincing-looking gibberish. The fix is in each prompt: generate
the frame **with the text areas blank**, then set the type yourself in
Photoshop/Figma/Canva and, where it needs to move, run it back through Flow as
**Frames to Video**. Do not fight Veo for legible type; you will lose.

**3. Keep the palette locked.** Every scene is pure black, one red
(`#E01B1B`-ish), and warm amber. The shaders re-light these assets assuming
that. A blue or teal frame will look wrong on the page no matter how good it
is on its own.

Output settings for all six: **highest quality, 24 fps, no audio needed.**

---

## A · Hero clip — the walking man
`assets_src/v1.mp4` → rebuilt into `public/media/hero.mp4`

**Format: 720×1280 vertical (9:16). 8–10 s.**

This one has hard technical constraints, because the white backdrop is removed
offline by `tools/matte.py` and the site anchors him by his **feet**:

- Pure white seamless studio backdrop, evenly lit, nothing else in frame.
- He must be **darker than the backdrop** — black suit, black shirt. No white
  or cream clothing, no white shoes. The matte preset keys on that contrast.
- **Full body, shoes visible, feet never leave the bottom of the frame.**
- He stays roughly centred and never exits frame.
- No hard cast shadow on the floor behind him.

> **Prompt**
>
> Full-body vertical studio shot of a young South Asian man in his mid-twenties,
> walking slowly straight toward the camera against a pure white seamless
> cyclorama. He wears a fitted matte-black two-piece suit over a black shirt,
> black leather shoes, dark sunglasses, dark curly hair. He carries a slim
> closed laptop in his left hand, held loosely at his side. Calm, composed,
> unhurried — a confident professional walk, about four steps over the shot,
> arms swinging naturally. He starts small in frame and ends closer to camera,
> head and shoes always fully inside frame. Camera is locked off at chest
> height, no pan, no zoom, no handheld shake. Flat, even, soft high-key studio
> lighting from both sides, no visible cast shadow on the floor, no coloured
> light. Clean commercial fashion-film look, shallow contrast, 24fps.
>
> **Negative / avoid:** white or light clothing, white shoes, cropped feet,
> cropped head, background objects, furniture, floor markings, text, logos,
> watermarks, camera movement, motion blur, lens flare, coloured backdrop,
> shadow on the backdrop, extra people.

*Note on the cigarette:* the original portfolio put a lit cigarette in his
hand, and it runs through the hero and the footer. For a business-analyst
portfolio aimed at UK employers I have written it out and put a laptop there
instead. If you want the original attitude back, swap the laptop line for
*"holding a lit cigarette in his right hand, a thin ribbon of smoke rising"* —
just make the same choice in prompt E so the two frames agree.

**After Flow:** save as `assets_src/v1.mp4`, then

```bash
python tools/build_media.py
python tools/track.py
```

If Flow gives you 8 s instead of 10 s, change the frame count in
`tools/build_media.py` first — `("hero", "v1.mp4", "v1", 720, 1280, 0, 240)`
becomes `0, 192`.

---

## B · Scene 2 film — the analyst's toolkit
`public/media/universe.mp4`

**Format: 1280×720 landscape (16:9). 8–10 s, seamless loop if Flow offers it.**

Twelve tool cards float around him in a dark room. In the original these were
Figma / Photoshop / After Effects; yours are the BA stack. **This is the asset
most damaged by Veo's text problem** — twelve legible logos is not something it
will give you. Two routes:

### Route 1 (recommended) — blank cards, logos added after
Generate the room with the cards as plain dark glass panels, then drop the real
logo PNGs on in After Effects / Canva / Premiere over the finished clip. The
cards barely move, so simple position tracking is enough.

> **Prompt**
>
> Cinematic wide shot inside a vast pitch-black studio void with a wet,
> reflective dark floor. A young South Asian man in a black suit stands in the
> centre with his back to camera, seen in near-silhouette, hands at his sides,
> looking up and forward. Floating around him at different depths are twelve
> large rounded-square glass panels, dark charcoal with faint white rim-light on
> their edges — completely blank, no icons, no writing, no symbols on them. A
> single continuous ribbon of glowing red light sweeps through the space around
> him, curving behind and in front of the panels, leaving a soft trail. Hundreds
> of tiny warm white embers drift low across the floor and reflect in it. The
> camera pushes in very slowly. Lighting is pure black and deep red only, a
> faint red rim on his shoulders, volumetric haze. Premium, restrained,
> high-end 3D product-film look. 24fps.
>
> **Negative / avoid:** text, letters, words, logos, icons, symbols, UI, numbers,
> watermarks, faces, bright white light, blue or teal light, daylight, clutter,
> fast camera movement, cuts.

Then composite these twelve, in this order (it matches the screen-reader list
in `index.html`): **SQL · Python · Power BI · Tableau · Excel · Power Query ·
Java · JavaScript · Firebase · HTML · CSS · R**.

### Route 2 — one still, fixed by hand, then animated
Generate a single 1280×720 still with the same prompt, set the twelve logos on
it properly in Figma, then feed that image back into Flow as **Frames to
Video** with:

> Very slow push-in on this scene. The red light ribbon travels around the
> figure. Embers drift and twinkle on the floor. The panels float and breathe
> almost imperceptibly. Everything else holds perfectly still. No cuts, no new
> elements, no text changes.

**After Flow:** drop the clip at `public/media/universe.mp4` and grab a poster
frame:

```bash
ffmpeg -i public/media/universe.mp4 -vframes 1 -q:v 3 public/media/universe.jpg
```

---

## C · Scene 3 still — a journey through time
`section 3 image.jpg` — **a still, not a video**

**Format: 1280×720 exactly.** `tools/extract_s3.py` cuts the six year photos and
the figure out of this one image, so the composition has to hold.

> **Prompt**
>
> Cinematic wide shot of a dark warm-black room with a polished reflective floor
> marked by faint concentric golden rings. A young South Asian man in a black
> suit stands centre-left in near-silhouette, back to camera, looking up to the
> right. Six rectangular photo cards hang in the air in a gentle arc that
> descends from upper-left to lower-right across the frame, evenly spaced,
> getting slightly larger toward the right. Each card is a dark desaturated
> photograph of a workspace with a thin warm border and a small glowing amber
> node above it. The rightmost card glows hot red and is lit by a narrow red
> beam coming down from above. A giant clock face arcs across the top of the
> frame, mostly out of frame, with a pale ball pivot and two long slender hands
> hanging from it like a pair of dividers. Palette strictly black, deep red and
> warm amber. Volumetric haze, heavy vignette, premium and restrained. Leave the
> left and right margins empty and dark for captions.
>
> **Negative / avoid:** text, numbers, dates, letters, labels, watermarks, bright
> white light, blue or cool light, daylight, windows, clutter, extra people,
> faces, colourful photographs.

The six card photos should read, left to right, as this progression — steer the
prompt with one extra line if you want it explicit:

| Card | Year | Photo should suggest |
|---|---|---|
| 1 | 2021 | a university computer lab, rows of desks |
| 2 | 2022 | a desk with an Android phone and a laptop, code on screen |
| 3 | 2023 | an office team at monitors, whiteboard behind |
| 4 | 2024 | one person at a desk, a wall of sticky notes and a process diagram |
| 5 | 2025 | a Birmingham lecture theatre, or a desk with dashboards on screen |
| 6 | 2026 | the same man looking out over a city skyline at sunset |

Regenerate the crops afterwards with `python tools/extract_s3.py`. The year
numerals and body copy are **live DOM text** — they are already written from
your CV in `src/scene3/layout3.js`, so they must NOT be in the image.

---

## D · Scene 4 still — the work universe
`section 4 image.jpg` — **a still, not a video**

**Format: 1600×900 exactly.** `tools/extract_s4.py` cuts twelve card sprites and
the figure out of this one image. The card *positions* are already measured into
`src/scene4/layout4.js`, so the closer your composition sits to the original
amphitheatre arrangement, the less re-measuring you do.

> **Prompt**
>
> Ultra-wide cinematic shot of a dark amphitheatre with a wet reflective black
> floor marked by glowing concentric circles. A young South Asian man in a black
> suit stands small at the centre, back to camera, in silhouette. Twelve large
> widescreen monitor panels curve around him in a shallow dome — one big hero
> screen high in the centre, two large screens flanking it left and right, a row
> of five smaller screens at eye level, and two wide screens low in the bottom
> corners. Each screen shows a dark dashboard or data-visualisation interface:
> line charts, bar charts, tables and KPI tiles in amber, red and pale green on
> near-black backgrounds. Thin glowing rim light in red, amber and green traces
> the edge of each screen. An overhead ring structure hangs above. Deep haze,
> heavy vignette, palette strictly black, red, amber and one muted green.
> Premium, expensive, restrained. Leave the four corners empty and dark.
>
> **Negative / avoid:** readable text, headlines, paragraphs, logos, watermarks,
> photographs of products, cars, food, landscapes, game controllers, faces on
> screens, bright white light, blue or purple light, daylight, clutter.

The twelve headlines are set **on the sprites**, so you will add them by hand
after generating. In this order (matching `src/scene4/layout4.js`):

| # | Position | Headline | From your CV |
|---|---|---|---|
| 01 | large left | **Sales Trends Made Visible** | Power BI sales dashboard |
| 02 | left mid | **Requirements Into Specifications** | Nexgen — elicit, clarify, spec |
| 03 | **centre hero** | **Reading The Real Demand** | Capstone — the logging-gap finding |
| 04 | large right | **Customers, Segmented** | SQL & Excel customer analysis |
| 05 | small row | **How The Process Really Runs** | as-is process mapping |
| 06 | small row | **Defects Traced To Cause** | test support, UAT, defect triage |
| 07 | small row | **Weather App, Java & API** | WeatherAPI project |
| 08 | small row | **Water Delivery, End To End** | Java & Firebase app |
| 09 | small row | **AICTE Support, Centralised** | the E-Governance internship |
| 10 | right mid | **Forecasting The Next Year** | exponential smoothing forecast |
| 11 | bottom left | **Reconciled Before Dawn** | Park Regis night audit |
| 12 | bottom right | **Traceable Through To Test** | requirements traceability |

Then `python tools/extract_s4.py`.

---

## E · Footer still — the closing shot
`Footer image.jpg` — **a still, not a video**

**Format: 1600×900 exactly.** The giant wordmark is baked into this image and
the man is GrabCut-matted out of it by `tools/extract_fin.py`. The site sets the
wordmark live in Anton on the hero — but **here it is pixels**, so this is the
one place `HARDHIK` has to be real, legible type.

**Generate it without the word, then set `HARDHIK` yourself** in Anton (the font
is already in `public/fonts/anton-400.woff2`), stretched wide, filling roughly
the full width of the frame, letters running behind him.

> **Prompt**
>
> Cinematic portrait-style poster shot, 16:9. A young South Asian man in his
> mid-twenties stands in the centre-right of frame, turned three-quarters to
> camera, in a matte-black suit over a black shirt, dark sunglasses, dark curly
> hair. One hand in his trouser pocket, the other raised near his face. He is
> lit hard from behind and the side so his edges catch a rim of light while his
> front stays deep in shadow. Behind him a wall of dense red and black smoke
> glows from within, brightest directly behind his head and falling off to pure
> black at the corners. Heavy film grain, strong vignette, high contrast,
> desaturated except for the red. The background wall is completely empty — no
> writing, no shapes, no pattern. Leave clear dark margins down the far left and
> far right of the frame. Premium fashion-editorial grade.
>
> **Negative / avoid:** text, letters, words, typography, logos, watermarks,
> background objects, furniture, windows, daylight, blue light, green light,
> extra people, busy background.

Then, in Photoshop/Figma:
1. Set `HARDHIK` in Anton, all caps, stretched to about **3.12 : 1**
   (width : cap-height) — that is the ratio the rest of the site is measured to.
2. Fill it with the same top-light gradient the smoke has: near-white at the
   top, deep red at the bottom.
3. Put it **behind** the man, letters disappearing behind his shoulders.
4. Export 1600×900 JPEG as `Footer image.jpg`, then `python tools/extract_fin.py`.

The captions around the edges — *"Good Data Speaks Louder."*, *An Analyst's
World*, *Ask Analyse Advise Repeat* — are **live DOM text** already in
`index.html`. Do not bake them in.

---

## F · Footer frame 2 — the last cut
`footer 2nd image.jpg`

**Format: 1600×900.** This slides in from the left as the very last thing on the
page. The original was a Ferrari. Yours should close on the work, not a car.

> **Prompt**
>
> Cinematic 16:9 still of a single wide curved monitor floating in a pitch-black
> void, seen slightly from the side at a low angle, glowing. On its screen is a
> dark analytics dashboard: a large ascending line chart in amber, a row of small
> KPI tiles, and a bar chart, all rendered in amber and red on near-black. Warm
> red and amber light spills out of the screen and pools on a wet reflective
> black floor beneath it, throwing a long soft reflection. Thin volumetric haze,
> heavy vignette, deep film grain, everything else pure black. Calm, still,
> expensive. Palette strictly black, red and amber.
>
> **Negative / avoid:** readable text, labels, numbers, logos, watermarks,
> people, hands, keyboards, desks, office furniture, daylight, blue or white
> screen glow, clutter.

Save as `footer 2nd image.jpg` in the project root and reload — nothing else to
wire up.

---

## Order to build them in

1. **A (hero)** — it establishes your face and wardrobe. Every other asset
   should reuse its best frame as a reference image.
2. **E (footer)** — the second most-seen frame.
3. **D (scene 4)** — the most work, because of the twelve headlines.
4. **C (scene 3)**.
5. **B (scene 2 film)**.
6. **F (frame 2)** — five minutes.

Until each one lands, the site runs on the original placeholder art, so you can
swap them in one at a time and never have a broken page.
