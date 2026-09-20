# The finale — step by step

## Why this one is split in two

The closing shot is the last thing anyone sees, and it is the only place on the
site where `HARDHIK` is **baked pixels** rather than live type — the hero renders
its wordmark in Anton every frame, but the footer's is part of the artwork.

At runtime the finale loads exactly three files:

```
public/fin/plate.jpg   the background: wordmark + red fog, with no man in it
public/fin/man.png     the man, matted, with a real alpha channel
public/fin/fin.json    where he sits on the plate
```

`tools/extract_fin.py` produces those by cutting one combined poster apart — and
it does it with **pixel surgery written for one specific photograph**: a
hardcoded 1600x900 assertion, a hardcoded box for the man, and hand-placed
GrabCut hints on his face, his raised hand, his cigarette, his spine and his
hair. A newly generated poster puts the man somewhere else and every one of
those hints lands on fog.

So do not regenerate the combined poster. **Generate the two layers separately**
and we assemble them, which is both easier to prompt and far more controllable:
a background with nothing in it, and you on a plain backdrop that mattes
cleanly with the pipeline already proven on your walking clip.

---

## Step 1 — the background plate

**Format: 16:9. One still.** No man, no text, nothing but atmosphere.

> **Prompt**
>
> Cinematic 16:9 background plate of a dense wall of swirling smoke, lit from
> within. Deep blood red at the centre, glowing brightest in the upper middle of
> the frame and falling away to pure black at all four corners and down both
> side edges. The smoke is thick and slow, with soft billowing forms and fine
> wisps catching the light. Heavy film grain, strong vignette, high contrast,
> completely desaturated except for the red. Nothing else is in the frame: no
> people, no objects, no shapes, no structures, no horizon. Premium film-poster
> background, expensive and restrained.
>
> **Negative / avoid:** text, letters, words, typography, logos, watermarks,
> people, figures, silhouettes, faces, hands, objects, furniture, buildings,
> windows, daylight, blue light, green light, orange fire, flames, sparks,
> bright white areas, busy detail.

The bright core matters: it is what the wordmark's light gradient is built from,
and it is what he is rim-lit against. Keep the side edges dark — the captions
(*"Good Data Speaks Louder."*, *An Analyst's World*, *Ask Analyse Advise
Repeat*) live there as live text and need somewhere quiet to sit.

## Step 2 — you, on a plain backdrop

**Format: 9:16 vertical or 1:1. A still or an 8-second clip — either is fine**,
I pull the best frame either way.

Same constraints as the walking clip, because it goes through the same matte:
**pure white seamless backdrop, black suit, black shirt, nothing else in frame,
never cropped at any edge.**

This is the poster pose, not the walk — three-quarter, still, weight settled.

> **Prompt**
>
> A young South Asian man in his mid-twenties standing against a pure white
> seamless studio backdrop, turned three-quarters to the camera, looking just
> past the lens. He wears a fitted matte-black two-piece suit over a black
> shirt, dark sunglasses, dark curly hair. His left hand is in his trouser
> pocket; his right arm is raised with his hand near his chin, fingers loosely
> closed, in a composed, thoughtful pose. Head to mid-thigh, centred, filling
> most of the frame height, never cropped at the top or the sides. He holds
> almost still — only a slow breath and the faintest shift of weight. Camera
> locked off, no pan, no zoom, no handheld shake. Flat, even, soft high-key
> studio lighting from both sides, no cast shadow on the backdrop, no coloured
> light. Clean commercial fashion-film look.
>
> **Negative / avoid:** white or light clothing, cropped head, cropped hands,
> background objects, furniture, floor markings, text, logos, watermarks,
> camera movement, motion blur, lens flare, coloured backdrop, shadow on the
> backdrop, extra people, walking, large gestures.

Keeping the suit and sunglasses identical to the walking clip is what makes the
first and last frames of the site read as the same person on the same day.

*On the cigarette:* the original poster had one, and its smoke is half of why
that frame works. I have written it out to match the hero. If you want it,
add *"holding a lit cigarette between two fingers of his raised hand, a thin
ribbon of smoke rising past his face"* — and say so, because the smoke has to
be matted as part of him rather than keyed away as backdrop.

## Step 3 — the last cut

**Format: 16:9. One still.** This slides in from the left as the final beat.
The original was a Ferrari; yours should close on the work.

> **Prompt**
>
> Cinematic 16:9 still of a single wide curved monitor floating in a pitch-black
> void, seen slightly from the side at a low angle, glowing. On its screen is a
> dark analytics dashboard: a large ascending line chart, a row of small metric
> tiles and a bar chart, all in amber and red on near-black. Warm red and amber
> light spills out of the screen and pools on a wet reflective black floor
> beneath it, throwing a long soft reflection. Thin volumetric haze, heavy
> vignette, deep film grain, everything else pure black. Calm, still, expensive.
>
> **Negative / avoid:** readable text, labels, numbers, logos, watermarks,
> people, hands, keyboards, desks, office furniture, daylight, blue or white
> screen glow, clutter.

---

## Step 4 — hand them over

Drop all three in the project root under any names and tell me which is which.
I will:

1. matte you off the white backdrop with the same pipeline the hero uses, so
   the edge quality matches;
2. set `HARDHIK` in Anton at the **3.121 width-to-cap ratio** the rest of the
   site is measured to, fill it with the plate's own light so it belongs to the
   smoke rather than sitting on it, and composite it into the plate;
3. write `public/fin/fin.json` from where he actually lands — measured, not
   guessed;
4. install the last cut as `footer 2nd image.jpg`.

The captions, the quote and the contact row are **already live DOM text** in
`index.html`, written from your CV. Nothing in these images should contain a
single word.

## One thing to watch

Your generator captions its output and burns in a sparkle watermark — it did
both on the six-year sheet. The prompts above ask for no text, but check the
corners before sending them over. If a mark turns up I will paint it out the
same way I did for the films; on a plain white or plain black background it
comes out invisibly.
