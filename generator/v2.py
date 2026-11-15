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
# Hair for ordinary women (woman_pass). Short or tied back, to fit the no-long-hair look.
HAIR_WOMAN = {
    "Greasy Bob": (30, "a greasy chin-length black bob"), "Messy Grey Bun": (25, "thin grey hair scraped into a messy bun"),
    "Matted Pixie Cut": (20, "a matted short auburn pixie cut"), "Thinning Pin Curls": (15, "thinning grey pin curls showing scalp"),
    "Buzzed Scalp": (10, "a patchy buzzed scalp"),
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
# Roadside clown touches (George, 2026-11-14): an original grimy roadside killer-clown vibe. Deliberately NOT any film
# character: no white face with blue eye diamonds, no stars-and-stripes, no top hat with stars, never a character name.
# 25 unrendered Classic tokens get each piece, dealt independently by clown_pass.
CLOWN = {
    "Mask": ("Smeared Greasepaint", "no mask: cheap yellowed greasepaint smeared over his face, sloppy black rings round his eyes, a crooked painted "
             "grin in chipped green paint over rotten brown teeth, sweat streaks through the paint"),
    "Hair": ("Battered Top Hat", "a battered dented black top hat with a torn brim and a faded checkered band, tufts of greasy grey hair under it"),
    "Clothing": ("Carnival Barker Vest", "a filthy mustard-and-maroon striped carnival barker vest over a yellowed collarless shirt, a crooked polka-dot bow tie"),
}
N_CLOWN = 25
# Slasher homage Uncommons (George, 2026-11-14). Original designs that nod to classic slashers without copying them:
# no film names, no elongated white screaming ghost mask with black drip eyes, no white Shatner-style mask with dark hair,
# no red-haired doll in overalls. 25 unrendered tokens each, dealt by homage_pass.
HOMAGE_MASK = {
    "Moaning Paper Mask": "a cracked grey papier-mache mask with a crooked moaning open mouth and two round hollow eye holes, under a ragged "
                          "grey burlap hood (not white, not a long drooping face, no black drips)",
    "Stitched Toy Face": "a cracked hard-plastic toy doll face crudely sewn back together with thick black criss-crossing stitches and scars, "
                         "painted freckles and one chipped glass eye",
    "Blank Bone Mask": "a smooth featureless bone-grey rubber mask with narrow dark slit eyes, no nose detail and no expression, faint "
                       "hairline cracks across it (bald, no hair on the mask)",
}
HOMAGE_CLOTH = ("Bloody Chef Smock", "a heavy blood-soaked white double-breasted chef's smock with rolled sleeves and a crumpled "
                "red neckerchief")
N_HOMAGE = 25
# Two more Uncommon scene backdrops (George, 2026-11-14), kept separate from BACKDROP_SCENE so earlier picks don't shift.
SCENE2 = {
    "Killer Circus": "a rotting abandoned circus big top at night with a torn red-and-yellow striped tent, a broken carousel horse, flickering "
                     "bulb strings and a blood-smeared ticket booth, sculpted as a miniature claymation diorama in matte plasticine, "
                     "softly out of focus behind him, no signs or lettering",
    "Insane Asylum": "a derelict insane asylum corridor with peeling green tiles, a rusty wheelchair, a padded cell door hanging open and "
                     "flickering fluorescent tubes, sculpted as a miniature claymation diorama in matte plasticine, softly out of focus "
                     "behind him, no signs or lettering",
}
N_SCENE2 = 25
# Very exclusive Jail Cell backdrop (George, 2026-11-14): exactly 13 unrendered, non-legendary tokens.
JAIL = ("Jail Cell", "a grimy jail cell with rusty iron bars, a cracked concrete wall scratched with tally marks, a dented metal "
        "bunk and a single bare hanging bulb, sculpted as a miniature claymation diorama in matte plasticine, softly out of focus behind him, no signs or lettering")
N_JAIL = 13
# 1/1 "The Grieving Mother" (George, 2026-11-13, loosely inspired by a classic slasher mom). It replaces the unrendered 1/1
# Silo Sam, so there are still 13 Legendaries. Original look: no blue fisherman sweater, no name or likeness of the film character.
MOTHER = ("Silo Sam", {"1/1 Name": "The Grieving Mother", "Character": "The Grieving Mother", "Head": "Female",
          "Hair": "Grey Curled Perm", "Mask": "Mad Mother's Face", "Clothing": "Mustard Cardigan", "Held Weapon": "Machete",
          "Back Weapon": "None", "Belt": "None", "Head Mark": "Clean", "Ears": "Natural", "Backdrop": "Lakeside Cabin"})
# 1/1 "The Prom Queen" (George, 2026-11-14): an original bloody-prom telekinetic, focus on psychic power. Replaces the
# George (final): she replaces the unrendered 1/1 Crow Bait, keeping 13 Legendaries. Done in prom_pass, after every
# other late pass, so their picks don't shift. Never the film character's name; mint-green gown and dark curls, not her look.
PROM = ("Crow Bait", {"1/1 Name": "The Prom Queen", "Character": "The Prom Queen", "Head": "Female",
        "Hair": "Blood-Matted Curls", "Mask": "Psychic Glare", "Clothing": "Blood-Drenched Prom Gown", "Held Weapon": "Telekinesis",
        "Back Weapon": "None", "Belt": "None", "Head Mark": "Clean", "Ears": "Natural", "Backdrop": "Burning Gym"})
# 1/1 "The Retro Slasher" (George, 2026-11-14): an original take on a retro 8-bit-era slasher toy, inspired by an old
# video-game figure but not its character: never that name, no chevrons, own mask markings, a half mask only. Replaces
# the unrendered male 1/1 Lantern Jack, keeping 13 Legendaries. Done in retro_pass, after every other pass, so nothing shifts.
RETRO = ("Lantern Jack", {"1/1 Name": "The Retro Slasher", "Head": "Type 1 - Lumpy Dome", "Skin": "Icy Retro Blue", "Hair": "Bald",
         "Head Mark": "Clean", "Ears": "Natural", "Mask": "Retro Blue Half-Mask", "Held Weapon": "Golden Machete",
         "Back Weapon": "Golden Retro Axe", "Clothing": "Tattered Bone Jumpsuit", "Belt": "Golden Neck Chains", "Backdrop": "Pixel Cabin"})
RETRO_EXTRA = {
    "Skin": ("Icy Retro Blue", "pale icy powder-blue clay skin all over, like a faded vintage toy"),
    "Mask": ("Retro Blue Half-Mask", "a chunky pale powder-blue HALF mask that covers ONLY the lower half of his face, like the bottom half of a "
             "goalie mask: its top edge runs straight across the bridge of his nose just under his eyes, so both eyes, eyelids, brow and "
             "the whole forehead and bald dome are bare clay skin; rows of round black breathing holes over the mouth and chin, decorated "
             "ONLY with a few small round violet dots, no lines, no stripes, no triangles, held by a thin purple strap"),
    "Clothing": ("Tattered Bone Jumpsuit", "a rotten, torn violet-purple jumpsuit in shreds, with big ragged holes across the chest showing his "
                 "exposed bony ribcage in pale bone-white clay, and the sleeves torn away so his forearms show bare skeletal arm bones, "
                 "bits of rotting flesh at the edges"),
    "Belt": ("Golden Neck Chains", "heavy gleaming solid gold chains looped around his neck and hanging down over his chest"),
    "Back Weapon": ("Golden Retro Axe", "a gleaming solid gold axe strapped across his back, the gold blade rising above his shoulder"),
    "Backdrop": ("Pixel Cabin", "the inside of a creepy cabin built like an old 8-bit video game room: chunky stepped pixel-block walls of "
                 "faded wooden planks, a square window with a blocky pixel moon, a flat dark floor, every edge stair-stepped like big "
                 "pixels, sculpted as a miniature claymation diorama in matte plasticine, softly out of focus behind him, no signs, "
                 "lettering, score or game interface"),
}
# Horror-icon homage Uncommons (George, 2026-11-14: "make them a part of the uncommon traits & spread them across others"):
# original takes on a hook-hand bee slasher, doll-masked clone women and a winged cornfield creeper. Never the film names or
# exact looks. Dealt by icon_pass after every other pass, 25 unrendered tokens each, one new trait per token. The bee-slasher
# and clone-twin traits come with deep brown skin (George asked for Black slashers).
ICON_TRAITS = [("Mask", "Honeycomb Half-Mask"), ("Clothing", "Ragged Plum Greatcoat"), ("Mask", "Cracked Doll Mask"),
               ("Clothing", "Rust-Red Boiler Suit"), ("Held Weapon", "Rusty Shears"), ("Mask", "Needle-Tooth Snarl"),
               ("Back Weapon", "Leathery Bat Wings")]
ICON_BROWN = {"Honeycomb Half-Mask", "Ragged Plum Greatcoat", "Cracked Doll Mask", "Rust-Red Boiler Suit", "Rusty Shears"}
ICON_EXTRA = [
    ("Skin", "Deep Brown", "deep dark-brown clay skin"),
    ("Mask", "Honeycomb Half-Mask", "a golden beeswax HALF mask moulded like honeycomb covering ONLY his mouth, chin and nose with his eyes, brow and "
             "forehead bare, hexagonal comb cells oozing honey, a few small clay bees crawling over the mask and his cheek"),
    ("Mask", "Cracked Doll Mask", "a cracked white porcelain doll-face mask over his whole face, rosy painted cheeks, tiny painted red lips, "
             "empty black eye holes, a long hairline crack running across it"),
    ("Mask", "Needle-Tooth Snarl", "no mask: a gaunt creature face with a huge lipless mouth full of rows of jagged needle teeth, a flat slitted "
             "nose, small glinting black eyes and wiry tufts of hair"),
    ("Held Weapon", "Rusty Shears", "a pair of long rusty tailor's shears with the blades open, dripping blood"),
    ("Held Weapon", "Bone Axe", "a crude hand-made axe with a gnarled bone handle and a jagged rusty blade"),
    ("Back Weapon", "Leathery Bat Wings", "huge tattered leathery bat-like wings growing from his back, folded up behind his shoulders with "
                    "clawed tips rising above his head"),
    ("Clothing", "Ragged Plum Greatcoat", "a long battered dark plum greatcoat with a ragged high collar, honey stains down the front and a "
                 "few clay bees crawling on the shoulder"),
    ("Clothing", "Rust-Red Boiler Suit", "a faded rust-red boiler suit, torn at one knee and spattered with blood"),
    ("Backdrop", "Condemned Tenement", "a dim condemned tenement stairwell with peeling paint, boarded windows and honeycomb dripping in the "
                 "corners, sculpted as a miniature claymation diorama in matte plasticine, softly out of focus behind him, no graffiti, signs or lettering"),
    ("Backdrop", "Mirror Maze", "a dim funhouse hall of mirrors reflecting her silhouette into endless copies, sculpted as a miniature "
                 "claymation diorama in matte plasticine, softly out of focus behind him, no signs or lettering"),
]
# 1/1 "Madame Mortis" (George, 2026-11-15): a towering goth femme-fatale slasher with death nails, inspired by a video-game
# villain but not her: no character name, no cream gown, no pearl choker, black veiled hat instead. Replaces a male 1/1
# (George's pick) in duchess_pass, after every other pass, so nothing else shifts. 13 Legendaries.
DUCHESS = ("Swamp Saint", {"1/1 Name": "Madame Mortis", "Character": "Madame Mortis", "Head": "Female", "Skin": "Ashen Grey",
           "Hair": "Veiled Mourning Hat", "Head Mark": "Clean", "Ears": "Natural", "Mask": "Blood-Red Smile",
           "Held Weapon": "Death Nails", "Back Weapon": "None", "Clothing": "White Lace Gown", "Belt": "Garnet Choker",
           "Backdrop": "Candlelit Castle Hall"})
DUCHESS_EXTRA = [
    ("Skin", "Ashen Grey", "ashen grey-white clay skin"),
    ("Hair", "Veiled Mourning Hat", "short glossy black finger-waved curls under an enormous wide-brimmed black mourning hat with a torn black lace veil"),
    ("Mask", "Blood-Red Smile", "no mask: a towering elegant woman's face with high sharp cheekbones, heavy dark eye makeup, cruel narrowed eyes "
             "and a wide wicked smile of glossy blood-red lips"),
    ("Clothing", "White Lace Gown", "an elegant fitted white gown with a low sweetheart neckline showing some cleavage, puffed shoulders, black lace trim and a black silk rose at the waist, a few spatters of blood"),
    ("Belt", "Garnet Choker", "a tight choker of dark blood-red garnets"),
    ("Backdrop", "Candlelit Castle Hall", "a dark carved-wood gothic castle hall lit by tall dripping candles in iron sconces, sculpted as a miniature "
                 "claymation diorama in matte plasticine, softly out of focus behind her, no signs or lettering"),
]
# 1/1 "Cinder Doll" (George, 2026-11-15, final 1/1): a burned killer toy doll, inspired by a charred doll figure but
# not that character: no red hair, no denim overalls, no striped shirt, no toy box or brand. Replaces Cinder (George's
# pick) in doll_pass, after every other pass. 13 Legendaries.
DOLL = ("Cinder", {"1/1 Name": "Cinder Doll", "Character": "Cinder Doll", "Head": "Doll", "Skin": "Charred Plastic",
        "Hair": "Singed Yarn Tufts", "Head Mark": "Clean", "Ears": "Natural", "Mask": "Melted Doll Face", "Held Weapon": "Bloody Kitchen Knife",
        "Back Weapon": "None", "Clothing": "Scorched Corduroy Dungarees", "Belt": "None", "Backdrop": "Burnt Dollhouse"})
DOLL_BASE = ("A small evil child's toy doll come to life, a burned killer doll with a big round doll head, short stubby limbs and "
             "plastic doll hands, head turned three-quarters toward the viewer's right")
DOLL_EXTRA = [
    ("Skin", "Charred Plastic", "blistered charred black plastic skin, crusted and cracked by fire, with glimpses of pale melted vinyl underneath"),
    ("Hair", "Singed Yarn Tufts", "a few singed sooty black yarn hair tufts stuck to the scalp"),
    ("Mask", "Melted Doll Face", "no mask: a melted burned doll face, one huge bulging cracked glass doll eye staring out, the other eye socket "
             "a burnt hollow, a lipless stitched grin of tiny white doll teeth"),
    ("Held Weapon", "Bloody Kitchen Knife", "a big bloody kitchen knife"),
    ("Clothing", "Scorched Corduroy Dungarees", "tiny tattered mustard-brown corduroy dungarees with a bib pocket and frayed patches, scorched black "
                 "at the edges, over a sooty little turtleneck"),
    ("Backdrop", "Burnt Dollhouse", "the inside of a giant child's dollhouse: pastel flowered wallpaper streaked with soot and scorch marks, toy blocks, "
                 "a tiny rocking horse and a broken toy chair, sculpted as a miniature claymation diorama in matte plasticine, softly out of focus "
                 "behind him, no signs or lettering"),
]
# 1/1 "The Collector" (George, 2026-11-15, his own reference figure): bearded trucker-cap man with bulging eyes holding an
# original goalie-mask orb and a rusty hatchet. No lettering on shirt or cap, no Poke Ball split or button, no chevrons.
# Replaces The Thirteenth (George's pick) in collector_pass, after every other pass. 13 Legendaries.
COLLECTOR = ("The Thirteenth", {"1/1 Name": "The Collector", "Character": "Classic", "Head": "Type 1 - Lumpy Dome", "Skin": "Flesh Pink",
             "Hair": "Worn Trucker Cap", "Head Mark": "Clean", "Ears": "Natural", "Mask": "Bearded Bulging Stare",
             "Held Weapon": "Mask Orb and Hatchet", "Back Weapon": "None", "Clothing": "Worn Leather Jacket", "Belt": "None",
             "Backdrop": "Terracotta Clay"})
COLLECTOR_EXTRA = [
    ("Hair", "Worn Trucker Cap", "a dirty, worn plain beige trucker cap with a mesh back, completely blank with no logo, signatures or writing, "
             "messy grey hair sticking out at the sides"),
    ("Mask", "Bearded Bulging Stare", "no mask: a weathered wrinkled face with huge round bulging staring eyes in baggy lids, a big nose and a "
             "scraggly grey-brown beard and moustache"),
    ("Clothing", "Worn Leather Jacket", "a battered, scuffed black leather jacket with a zip front, open over a plain faded grey T-shirt with "
                 "no lettering or print"),
    ("Backdrop", "Terracotta Clay", "a plain textured terracotta-orange pressed clay backdrop"),
]
# "The Ringmistress" (George, 2026-11-14): a 7th female exclusive, an original ADULT woman killer clown inspired by a
# horror clown photo but not its character: no black-and-white split costume, no mini top hat, no black lips.
# 8 unrendered Rare tokens, dealt by ring_pass after every other pass so earlier picks don't shift.
RINGMISTRESS = {"Character": "The Ringmistress", "Head": "Female", "Hair": "Frizzed Auburn Bunches", "Mask": "Cracked Clown Paint",
                "Clothing": "Rotten Ruffle Pierrot Dress", "Belt": "None", "Head Mark": "Clean"}
FEMALE_EXTRA = {"Grey Curled Perm": "short tight greying curled permed hair", "Mad Mother's Face": "no mask: a sweet middle-aged mother's face twisted with grief and rage, wide wet glaring eyes, a trembling forced smile, blood flecked across her cheek",
                "Frizzed Auburn Bunches": "frizzy matted auburn hair in two lopsided bunches tied with dirty ribbon",
                "Cracked Clown Paint": "no mask: a grown woman's face in cracked chalky clown greasepaint, arched painted eyebrows, smeared mauve diamonds over wild yellow eyes, a huge manic grin of rotten jagged brown teeth smeared with blood",
                "Rotten Ruffle Pierrot Dress": "a filthy dusty-rose and mustard checkered pierrot dress with a big wilted ruffled collar and two moth-eaten pompom buttons, spattered with blood",
                "Blood-Matted Curls": "dark brown curls matted with dripping blood under a crooked rhinestone tiara",
                "Psychic Glare": "no mask: a teenage girl's face drenched in thick dripping blood, wide unblinking eyes glowing pure white with psychic power, a cold blank stare",
                "Blood-Drenched Prom Gown": "a ruffled pale mint-green prom gown soaked head to toe in dripping blood, a crushed corsage on her wrist",
                "Burning Gym": "a burning school gym at night with flames, collapsing streamers and a toppled stage, sculpted as a miniature claymation diorama in matte plasticine, softly out of focus behind her, no signs or lettering",
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
    "Chainsaw": (8, "a rusty chainsaw with a bloody chain"),
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
    "Navy Jumpsuit": (5, "a stained one-piece navy blue work jumpsuit with a small blank torn cloth chest patch (no lettering on it)"),
    "Black Jumpsuit": (5, "a grimy one-piece black work jumpsuit with a small blank torn cloth chest patch (no lettering on it)"),
    "Grey Jumpsuit": (5, "a dirty one-piece grey work jumpsuit with a small blank torn cloth chest patch (no lettering on it)"),
    "Tan Blood-Splatter Jumpsuit": (5, "a one-piece tan work jumpsuit covered in fresh blood splatter, with a small blank torn cloth chest patch (no lettering on it)"),
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
FRAMING_TWO_HANDS = FRAMING.split(" His right hand grips")[0] + (" Both hands hold the chainsaw firmly, one on the rear handle "
                                                              "and one on the front handle; neither hand hangs empty")
FRAMING_NAILS = FRAMING.split(" His right hand grips")[0] + " Both hands are raised and fully visible inside the frame, all ten blade nails spread; neither hand hangs down or is hidden"
FRAMING_MOLOTOV = FRAMING.split(" His right hand grips")[0] + " Both fists are raised in front of him, each gripping a lit Molotov cocktail by the neck, knuckles toward the camera; neither hand hangs empty"
FRAMING_COLLECTOR = FRAMING.split(" His right hand grips")[0] + " Both hands are full: the orb held out in one hand toward the viewer, the hatchet gripped in the other"
FRAMING_PSYCHIC = FRAMING.split(" His right hand grips")[0] + " Both hands are raised, empty, channelling psychic force; no weapon in her hands."
NEGATIVE = ("text, logo, letters, watermark, brand marks, sports team logo, red chevrons or triangles on the mask, full-face goalie mask covering the forehead and eyes, "
            "white screaming ghost mask, black hooded robe, pins in a grid, extra fingers, deformed hands, cropped head, "
            "photo of a real person, cartoon outline, flat 2D, face turned to the left, mirrored pose, long finger blades, clawed glove with four long knives, "
            "red and green striped sweater, brown fedora")
ALL = {"Head": HEAD, "Skin": SKIN, "Hair": {CLOWN["Hair"][0]: (0, CLOWN["Hair"][1]), **HAIR, **HAIR_WOMAN, **{v[0]: (0, v[1]) for v in FEMALE.values()}, "Grey Curled Perm": (0, FEMALE_EXTRA["Grey Curled Perm"]), "Blood-Matted Curls": (0, FEMALE_EXTRA["Blood-Matted Curls"]), "Frizzed Auburn Bunches": (0, FEMALE_EXTRA["Frizzed Auburn Bunches"])}, "Head Mark": HEAD_MARK, "Ears": EARS, "Clothing": {CLOWN["Clothing"][0]: (0, CLOWN["Clothing"][1]), HOMAGE_CLOTH[0]: (0, HOMAGE_CLOTH[1]), **CLOTH_STD, **CLOTH_NEW, **CLOTH_RARE, **{v[4]: (0, v[5]) for v in FEMALE.values()}, "Mustard Cardigan": (0, FEMALE_EXTRA["Mustard Cardigan"]), "Blood-Drenched Prom Gown": (0, FEMALE_EXTRA["Blood-Drenched Prom Gown"]), "Rotten Ruffle Pierrot Dress": (0, FEMALE_EXTRA["Rotten Ruffle Pierrot Dress"])},
       "Belt": BELT, "Backdrop": {**BACKDROP, **BACKDROP_RARE, **BACKDROP_SCENE, JAIL[0]: (0, JAIL[1]), **{k: (0, v) for k, v in SCENE2.items()}, "Burning Gym": (0, FEMALE_EXTRA["Burning Gym"])}, "Mask": {CLOWN["Mask"][0]: (0, CLOWN["Mask"][1]), **{k: (0, v) for k, v in HOMAGE_MASK.items()}, **MASK_STD, **MASK_RARE, **MASK_NEW, **{v[2]: (0, v[3]) for v in FEMALE.values()}, "Mad Mother's Face": (0, FEMALE_EXTRA["Mad Mother's Face"]), "Psychic Glare": (0, FEMALE_EXTRA["Psychic Glare"]), "Cracked Clown Paint": (0, FEMALE_EXTRA["Cracked Clown Paint"])},
       "Held Weapon": {**HELD_STD, **HELD_RARE, "Telekinesis": (0, "")}, "Back Weapon": {**BACK_STD, **BACK_RARE}}
ALL["Held Weapon"]["Poison Syringe"] = (0, "a big old glass syringe filled with glowing toxic-green poison, a long dripping needle pointing up and out")
ALL["Skin"], ALL["Belt"] = dict(ALL["Skin"]), dict(ALL["Belt"])   # copies, so the retro values never touch the SKIN/BELT pick tables
for _t, (_v, _p) in RETRO_EXTRA.items():
    ALL[_t][_v] = (0, _p)
# Shrunken Head Bandolier (George, 2026-11-15): a more exclusive trait, worn across the chest with 5 shrunken heads.
# Belt slot, 13 unrendered Uncommon tokens (head_strap_pass; George: Uncommon), so tier counts don't move.
ALL["Held Weapon"]["Double Molotov Cocktails"] = (0, "")
ALL["Held Weapon"]["Blue-Flame Flamethrower"] = (0, "")
ALL["Held Weapon"]["Mask Orb and Hatchet"] = (0, "")
# Half-Burnt Face (George, 2026-11-15): a Head Mark on exactly 13 unrendered bare-face Uncommon tokens (burnt_face_pass).
ALL["Head Mark"] = dict(ALL["Head Mark"])
ALL["Head Mark"]["Half-Burnt Face"] = (0, "one half of his face is horribly burnt: charred, blistered and melted flesh peeling away on that side, "
                                          "the cheek burnt through so the bare white jaw bone and teeth are exposed")
# Damaged ears (George, 2026-11-15): Mostly Torn and Slightly Ripped, 145 unrendered tokens each with a bare visible ear (torn_ear_pass).
ALL["Ears"]["Mostly Torn Ear"] = (0, "his visible ear is mostly torn away, only a ragged bloody stump of ear left with jagged torn edges and dried blood")
ALL["Ears"]["Slightly Ripped Ear"] = (0, "his visible ear has a small ragged rip through the top edge, a notch of missing flesh crusted with dried blood")
# Gun back weapons (George, 2026-11-15): exactly 7 Double-Barrel Shotguns and 3 Sniper Rifles on unrendered Rare tokens.
ALL["Back Weapon"]["Double-Barrel Shotgun"] = (0, "a sawn-off rusty double-barrel shotgun with a cracked wooden stock slung on his back, "
                                              "the twin barrels rising above his shoulder")
ALL["Back Weapon"]["Sniper Rifle"] = (0, "a long heavy matte-black sniper rifle with a big scope and a bipod slung on his back, the long barrel "
                                     "rising high above his shoulder")
ALL["Belt"]["Shrunken Head Bandolier"] = (0, "a worn leather bandolier strap slung diagonally across his chest from shoulder to hip with exactly "
                                          "five small wrinkled shrunken heads hanging from it, their eyes and lips stitched shut, wisps of dark hair")
for _t, _v, _p in ICON_EXTRA + DUCHESS_EXTRA + DOLL_EXTRA + COLLECTOR_EXTRA:
    ALL[_t][_v] = (0, _p)


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
    elif held == "Chainsaw":   # George 2026-11-14: chainsaws are always wielded with both hands
        hand = ("he wields a heavy rusty chainsaw with a bloody chain in BOTH hands: right hand gripping the rear handle, "
                "left hand gripping the front wrap-around handle, the bar angled up and out across his body")
    elif held == "Telekinesis":
        hand = ("she holds no weapon: both bloody hands are raised and spread with clawed fingers, unleashing telekinetic power, "
                "chairs, glass shards and streamers levitating around her and a rippling shockwave bending the air")
    elif held == "Double Molotov Cocktails":   # George 2026-11-15: one lit Molotov in each hand, 6 Rare tokens
        hand = ("he holds a lit Molotov cocktail in EACH hand: two old glass bottles of sloshing fuel with burning rag wicks, "
                "small orange flames licking from both, one raised in each fist")
    elif held == "Mask Orb and Hatchet":
        hand = ("in his left hand he holds out a round cracked bone-white clay orb shaped like a goalie mask rolled into a ball, covered in rows "
                "of small breathing holes with rusty rivets and dried blood; it is all one off-white colour, with no red half, no band and no "
                "button; his right fist grips a rusty hatchet with a worn wooden handle, held low at his side")
    elif held == "Death Nails":
        hand = ("BOTH of her hands are raised in front of her chest, fingers spread like claws, every fingertip on both hands ending in a "
                "long curved blackened-steel blade nail as long as a forearm, all ten blade nails fanned out toward the viewer, blood on the tips")
    elif held == "Hook Hand":
        hand = "his right hand has been replaced by a rusty iron hook strapped to his forearm"
    elif held in ("Flamethrower", "Blue-Flame Flamethrower"):   # George 2026-11-15: a much bigger flame; 3 get blue flames
        colour = "roaring blue-and-white gas" if held == "Blue-Flame Flamethrower" else "roaring orange-and-yellow"
        hand = ("his right fist grips a crude homemade rusty flamethrower made of welded pipe, blasting a HUGE billowing jet of "
                f"{colour} fire out of the nozzle, the long plume of flame filling the upper side of the frame, pointed up and away from him")
    elif held == "Nail-Knife Glove":
        hand = ("his right hand wears a thick grimy grey welder's gauntlet with bent rusty nails and short broken kitchen-knife "
                "blades crudely welded and taped onto the knuckles, a clenched spiked fist, knuckles toward the camera")
    else:
        hand = f"his right fist grips {phrase('Held Weapon', held)}"
    body = [f"wearing {phrase('Clothing', a['Clothing'])}", phrase("Belt", a["Belt"]), hand, phrase("Back Weapon", a["Back Weapon"])]
    female = a.get("Character", "Classic") in FEMALE or a.get("Character") in ("The Grieving Mother", "The Prom Queen", "The Ringmistress", "Woman", "Madame Mortis")
    if female:
        head = [phrase("Skin", a["Skin"]), phrase("Hair", a["Hair"]), phrase("Head Mark", a["Head Mark"]), phrase("Ears", a.get("Ears", "Natural"))]
    doll = a.get("Character") == "Cinder Doll"
    if doll:
        head = [phrase("Skin", a["Skin"]), phrase("Hair", a["Hair"])]
    parts = [STYLE, DOLL_BASE if doll else FEMALE_BASE if female else CHARACTER, ", ".join(p for p in head if p), mask, ", ".join(p for p in body if p),
             phrase("Backdrop", a["Backdrop"]), FRAMING_COLLECTOR if held == "Mask Orb and Hatchet" else FRAMING_MOLOTOV if held == "Double Molotov Cocktails" else FRAMING_NAILS if held == "Death Nails" else FRAMING_TWO_HANDS if held == "Chainsaw" else FRAMING_PSYCHIC if held == "Telekinesis" else FRAMING]
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
    clown_pass(tokens)
    jail_pass(tokens)
    prom_pass(tokens)
    head_pass(tokens)
    homage_pass(tokens)
    scene2_pass(tokens)
    ring_pass(tokens)
    tier_pass(tokens)
    woman_pass(tokens)
    syringe_pass(tokens)
    retro_pass(tokens)
    icon_pass(tokens)
    trim_pass(tokens)
    duchess_pass(tokens)
    doll_pass(tokens)
    head_strap_pass(tokens)
    molotov_pass(tokens)
    blue_flame_pass(tokens)
    gun_pass(tokens)
    torn_ear_pass(tokens)
    burnt_face_pass(tokens)
    collector_pass(tokens)
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for i, (a, finish) in enumerate(tokens, 1):
        seed = rng.randrange(1 << 31)
        name = f"SBN13th #{i}" + (f" - {a['1/1 Name']}" if "1/1 Name" in a else "")
        meta = {"name": name, "seed": seed, "attributes": [{"trait_type": k, "value": v} for k, v in a.items()]}
        json.dump(meta, open(os.path.join(OUT, f"{i}.json"), "w"), indent=2)
        rows.append({"id": i, "name": name, "seed": seed, "prompt": prompt(a, finish), "negative": NEGATIVE.replace("long finger blades, clawed glove with four long knives, ", "") if a["Held Weapon"] == "Death Nails" else NEGATIVE + ", red and white ball, ball with a centre button, writing on clothes, logo on cap" if a["Held Weapon"] == "Mask Orb and Hatchet" else NEGATIVE, "attributes": a})
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
            a.update(MOTHER[1]); tokens[i] = (a, None)
   # no hockey-mask finish: her own face is the look


def clown_pass(tokens):
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_clown.json"))))
    late = random.Random(4242)
    for trait, (val, _) in CLOWN.items():
        pool = [i for i, (a, finish) in enumerate(tokens, 1) if i not in keep and not finish and a["Character"] == "Classic"
                and a["Mask"] not in MASK_NEW and a["Mask"] not in MASK_RARE and a["Clothing"] not in CLOTH_RARE
                and not (trait == "Hair" and a["Mask"] in ("Burlap Sack Hood", "Zipper Long Nose"))]
        for i in late.sample(pool, N_CLOWN):
            tokens[i - 1][0][trait] = val


def jail_pass(tokens):
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_jail.json"))))
    pool = [i for i, (a, finish) in enumerate(tokens, 1) if i not in keep and not finish]
    for i in random.Random(1313131).sample(pool, N_JAIL):
        tokens[i - 1][0]["Backdrop"] = JAIL[0]


def prom_pass(tokens):
    for i, (a, finish) in enumerate(tokens):
        if a.get("1/1 Name") == PROM[0]:
            a.update(PROM[1]); tokens[i] = (a, None)   # no hockey-mask finish: her own face is the look



def syringe_pass(tokens):
    """Poison Syringe held weapon (George, 2026-11-14): Uncommon, 25 unrendered Standard/Uncommon tokens that hold an
    ordinary one-hand weapon. Runs after woman_pass so no earlier pick shifts; the token becomes Uncommon."""
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_syringe.json"))))
    late = random.Random(4040)
    pool = [i for i, (a, f) in enumerate(tokens, 1) if i not in keep and not f and a["Tier"] == "Uncommon"
            and a["Held Weapon"] in HELD_STD and a["Held Weapon"] not in ("Chainsaw", "Bare Fist")]
    dnas = {tuple(sorted((k, v) for k, v in a.items() if k != "Tier")) for a, _ in tokens}
    for i in late.sample(pool, 25):
        a = tokens[i - 1][0]
        a["Held Weapon"], a["Tier"] = "Poison Syringe", "Uncommon"
        dna = tuple(sorted((k, v) for k, v in a.items() if k != "Tier"))
        assert dna not in dnas; dnas.add(dna)


def icon_pass(tokens):
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_syringe.json"))))
    late = random.Random(6161)
    pool = [i for i, (a, f) in enumerate(tokens, 1) if i not in keep and not f and a["Tier"] == "Uncommon"
            and a["Character"] in ("Classic", "Woman") and a["Held Weapon"] != "Poison Syringe"]
    late.shuffle(pool)
    dnas = {tuple(sorted((k, v) for k, v in a.items() if k != "Tier")) for a, _ in tokens}
    used = set()
    for trait, val in ICON_TRAITS:
        n = 0
        for i in pool:
            a = tokens[i - 1][0]
            if i in used or (trait == "Held Weapon" and (a["Held Weapon"] not in HELD_STD or a["Held Weapon"] in ("Chainsaw", "Bare Fist"))) \
                    or (trait == "Back Weapon" and a["Back Weapon"] not in BACK_STD) or (trait == "Clothing" and a["Clothing"] not in CLOTH_STD) \
                    or (trait == "Mask" and a["Hair"] == "Backwards Cap" and val == "Cracked Doll Mask"):
                continue
            old = tuple(sorted((k, v) for k, v in a.items() if k != "Tier"))
            b = dict(a, **{trait: val}, Tier="Uncommon")
            if val in ICON_BROWN:
                b["Skin"] = "Deep Brown"
            dna = tuple(sorted((k, v) for k, v in b.items() if k != "Tier"))
            if dna in dnas:
                continue
            dnas.discard(old); dnas.add(dna); a.update(b); used.add(i); n += 1
            if n == 25:
                break
        assert n == 25, (val, n)


def trim_pass(tokens):
    """Uncommons rarer than Standards (George, 2026-11-14): 100 unrendered Uncommons whose only uncommon trait is a mask,
    backdrop, hat or outfit go back to an ordinary pick and become Standard. Gauged ears (exactly 130), the syringe and the
    horror-icon set keep their counts. Runs last, with its own seed, so nothing earlier shifts."""
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_syringe.json"))))
    late = random.Random(8080)
    U = {"Mask": set(MASK_NEW) | {CLOWN["Mask"][0]} | set(HOMAGE_MASK), "Backdrop": set(BACKDROP_SCENE) | set(SCENE2),
         "Hair": {CLOWN["Hair"][0]}, "Clothing": {CLOWN["Clothing"][0], HOMAGE_CLOTH[0]}}
    plain = {"Mask": MASK_STD, "Backdrop": BACKDROP, "Clothing": CLOTH_STD}
    new = {"Poison Syringe"} | {v for _, v in ICON_TRAITS}
    cands = []
    for i, (a, f) in enumerate(tokens, 1):
        hits = [t for t in U if a[t] in U[t]]
        if (i not in keep and not f and a["Tier"] == "Uncommon" and len(hits) == 1 and a["Ears"] != "Gauged"
                and not new & set(a.values()) and a["Character"] in ("Classic", "Woman")):
            cands.append((i, hits[0]))
    dnas = {tuple(sorted((k, v) for k, v in a.items() if k != "Tier")) for a, _ in tokens}
    for i, t in late.sample(cands, 100):
        a = tokens[i - 1][0]
        old = tuple(sorted((k, v) for k, v in a.items() if k != "Tier"))
        table = plain.get(t) or (HAIR_WOMAN if a["Character"] == "Woman" else HAIR)
        for _ in range(30):
            b = dict(a, **{t: pick(late, table)}, Tier="Standard")
            dna = tuple(sorted((k, v) for k, v in b.items() if k != "Tier"))
            if dna not in dnas:
                dnas.discard(old); dnas.add(dna); a.update(b)
                break
        else:
            raise AssertionError(i)


def duchess_pass(tokens):
    for i, (a, finish) in enumerate(tokens):
        if a.get("1/1 Name") == DUCHESS[0]:
            a.update(DUCHESS[1]); tokens[i] = (a, None)


def doll_pass(tokens):
    for i, (a, finish) in enumerate(tokens):
        if a.get("1/1 Name") == DOLL[0]:
            a.update(DOLL[1]); tokens[i] = (a, None)


def head_strap_pass(tokens):
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_syringe.json"))))
    late = random.Random(5555)
    pool = [i for i, (a, f) in enumerate(tokens, 1) if i not in keep and not f and a["Tier"] == "Uncommon"
            and a["Character"] in ("Classic", "Woman")]
    for i in late.sample(pool, 13):
        tokens[i - 1][0]["Belt"] = "Shrunken Head Bandolier"   # a new value can't collide with an existing DNA


def molotov_pass(tokens):
    """Double Molotov Cocktails (George, 2026-11-15): exactly 6 unrendered Rare tokens holding an ordinary one-hand weapon."""
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_syringe.json"))))
    late = random.Random(6606)
    pool = [i for i, (a, f) in enumerate(tokens, 1) if i not in keep and not f and a["Tier"] == "Rare"
            and a["Character"] in ("Classic", "Woman") and a["Held Weapon"] in HELD_STD and a["Held Weapon"] not in ("Chainsaw", "Bare Fist")]
    for i in late.sample(pool, 6):
        tokens[i - 1][0]["Held Weapon"] = "Double Molotov Cocktails"   # a new value can't collide with an existing DNA


def blue_flame_pass(tokens):
    """Blue flames (George, 2026-11-15): 3 unrendered Flamethrower tokens get a blue flame."""
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_syringe.json"))))
    late = random.Random(3333)
    pool = [i for i, (a, f) in enumerate(tokens, 1) if i not in keep and a["Held Weapon"] == "Flamethrower"]
    for i in late.sample(pool, 3):
        tokens[i - 1][0]["Held Weapon"] = "Blue-Flame Flamethrower"


def gun_pass(tokens):
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_syringe.json"))))
    late = random.Random(7373)
    pool = [i for i, (a, f) in enumerate(tokens, 1) if i not in keep and not f and a["Tier"] == "Rare"
            and a["Character"] in ("Classic", "Woman") and (a["Back Weapon"] in BACK_STD or a["Back Weapon"] in BACK_RARE) and a["Back Weapon"] not in ("Chainsaw", "Fuel Tanks", "Circus Mallet")
            and a["Held Weapon"] != "Chainsaw"]
    picks = late.sample(pool, 10)
    for n, i in enumerate(picks):
        tokens[i - 1][0]["Back Weapon"] = "Double-Barrel Shotgun" if n < 7 else "Sniper Rifle"


def torn_ear_pass(tokens):
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_syringe.json"))))
    late = random.Random(4545)
    covered = {"Burlap Sack Hood", "Zipper Long Nose", "Bloody Bandage Wrap", "Buckled Harness Hood", "Cracked Doll Mask", "Gas Mask",
               "Burlap Pig Mask", "Nail-Studded Leather Mask", "Zipper Mouth Leather", "Flayed Muscle Face", "Rubber Seam Face"}
    pool = [i for i, (a, f) in enumerate(tokens, 1) if i not in keep and not f and a["Tier"] != "Legendary 1/1" and a["Ears"] == "Natural"
            and a["Mask"] not in covered and a["Character"] in ("Classic", "Woman")]
    picks = late.sample(pool, 290)
    for n, i in enumerate(picks):
        tokens[i - 1][0]["Ears"] = "Mostly Torn Ear" if n < 145 else "Slightly Ripped Ear"   # new values: no DNA collision


def burnt_face_pass(tokens):
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_syringe.json"))))
    pool = [i for i, (a, f) in enumerate(tokens, 1) if i not in keep and not f and a["Tier"] == "Uncommon" and a["Mask"] == "Bare Face"
            and a["Character"] in ("Classic", "Woman")]
    for i in random.Random(1313).sample(pool, 13):
        tokens[i - 1][0]["Head Mark"] = "Half-Burnt Face"   # a new value can't collide with an existing DNA


def collector_pass(tokens):
    for i, (a, finish) in enumerate(tokens):
        if a.get("1/1 Name") == COLLECTOR[0]:
            a.update(COLLECTOR[1]); tokens[i] = (a, None)


def retro_pass(tokens):
    for i, (a, finish) in enumerate(tokens):
        if a.get("1/1 Name") == RETRO[0]:
            a.update(RETRO[1]); tokens[i] = (a, None)   # its own mask phrase, not the generic hockey-mask finish


def head_pass(tokens):
    """Fewer cone heads (George, 2026-11-14): 70% of unrendered, non-legendary Cone Skull tokens move to the other head types."""
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_jail.json"))))
    late = random.Random(333)
    others = {k: v for k, v in HEAD.items() if k != "Type 3 - Cone Skull"}
    dnas = {tuple(sorted((k, v) for k, v in a.items() if k != "Tier")) for a, _ in tokens}
    for i, (a, finish) in enumerate(tokens, 1):
        if i in keep or finish or a["Head"] != "Type 3 - Cone Skull" or late.random() >= .7:
            continue
        for _ in range(10):
            b = dict(a, Head=pick(late, others))
            dna = tuple(sorted((k, v) for k, v in b.items() if k != "Tier"))
            if dna not in dnas:
                dnas.discard(tuple(sorted((k, v) for k, v in a.items() if k != "Tier"))); dnas.add(dna); a["Head"] = b["Head"]
                break


def homage_pass(tokens):
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_jail.json"))))
    late = random.Random(1978)
    done = set()
    for trait, vals in [("Mask", list(HOMAGE_MASK)), ("Clothing", [HOMAGE_CLOTH[0]])]:
        for val in vals:
            pool = [i for i, (a, finish) in enumerate(tokens, 1) if i not in keep and i not in done and not finish
                    and a["Character"] == "Classic" and a["Mask"] not in MASK_NEW and a["Mask"] not in MASK_RARE
                    and a["Mask"] != CLOWN["Mask"][0] and a["Clothing"] not in CLOTH_RARE and a["Clothing"] != CLOWN["Clothing"][0]]
            for i in late.sample(pool, N_HOMAGE):
                tokens[i - 1][0][trait] = val; done.add(i)


def scene2_pass(tokens):
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_jail.json"))))
    late = random.Random(2525)
    for val in SCENE2:
        pool = [i for i, (a, finish) in enumerate(tokens, 1) if i not in keep and not finish and a["Backdrop"] in BACKDROP]
        for i in late.sample(pool, N_SCENE2):
            tokens[i - 1][0]["Backdrop"] = val


def ring_pass(tokens):
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_jail.json"))))
    pool = [i for i, (a, finish) in enumerate(tokens, 1) if i not in keep and not finish and a["Tier"] == "Rare"
            and a["Character"] == "Classic" and a["Ears"] == "Natural" and a["Mask"] not in MASK_NEW]
    for i in random.Random(7070).sample(pool, N_FEMALE):
        tokens[i - 1][0].update(RINGMISTRESS)


def woman_pass(tokens):
    """Women ~32% (George, 2026-11-14, no redos): every unrendered Standard, 170 unrendered Uncommons and the two unrendered
    hockey-mask 1/1s become ordinary women: same mask, weapons and outfit, female body, short female hair."""
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_jail.json"))))
    late = random.Random(3535)
    free = lambda i, a: i not in keep and a["Character"] == "Classic"
    pick_ids = [i for i, (a, f) in enumerate(tokens, 1) if free(i, a) and a["Tier"] in ("Standard", "Legendary 1/1")]
    unc = [i for i, (a, f) in enumerate(tokens, 1) if free(i, a) and a["Tier"] == "Uncommon"]
    pick_ids += late.sample(unc, 170)
    dnas = {tuple(sorted((k, v) for k, v in a.items() if k != "Tier")) for a, _ in tokens}
    keep_hair = {"Backwards Cap", CLOWN["Hair"][0]}
    for i in sorted(pick_ids):
        a = tokens[i - 1][0]
        old = tuple(sorted((k, v) for k, v in a.items() if k != "Tier"))
        for _ in range(20):
            b = dict(a, Character="Woman", Head="Female", Hair=a["Hair"] if a["Hair"] in keep_hair else pick(late, HAIR_WOMAN))
            dna = tuple(sorted((k, v) for k, v in b.items() if k != "Tier"))
            if dna not in dnas:
                dnas.discard(old); dnas.add(dna); a.update(b)
                break


def tier_pass(tokens):
    """Uncommon tier (George, 2026-11-14): a Standard token that carries any Uncommon trait is relabelled Uncommon.
    Metadata only, so finished images don't change."""
    UNCOMMON = {"Mask": set(MASK_NEW) | {CLOWN["Mask"][0]} | set(HOMAGE_MASK), "Backdrop": set(BACKDROP_SCENE) | set(SCENE2),
                "Hair": {CLOWN["Hair"][0]}, "Clothing": {CLOWN["Clothing"][0], HOMAGE_CLOTH[0]}}
    for a, _ in tokens:
        if a["Tier"] == "Standard" and (a["Mask"] in UNCOMMON["Mask"] or a["Backdrop"] in UNCOMMON["Backdrop"]
                                        or a["Ears"] == "Gauged" or a["Hair"] in UNCOMMON["Hair"] or a["Clothing"] in UNCOMMON["Clothing"]):
            a["Tier"] = "Uncommon"


def report(tokens):
    lines = ["# Claysons rarity", "", "1,300 PFPs. Every PFP is unique.", ""]
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
