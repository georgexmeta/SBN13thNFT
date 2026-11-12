# SBN13th: grotesque PFP collection

Layered 2D cartoon generator for a 1,300-piece collection of original, disfigured
characters drawn in a three-quarter view (head turned ~45° right): bold black
outlines, flat cel shading, solid backgrounds.

## Layout
- `generator/traits.py`: every trait layer as SVG (background, clothing, neck, lumpy head,
  ear, skin details, eyes, brows, nose, mouth, hair).
- `generator/generate.py`: composes characters and writes SVG + metadata JSON.
- `generator/render.js`: renders SVGs to 1000x1000 PNGs plus a contact sheet (Playwright).
- `output/samples/`: the review samples.

## Usage
```bash
python3 generator/generate.py samples        # hand-picked review samples
python3 generator/generate.py random 1300    # full random run (seeded)
node generator/render.js output/samples
```
