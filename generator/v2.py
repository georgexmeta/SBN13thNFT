"""SBN13th v2 traits for the Gemini clay collection (George, 2026-11-13).

    python3 generator/v2.py      # writes output/collection-v2/<id>.json, RARITY-v2.md, output/ai/manifest-v2.json

Every PFP is the master-reference character (lumpy disfigured clay man, bobble head, slate work jacket look) with
variety in: head type (1-4), mask, held weapon, back weapon, clothing, backdrop and extras.
Tiers: 1,157 Standard, 130 Rare, 13 Legendary 1/1s. Rare-only and 1/1-only values never appear lower down.

Masks are ORIGINAL designs in the spirit of heavy-metal and slasher horror. They must not reproduce a specific
film character's or band member's mask (no white screaming hooded mask, no grid of pins on a pale face, no
red-chevron hockey mask, no copied clown make-up), so the collection stays clear of takedowns.
"""
import json
import os
import random
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output", "collection-v2")
TOTAL, N_RARE = 1300, 130

# ----------------------------------------------------------------------------------------------- trait tables
# value: (weight, prompt phrase). Weights are relative within the tier.
HEAD = {   # the four disfigured head types
    "Type 1 - Lumpy Dome": (34, "head type: a huge tall lumpy dome skull with dents and bumps, like the master reference"),
    "Type 2 - Melted Lopsided": (26, "head type: a lopsided skull that sags and melts down one side, one cheek drooping lower than the other"),
    "Type 3 - Cone Skull": (22, "head type: a tall cone-shaped pointed skull with ridged wrinkles running up to the point"),
    "Type 4 - Split Cranium": (18, "head type: a cranium split by a deep stitched crease down the middle, swollen lobes either side"),
}
SKIN = {
    "Flesh Pink": (30, "pink flesh-toned clay skin"), "Corpse Grey": (18, "corpse-grey clay skin"),
    "Sallow": (16, "sallow yellowish clay skin"), "Ruddy": (14, "ruddy red-pink clay skin"),
    "Pale Wax": (12, "pale waxy clay skin"), "Bloodless Blue": (6, "bloodless pale blue clay skin"),
    "Toxic Green": (4, "sickly toxic-green clay skin"),
}
HAIR = {
    "Grey Side Tufts": (40, "bald crown with stringy grey clay hair tufts above the ears"),
    "Bald": (22, "completely bald"), "Greasy Comb-over": (16, "a greasy black comb-over"),
    "Wild Grey Tufts": (14, "wild spiky grey hair tufts"), "Backwards Cap": (8, "a filthy plain backwards baseball cap with no logo"),
}
HEAD_MARK = {
    "Blue Veins": (40, "raised blue clay veins on the forehead"), "Grey Wrinkles": (25, "raised grey clay wrinkle ridges on the forehead"),
    "Stitched Scar": (15, "a stitched scar across the scalp"), "Boils": (10, "a few angry boils on the scalp"),
    "Clean": (10, ""),
}
MASK_STD = {
    "Bare Face": (22, "no mask: his disfigured face is bare, small sunken bloodshot eyes in swollen red lids, a crooked broken nose and rotten yellow teeth"),
    "Hockey Half-Mask": (18, "an aged yellowed lower-face hockey mask with blood smears, round breathing holes and a moulded beak nose, held by rusty leather straps with a riveted plate and a buckle under the ear, eyes visible above it"),
    "Burlap Pig Mask": (14, "a frayed stitched burlap pig mask with floppy ears, a pink clay snout and a blocky burlap-toothed grin, a rusty leather strap with a buckle over the crown"),
    "Burlap Sack Hood": (12, "his huge oversized bobble head is entirely covered by a filthy lumpy burlap sack pulled all the way down over the whole skull and face, ragged cut eye holes, a cross-stitched mouth, rope tied tight at the neck; no skin or hair visible"),
    "Patchwork Goggle Mask": (12, "a patchwork mask of stitched burlap and riveted scrap-metal plates, round brass goggle eyes with red lenses, a wire-stitched mouth, a leather strap with a buckle over the crown"),
    "Gas Mask": (10, "a cracked black rubber respirator over his nose and mouth with an olive filter canister and ribbed hose, eyes visible above"),
    "Paisley Bandana": (8, "a navy paisley bandana tied snug over his nose and mouth, point hanging on the chest"),
    "Iron Muzzle": (4, "a crude welded scrap-metal jaw cage made of bent rebar bars and bolts wrapped round his mouth and chin, rusty and bloody, eyes visible above"),
}
MASK_RARE = {   # monster-like; original takes on slasher and metal archetypes
    "Stitched Skin Mask": (16, "a crude mask of mismatched stitched leathery skin patches sewn with thick black thread, uneven eye holes, ragged edges"),
    "Nail-Studded Leather Mask": (14, "a cracked black leather mask with bent rusty nails and screws driven through it at random angles, blood seeping from the holes"),
    "Fanged Killer Clown": (14, "a cracked greasepaint killer clown face with green diamond eye paint, a red bulb nose, a ragged fanged grin dripping blood and wild orange hair puffs"),
    "Porcelain Doll Face": (12, "a cracked porcelain doll face mask with a chipped cheek, painted rosy cheeks, black empty eyes and a tiny painted mouth"),
    "Zipper Mouth Leather": (12, "a stitched black leather full-face mask with laced seams and a metal zipper across the mouth"),
    "Oni Demon Mask": (10, "a red lacquered demon mask with gold horns, a snarling fanged mouth and furrowed brows"),
    "Bone Skull Mask": (10, "a carved bone skull mask with cracked teeth and hollow eye sockets"),
    "Rusted Knight Helm": (8, "HIS WHOLE HEAD IS INSIDE a dented rusty medieval knight's great helm (a closed bucket-shaped steel helmet covering the entire head and face, with a narrow eye slit and breathing holes); no face or skin visible"),
    "Long Nose Latex": (4, "a pale grey latex mask with a long crooked warty nose and a dark slit mouth"),
}
HELD_STD = {
    "Machete": (20, "a long rusty machete dripping blood"), "Butcher Cleaver": (16, "a bloody rusty butcher's cleaver"),
    "Hunting Knife": (14, "a bloody hunting knife"), "Hatchet": (12, "a rusty hatchet with a chipped blade"),
    "Meat Hook": (10, "a big rusty meat hook"), "Sickle": (10, "a rusty curved sickle"),
    "Nail Bat": (8, "a wooden bat studded with bent rusty nails"), "Ice Pick": (6, "a rusty ice pick"), "Bare Fist": (4, None),
}
HELD_RARE = {"Golden Machete": (40, "a gleaming golden machete dripping blood"), "Bone Saw": (30, "a rusty serrated bone saw"),
             "Hook Hand": (30, None)}
BACK_STD = {
    "Weed Whacker": (22, "a rusty backpack weed whacker: engine pack on his back with padded harness straps over the shoulder, the trimmer shaft and head rising above his shoulder, grass clippings on his sleeve"),
    "Pitchfork": (16, "a rusty pitchfork slung on his back, tines rising above his shoulder"),
    "Chainsaw": (14, "a rusty chainsaw strapped to his back, the bar rising above his shoulder"),
    "Woodcutter Axe": (14, "a long woodcutter's axe slung on his back, head above his shoulder"),
    "Sledgehammer": (12, "a heavy sledgehammer slung on his back"), "Rusty Shovel": (10, "a rusty shovel slung on his back"),
    "None": (12, None),
}
BACK_RARE = {"Scythe": (40, "a huge rusty scythe slung on his back, the curved blade arching above his head"),
             "Circus Mallet": (30, "a giant red-and-cream striped circus mallet slung behind his back"),
             "Harpoon Gun": (30, "a rusty harpoon gun slung on his back")}
CLOTH_STD = {
    "Patched Work Jacket": (22, "a slate-blue clay work jacket with a brown leather collar, stitched leather patches and a grey knit undershirt"),
    "Plaid Flannel": (18, "a grimy plaid flannel shirt"), "Mechanic Coveralls": (14, "stained grey mechanic coveralls"),
    "Grimy Hoodie": (12, "a grimy torn hoodie"), "Butcher Apron": (10, "a blood-stained butcher's apron over a work shirt"),
    "Denim Jacket": (10, "a dirty denim jacket"), "Torn Undershirt": (8, "a stained torn undershirt"), "Trench Coat": (6, "a filthy long trench coat"),
}
CLOTH_RARE = {"Bloody Clown Suit": (35, "a baggy bloody harlequin clown suit with a ruffled collar and pom-pom buttons"),
              "Tattered Undertaker Suit": (35, "a tattered black undertaker's suit with a rotten flower in the lapel"),
              "Fur-Trimmed Cape": (30, "a ragged fur-trimmed cape over his work clothes")}
BELT = {"Tool Belt": (35, "a worn leather tool belt with rusty tools and pouches"), "None": (65, "")}
BACKDROP = {
    "Sage Clay": (20, "a sage-green pressed-clay backdrop"), "Swamp Clay": (16, "a swamp-green pressed-clay backdrop"),
    "Slate Clay": (14, "a slate-grey pressed-clay backdrop"), "Teal Clay": (12, "a dusty teal pressed-clay backdrop"),
    "Rust Clay": (12, "a rusty orange pressed-clay backdrop"), "Bruise Clay": (10, "a bruise-purple pressed-clay backdrop"),
    "Bone Clay": (8, "a bone-white pressed-clay backdrop"), "Blood Splatter": (8, "a cream pressed-clay backdrop with blood-red dripping splatter"),
}
BACKDROP_RARE = {"Blood Moon": (50, "a dark night backdrop with a huge cratered blood-red clay moon"),
                 "Cornfield": (50, "a cornfield of dry clay corn stalks at dusk")}

# 13 Legendary 1/1s: the hockey half-mask in a unique finish, plus unique backdrop/weapon combos
LEGENDARY = [
    ("The Harvester", "rust-stained", "Type 2 - Melted Lopsided", "Sickle", "Scythe", "Cornfield"),
    ("Moonface", "bone-white and cracked", "Type 3 - Cone Skull", "Meat Hook", "None", "Blood Moon"),
    ("Old Gilded", "solid gold", "Type 1 - Lumpy Dome", "Golden Machete", "Woodcutter Axe", "Slate Clay"),
    ("Cinder", "charred black with glowing ember cracks", "Type 4 - Split Cranium", "Machete", "Chainsaw", "Rust Clay"),
    ("The Pale Deacon", "stitched together with black thread", "Type 3 - Cone Skull", "Butcher Cleaver", "Rusty Shovel", "Bone Clay"),
    ("Hookjaw", "yellowed and smeared with dripping blood", "Type 1 - Lumpy Dome", "Meat Hook", "Harpoon Gun", "Blood Splatter"),
    ("Silo Sam", "caked in mud", "Type 4 - Split Cranium", "Hatchet", "Weed Whacker", "Cornfield"),
    ("Mother's Boy", "smeared with red lipstick", "Type 2 - Melted Lopsided", "Butcher Cleaver", "None", "Bruise Clay"),
    ("The Thirteenth", "polished chrome", "Type 1 - Lumpy Dome", "Golden Machete", "Scythe", "Blood Moon"),
    ("Gristle", "dripping glowing toxic-green slime", "Type 4 - Split Cranium", "Hunting Knife", "Chainsaw", "Swamp Clay"),
    ("Crow Bait", "cracked with a chunk broken away", "Type 2 - Melted Lopsided", "Machete", "Pitchfork", "Cornfield"),
    ("Lantern Jack", "pumpkin orange with a carved glowing grin", "Type 3 - Cone Skull", "Sickle", "Weed Whacker", "Blood Moon"),
    ("Swamp Saint", "overgrown with green moss", "Type 1 - Lumpy Dome", "Bone Saw", "Pitchfork", "Swamp Clay"),
]

STYLE = ("Photograph of a hand-sculpted stop-motion claymation figure, matte plasticine with fingerprints, tool marks "
         "and pressed texture, soft studio lighting, highly detailed, in exactly the style of the reference photos")
CHARACTER = ("A grotesque disfigured old man with an oversized bobble head, mottled skin with age spots, small sunken "
             "bloodshot eyes in swollen red-rimmed lids, a large ear with a fat hanging lobe, thick neck, hunched broad "
             "shoulders, head turned three-quarters toward the viewer's right")
FRAMING = ("Three-quarter view from the hips up, whole head, mask and weapons inside the frame with a little space "
           "above the head, figure centred, square 1:1 composition. His right hand grips the held weapon in a tight "
           "clenched fist seen from the back of the hand, knuckles toward the camera, palm hidden, the blade angled up "
           "and out; his other hand hangs open")
NEGATIVE = ("text, logo, letters, watermark, brand marks, sports team logo, red chevrons or triangles on the mask, "
            "white screaming ghost mask, black hooded robe, pins in a grid, extra fingers, deformed hands, cropped head, "
            "photo of a real person, cartoon outline, flat 2D")
ALL = {"Head": HEAD, "Skin": SKIN, "Hair": HAIR, "Head Mark": HEAD_MARK, "Clothing": {**CLOTH_STD, **CLOTH_RARE},
       "Belt": BELT, "Backdrop": {**BACKDROP, **BACKDROP_RARE}, "Mask": {**MASK_STD, **MASK_RARE},
       "Held Weapon": {**HELD_STD, **HELD_RARE}, "Back Weapon": {**BACK_STD, **BACK_RARE}}


def pick(rng, table):
    vals = list(table)
    return rng.choices(vals, weights=[table[v][0] for v in vals])[0]


def phrase(trait, value):
    return ALL[trait][value][1] if value in ALL[trait] else None


def prompt(a, legendary_finish=None):
    head = [phrase("Head", a["Head"]), phrase("Skin", a["Skin"]), phrase("Hair", a["Hair"]), phrase("Head Mark", a["Head Mark"])]
    if legendary_finish:
        mask = (f"an aged lower-face hockey mask, {legendary_finish}, covering only his nose and mouth, round breathing "
                "holes, moulded beak nose, held by rusty leather straps with a riveted plate and a buckle under the ear, "
                "eyes visible above it, no chevron markings")
    else:
        mask = phrase("Mask", a["Mask"])
    held = a["Held Weapon"]
    if held == "Bare Fist":
        hand = "his right hand is a clenched bare fist, knuckles toward the camera"
    elif held == "Hook Hand":
        hand = "his right hand has been replaced by a rusty iron hook strapped to his forearm"
    else:
        hand = f"his right fist grips {phrase('Held Weapon', held)}"
    body = [f"wearing {phrase('Clothing', a['Clothing'])}", phrase("Belt", a["Belt"]), hand, phrase("Back Weapon", a["Back Weapon"])]
    parts = [STYLE, CHARACTER, ", ".join(p for p in head if p), mask, ", ".join(p for p in body if p),
             phrase("Backdrop", a["Backdrop"]), FRAMING]
    return ". ".join(p[0].upper() + p[1:] for p in parts if p) + "."


def build():
    rng = random.Random(13)
    tokens, seen = [], set()
    for name, finish, head, held, back, bg in LEGENDARY:
        a = {"Tier": "Legendary 1/1", "1/1 Name": name, "Head": head, "Skin": pick(rng, SKIN), "Hair": pick(rng, HAIR),
             "Head Mark": pick(rng, HEAD_MARK), "Mask": f"Hockey Half-Mask ({finish.split(' with')[0].split(',')[0]})",
             "Held Weapon": held, "Back Weapon": back, "Clothing": "Patched Work Jacket", "Belt": "Tool Belt", "Backdrop": bg}
        tokens.append((a, finish))
    def deal(tier):
        while True:
            rare = tier == "Rare"
            a = {"Tier": tier, "Head": pick(rng, HEAD), "Skin": pick(rng, SKIN), "Hair": pick(rng, HAIR),
                 "Head Mark": pick(rng, HEAD_MARK),
                 "Mask": pick(rng, MASK_RARE if rare else MASK_STD),
                 "Held Weapon": pick(rng, HELD_RARE) if rare and rng.random() < .3 else pick(rng, HELD_STD),
                 "Back Weapon": pick(rng, BACK_RARE) if rare and rng.random() < .35 else pick(rng, BACK_STD),
                 "Clothing": pick(rng, CLOTH_RARE) if rare and rng.random() < .35 else pick(rng, CLOTH_STD),
                 "Belt": pick(rng, BELT),
                 "Backdrop": pick(rng, BACKDROP_RARE) if rare and rng.random() < .25 else pick(rng, BACKDROP)}
            if a["Mask"] == "Fanged Killer Clown" and rng.random() < .7:
                a["Clothing"], a["Back Weapon"] = "Bloody Clown Suit", "Circus Mallet"
            if a["Hair"] == "Backwards Cap" and a["Mask"] in ("Burlap Sack Hood", "Rusted Knight Helm"):
                continue
            dna = tuple(sorted((k, v) for k, v in a.items() if k != "Tier"))
            if dna not in seen:
                seen.add(dna)
                return a
    tokens += [(deal("Rare"), None) for _ in range(N_RARE)]
    tokens += [(deal("Standard"), None) for _ in range(TOTAL - N_RARE - len(LEGENDARY))]
    rng.shuffle(tokens)
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for i, (a, finish) in enumerate(tokens, 1):
        seed = rng.randrange(1 << 31)
        name = f"SBN13th #{i}" + (f" - {a['1/1 Name']}" if "1/1 Name" in a else "")
        meta = {"name": name, "seed": seed, "attributes": [{"trait_type": k, "value": v} for k, v in a.items()]}
        json.dump(meta, open(os.path.join(OUT, f"{i}.json"), "w"), indent=2)
        rows.append({"id": i, "name": name, "seed": seed, "prompt": prompt(a, finish), "negative": NEGATIVE, "attributes": a})
    os.makedirs(os.path.join(ROOT, "output", "ai"), exist_ok=True)
    json.dump(rows, open(os.path.join(ROOT, "output", "ai", "manifest-v2.json"), "w"), indent=1)
    report(tokens)


def report(tokens):
    lines = ["# SBN13th v2 rarity", "", "1,300 PFPs: 1,157 Standard, 130 Rare, 13 Legendary 1/1s. Every PFP is unique.", ""]
    rare_only = {k: set(t) for k, t in [("Mask", MASK_RARE), ("Held Weapon", HELD_RARE), ("Back Weapon", BACK_RARE),
                                         ("Clothing", CLOTH_RARE), ("Backdrop", BACKDROP_RARE)]}
    for trait in ["Tier", "Head", "Mask", "Held Weapon", "Back Weapon", "Clothing", "Belt", "Backdrop", "Skin", "Hair", "Head Mark"]:
        c = Counter(a[trait] for a, _ in tokens)
        lines += [f"## {trait}", "", "| Value | Count | Share |", "|---|---|---|"]
        for v, n in c.most_common():
            tag = " (Rare+)" if v in rare_only.get(trait, ()) else ""
            lines.append(f"| {v}{tag} | {n} | {n / len(tokens):.1%} |")
        lines.append("")
    open(os.path.join(OUT, "RARITY-v2.md"), "w").write("\n".join(lines))


if __name__ == "__main__":
    build()
    print("wrote", OUT)
