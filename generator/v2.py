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
import re
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
# Ears (George, 2026-11-13): exactly 130 tokens get stretched gauged earlobes, dealt by ear_pass to tokens not yet rendered.
EARS = {"Natural": (0, ""), "Gauged": (0, "a heavily stretched earlobe on his visible ear holding a large shiny polished silver steel tunnel gauge, a hollow metal ring about an inch wide with flared rims that you can see straight through, hanging just below the ear")}
N_GAUGED = 130
# Bloody bandage head wrap (George, 2026-11-13): an uncommon mask on 40 unrendered tokens, dealt by mask_pass.
MASK_NEW = {"Bloody Bandage Wrap": (0, "his whole head and face wrapped in filthy blood-soaked medical gauze bandages, loosely wound with frayed "
                                       "dangling ends and fresh red blood seeping through, narrow gaps showing his bloodshot eyes and a torn gap over his rotten teeth")}
N_BANDAGE = 40
# Two more original uncommon masks from George's 2026-11-13 band-mask mood board. Broad themes only (pale rubber, seams);
# they deliberately don't copy any band member's signature mask. 25 tokens each, dealt after the bandage wrap.
MASK_NEW2 = {
    "Rubber Seam Face": (0, "a pale grey-green cracked rubber full-face mask with one crude surgical seam of thick black stitches running from the "
                            "scalp down across one cheek, two mismatched ragged eye holes of different sizes and a slack open mouth hole"),
    "Melted Wax Face": (0, "a dirty ivory candle-wax mask that has partly melted, drooping and dripping off one side of his face in thick waxy runs, "
                           "one eye hole stretched long by the melt, his bloodshot eyes peering out"),
}
MASK_NEW.update(MASK_NEW2)
N_NEW2 = 25
# Second mood board (2026-11-13): leather harness hood and flayed-muscle face, as original takes (no steel ball nose,
# no slot-teeth grille, no band colour schemes). 25 tokens each, dealt after MASK_NEW2.
MASK_NEW3 = {
    "Buckled Harness Hood": (0, "a cracked black leather hood stitched from scrap panels, cinched round the skull and jaw by several rusty buckled "
                                "straps, a short zipper on each cheek and a riveted brass vent grille over the mouth, ragged eye holes showing his bloodshot eyes"),
    "Flayed Muscle Face": (0, "a mask sculpted like a skinned face of raw red muscle fibres and pale sinew strands, bone-white cheekbones poking "
                              "through, a lipless grin of crooked yellow teeth, one bloodshot eye glaring through a torn hole"),
}
MASK_NEW.update(MASK_NEW3)

# Female Claysons (George, 2026-11-13): 6 ORIGINAL archetypes loosely inspired by famous horror roles. Each deliberately
# avoids the source character's signature look (no braided-pigtail doll, no platinum-bob android in a bow dress,
# no blonde leather bride, no red bow dress, no white-faced fanged nun). 8 each, all on unrendered Rare tokens.
FEMALE_BASE = ("A grotesque disfigured clay WOMAN (female, not the man in the reference: copy only the reference's clay style, pose and framing) "
               "with an oversized bobble head, mottled skin, small sunken bloodshot eyes in swollen red-rimmed lids, a thin neck and "
               "narrow hunched shoulders, head turned three-quarters toward the viewer's right")
FEMALE = {   # name: (Hair value, hair phrase, Mask value, face phrase, Clothing value, clothing phrase)
    "Cursed Porcelain Doll": ("Lace Bonnet", "a yellowed lace bonnet over a tight auburn bun",
        "Cracked Porcelain Face", "a chipped and cracked porcelain doll face with glossy glass eyes, flaking painted rosy cheeks and a tiny painted smile",
        "Faded Lace Gown", "a faded, mouldy cream lace doll's gown with a high collar"),
    "Drowned Well Girl": ("Soaked Black Veil Hair", "soaked lank black hair hanging down over most of her face, one bloodshot eye showing through",
        "Waterlogged Face", "grey waterlogged wrinkled skin with blue lips and dripping water",
        "Dripping Nightgown", "a dripping torn grey nightgown streaked with mud and pond weed"),
    "Glitch Android": ("Choppy Teal Wig", "a choppy short teal-blue synthetic wig, half torn away to show metal (never red or orange hair, never blonde)",
        "Split Faceplate", "a cracked clay faceplate split open down one cheek to reveal wires, gears and one glowing red LED eye",
        "Pastel Tracksuit", "a stained pastel lilac tracksuit jacket zipped to the chin"),
    "Rotten Bride": ("Wilted Flower Crown", "matted dark brown hair pinned low with a crown of wilted dead flowers (no beehive, no white streaks)",
        "Stitched Bride Face", "crude black stitches across both cheeks, smeared black lipstick and running mascara",
        "Rotting Wedding Gown", "a rotting, blood-spattered ivory wedding gown with a torn veil trailing from her hair"),
    "Farmhouse Smile": ("Straw Sun Bonnet", "a frayed straw sun bonnet tied under the chin",
        "Manic Grin", "a stretched manic too-wide grin of crooked teeth and wide unblinking eyes, freckles and dirt",
        "Gingham Farm Dress", "a faded blue gingham farm dress with a blood-soaked white apron"),
    "Hollow Sister": ("Black Veil", "a long black wimple veil covering her hair",
        "Hollow Grey Face", "a cracked grey clay face with deep empty black eye sockets and a crudely stitched-shut mouth",
        "Tattered Nun Habit", "a tattered black habit with a stained white collar and a rusty chain rosary"),
}
N_FEMALE = 8
# 1/1 "The Grieving Mother" (George, 2026-11-13, loosely inspired by a classic slasher mom). It replaces the unrendered 1/1
# Silo Sam, so there are still 13 Legendaries. Original look: no blue fisherman sweater, no name or likeness of the film character.
MOTHER = ("Silo Sam", {"1/1 Name": "The Grieving Mother", "Character": "The Grieving Mother", "Head": "Female",
          "Hair": "Grey Curled Perm", "Mask": "Mad Mother's Face", "Clothing": "Mustard Cardigan", "Held Weapon": "Machete",
          "Back Weapon": "None", "Belt": "None", "Head Mark": "Clean", "Ears": "Natural", "Backdrop": "Lakeside Cabin"})
FEMALE_EXTRA = {"Grey Curled Perm": "short tight greying curled permed hair", "Mad Mother's Face": "no mask: a sweet middle-aged mother's face twisted with grief and rage, wide wet glaring eyes, a trembling forced smile, blood flecked across her cheek",
                "Mustard Cardigan": "a mustard-yellow hand-knitted cardigan over a ruffled cream blouse, a small gold heart locket on a chain"}
MASK_STD = {
    "Bare Face": (22, "no mask: his disfigured face is bare, small sunken bloodshot eyes in swollen red lids, a crooked broken nose and rotten yellow teeth"),
    "Hockey Half-Mask": (18, "an aged yellowed HALF mask covering ONLY his mouth, chin and the tip of his nose, the top edge sitting just under his eyes, his eyes, brow and forehead completely bare, round breathing holes, random blood splatters (never triangles or stripes), held by rusty leather straps with a riveted plate and a buckle under the ear"),
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
    "Sewn-On Pig Face": (8, "a pink fleshy pig-skin face (real clay pig hide, NOT burlap or fabric) crudely sewn onto his own face with thick black stitches round the edges, a raw pink pig snout, pig ears, blood seeping along the seams, his own eyes staring through"),
    "Zipper Long Nose": (8, "a stitched black leather full-face mask covering his whole face and head, with a long rigid erect pointed nose sticking straight out horizontally toward the viewer's right like a spike, and a metal zipper across the mouth"),
    "Crown of Nails": (8, "no mask: a ring of long rusty nails hammered into his skull all the way round like a crown, blood dripping down his forehead and face from every nail, his disfigured bloodshot face bare below"),
    "Long Nose Latex": (4, "a pale grey latex mask with a long crooked warty nose and a dark slit mouth"),
}
HELD_STD = {
    "Machete": (20, "a long rusty machete dripping blood"), "Butcher Cleaver": (16, "a bloody rusty butcher's cleaver"),
    "Hunting Knife": (14, "a bloody hunting knife"), "Hatchet": (12, "a rusty hatchet with a chipped blade"),
    "Meat Hook": (10, "a big rusty meat hook"), "Sickle": (10, "a rusty curved sickle"),
    "Nail Bat": (8, "a wooden bat studded with bent rusty nails"), "Ice Pick": (6, "a rusty ice pick"), "Bare Fist": (4, None),
    "Chainsaw": (8, "a small rusty one-handed chainsaw with a bloody chain, the bar pointing up and out"),
    "Fish Hook": (8, "a huge rusty barbed fish hook on a short wooden handle, fishing line and a bloody bait scrap dangling from it"),
    "Spear": (8, "a crude spear: a long wooden pole with a rusty jagged blade lashed to the top with wire and rag, held upright with the blade above his shoulder"),
}
HELD_RARE = {"Golden Machete": (40, "a gleaming golden machete dripping blood"), "Bone Saw": (30, "a rusty serrated bone saw"),
             "Hook Hand": (30, None), "Flamethrower": (30, None), "Nail-Knife Glove": (30, None)}
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
             "Harpoon Gun": (30, "a rusty harpoon gun slung on his back"),
             "Fuel Tanks": (0, "twin dented rusty propane fuel tanks strapped to his back on a harness, a rubber hose running from them to the flamethrower")}
CLOTH_STD = {
    "Patched Work Jacket": (22, "a slate-blue clay work jacket with a brown leather collar, stitched leather patches and a grey knit undershirt"),
    "Plaid Flannel": (18, "a grimy plaid flannel shirt"), "Mechanic Coveralls": (14, "stained grey mechanic coveralls"),
    "Grimy Hoodie": (12, "a grimy torn hoodie"), "Butcher Apron": (10, "a blood-stained butcher's apron over a work shirt"),
    "Denim Jacket": (10, "a dirty denim jacket"), "Torn Undershirt": (8, "a stained torn undershirt"), "Trench Coat": (6, "a filthy long trench coat"),
}
# Outfits George added on 2026-11-13. They are dealt in a separate late pass (outfit_pass) so tokens that were
# already rendered (generator/rendered_keep.json) keep their traits and images.
CLOTH_NEW = {
    "Orange Prison Jumpsuit": (16, "a stained bright orange prison convict jumpsuit with the inmate number 666 stencilled in black on a white chest patch (the only lettering in the image)"),
    "Bloody Surgeon Scrubs": (14, "blood-soaked green surgeon's scrubs with a surgical cap and a stained surgical mask hanging round his neck"),
    "Tattered Shirt": (14, "a shredded, ripped and tattered button-up shirt hanging in rags"),
    "Navy Jumpsuit": (5, "a stained one-piece navy blue work jumpsuit with a torn name patch"),
    "Black Jumpsuit": (5, "a grimy one-piece black work jumpsuit with a torn name patch"),
    "Grey Jumpsuit": (5, "a dirty one-piece grey work jumpsuit with a torn name patch"),
    "Tan Blood-Splatter Jumpsuit": (5, "a one-piece tan work jumpsuit covered in fresh blood splatter, with a torn name patch"),
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
# Exclusive scene backdrops George added on 2026-11-13. Dealt by backdrop_pass (separate RNG) only to tokens not
# yet rendered (generator/rendered_keep_bg.json): 30% of Rare and 20% of Standard tokens get one,
# so each scene is uncommon (~2-3%), rarer than the common clay backdrops (6-16%).
SCENE = ", sculpted as a miniature claymation diorama in matte plasticine, softly out of focus behind him, no signs or lettering"
BACKDROP_SCENE = {
    "Haunted Mansion": (1, "a crooked haunted Victorian mansion on a hill at night with dim glowing windows, bare twisted trees and a pale moon" + SCENE),
    "Graveyard": (1, "a foggy moonlit graveyard of cracked tombstones, crooked crosses and dead trees" + SCENE),
    "Lakeside Cabin": (1, "a rundown wooden cabin beside a misty dark lake at dusk with a rotting dock and pine trees" + SCENE),
    "Doctor's Hospital Room": (1, "a grimy abandoned hospital room with a rusty bed, a flickering lamp, an IV stand and blood-smeared tiled walls" + SCENE),
    "Abandoned Laboratory": (1, "an abandoned laboratory with cracked glass jars of murky green liquid, rusty machinery and dangling wires" + SCENE),
    "Radioactive Wasteland": (1, "a toxic wasteland with glowing green puddles, rusted leaking barrels and a smoky orange sky" + SCENE),
    "Nightmare Sequence": (1, "a surreal nightmare dreamscape of melting swirling deep red and purple clay, floating eyeballs and twisted staircases" + SCENE),
}

# 13 Legendary 1/1s: the hockey half-mask in a unique finish, plus unique backdrop/weapon combos
LEGENDARY = [
    ("The Harvester", "rust-stained", "Type 2 - Melted Lopsided", "Sickle", "Scythe", "Cornfield"),
    ("Diamond Wraith", "MASK:Diamond Wraith Mask|a full-face mask completely encrusted with thousands of sparkling cut diamonds and clear crystals, rounded skull-like shape with two deep hollow black eye sockets and a small jagged stitched-shut slit mouth, catching glints of light, no hood", "Type 3 - Cone Skull", "Machete", "Scythe", "Blood Moon"),
    ("Old Gilded", "solid polished gold, gleaming", "Type 1 - Lumpy Dome", "Golden Machete", "Woodcutter Axe", "Slate Clay"),
    ("Cinder", "charred black with glowing ember cracks", "Type 4 - Split Cranium", "Machete", "Chainsaw", "Rust Clay"),
    ("The Pale Deacon", "stitched together with black thread", "Type 3 - Cone Skull", "Butcher Cleaver", "Rusty Shovel", "Bone Clay"),
    ("Hookjaw", "yellowed and smeared with dripping blood", "Type 1 - Lumpy Dome", "Meat Hook", "Harpoon Gun", "Blood Splatter"),
    ("Silo Sam", "caked in mud", "Type 4 - Split Cranium", "Hatchet", "Weed Whacker", "Cornfield"),
    ("The Frontman", "MASK:Frontman Mask|a battered black leather full-face mask with a round rusty microphone grille riveted over the mouth, snapped guitar strings laced across the cheeks like stitches, a dented steel tag stamped 13 on the forehead, small red-rimmed eye holes", "Type 2 - Melted Lopsided", "Nail Bat", "Chainsaw", "Blood Splatter"),
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
FRAMING = ("FACING: exactly like the first reference photo, his body is in three-quarter view and his head and face are "
           "turned about 45 degrees toward the RIGHT side of the image (the viewer's right), nose pointing right; never turned "
           "to the left side and never straight on. Three-quarter view from the hips up, whole head, mask and weapons inside the frame with a little space "
           "above the head, figure centred, square 1:1 composition. His right hand grips the held weapon in a tight "
           "clenched fist seen from the back of the hand, knuckles toward the camera, palm hidden, the blade angled up "
           "and out; his other hand hangs open")
NEGATIVE = ("text, logo, letters, watermark, brand marks, sports team logo, red chevrons or triangles on the mask, full-face goalie mask covering the forehead and eyes, "
            "white screaming ghost mask, black hooded robe, pins in a grid, extra fingers, deformed hands, cropped head, "
            "photo of a real person, cartoon outline, flat 2D, face turned to the left, mirrored pose, long finger blades, clawed glove with four long knives, "
            "red and green striped sweater, brown fedora")
ALL = {"Head": HEAD, "Skin": SKIN, "Hair": {**HAIR, **{v[0]: (0, v[1]) for v in FEMALE.values()}, "Grey Curled Perm": (0, FEMALE_EXTRA["Grey Curled Perm"])}, "Head Mark": HEAD_MARK, "Ears": EARS, "Clothing": {**CLOTH_STD, **CLOTH_NEW, **CLOTH_RARE, **{v[4]: (0, v[5]) for v in FEMALE.values()}, "Mustard Cardigan": (0, FEMALE_EXTRA["Mustard Cardigan"])},
       "Belt": BELT, "Backdrop": {**BACKDROP, **BACKDROP_RARE, **BACKDROP_SCENE}, "Mask": {**MASK_STD, **MASK_RARE, **MASK_NEW, **{v[2]: (0, v[3]) for v in FEMALE.values()}, "Mad Mother's Face": (0, FEMALE_EXTRA["Mad Mother's Face"])},
       "Held Weapon": {**HELD_STD, **HELD_RARE}, "Back Weapon": {**BACK_STD, **BACK_RARE}}


def pick(rng, table):
    vals = list(table)
    return rng.choices(vals, weights=[table[v][0] for v in vals])[0]


def phrase(trait, value):
    return ALL[trait][value][1] if value in ALL[trait] else None


def prompt(a, legendary_finish=None):
    head = [phrase("Head", a["Head"]), phrase("Skin", a["Skin"]), phrase("Hair", a["Hair"]), phrase("Head Mark", a["Head Mark"]), phrase("Ears", a.get("Ears", "Natural"))]
    if legendary_finish and legendary_finish.startswith("MASK:"):
        mask = legendary_finish.split("|", 1)[1]
    elif legendary_finish:
        mask = (f"an aged HALF mask, {legendary_finish}, covering ONLY his mouth, chin and nose with his eyes, brow and forehead "
                "completely bare, round breathing holes, moulded beak nose, held by rusty leather straps with a riveted plate and a buckle under the ear, "
                "eyes visible above it, no chevron markings")
    else:
        mask = phrase("Mask", a["Mask"])
    held = a["Held Weapon"]
    if held == "Bare Fist":
        hand = "his right hand is a clenched bare fist, knuckles toward the camera"
    elif held == "Hook Hand":
        hand = "his right hand has been replaced by a rusty iron hook strapped to his forearm"
    elif held == "Flamethrower":
        hand = ("his right fist grips a crude homemade rusty flamethrower made of welded pipe, a small orange flame "
                "licking from the nozzle, pointed up and away from him")
    elif held == "Nail-Knife Glove":
        hand = ("his right hand wears a thick grimy grey welder's gauntlet with bent rusty nails and short broken kitchen-knife "
                "blades crudely welded and taped onto the knuckles, a clenched spiked fist, knuckles toward the camera")
    else:
        hand = f"his right fist grips {phrase('Held Weapon', held)}"
    body = [f"wearing {phrase('Clothing', a['Clothing'])}", phrase("Belt", a["Belt"]), hand, phrase("Back Weapon", a["Back Weapon"])]
    female = a.get("Character", "Classic") in FEMALE or a.get("Character") == "The Grieving Mother"
    if female:
        head = [phrase("Skin", a["Skin"]), phrase("Hair", a["Hair"])]
    parts = [STYLE, FEMALE_BASE if female else CHARACTER, ", ".join(p for p in head if p), mask, ", ".join(p for p in body if p),
             phrase("Backdrop", a["Backdrop"]), FRAMING]
    text = ". ".join(p[0].upper() + p[1:] for p in parts if p) + "."
    if female:
        for m, f in [(r"\bhis\b", "her"), (r"\bHis\b", "Her"), (r"\bhim\b", "her"), (r"\bhimself\b", "herself"), (r"\bhe\b", "she"), (r"\bHe\b", "She")]:
            text = re.sub(m, f, text)
    return text


def build():
    rng = random.Random(13)
    tokens, seen = [], set()
    for name, finish, head, held, back, bg in LEGENDARY:
        a = {"Tier": "Legendary 1/1", "1/1 Name": name, "Head": head, "Skin": pick(rng, SKIN), "Hair": pick(rng, HAIR),
             "Head Mark": pick(rng, HEAD_MARK), "Mask": finish[5:].split("|")[0] if finish.startswith("MASK:") else f"Hockey Half-Mask ({finish.split(' with')[0].split(',')[0]})",
             "Held Weapon": held, "Back Weapon": back, "Clothing": "Patched Work Jacket", "Belt": "Tool Belt", "Backdrop": bg}
        tokens.append((a, finish))
    def deal(tier):
        while True:
            rare = tier == "Rare"
            a = {"Tier": tier, "Head": pick(rng, HEAD), "Skin": pick(rng, SKIN), "Hair": pick(rng, HAIR),
                 "Head Mark": pick(rng, HEAD_MARK),
                 "Mask": pick(rng, MASK_RARE if rare else MASK_STD),
                 "Held Weapon": pick(rng, HELD_RARE) if rare and rng.random() < .4 else pick(rng, HELD_STD),
                 "Back Weapon": pick(rng, BACK_RARE) if rare and rng.random() < .35 else pick(rng, BACK_STD),
                 "Clothing": pick(rng, CLOTH_RARE) if rare and rng.random() < .35 else pick(rng, CLOTH_STD),
                 "Belt": pick(rng, BELT),
                 "Backdrop": pick(rng, BACKDROP_RARE) if rare and rng.random() < .25 else pick(rng, BACKDROP)}
            if a["Mask"] == "Fanged Killer Clown" and rng.random() < .7:
                a["Clothing"], a["Back Weapon"] = "Bloody Clown Suit", "Circus Mallet"
            if a["Held Weapon"] == "Flamethrower":
                a["Back Weapon"] = "Fuel Tanks"
            if a["Hair"] == "Backwards Cap" and a["Mask"] in ("Burlap Sack Hood", "Crown of Nails"):
                continue
            dna = tuple(sorted((k, v) for k, v in a.items() if k != "Tier"))
            if dna not in seen:
                seen.add(dna)
                return a
    tokens += [(deal("Rare"), None) for _ in range(N_RARE)]
    tokens += [(deal("Standard"), None) for _ in range(TOTAL - N_RARE - len(LEGENDARY))]
    rng.shuffle(tokens)
    outfit_pass(tokens)
    backdrop_pass(tokens)
    ear_pass(tokens)
    mask_pass(tokens)
    female_pass(tokens)
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


def outfit_pass(tokens):
    """Re-deal Clothing from the expanded table for tokens not yet rendered. Rare-only outfits are left alone."""
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep.json"))))
    late = random.Random(2611)
    table = {**CLOTH_STD, **CLOTH_NEW}
    dnas = {tuple(sorted((k, v) for k, v in a.items() if k != "Tier")) for a, _ in tokens}
    for i, (a, finish) in enumerate(tokens, 1):
        if i in keep or finish or a["Clothing"] in CLOTH_RARE:
            continue
        for _ in range(20):
            old = tuple(sorted((k, v) for k, v in a.items() if k != "Tier"))
            new_val = pick(late, table)
            b = dict(a, Clothing=new_val)
            dna = tuple(sorted((k, v) for k, v in b.items() if k != "Tier"))
            if dna == old or dna not in dnas:
                dnas.discard(old); dnas.add(dna); a["Clothing"] = new_val
                break


def backdrop_pass(tokens):
    """Give unrendered tokens a chance at an exclusive scene backdrop. Legendaries keep their own backdrops."""
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_bg.json"))))
    late = random.Random(1313)
    for i, (a, finish) in enumerate(tokens, 1):
        roll, val = late.random(), pick(late, BACKDROP_SCENE)   # always draw, so odds don't depend on the keep list
        if i in keep or finish:
            continue
        if roll < (.3 if a["Tier"] == "Rare" else .2):
            a["Backdrop"] = val   # a new backdrop value can't collide with an existing DNA


def ear_pass(tokens):
    """Every token gets an Ears trait; exactly N_GAUGED unrendered, non-legendary tokens get Gauged."""
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_ears.json"))))
    for a, _ in tokens:
        a["Ears"] = "Natural"
    hidden = {"Burlap Sack Hood", "Zipper Long Nose"}   # these cover the whole head, so a gauge wouldn't show
    pool = [i for i, (a, finish) in enumerate(tokens, 1) if i not in keep and not finish and a["Mask"] not in hidden]
    for i in random.Random(130).sample(pool, N_GAUGED):
        tokens[i - 1][0]["Ears"] = "Gauged"


def mask_pass(tokens):
    """Give N_BANDAGE unrendered, non-legendary tokens the bandage wrap (not over a gauge or a cap, which it would hide)."""
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_ears.json"))))
    pool = [i for i, (a, finish) in enumerate(tokens, 1) if i not in keep and not finish and a["Ears"] == "Natural"
            and a["Hair"] != "Backwards Cap" and a["Mask"] not in MASK_RARE]
    for i in random.Random(1366).sample(pool, N_BANDAGE):
        tokens[i - 1][0]["Mask"] = "Bloody Bandage Wrap"
    pool = [i for i in pool if tokens[i - 1][0]["Mask"] != "Bloody Bandage Wrap"]
    picks = random.Random(2626).sample(pool, N_NEW2 * len(MASK_NEW2))
    for k, i in enumerate(picks):
        tokens[i - 1][0]["Mask"] = list(MASK_NEW2)[k % len(MASK_NEW2)]
    pool = [i for i in pool if i not in set(picks)]
    for k, i in enumerate(random.Random(2727).sample(pool, N_NEW2 * len(MASK_NEW3))):
        tokens[i - 1][0]["Mask"] = list(MASK_NEW3)[k % len(MASK_NEW3)]


def female_pass(tokens):
    """Every token gets a Character trait; N_FEMALE per archetype on unrendered Rare tokens (tier counts stay the same)."""
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_ears.json"))))
    for a, _ in tokens:
        a["Character"] = "Classic"
    pool = [i for i, (a, finish) in enumerate(tokens, 1) if i not in keep and not finish and a["Tier"] == "Rare"
            and a["Ears"] == "Natural" and a["Mask"] not in MASK_NEW]
    for k, i in enumerate(random.Random(6666).sample(pool, N_FEMALE * len(FEMALE))):
        name = list(FEMALE)[k % len(FEMALE)]
        hair, _, mask, _, cloth, _ = FEMALE[name]
        tokens[i - 1][0].update({"Character": name, "Head": "Female", "Hair": hair, "Mask": mask, "Clothing": cloth, "Head Mark": "Clean", "Belt": "None"})
    for i, (a, finish) in enumerate(tokens):
        if a.get("1/1 Name") == MOTHER[0]:
            a.update(MOTHER[1]); tokens[i] = (a, None)   # no hockey-mask finish: her own face is the look


def report(tokens):
    lines = ["# SBN13th v2 rarity", "", "1,300 PFPs: 1,157 Standard, 130 Rare, 13 Legendary 1/1s. Every PFP is unique.", ""]
    rare_only = {k: set(t) for k, t in [("Mask", MASK_RARE), ("Held Weapon", HELD_RARE), ("Back Weapon", BACK_RARE),
                                         ("Clothing", CLOTH_RARE), ("Backdrop", BACKDROP_RARE)]}
    for trait in ["Tier", "Head", "Mask", "Held Weapon", "Back Weapon", "Clothing", "Belt", "Backdrop", "Skin", "Hair", "Head Mark", "Ears", "Character"]:
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
