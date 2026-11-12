"""Compose grotesque PFPs from trait layers.

Usage:
    python generator/generate.py samples      # the hand-picked review samples
    python generator/generate.py random N     # N random characters (seeded)

Writes SVG + metadata JSON into output/<mode>/.  Render to PNG with
    node generator/render.js output/<mode>
"""
import json
import os
import random
import sys

import traits as T
import weapons as W

LAYER_ORDER = ["Background", "Clothing", "Head", "Ear", "Skin", "Eyes",
               "Brows", "Nose", "Mouth", "Hair"]

CHOICES = {
    "Background": list(T.BACKGROUNDS),
    "Skin Tone": list(T.SKINS),
    "Swelling": ["Mild", "Lumpy", "Grotesque"],
    "Ear": ["Normal", "Cauliflower", "Torn"],
    "Eyes": ["Droopy Mismatch", "Swollen Shut", "Lazy Eye", "Sunken Socket", "Pinprick"],
    "Brows": ["None", "Bushy", "Scarred"],
    "Nose": ["Split Nostril", "Bulbous", "Smashed Flat", "Missing"],
    "Mouth": ["Snarl", "Slack Jaw", "Crooked Grin", "Lipless"],
    "Hair": ["Bald", "Stringy Long", "Patchy Tufts", "Greasy Comb-over", "Backwards Cap"],
    "Hair Color": list(T.HAIR_COLORS),
    "Clothing": ["Denim Shirt", "Red Flannel", "Green Flannel", "Chore Coat", "Stained Undershirt"],
    "Skin Detail": ["None", "Stitches", "Veins", "Boils", "Burn Scar", "Wart"],
    "Weapon": W.WEAPONS,
}
# sleeve fill for the arm that holds a weapon (bare arm for the undershirt)
SLEEVES = {"Denim Shirt": "#4f6fa3", "Red Flannel": "url(#plaida8322db)",
           "Green Flannel": "url(#plaid3f6b3ab)", "Chore Coat": "#3e4752",
           "Stained Undershirt": None}
HEAD_T = "translate(-35 25) scale(1.07)"
SWELL = {"Mild": 14, "Lumpy": 34, "Grotesque": 58}


def compose(attrs, seed):
    rng = random.Random(seed)
    skin = T.SKINS[attrs["Skin Tone"]]
    hair_c = T.HAIR_COLORS[attrs["Hair Color"]]
    details = [] if attrs["Skin Detail"] == "None" else [attrs["Skin Detail"]]
    cloth_back, cloth_front = T.clothing(attrs["Clothing"], rng)
    layers = [
        T.background(T.BACKGROUNDS[attrs["Background"]]),
        '<g transform="translate(0 -55)">',
        W.slung(attrs.get("Weapon", "None")),
        f'<g transform="{HEAD_T}">',
        T.hair_back(attrs["Hair"], hair_c, rng),
        '</g>',
        T.neck(skin),
        cloth_back,
        cloth_front,
        W.sling_strap(attrs.get("Weapon", "None")),
        f'<g transform="{HEAD_T}">',
        T.head(skin, rng, min(SWELL[attrs["Swelling"]], 34) if attrs["Hair"] == "Backwards Cap" else SWELL[attrs["Swelling"]]),
        T.skin_details(details, skin, rng),
        T.ear(skin, attrs["Ear"]),
        T.eyes(attrs["Eyes"], skin, rng),
        T.brows(attrs["Brows"], hair_c),
        T.nose(attrs["Nose"], skin),
        T.mouth(attrs["Mouth"], skin, rng),
        T.hair(attrs["Hair"], hair_c, rng),
        '</g>',
        W.held(attrs.get("Weapon", "None"), skin, SLEEVES[attrs["Clothing"]]),
        '</g>',
    ]
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">'
            + "".join(layers) + "</svg>")


SAMPLES = [
    {"Background": "Swamp Green", "Skin Tone": "Pink Flesh", "Swelling": "Grotesque", "Ear": "Cauliflower",
     "Eyes": "Droopy Mismatch", "Brows": "None", "Nose": "Split Nostril", "Mouth": "Lipless",
     "Hair": "Bald", "Hair Color": "Mud Brown", "Clothing": "Chore Coat", "Skin Detail": "Veins", "Weapon": "Machete"},
    {"Background": "Mustard", "Skin Tone": "Sallow", "Swelling": "Lumpy", "Ear": "Normal",
     "Eyes": "Sunken Socket", "Brows": "Bushy", "Nose": "Bulbous", "Mouth": "Crooked Grin",
     "Hair": "Stringy Long", "Hair Color": "Ginger", "Clothing": "Denim Shirt", "Skin Detail": "None", "Weapon": "Pitchfork"},
    {"Background": "Dusty Teal", "Skin Tone": "Corpse Grey", "Swelling": "Grotesque", "Ear": "Torn",
     "Eyes": "Swollen Shut", "Brows": "Scarred", "Nose": "Missing", "Mouth": "Snarl",
     "Hair": "Patchy Tufts", "Hair Color": "Ash Grey", "Clothing": "Red Flannel", "Skin Detail": "Stitches", "Weapon": "Fish Hook"},
    {"Background": "Rust", "Skin Tone": "Ruddy", "Swelling": "Lumpy", "Ear": "Cauliflower",
     "Eyes": "Lazy Eye", "Brows": "Bushy", "Nose": "Smashed Flat", "Mouth": "Slack Jaw",
     "Hair": "Backwards Cap", "Hair Color": "Greasy Black", "Clothing": "Stained Undershirt", "Skin Detail": "Boils", "Weapon": "Weed Whacker"},
    {"Background": "Bruise Purple", "Skin Tone": "Pale Wax", "Swelling": "Grotesque", "Ear": "Normal",
     "Eyes": "Pinprick", "Brows": "None", "Nose": "Split Nostril", "Mouth": "Snarl",
     "Hair": "Greasy Comb-over", "Hair Color": "Dirty Blonde", "Clothing": "Green Flannel", "Skin Detail": "Burn Scar", "Weapon": "Butcher Knife"},
    {"Background": "Bone", "Skin Tone": "Leather", "Swelling": "Mild", "Ear": "Torn",
     "Eyes": "Droopy Mismatch", "Brows": "Scarred", "Nose": "Bulbous", "Mouth": "Lipless",
     "Hair": "Stringy Long", "Hair Color": "Greasy Black", "Clothing": "Chore Coat", "Skin Detail": "Wart", "Weapon": "Hunting Knife"},
]


def write(out_dir, idx, attrs, seed):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f"{idx}.svg"), "w") as f:
        f.write(compose(attrs, seed))
    meta = {"name": f"SBN13th #{idx}", "seed": seed,
            "attributes": [{"trait_type": k, "value": v} for k, v in attrs.items()]}
    with open(os.path.join(out_dir, f"{idx}.json"), "w") as f:
        json.dump(meta, f, indent=2)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "samples"
    root = os.path.join(os.path.dirname(__file__), "..", "output", mode)
    if mode == "samples":
        for i, attrs in enumerate(SAMPLES, 1):
            write(root, i, attrs, seed=1300 + i)
    else:
        n = int(sys.argv[2])
        rng = random.Random(13)
        for i in range(1, n + 1):
            attrs = {k: rng.choice(v) for k, v in CHOICES.items()}
            write(root, i, attrs, seed=rng.randrange(1 << 30))
    print("wrote", os.path.abspath(root))


if __name__ == "__main__":
    main()
