"""Compose grotesque PFPs from trait layers.

Usage:
    python generator/generate.py samples      # the hand-picked review samples
    python generator/generate.py oneofones    # the 13 named 1/1s
    python generator/generate.py collection   # the full 1,300 (1,287 generic + 13 1/1s)

Writes SVG + metadata JSON into output/<mode>/ (collection also writes
RARITY.md and ranks.json).  Render to PNG with
    node generator/render.js output/<mode>
"""
import json
import os
import random
import sys
from collections import Counter

import traits as T
import weapons as W

# Rarity weights. A value's share of the generic PFPs is its weight divided
# by the trait's total weight. Tiers (by share of the whole collection):
# Common >= 10%, Uncommon 5-10%, Rare 2-5%, Epic 0.5-2%, Legendary < 0.5%.
WEIGHTS = {
    "Background": {"Swamp Green": 11, "Mustard": 11, "Dusty Teal": 11, "Rust": 11, "Bruise Purple": 11,
                   "Fog Grey": 11, "Bone": 11, "Blood Orange": 11, "Blood Red": 4, "Midnight": 4,
                   "Toxic Slime": 1.6, "Gold": 0.4},
    "Skin Tone": {"Pink Flesh": 16, "Sallow": 16, "Ruddy": 16, "Corpse Grey": 16, "Leather": 15,
                  "Pale Wax": 14, "Bloodless Blue": 5, "Radioactive": 1.6},
    "Swelling": {"Mild": 40, "Lumpy": 40, "Grotesque": 20},
    "Ear": {"Normal": 55, "Cauliflower": 30, "Torn": 15},
    "Eyes": {"Droopy Mismatch": 26, "Lazy Eye": 26, "Sunken Socket": 18, "Swollen Shut": 14,
             "Pinprick": 11, "Hollow Sockets": 4, "Glowing Red": 1},
    "Brows": {"Bushy": 50, "None": 30, "Scarred": 20},
    "Nose": {"Bulbous": 35, "Smashed Flat": 30, "Split Nostril": 25, "Missing": 10},
    "Mouth": {"Crooked Grin": 30, "Snarl": 28, "Slack Jaw": 24, "Lipless": 14, "Stitched Shut": 4},
    "Head Shape": {"Swollen Dome": 30, "Brow Bulge": 18, "Lopsided": 16, "Flat Top": 14, "Cone Head": 12,
                   "Split Skull": 7, "Tumor Cluster": 3},
    "Hair": {"Bald": 28, "Greasy Comb-over": 26, "Patchy Tufts": 26, "Backwards Cap": 20},
    "Hair Color": {"Ginger": 19, "Dirty Blonde": 19, "Greasy Black": 20, "Ash Grey": 19, "Mud Brown": 19,
                   "Blood-Matted": 4},
    "Clothing": {"Red Flannel": 9, "Green Flannel": 7, "Blue Flannel": 7, "Mustard Flannel": 5,
                 "Grey Flannel": 6, "Orange Flannel": 4, "Purple Flannel": 3, "Denim Shirt": 9,
                 "Chore Coat": 7, "Stained Undershirt": 7, "Torn White Tee": 5, "Torn Black Tee": 5,
                 "Torn Army Tee": 4, "Grey Hoodie": 5, "Black Hoodie": 5, "Maroon Hoodie": 3,
                 "Khaki Trench Coat": 3, "Black Trench Coat": 2, "Olive Trench Coat": 1.5, "Butcher Apron": 1.5},
    "Skin Detail": {"None": 40, "Wart": 15, "Veins": 14, "Boils": 12, "Stitches": 11, "Burn Scar": 8},
    "Weapon": {"None": 18, "Hunting Knife": 18, "Machete": 16, "Butcher Knife": 14, "Pitchfork": 13,
               "Fish Hook": 11, "Weed Whacker": 9.6, "Golden Machete": 0.4},
    "Bandana": {"None": 82, "Red Bandana": 6, "Black Bandana": 5, "Blue Bandana": 4, "Faded Paisley": 3},
}

TOTAL = 1300


def _o(bg, skin, swell, ear, eyes, brows, nose, mouth, hair, hair_c, cloth, detail, weapon, bandana="None",
       shape="Swollen Dome"):
    return {"Background": bg, "Skin Tone": skin, "Head Shape": shape, "Swelling": swell, "Ear": ear, "Eyes": eyes,
            "Brows": brows, "Nose": nose, "Mouth": mouth, "Hair": hair, "Hair Color": hair_c,
            "Clothing": cloth, "Skin Detail": detail, "Weapon": weapon, "Bandana": bandana}


# 13 named 1/1s. Each uses at least one exclusive trait (see EXCLUSIVE) that
# never appears in the generic PFPs.
ONE_OF_ONES = [
    ("The Harvester", _o("Cornfield", "Leather", "Grotesque", "Torn", "Glowing Red", "Scarred", "Missing",
                         "Lipless", "Patchy Tufts", "Ash Grey", "Chore Coat", "Stitches", "Pitchfork", "Faded Paisley")),
    ("Moonface", _o("Full Moon", "Albino", "Grotesque", "Normal", "Hollow Sockets", "None", "Split Nostril",
                    "Stitched Shut", "Bald", "Ash Grey", "Black Trench Coat", "Veins", "Fish Hook")),
    ("Old Gilded", _o("Midnight", "Gilded", "Lumpy", "Cauliflower", "Droopy Mismatch", "Bushy", "Bulbous",
                      "Crooked Grin", "Greasy Comb-over", "Dirty Blonde", "Mustard Flannel", "Wart", "Golden Machete")),
    ("Cinder", _o("Blood Red", "Charred", "Grotesque", "Torn", "Glowing Red", "None", "Missing",
                  "Snarl", "Bald", "Greasy Black", "Torn Black Tee", "Burn Scar", "Machete")),
    ("The Pale Deacon", _o("Midnight", "Albino", "Mild", "Normal", "Pinprick", "Scarred", "Smashed Flat",
                           "Stitched Shut", "Patchy Tufts", "Ash Grey", "Black Trench Coat", "Stitches", "Butcher Knife")),
    ("Hookjaw", _o("Blood Drip", "Corpse Grey", "Lumpy", "Cauliflower", "Swollen Shut", "Bushy", "Split Nostril",
                   "Slack Jaw", "Backwards Cap", "Mud Brown", "Butcher Apron", "Boils", "Fish Hook")),
    ("Silo Sam", _o("Cornfield", "Ruddy", "Grotesque", "Cauliflower", "Glowing Green", "Bushy", "Bulbous",
                    "Crooked Grin", "Backwards Cap", "Ginger", "Red Flannel", "Wart", "Weed Whacker")),
    ("Mother's Boy", _o("Blood Drip", "Pale Wax", "Grotesque", "Normal", "Glowing Green", "None", "Smashed Flat",
                        "Lipless", "Greasy Comb-over", "Greasy Black", "Grey Hoodie", "Veins", "Butcher Knife")),
    ("The Thirteenth", _o("Full Moon", "Charred", "Grotesque", "Torn", "Glowing Green", "Scarred", "Missing",
                          "Snarl", "Bald", "Blood-Matted", "Olive Trench Coat", "Burn Scar", "Golden Machete")),
    ("Gristle", _o("Toxic Slime", "Radioactive", "Grotesque", "Cauliflower", "Glowing Green", "None", "Split Nostril",
                   "Lipless", "Bald", "Mud Brown", "Torn Army Tee", "Boils", "Hunting Knife")),
    ("Crow Bait", _o("Cornfield", "Bloodless Blue", "Lumpy", "Torn", "Sunken Socket", "Scarred", "Smashed Flat",
                     "Stitched Shut", "Patchy Tufts", "Greasy Black", "Purple Flannel", "Stitches", "Machete", "Black Bandana")),
    ("Lantern Jack", _o("Midnight", "Albino", "Grotesque", "Normal", "Glowing Red", "Bushy", "Bulbous",
                        "Crooked Grin", "Patchy Tufts", "Ginger", "Orange Flannel", "Wart", "Weed Whacker")),
    ("Swamp Saint", _o("Full Moon", "Corpse Grey", "Grotesque", "Cauliflower", "Glowing Green", "None", "Missing",
                       "Slack Jaw", "Greasy Comb-over", "Blood-Matted", "Maroon Hoodie", "Veins", "Pitchfork")),
]
ONE_OF_ONE_SHAPES = {'The Harvester': 'Lopsided', 'Moonface': 'Cone Head', 'Old Gilded': 'Brow Bulge', 'Cinder': 'Tumor Cluster', 'The Pale Deacon': 'Cone Head', 'Hookjaw': 'Flat Top', 'Silo Sam': 'Split Skull', "Mother's Boy": 'Lopsided', 'The Thirteenth': 'Split Skull', 'Gristle': 'Tumor Cluster', 'Crow Bait': 'Flat Top', 'Lantern Jack': 'Brow Bulge', 'Swamp Saint': 'Cone Head'}
ONE_OF_ONE_MASKS = {'The Harvester': 'Rusted Mask', 'Moonface': 'Bone Mask', 'Old Gilded': 'Gold Mask', 'Cinder': 'Charred Mask', 'The Pale Deacon': 'Stitched Mask', 'Hookjaw': 'Bloody Mask', 'Silo Sam': 'Muddy Mask', "Mother's Boy": 'Lipstick Mask', 'The Thirteenth': 'Chrome Mask', 'Gristle': 'Toxic Mask', 'Crow Bait': 'Broken Mask', 'Lantern Jack': "Jack-o'-Lantern Mask", 'Swamp Saint': 'Mossy Mask'}
for _name, _a in ONE_OF_ONES:
    _a["Head Shape"] = ONE_OF_ONE_SHAPES[_name]
    _a["Bandana"] = "None"  # the mask replaces it
    _a["Mask"] = ONE_OF_ONE_MASKS[_name]
EXCLUSIVE = {"Background": {"Full Moon", "Cornfield", "Blood Drip"},
             "Skin Tone": {"Charred", "Gilded", "Albino"},
             "Eyes": {"Glowing Green"},
             "Mask": set(ONE_OF_ONE_MASKS.values())}

HEAD_T = "translate(-35 25) scale(1.07)"
SWELL = {"Mild": 14, "Lumpy": 34, "Grotesque": 58}


def compose(attrs, seed):
    rng = random.Random(seed)
    skin = T.SKINS[attrs["Skin Tone"]]
    hair_c = T.HAIR_COLORS[attrs["Hair Color"]]
    details = [] if attrs["Skin Detail"] == "None" else [attrs["Skin Detail"]]
    cloth_behind, cloth_back, cloth_front = T.clothing(attrs["Clothing"], rng, skin)
    swell = SWELL[attrs["Swelling"]]
    if attrs["Hair"] == "Backwards Cap":
        swell = min(swell, 34)  # keep the skull lumps inside the cap
    layers = [
        T.background(attrs["Background"]),
        '<g transform="translate(0 -55)">',
        W.slung(attrs.get("Weapon", "None")),
        f'<g transform="{HEAD_T}">',
        T.hair_back(attrs["Hair"], hair_c, rng),
        '</g>',
        cloth_behind,
        T.neck(skin),
        cloth_back,
        cloth_front,
        W.sling_strap(attrs.get("Weapon", "None")),
        f'<g transform="{HEAD_T}">',
        T.head(skin, rng, swell, attrs.get("Head Shape", "Swollen Dome")),
        T.skin_details(details, skin, rng),
        T.ear(skin, attrs["Ear"]),
        T.eyes(attrs["Eyes"], skin, rng),
        T.brows(attrs["Brows"], hair_c),
        T.nose(attrs["Nose"], skin),
        T.mouth(attrs["Mouth"], skin, rng),
        T.bandana(attrs.get("Bandana", "None"), rng) if attrs.get("Mask", "None") == "None" else "",
        T.mask_straps(attrs.get("Mask", "None"), skin),
        T.hair(attrs["Hair"], hair_c, rng),
        T.mask(attrs.get("Mask", "None"), skin, attrs["Eyes"], rng),
        '</g>',
        W.held(attrs.get("Weapon", "None"), skin, T.sleeve_fill(attrs["Clothing"])),
        '</g>',
    ]
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">'
            + "".join(layers) + "</svg>")


SAMPLES = [
    _o("Swamp Green", "Pink Flesh", "Grotesque", "Cauliflower", "Droopy Mismatch", "None", "Split Nostril",
       "Lipless", "Bald", "Mud Brown", "Chore Coat", "Veins", "Machete"),
    _o("Mustard", "Sallow", "Lumpy", "Normal", "Sunken Socket", "Bushy", "Bulbous", "Crooked Grin",
       "Patchy Tufts", "Ginger", "Denim Shirt", "None", "Pitchfork", "None", "Lopsided"),
    _o("Dusty Teal", "Corpse Grey", "Grotesque", "Torn", "Swollen Shut", "Scarred", "Missing", "Snarl",
       "Patchy Tufts", "Ash Grey", "Red Flannel", "Stitches", "Fish Hook", "Red Bandana", "Split Skull"),
    _o("Rust", "Ruddy", "Lumpy", "Cauliflower", "Lazy Eye", "Bushy", "Smashed Flat", "Slack Jaw",
       "Backwards Cap", "Greasy Black", "Stained Undershirt", "Boils", "Weed Whacker"),
    _o("Bruise Purple", "Pale Wax", "Grotesque", "Normal", "Pinprick", "None", "Split Nostril", "Snarl",
       "Greasy Comb-over", "Dirty Blonde", "Green Flannel", "Burn Scar", "Butcher Knife", "None", "Brow Bulge"),
    _o("Bone", "Leather", "Mild", "Torn", "Droopy Mismatch", "Scarred", "Bulbous", "Lipless",
       "Bald", "Greasy Black", "Chore Coat", "Wart", "Hunting Knife", "Faded Paisley", "Cone Head"),
]


def write(out_dir, idx, attrs, seed, name=None):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f"{idx}.svg"), "w") as f:
        f.write(compose(attrs, seed))
    meta = {"name": f"SBN13th #{idx}" + (f" - {name}" if name else ""), "seed": seed,
            "attributes": ([{"trait_type": "Type", "value": "1/1" if name else "Generic"}]
                           + ([{"trait_type": "1/1 Name", "value": name}] if name else [])
                           + [{"trait_type": k, "value": v} for k, v in attrs.items()])}
    with open(os.path.join(out_dir, f"{idx}.json"), "w") as f:
        json.dump(meta, f, indent=2)


def _pick(rng, weights):
    vals = list(weights)
    return rng.choices(vals, weights=[weights[v] for v in vals])[0]


def tier(share):
    if share >= 0.10:
        return "Common"
    if share >= 0.05:
        return "Uncommon"
    if share >= 0.02:
        return "Rare"
    if share >= 0.005:
        return "Epic"
    return "Legendary"


def build_collection(root):
    rng = random.Random(1300)
    n_generic = TOTAL - len(ONE_OF_ONES)
    seen = {tuple(sorted(a.items())) for _, a in ONE_OF_ONES}
    generics = []
    while len(generics) < n_generic:
        attrs = {k: _pick(rng, w) for k, w in WEIGHTS.items()}
        dna = tuple(sorted(attrs.items()))
        if attrs["Hair"] == "Backwards Cap" and attrs["Head Shape"] not in T.CAP_OK:
            continue  # the cap only fits some skulls
        if dna in seen:  # every PFP is unique
            continue
        seen.add(dna)
        generics.append(attrs)
    tokens = [(None, a) for a in generics] + list(ONE_OF_ONES)
    rng.shuffle(tokens)  # spread the 1/1s through the token ids
    seeds = [rng.randrange(1 << 30) for _ in tokens]
    for idx, ((name, attrs), seed) in enumerate(zip(tokens, seeds), 1):
        write(root, idx, attrs, seed=seed, name=name)
    report(root, tokens, n_generic)


def report(root, tokens, n_generic):
    counts = {k: Counter() for k in list(WEIGHTS) + ["Mask"]}
    for _, attrs in tokens:
        for k in counts:
            counts[k][attrs.get(k, "None")] += 1
    total = len(tokens)
    # rarity score: sum of (total / count) over traits; 1/1s always rank first
    scored = []
    for idx, (name, attrs) in enumerate(tokens, 1):
        score = sum(total / counts[k][attrs.get(k, "None")] for k in counts)
        scored.append((name is not None, score, idx, name))
    scored.sort(reverse=True)
    rank = {idx: r for r, (_, _, idx, _) in enumerate(scored, 1)}
    lines = ["# SBN13th collection rarity report", "",
             f"{total} PFPs: {n_generic} generic and {total - n_generic} 1/1s. Every PFP has a unique trait combination.",
             "", "Tiers by share of the collection: Common >= 10%, Uncommon 5-10%, Rare 2-5%, Epic 0.5-2%, Legendary < 0.5%.",
             "", "## 1/1s", "", "| Token | Name | Rank |", "|---|---|---|"]
    for idx, (name, _) in enumerate(tokens, 1):
        if name:
            lines.append(f"| #{idx} | {name} | {rank[idx]} |")
    for k, c in counts.items():
        lines += ["", f"## {k}", "", "| Value | Count | Share | Tier |", "|---|---|---|---|"]
        for v, n in c.most_common():
            excl = " (1/1 only)" if v in EXCLUSIVE.get(k, ()) else ""
            lines.append(f"| {v}{excl} | {n} | {n / total:.1%} | {tier(n / total)} |")
    lines += ["", "## Top 25 by rarity score", "", "| Rank | Token | Score |", "|---|---|---|"]
    for r, (_, score, idx, name) in enumerate(scored[:25], 1):
        lines.append(f"| {r} | #{idx}{' - ' + name if name else ''} | {score:.0f} |")
    with open(os.path.join(root, "RARITY.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    with open(os.path.join(root, "ranks.json"), "w") as f:
        json.dump(rank, f)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "samples"
    root = os.path.join(os.path.dirname(__file__), "..", "output", mode)
    if mode == "samples":
        for i, attrs in enumerate(SAMPLES, 1):
            write(root, i, attrs, seed=1300 + i)
    elif mode == "oneofones":
        for i, (name, attrs) in enumerate(ONE_OF_ONES, 1):
            write(root, i, attrs, seed=1300 + i, name=name)
    elif mode == "collection":
        build_collection(root)
    else:
        sys.exit(f"unknown mode {mode}")
    print("wrote", os.path.abspath(root))


if __name__ == "__main__":
    main()
