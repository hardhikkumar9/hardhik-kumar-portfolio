// Scene four's measured geometry — every number read off the supplied
// reference (section 4 image.jpg, 1600x900), which is the source of truth.
// The card sprites and the environment plate are cut from that image by
// tools/extract_s4.py; this module records where each piece goes back.
//
// Coordinates are reference-frame pixels. fitCover() maps the frame onto the
// viewport the way the plate shader does (cover: fill, centre-anchored), so
// the DOM cards and the canvas can never drift apart.

export const FRAME = [1600, 900];

// Six panels in three mirrored pairs about the frame centre (x=800), with the
// centre column left clear for the figure, the floor circle and the overhead
// ring. The reference's own boxes were measured for a twelve-card arc; with six
// of them kept they read as scattered, so the composition is rebuilt rather
// than inherited. Pairs are exact mirrors: right.x = 1600 - left.x - w.
//
// The top pair is largest and furthest (depth 0.8), the bottom pair smallest
// and nearest (0.2), so the pointer parallax still separates the rows.
//
// href/host: every panel goes somewhere real. Repo-backed projects open the
// repository; the analysis work, which has no public artefact, opens the
// LinkedIn profile rather than pretending to a link that does not exist.
export const CARDS = [
  { id: 'p01_capstone', title: 'Reading The Real Demand',
    href: 'https://www.linkedin.com/in/hardhik-kumar', host: 'LinkedIn',
    box: [310, 90, 420, 240], depth: 0.8,
    tint: [0.414, 0.291, 0.291] },
  { id: 'p02_dashboard', title: 'Sales Trends Made Visible',
    href: 'https://www.linkedin.com/in/hardhik-kumar', host: 'LinkedIn',
    box: [870, 90, 420, 240], depth: 0.8,
    tint: [0.309, 0.334, 0.382] },
  { id: 'p03_segments', title: 'Customers, Segmented',
    href: 'https://www.linkedin.com/in/hardhik-kumar', host: 'LinkedIn',
    box: [150, 355, 390, 225], depth: 0.5,
    tint: [0.322, 0.278, 0.261] },
  { id: 'p04_requirements', title: 'Requirements Into Specifications',
    href: 'https://www.linkedin.com/in/hardhik-kumar', host: 'LinkedIn',
    box: [1060, 355, 390, 225], depth: 0.5,
    tint: [0.249, 0.267, 0.295] },
  { id: 'p05_weather', title: 'Weather App',
    href: 'https://github.com/hardhikkumar9/Weather-App', host: 'GitHub',
    box: [110, 605, 350, 205], depth: 0.2,
    tint: [0.311, 0.339, 0.263] },
  { id: 'p06_water', title: 'Water Delivery App',
    href: 'https://github.com/hardhikkumar9/Water-Delivery-App', host: 'GitHub',
    box: [1140, 605, 350, 205], depth: 0.2,
    tint: [0.31, 0.317, 0.302] },
];

// the central figure: crop box in frame px (his lighting is baked in)
// boot4 sets his WIDTH and lets height follow the sprite's own aspect, so
// w is derived from it: the figure is cut from the hero matte (a real
// silhouette of Hardhik) and is a different shape from the reference's.
// h is the height the amphitheatre was composed for; cx is unchanged.
export const PERSON = { x: 750, y: 483, w: 97, h: 335 };

// the floor's lit ellipses (centre x, centre y, rx, ry) and the overhead ring,
// used by the live glints the canvas draws over the baked plate
export const FLOOR_OUT = [798, 735, 372, 80];
export const FLOOR_IN = [798, 741, 240, 57];
export const RING = [802, 34, 392, 148];

/** Cover-fit the reference frame onto a viewport. */
export function fitCover(w, h) {
  const s = Math.max(w / FRAME[0], h / FRAME[1]);
  return { s, ox: (w - FRAME[0] * s) / 2, oy: (h - FRAME[1] * s) / 2 };
}

// --------------------------------------------------------------------------
// Portrait is a recomposition, not a crop: cover-fitting a 16:9 amphitheatre
// to a phone leaves only the centre quarter on screen. The plate still cover-
// fits (floor, circle and haze survive centred), and a curated set of cards
// restacks into a column that keeps the reference hierarchy: hero screen up
// top, the small row over the figure, the two green closers at his feet.
// Entries: card index -> centre x/y (viewport fractions), width (vw fraction).
// --------------------------------------------------------------------------
export const PORTRAIT = new Map([
  [0, { cx: 0.50, cy: 0.155, w: 0.86 }],
  [1, { cx: 0.50, cy: 0.345, w: 0.86 }],
  [2, { cx: 0.29, cy: 0.545, w: 0.52 }],
  [3, { cx: 0.71, cy: 0.545, w: 0.52 }],
  [4, { cx: 0.29, cy: 0.775, w: 0.52 }],
  [5, { cx: 0.71, cy: 0.775, w: 0.52 }],
]);
