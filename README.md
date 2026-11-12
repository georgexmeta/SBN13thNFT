# SBN13th: grotesque PFP collection

Layered 2D cartoon generator for a 1,300-piece collection of original, disfigured
characters drawn in a three-quarter view (head turned ~45° right): bold black
outlines, flat cel shading, solid backgrounds.

## Layout
- `generator/weapons.py`: Weapon trait. Held weapons (machete, hunting knife, butcher knife,
  fish hook) are gripped in a fist; long ones (pitchfork, weed whacker) are slung on the back.
- `generator/traits.py`: every trait layer as SVG (background, clothing, neck, lumpy head,
  ear, skin details, eyes, brows, nose, mouth, hair).
- `generator/generate.py`: composes characters and writes SVG + metadata JSON.
- `generator/render.js`: renders SVGs to 1000x1000 PNGs plus a contact sheet (Playwright).
- `output/samples/`: the review samples.

## Usage
```bash
python3 generator/generate.py samples        # hand-picked review samples
python3 generator/generate.py oneofones      # the 13 named 1/1s
python3 generator/generate.py collection     # all 1,300 (1,287 generic + 13 1/1s) + RARITY.md
node generator/render.js output/samples
```

## Collection
1,300 PFPs: 1,287 generic ones with weighted traits (Common to Legendary) and 13
named 1/1s that use exclusive traits (Full Moon, Cornfield and Blood Drip
backgrounds; Charred, Gilded and Albino skin; Glowing Green eyes) and each wears
one of 13 original goalie-mask finishes (Chrome, Bloody, Broken and more). Every PFP is a
unique trait combination. Weights live in `WEIGHTS` in `generator/generate.py`;
the generated breakdown is in `docs/RARITY.md`. The build is seeded, so it is
reproducible.
