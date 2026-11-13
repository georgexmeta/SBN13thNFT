"""Turn every token's traits into an image-generation prompt anchored to George's master reference.

    python3 generator/prompts.py            # writes output/ai/manifest.json and manifest.csv

Each prompt = locked STYLE + locked CHARACTER + one phrase per trait + framing. The master reference image is
passed to the image tool as a character/style reference on every call, and each token gets a fixed seed, so
re-running a token gives the same picture.
"""
import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLL = os.path.join(ROOT, "output", "collection")
OUT = os.path.join(ROOT, "output", "ai")

STYLE = ("Photograph of a hand-sculpted stop-motion claymation figure, matte plasticine with visible fingerprints, "
         "tool marks and pressed texture, soft studio lighting, shallow depth of field, highly detailed, "
         "pressed-clay backdrop with thumbprint swirls")
FACE_LOCK = ("Keep the exact same face sculpt, head proportions and character from the second reference image. ")
CHARACTER = ("a grotesque, disfigured old man with a huge lumpy bald bobble-head skull covered in bumps and dents, "
             "mottled skin with age spots, raised clay forehead wrinkles, small sunken bloodshot eyes in swollen "
             "red-rimmed lids, thick neck, head turned three-quarters toward the viewer's right")
FRAMING = ("three-quarter view from the waist up, the whole head and weapon inside the frame with space above the head, "
           "figure centred, square 1:1 profile picture composition. Hand pose: any held weapon is gripped in a tight clenched fist seen "
           "from the back of the hand, the four knuckles and the back of the hand face the camera, fingers wrap around the handle on "
           "the far side and are hidden, the palm is not visible")
NEGATIVE = ("ape, monkey, gorilla, cartoon outline, flat 2D, anime, text, watermark, logo, signature, "
            "red chevrons, red triangle markings, extra fingers, deformed hands, cropped head")

BG = {
    "Bone": "pale bone-white", "Rust": "rusty orange-brown", "Fog Grey": "foggy grey", "Dusty Teal": "dusty teal",
    "Swamp Green": "swamp green", "Bruise Purple": "bruise purple", "Blood Orange": "blood orange",
    "Toxic Slime": "toxic slime green with dripping goo", "Blood Splatter": "cream with blood-red dripping splatter",
    "Mustard": "mustard yellow", "Blood Red": "deep blood red", "Midnight": "midnight navy with tiny clay stars",
    "Cornfield": "cornfield of dry clay corn stalks", "Blood Drip": "cream with thick blood dripping from the top",
    "Full Moon": "night sky with a big cratered clay full moon", "Gold": "burnished gold",
}
SKIN = {
    "Corpse Grey": "corpse-grey", "Ruddy": "ruddy red-pink", "Pale Wax": "pale waxy", "Pink Flesh": "pink flesh-toned",
    "Leather": "tanned leathery brown", "Sallow": "sallow yellowish", "Radioactive": "glowing radioactive green",
    "Albino": "chalk-white albino", "Bloodless Blue": "bloodless pale blue", "Charred": "charred black with glowing ember cracks",
    "Gilded": "metallic gold-leafed",
}
SWELL = {"Mild": "mildly swollen features", "Lumpy": "lumpy swollen features", "Grotesque": "grotesquely swollen, bulging features"}
EAR = {"Normal": "a large ear with a fat hanging lobe", "Cauliflower": "a crumpled cauliflower ear",
       "Torn": "a torn, ragged ear", "Gauged": "a stretched earlobe with a large tunnel gauge"}
EYES = {
    "Droopy Mismatch": "droopy mismatched eyes, one bigger than the other", "Lazy Eye": "one lazy eye drifting sideways",
    "Sunken Socket": "deeply sunken eye sockets", "Swollen Shut": "one eye swollen shut, the other squinting",
    "Pinprick": "wide staring eyes with pinprick pupils", "Hollow Sockets": "empty black hollow eye sockets",
    "Glowing Red": "glowing red eyes", "Glowing Green": "glowing green eyes",
    "Popped Out": "one eyeball popped out of its socket hanging on a stalk",
    "Cyborg Eye": "one eye replaced by a bolted steel cyborg eye with a glowing red lens",
    "Missing Left Eye": "the left eye missing, a stitched scarred socket", "Missing Right Eye": "the right eye missing, a stitched scarred socket",
}
EYE_COLOR = {"Swamp Green": "swamp-green irises", "Ice Blue": "ice-blue irises", "Mud Brown": "muddy brown irises",
             "Hazel": "hazel irises", "Steel Grey": "steel-grey irises", "Jaundice Yellow": "jaundiced yellow irises",
             "Mismatched": "one ice-blue and one brown iris", "Milky White": "milky white cataract irises", "None": ""}
BROWS = {"Bushy": "bushy clay eyebrows", "None": "no eyebrows", "Scarred": "a scar slicing through one eyebrow"}
NOSE = {"Bulbous": "a big bulbous red-tipped nose", "Smashed Flat": "a smashed, flattened crooked nose",
        "Split Nostril": "a split nostril", "Missing": "a missing nose, just a raw hole"}
MOUTH = {"Crooked Grin": "a crooked grin with chunky yellow rotten teeth", "Snarl": "a snarling mouth with gapped yellow teeth",
         "Slack Jaw": "a slack open jaw with a few rotten teeth", "Lipless": "lipless exposed teeth and gums",
         "Stitched Shut": "a mouth stitched shut with thick thread"}
SHAPE = {"Swollen Dome": "a tall swollen dome skull", "Brow Bulge": "a heavy bulging brow", "Lopsided": "a lopsided skull",
         "Flat Top": "a flat-topped skull", "Cone Head": "a cone-shaped skull", "Split Skull": "a skull with a deep split crease",
         "Tumor Cluster": "a cluster of blended lumps on the skull"}
HAIR_C = {"Ginger": "ginger", "Dirty Blonde": "dirty blonde", "Greasy Black": "greasy black", "Ash Grey": "ash-grey",
          "Mud Brown": "mud-brown", "Blood-Matted": "blood-matted"}
CLOTH = {
    "Denim Shirt": "a dirty denim work shirt", "Chore Coat": "a worn canvas chore coat",
    "Stained Undershirt": "a stained, torn undershirt", "Butcher Apron": "a blood-stained butcher's apron",
    "Grey Hoodie": "a grimy grey hoodie", "Black Hoodie": "a grimy black hoodie", "Maroon Hoodie": "a grimy maroon hoodie",
    "Khaki Trench Coat": "a khaki trench coat", "Black Trench Coat": "a black trench coat", "Olive Trench Coat": "an olive trench coat",
    "Clown Suit": "a baggy bloody harlequin clown suit, red and cream halves with polka dots, a ruffled collar and pom-pom buttons",
    "Torn White Tee": "a torn white t-shirt", "Torn Black Tee": "a torn black t-shirt", "Torn Army Tee": "a torn army-green t-shirt",
}
DETAIL = {"Rusty Nails": "bent rusty nails hammered unevenly into the top and back of his skull with blood weeping around them", "None": "", "Wart": "a hairy wart", "Veins": "bulging blue forehead veins", "Boils": "a few angry boils",
          "Stitches": "a stitched gash", "Burn Scar": "a melted burn scar"}
WEAPON = {
    "None": "both hands empty, one hanging open",
    "Hunting Knife": "his right fist, knuckles facing the viewer, grips a bloody hunting knife held up and out",
    "Machete": "his right fist, knuckles facing the viewer, grips a long rusty machete dripping blood, blade angled up and out",
    "Golden Machete": "his right fist, knuckles facing the viewer, grips a gleaming golden machete held up and out",
    "Butcher Knife": "his right fist, knuckles facing the viewer, grips a bloody butcher's cleaver held up and out",
    "Fish Hook": "his right fist, knuckles facing the viewer, holds a huge rusty fish hook",
    "Pitchfork": "a rusty pitchfork slung on his back, tines rising above his shoulder",
    "Weed Whacker": "a rusty backpack weed whacker strapped to his back with padded harness straps, the trimmer head rising above his shoulder, grass clippings on his sleeve",
}
BANDANA = {"None": "", "Red Bandana": "a red bandana tied over his nose and mouth", "Black Bandana": "a black bandana tied over his nose and mouth",
           "Blue Bandana": "a navy paisley bandana tied over his nose and mouth", "Faded Paisley": "a faded paisley bandana tied over his nose and mouth"}
# 1/1 masks: the lower-face hockey mask from George's mask reference, each in its own finish (no chevron markings)
MASK = ("an aged lower-face hockey mask covering only his nose and mouth, starting just under the eyes, moulded beak "
        "nose, rows of round breathing holes, held on by rusty worn leather straps with a riveted metal plate at the "
        "temple and a metal buckle under the ear")
MASK_FINISH = {
    "Chrome Mask": "polished chrome", "Bloody Mask": "yellowed and smeared with dripping blood", "Broken Mask": "cracked with a chunk broken away",
    "Gold Mask": "gold", "Charred Mask": "charred black with glowing ember cracks", "Bone Mask": "bone-white and cracked",
    "Rusted Mask": "rust-stained", "Stitched Mask": "stitched together with black thread", "Muddy Mask": "caked in mud",
    "Lipstick Mask": "smeared with red lipstick", "Toxic Mask": "dripping glowing toxic green slime",
    "Jack-o'-Lantern Mask": "pumpkin orange with a carved glowing grin", "Mossy Mask": "overgrown with green moss",
}


# Rare-only masks (130 Rare tokens): original designs, full-face unless noted
RARE_MASK = {
    "Patchwork Mask": "a patchwork mask of stitched burlap and riveted scrap-metal plates, round brass goggle eyes with red lenses, a wire-stitched mouth, a leather strap with a buckle over the crown",
    "Burlap Pig Mask": "a stitched burlap pig mask with frayed edges, floppy burlap ears, a pink clay pig snout, a blocky burlap-toothed grin, a leather strap with a buckle over the crown",
    "Gas Mask": "a black rubber respirator gas mask over his nose and mouth with a round olive filter canister and ribbed hose, eyes visible above it",
    "Iron Plate Mask": "HE WEARS A MASK: a heavy riveted rusty iron plate mask strapped over his nose, mouth and chin, with vertical grille slots over the mouth and rivets round the edge, eyes visible above it",
    "Sack Hood": "a filthy burlap sack hood pulled over his whole head with ragged eye holes, a cross-stitched mouth and a rope tied round the neck",
    "Zipper Leather Mask": "a stitched black leather full-face mask with laced seams and a metal zipper across the mouth",
    "Clown Mask": "a cracked white latex clown mask with black diamond eye paint, a red bulb nose and a painted red grin",
    "Long Nose Mask": "a pale grey latex full-face mask with a long crooked warty nose and a dark slit mouth",
    "Killer Clown Mask": "a crazed killer clown mask with a slashed red grin full of fangs dripping blood, black diamond eye paint, a red bulb nose and wild green and red hair puffs",
}


def hair(a):
    h, c = a["Hair"], HAIR_C.get(a["Hair Color"], "")
    if h == "Bald":
        return "bald with a few grey side tufts above the ears"
    if h == "Greasy Comb-over":
        return f"a greasy {c} comb-over"
    if h == "Patchy Tufts":
        return f"patchy {c} hair tufts"
    if h == "Backwards Cap":
        return "a dirty backwards baseball cap"
    return ""


def clothing(a):
    c = a["Clothing"]
    if c.endswith("Flannel"):
        return f"a grimy {c.split()[0].lower()} plaid flannel shirt"
    return CLOTH.get(c, c.lower())


def prompt(a):
    face = [SHAPE[a["Head Shape"]], SKIN[a["Skin Tone"]] + " clay skin", SWELL[a["Swelling"]], EAR[a["Ear"]],
            BROWS[a["Brows"]], DETAIL[a["Skin Detail"]], hair(a)]
    masked = a.get("Mask", "None") not in ("None", None)
    if a.get("Mask") in RARE_MASK:
        face.append(RARE_MASK[a["Mask"]])
        if "visible above" in RARE_MASK[a["Mask"]]:
            face.append(EYES[a["Eyes"]])
    elif masked:
        face.append(f"{MASK}, {MASK_FINISH[a['Mask']]}")
        face.append(EYES[a["Eyes"]] + (", " + EYE_COLOR[a["Eye Color"]] if EYE_COLOR.get(a["Eye Color"]) else "") + ", visible above the mask")
    else:
        face += [EYES[a["Eyes"]], EYE_COLOR.get(a["Eye Color"], ""), NOSE[a["Nose"]]]
        face.append(BANDANA[a["Bandana"]] if a["Bandana"] != "None" else MOUTH[a["Mouth"]])
    body = [f"wearing {clothing(a)}", WEAPON[a["Weapon"]]]
    if a.get("Back Weapon") == "Circus Mallet":
        body.append("a giant red-and-cream striped circus mallet slung behind his back, its head above his shoulder")
    parts = [STYLE, CHARACTER, ", ".join(p for p in face if p), ", ".join(body), f"{BG[a['Background']]} backdrop", FRAMING]
    return ". ".join(parts) + "."


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for i in range(1, 1301):
        m = json.load(open(os.path.join(COLL, f"{i}.json")))
        a = {x["trait_type"]: x["value"] for x in m["attributes"]}
        rows.append({"id": i, "name": m["name"], "seed": m["seed"] % 2 ** 31, "reference": "george-master-reference.jpg",
                     "prompt": prompt(a), "negative": NEGATIVE, "attributes": a})
    json.dump(rows, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
    with open(os.path.join(OUT, "manifest.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "seed", "reference", "prompt", "negative"])
        for r in rows:
            w.writerow([r["id"], r["name"], r["seed"], r["reference"], r["prompt"], r["negative"]])
    print(f"{len(rows)} prompts -> {OUT}")


if __name__ == "__main__":
    main()
