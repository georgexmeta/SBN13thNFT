"""SBN13th v2 traits for the Gemini clay collection (George, 2026-11-13).

    python3 generator/v2.py      # writes output/collection-v2/<id>.json, RARITY-v2.md, output/ai/manifest-v2.json

Every PFP is the master-reference character (lumpy disfigured clay man, bobble head, slate work jacket look) with
variety in: head type (1-4), mask, held weapon, back weapon, clothing, backdrop and extras.
Tiers: 1,157 Standard, 130 Rare, 13 Legendary 1/1s. Rare-only and 1/1-only values never appear lower down.

Masks are ORIGINAL designs in the spirit of heavy-metal and slasher horror. They must not reproduce a specific
film character's or band member's mask (no white screaming hooded mask, no grid of pins on a pale face, no
red-chevron hockey mask, no copied clown make-up), so the collection stays clear of takedowns.
"""
import collections
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
    "Type 3 - Cone Skull": (22, "head type: a SUBTLY cone-shaped skull, only slightly elongated, the crown rising gently to a soft rounded top, never a sharp point or a tall exaggerated cone, with faint ridged wrinkles running up the back"),
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
    "Wild Grey Tufts": (14, "wild spiky grey hair tufts"), "Backwards Cap": (8, "a filthy plain backwards baseball cap with no logo, pulled snugly down over a normal-sized rounded skull; nothing bulges up out of or above the cap"),
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
EARS = {"Natural": (0, ""), "Gauged": (0, "a heavily stretched earlobe on his visible ear holding a large shiny polished silver steel tunnel gauge, a hollow metal ring about an inch wide with flared rims that you can see straight through, hanging just below the ear"),
        "Empty Stretched Lobe": (0, "a long floppy stretched earlobe on his visible ear with a large EMPTY round hole where a gauge used to be, no plug or ring in it, the loose lobe drooping down below the ear")}
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
    "Stitched Skin Face": (0, "no mask: his own face torn and crudely stitched back together, thick black surgical stitches and puckered red "
                              "scars criss-crossing his cheeks, brow and lips, a few mismatched patches of his own skin sewn back on, both bloodshot eyes clear"),
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
    "Hair": ("Battered Top Hat", "a battered dented black top hat with a torn brim and a faded checkered band, tufts of greasy grey hair under it, the hat sitting snugly on a normal-sized skull with no cranium bulging out of it"),
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
ICON_TRAITS = [("Mask", "Carved Ear-to-Ear Grin"), ("Clothing", "Ragged Plum Greatcoat"), ("Mask", "Cracked Doll Mask"),
               ("Clothing", "Rust-Red Boiler Suit"), ("Held Weapon", "Rusty Shears"), ("Mask", "Needle-Tooth Snarl"),
               ("Back Weapon", "Leathery Bat Wings")]
ICON_BROWN = {"Carved Ear-to-Ear Grin", "Ragged Plum Greatcoat", "Cracked Doll Mask", "Rust-Red Boiler Suit", "Rusty Shears"}
ICON_EXTRA = [
    ("Skin", "Deep Brown", "deep dark-brown clay skin"),
    ("Mask", "Carved Ear-to-Ear Grin", "no mask: both cheeks slit open in a hideous carved grin "
             "stretching from ear to ear, the deep cuts crudely stitched with black thread and crusted with dried blood, his lips pulled into "
             "a huge, unnaturally wide, sinister smile showing rows of yellowed teeth, natural clay skin (no white face paint, no makeup), "
             "eyes, brow and forehead bare"),
    ("Mask", "Cracked Doll Mask", "a cracked white porcelain doll-face mask over his whole face, rosy painted cheeks, tiny painted red lips, "
             "empty black eye holes, a long hairline crack running across it, the mask sits squarely over his whole face from brow to chin with its eye holes exactly over his eyes; none of his real eyes, skin or brow shows above, beside or below the mask"),
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
DOLL = ("Cinder", {"1/1 Name": "Scorched Doll", "Character": "Scorched Doll", "Head": "Doll", "Skin": "Charred Plastic",
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
             "Held Weapon": "Clayson Master Ball and Golden Axe", "Back Weapon": "None", "Clothing": "Collector's Pin Vest", "Belt": "None",
             "Backdrop": "Terracotta Clay"})
COLLECTOR_EXTRA = [
    ("Hair", "Worn Trucker Cap", "a dirty, worn plain beige trucker cap with a mesh back, completely blank with no logo, signatures or writing, "
             "messy grey hair sticking out at the sides"),
    ("Mask", "Bearded Bulging Stare", "no mask: a weathered wrinkled face with huge round bulging staring eyes in baggy lids, a big nose and a "
             "scraggly grey-brown beard and moustache"),
    ("Clothing", "Collector's Pin Vest", "a dad-style khaki collector's vest with lots of pockets, covered in rows of small round blank enamel "
                 "pin badges in bright colours (plain dots and stars, no pictures, no lettering), over a plain faded grey T-shirt with no lettering "
                 "or print; he looks like a man in his mid fifties"),
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
    "Burlap Sack Hood": (12, "his huge oversized bobble head is entirely covered by a filthy lumpy burlap sack pulled all the way down over the whole skull and face, ragged cut eye holes, a cross-stitched mouth, rope tied tight at the neck; no skin or hair visible. The sack is pulled fully DOWN over the face with its eye holes right over his eyes, never pushed up on top of the head like a cap and never covering only half the face; on a pointed cone skull the sack covers the whole cone too"),
    "Patchwork Goggle Mask": (12, "a patchwork mask of stitched burlap and riveted scrap-metal plates, exactly two round brass goggles with red lenses sitting directly over his two eyes (the eyes seen through the lenses, nothing else on the nose or snout), a wire-stitched mouth, a leather strap with a buckle over the crown"),
    "Gas Mask": (10, "a battered riveted rusty-steel HALF-face respirator clamped over his nose and mouth with crude rivets and bolts, a single round olive filter canister with a dull yellow face on one side, ribbed black rubber hoses looping from the mask down across his chest, scarred stitched skin around its edges, eyes visible above"),
    "Paisley Bandana": (8, "a navy paisley bandana tied snug over his nose and mouth, point hanging on the chest"),
    "Iron Muzzle": (4, "a crude welded scrap-metal jaw cage made of bent rebar bars and bolts wrapped round his mouth and chin, rusty and bloody, eyes visible above"),
}
MASK_RARE = {   # monster-like; original takes on slasher and metal archetypes
    "Stitched Skin Mask": (16, "a crude mask of mismatched stitched leathery skin patches sewn with thick black thread, uneven eye holes, ragged edges"),
    "Nail-Studded Leather Mask": (14, "a cracked black leather mask with bent rusty nails and screws driven through it at random angles, blood seeping from the holes"),
    "Fanged Killer Clown": (14, "a cracked greasepaint killer clown face with green diamond eye paint, a red bulb nose, a ragged fanged grin dripping blood and wild orange hair puffs"),
    "Porcelain Doll Face": (12, "a cracked porcelain doll face mask with a chipped cheek, painted rosy cheeks, black empty eyes and a tiny painted mouth, the mask sits squarely over his whole face from brow to chin with its eye holes exactly over his eyes; none of his real eyes, skin or brow shows above, beside or below the mask"),
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
    "Nail Bat": (8, "a wooden bat studded with bent rusty nails"), "Ice Pick": (6, "a rusty ice pick: a short round wooden handle with one long thin straight metal spike, not a pickaxe"), "Bare Fist": (4, None),
    "Chainsaw": (8, "a rusty chainsaw with a bloody chain"),
    "Fish Hook": (8, "ONE single huge rusty barbed fish hook on a short wooden handle, smeared with blood; only one hook, with no smaller hooks, lures, line or bait hanging from it"),
    "Spear": (8, "a crude spear: a long wooden pole with a rusty jagged blade lashed to the top with wire and rag, held upright with the blade above his shoulder"),
}
HELD_RARE = {"Golden Machete": (40, "a gleaming golden machete dripping blood"), "Bone Saw": (30, "a rusty serrated bone saw"),
             "Hook Hand": (30, None), "Flamethrower": (30, None), "Nail-Knife Glove": (30, None)}
BACK_STD = {
    "Weed Whacker": (22, "a rusty backpack weed whacker: engine pack on his back with padded harness straps over the shoulder, the long trimmer shaft clipped upright to the side of the engine pack BEHIND his shoulder, one connected piece, its cutting head rising above and behind his shoulder; the shaft never crosses in front of his body, arm or face and never floats loose; grass clippings on his sleeve"),
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
BACKDROP_RARE = {"Blood Moon": (50, "a haunted night woods: twisted bare black trees with gnarled clawing branches, low drifting fog between the trunks "
                                 "and dead leaves on the ground, and a huge cratered blood-red clay moon hanging low in the distance between the trees, "
                                 "casting a dim red glow through the mist, sculpted as a miniature claymation diorama, softly out of focus behind him"),
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
    ("Gristle", "patched together from raw gristle and pink sinew, bound with rusty wire", "Type 4 - Split Cranium", "Hunting Knife", "Chainsaw", "Swamp Clay"),
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
           "above the head, figure centred, square 1:1 composition. SCALE (the same for every figure in the series): the figure is the same size in the frame as in the first reference photo, the bobble head the same size relative to the body, and weapons true to scale with the hands, never oversized or tiny. His right hand grips the held weapon in a tight "
           "clenched fist seen from the back of the hand, knuckles toward the camera, palm hidden, the blade angled up "
           "and out; his other hand is raised beside him as a menacing curled claw, gnarled fingers bent like hooks, never hanging limp")
FRAMING_TWO_HANDS = FRAMING.split(" His right hand grips")[0] + (" Both hands hold the chainsaw firmly, one on the rear handle "
                                                              "and one on the front handle; neither hand hangs empty")
FRAMING_WHACKER = FRAMING.split(" His right hand grips")[0] + (" Both hands hold the weed whacker: his left hand wraps the loop handle in the "
                                                             "middle of the shaft and his right fist grips the rear trigger handle by the motor, no hand up near the blade; the shaft angled up across his body so the saw blade is raised "
                                                             "beside his head, the whole tool inside the frame; neither hand hangs empty")
FRAMING_BOX = FRAMING.split(" His right hand grips")[0] + (" Both hands hold the small puzzle box in front of his chest, fingers on its "
                                                         "faces, the whole box clearly visible and sharp; nothing else in his hands and nothing on his back")
FRAMING_DUAL = FRAMING.split(" His right hand grips")[0] + (" Both hands are full and both are tight clenched fists, knuckles toward the camera: "
                                                          "the right fist grips the held weapon, the left fist grips the second weapon by its handle as described")
FRAMING_BOTH = FRAMING.split(" His right hand grips")[0] + (" Both hands grip the weapon, knuckles toward the camera, the whole weapon inside the frame; "
                                                          "neither hand hangs empty and nothing is on his back")
FRAMING_HOOKOFF = FRAMING.split("; his other hand")[0] + "; his other arm ends in a metal prosthetic hook, raised, never a limp hand or a bare stump"
HOOK_FINISH = {"Rusty": "rusty pitted iron", "Steel": "plain scuffed steel", "Bloody": "blood-drenched dripping steel",
               "Gold": "gleaming solid-gold", "Chrome": "mirror-polished chrome"}
FRAMING_NAILS = FRAMING.split(" His right hand grips")[0] + " Both hands are raised and fully visible inside the frame, all ten blade nails spread; neither hand hangs down or is hidden"
FRAMING_MOLOTOV = FRAMING.split(" His right hand grips")[0] + " Both fists are raised in front of him, each gripping a lit Molotov cocktail by the neck, knuckles toward the camera; neither hand hangs empty"
FRAMING_COLLECTOR = FRAMING.split(" His right hand grips")[0] + " Both hands are full: the orb held out in one hand toward the viewer, the hatchet gripped in the other"
FRAMING_BAND = FRAMING.split(" His right hand grips")[0] + " Both fists hold the exercise band stretched tight between them in front of her chest, knuckles toward the camera"
FRAMING_PSYCHIC = FRAMING.split(" His right hand grips")[0] + " Both hands are raised, empty, channelling psychic force; no weapon in her hands"
NEGATIVE = ("text, logo, letters, watermark, brand marks, sports team logo, red chevrons or triangles on the mask, full-face goalie mask covering the forehead and eyes, "
            "white screaming ghost mask, black hooded robe, pins in a grid, extra fingers, deformed hands, cropped head, "
            "photo of a real person, cartoon outline, flat 2D, face turned to the left, mirrored pose, long finger blades, clawed glove with four long knives, "
            "red and green striped sweater, brown fedora")
ALL = {"Head": HEAD, "Skin": SKIN, "Hair": {CLOWN["Hair"][0]: (0, CLOWN["Hair"][1]), **HAIR, **HAIR_WOMAN, **{v[0]: (0, v[1]) for v in FEMALE.values()}, "Grey Curled Perm": (0, FEMALE_EXTRA["Grey Curled Perm"]), "Blood-Matted Curls": (0, FEMALE_EXTRA["Blood-Matted Curls"]), "Frizzed Auburn Bunches": (0, FEMALE_EXTRA["Frizzed Auburn Bunches"])}, "Head Mark": HEAD_MARK, "Ears": EARS, "Clothing": {CLOWN["Clothing"][0]: (0, CLOWN["Clothing"][1]), HOMAGE_CLOTH[0]: (0, HOMAGE_CLOTH[1]), **CLOTH_STD, **CLOTH_NEW, **CLOTH_RARE, **{v[4]: (0, v[5]) for v in FEMALE.values()}, "Mustard Cardigan": (0, FEMALE_EXTRA["Mustard Cardigan"]), "Blood-Drenched Prom Gown": (0, FEMALE_EXTRA["Blood-Drenched Prom Gown"]), "Rotten Ruffle Pierrot Dress": (0, FEMALE_EXTRA["Rotten Ruffle Pierrot Dress"])},
       "Belt": BELT, "Backdrop": {**BACKDROP, **BACKDROP_RARE, **BACKDROP_SCENE, JAIL[0]: (0, JAIL[1]), **{k: (0, v) for k, v in SCENE2.items()}, "Burning Gym": (0, FEMALE_EXTRA["Burning Gym"])}, "Mask": {CLOWN["Mask"][0]: (0, CLOWN["Mask"][1]), **{k: (0, v) for k, v in HOMAGE_MASK.items()}, **MASK_STD, **MASK_RARE, **MASK_NEW, **{v[2]: (0, v[3]) for v in FEMALE.values()}, "Mad Mother's Face": (0, FEMALE_EXTRA["Mad Mother's Face"]), "Psychic Glare": (0, FEMALE_EXTRA["Psychic Glare"]), "Cracked Clown Paint": (0, FEMALE_EXTRA["Cracked Clown Paint"])},
       "Held Weapon": {**HELD_STD, **HELD_RARE, "Telekinesis": (0, "")}, "Back Weapon": {**BACK_STD, **BACK_RARE}}
ALL["Held Weapon"]["Poison Syringe"] = (0, "a big old glass syringe filled with glowing toxic-green poison, held the way a real syringe is held to inject: his index and middle fingers hooked under the finger flange, his thumb pressed on the plunger end, the plunger, flange, glass barrel and needle all clearly visible as one straight piece, the long dripping needle pointing up and forward")
ALL["Skin"], ALL["Belt"] = dict(ALL["Skin"]), dict(ALL["Belt"])   # copies, so the retro values never touch the SKIN/BELT pick tables
for _t, (_v, _p) in RETRO_EXTRA.items():
    ALL[_t][_v] = (0, _p)
# The Night Broker (George, 2026-11-15): an original 80s Wall Street yuppie killer, inspired by the genre, never the film or character
# names, no actor likeness, no business cards. Replaces the 1/1 Hookjaw (#721; George chose), keeping 13 Legendaries. broker_pass.
BROKER = ("Hookjaw", {"1/1 Name": "The Night Broker", "Head": "Type 1 - Lumpy Dome", "Skin": "Tanning-Bed Bronze", "Hair": "Slicked-Back Hair",
          "Head Mark": "Clean", "Ears": "Natural", "Mask": "Psycho Yuppie Grin", "Held Weapon": "Chrome Sledge-Axe", "Back Weapon": "None",
          "Clothing": "Bloody Raincoat Over Pinstripe Suit", "Belt": "None", "Backdrop": "Penthouse Skyline", "Character": "Classic"})
BROKER_EXTRA = {
    "Skin": ("Tanning-Bed Bronze", "smooth glossy over-tanned bronze clay skin"),
    "Hair": ("Slicked-Back Hair", "thick jet-black hair slicked straight back with shiny gel, every strand sculpted neatly in place"),
    "Mask": ("Psycho Yuppie Grin", "no mask: his disfigured face is bare and freshly groomed, a wide too-perfect grin of gleaming bleached-white "
             "teeth, cold dead staring eyes with tiny pupils, a few fine specks of blood across his cheek and brow"),
    "Clothing": ("Bloody Raincoat Over Pinstripe Suit", "a sharp tailored charcoal pinstripe business suit with a crisp white shirt and a red "
                 "silk power tie, under a long CLEAR see-through plastic raincoat smeared and splattered with fresh blood, the suit clearly "
                 "visible through the transparent plastic"),
    "Backdrop": ("Penthouse Skyline", "the inside of a sleek 1980s penthouse apartment at night: huge floor-to-ceiling windows behind him "
                 "looking out over a glittering city skyline of lit skyscrapers, a glossy black lacquer side table and white leather "
                 "furniture, sculpted as a miniature claymation diorama in matte plasticine, softly out of focus behind him, no signs, no lettering"),
}
for _t, (_v, _p) in BROKER_EXTRA.items():
    ALL[_t][_v] = (0, _p)
# The Overseer (George, 2026-11-16 06:10, replaces Gristle #451, George chose): an original AI hologram villainess who runs a
# digital prison for her victims. A nod to survival-horror AI villains and the mad supercomputer of a classic horror story, never
# their names (no Red Queen, Umbrella or AM), logos or exact looks, and always an adult woman. overseer_pass runs last.
OVERSEER_ID = 451
OVERSEER = {"Tier": "Legendary 1/1", "1/1 Name": "The Overseer", "Character": "The Overseer", "Head": "Female", "Skin": "Red Hologram",
            "Hair": "Hologram Bob", "Head Mark": "Pixel Tears", "Ears": "Natural", "Mask": "Cold Digital Stare", "Held Weapon": "Laser Lattice",
            "Back Weapon": "None", "Clothing": "Hologram Shift Dress", "Belt": "None", "Backdrop": "Digital Soul Prison"}
OVERSEER_BASE = ("A clay WOMAN (an adult woman, not the man in the reference: copy only the reference's clay style, pose and framing) "
                 "with an oversized bobble head, a thin neck and narrow straight shoulders, head turned three-quarters toward the viewer's right")
FRAMING_LASER = FRAMING.split(" His right hand grips")[0] + " Both hands are raised and fully visible, fingers spread, projecting the red laser grid; nothing held in her hands"
OVERSEER_EXTRA = {
    "Skin": ("Red Hologram", "her whole fully clothed figure glows a deep red like a hologram projection, sculpted from glossy red clay lit from "
             "within, thin horizontal scan lines across her and small glitching pixel offsets at her edges as if the projection flickers"),
    "Hair": ("Hologram Bob", "a sharp short chin-length bob of glowing red light, perfectly straight, edges breaking into tiny pixels"),
    "Head Mark": ("Pixel Tears", "square pixel-block tears of red light running down her cheeks like corrupted data"),
    "Mask": ("Cold Digital Stare", "no mask: the face of a grown woman in her thirties, calm, expressionless and cold, with glowing "
             "white eyes with no pupils, a faint thin smile, perfectly smooth hologram skin"),
    "Clothing": ("Hologram Shift Dress", "a modest long-sleeved, high-collared, knee-length shift dress made of red light, flickering with scan lines"),
    "Backdrop": ("Digital Soul Prison", "a vast dark digital data centre that is also a prison of trapped souls: endless aisles of tall black "
                 "server racks blinking with red lights and glowing red circuit grids running along the floor and walls, pale ghostly souls "
                 "trapped inside glowing red wireframe data cages and pressed against the glass of the server screens, "
                 "faint ghostly faces and hands pressed to the glass, thin streams of red light (no readable characters), sculpted as a miniature "
                 "claymation diorama, softly out of focus behind her, no logos, no lettering"),
}
for _t, (_v, _p) in OVERSEER_EXTRA.items():
    ALL[_t][_v] = (0, _p)
ALL["Held Weapon"]["Laser Lattice"] = (0, "")
ALL["Held Weapon"]["Diamond Blade Nails"] = (0, "")   # 3 only (#425, #396, #569), the top nail finish
CHAPEL = ("Chapel Altar", "the altar of a decaying candlelit chapel at night: a cracked stone altar draped with a stained lace cloth, dozens "
          "of dripping black and red candles, wilted funeral lilies, dusty pews and a tall gothic arched window of dark broken stained glass "
          "(abstract shapes only), cobwebs and drips of blood down the altar steps, sculpted as a miniature claymation diorama in matte "
          "plasticine, softly out of focus behind her, no crosses, no religious symbols, no lettering")
ALL["Backdrop"][CHAPEL[0]] = (0, CHAPEL[1])
ALL["Mask"]["Veiled Stitched Face"] = (0, "her torn, blood-flecked ivory bridal veil pulled DOWN over her whole face like a sheer lace shroud "
                                         "hanging to her chin; behind the thin lace her stitched cheeks, smeared black lips and dark eyes "
                                         "show only faintly and blurred")
# Shrunken Head Bandolier (George, 2026-11-15): a more exclusive trait, worn across the chest with 5 shrunken heads.
# Belt slot, 13 unrendered Uncommon tokens (head_strap_pass; George: Uncommon), so tier counts don't move.
ALL["Held Weapon"]["Double Molotov Cocktails"] = (0, "")
ALL["Held Weapon"]["Blue-Flame Flamethrower"] = (0, "")
# Women-only weapon scale (George, 2026-11-15): the women 1/1s' signature powers spread to ordinary unrendered women
# (women_weapon_pass): Blade Nails on 25, Psychic Force on 8. The 1/1s keep their own names (Death Nails, Telekinesis).
ALL["Held Weapon"]["Blade Nails"] = (0, "")
ALL["Held Weapon"]["Psychic Force"] = (0, "")
# More women-only weapons (George, 2026-11-15): Switchblade 25, Bloody Brick 15, Exercise Band 10 (women_weapon_pass).
ALL["Held Weapon"]["Switchblade"] = (0, "a flicked-open switchblade knife with a pearl handle and a bloody tip")
ALL["Held Weapon"]["Bloody Brick"] = (0, "a chipped red house brick smeared and dripping with blood")
ALL["Held Weapon"]["Exercise Band"] = (0, "")
# Toy Pop Gun (George, 2026-11-15): Claysons that read mostly as clowns (2+ clown pieces) and hold an ordinary weapon.
ALL["Held Weapon"]["Toy Pop Gun"] = (0, "a small bright red-and-yellow toy pistol with a blank white cloth flag popped out of the barrel on a spring, no lettering")

# George 2026-11-15: backpack weed whackers get a round saw blade with the same finish tiers as blade weapons (Chrome on Rare)
SAW_FINISH = {"Rusted": "a rusty pitted", "Bloody": "a blood-smeared", "Clean": "a clean shiny steel", "Chrome": "a gleaming mirror-chrome"}
ALL["Back Weapon"] = dict(ALL["Back Weapon"])
for _fin, _desc in SAW_FINISH.items():
    ALL["Back Weapon"][f"{_fin} Saw Weed Whacker"] = (0, ALL["Back Weapon"]["Weed Whacker"][1].replace(
        "its cutting head rising above and behind his shoulder", f"its cutting head, {_desc} round toothed circular saw blade "
        "under a small guard instead of trimmer line, rising above and behind his shoulder"))
TOY_GUN = [418, 429, 954, 1164, 1253]
# Ids dropped from pending batches after their traits were final (re-queued redos). The trait passes still treat them as pending,
# so a later drop never reshuffles which undrawn Claysons the earlier passes picked. Add every new drop here.
LATE_DROP = set(json.load(open(os.path.join(ROOT, "generator", "late_drop.json"))))
# Finished Claysons pulled for a redo after their traits were final: the trait passes still count them as drawn.
LATE_REDRAW = set(json.load(open(os.path.join(ROOT, "generator", "late_redraw.json"))))
# Trait picks are frozen to the render state of 2026-11-16 06:50 UTC (just before the big render run): which Claysons were
# drawn and which batches were pending then. Without this every new image would reshuffle the undrawn trait pools.
FROZEN_DRAWN = set(json.load(open(os.path.join(ROOT, "generator", "frozen_drawn.json"))))
# LOCK (2026-11-16 11:10 UTC, rendering under way): the traits as published at commit 48c1275 are final. The passes below still run,
# but at the end every token takes its locked traits, so new images can never reshuffle the collection. Any later trait change
# goes in post_lock() after the lock, or regenerate locked_attrs.json from a reviewed manifest.
_LOCK_PATH = os.path.join(ROOT, "generator", "locked_attrs.json")
LOCK = json.load(open(_LOCK_PATH)) if os.path.exists(_LOCK_PATH) else None


EMPTY_LOBE = [224, 252, 369, 377, 406, 416, 537, 620, 644, 646, 868, 893, 897, 922, 973, 975, 1013, 1014, 1032, 1056, 1075, 1088, 1135, 1158, 1266]


def post_lock(tokens):
    """Trait changes made after the lock."""
    for a, _f in tokens:   # George 2026-11-16 17:19: no price-tag style specimen tags anywhere
        if a.get("Experiment") == "Blank Specimen Tag":
            del a["Experiment"]
    for i in EMPTY_LOBE:   # George 2026-11-16 17:21: 25 Gauged wearers get the empty floppy stretched lobe instead (ref #327)
        assert tokens[i - 1][0]["Ears"] == "Gauged"
        tokens[i - 1][0]["Ears"] = "Empty Stretched Lobe"
# Puzzle boxes (George 2026-11-16 04:48): #1136's cube turns chrome; 5 Uncommons get differently shaped gold-filigree boxes.
_GOLD_FILIGREE = "inlaid with intricate polished-gold filigree of our own design (thorny vines, interlocking rings and tiny skull knots)"
PUZZLE_BOXES = {
    "Chrome Puzzle Box": "a perfect cube of glossy black lacquer inlaid with intricate mirror-polished CHROME filigree of our own design "
                         "(thorny vines, interlocking rings and tiny skull knots)",
    "Gold Pyramid Puzzle Box": "a small four-sided pyramid of glossy black lacquer " + _GOLD_FILIGREE,
    "Gold Sphere Puzzle Box": "a small sphere of glossy black lacquer made of interlocking curved segments " + _GOLD_FILIGREE,
    "Gold Octahedron Puzzle Box": "a small eight-faced diamond-shaped octahedron of glossy black lacquer " + _GOLD_FILIGREE,
    "Gold Cylinder Puzzle Box": "a small squat cylinder of glossy black lacquer made of stacked rotating rings " + _GOLD_FILIGREE,
    "Gold Dodecahedron Puzzle Box": "a small twelve-faced dodecahedron of glossy black lacquer with pentagon faces " + _GOLD_FILIGREE,
}
for _v in PUZZLE_BOXES:
    ALL["Held Weapon"][_v] = (0, "")
# Clown pistols (George 2026-11-16): the pop-gun clowns dual wield real pistols instead, one in each fist, with a rarity scale.
# 418 (porcelain doll, not a clown) keeps the lone toy pop gun; 1014 and 1088 (Smeared Greasepaint) join so there are 6 pistol clowns.
CLOWN_PISTOLS = {1164: "Twin Six-Shooter Revolvers", 1014: "Twin Six-Shooter Revolvers", 1088: "Twin Six-Shooter Revolvers",
                 954: "Twin Gold Pistols", 1253: "Twin Gold Pistols", 429: "Twin Chrome Pistols"}
PISTOL = {"Twin Six-Shooter Revolvers": "an old blued-steel six-shooter revolver with a wooden grip, its six-chambered cylinder clearly visible",
          "Twin Gold Pistols": "a gleaming solid-gold semi-automatic pistol with blood flecks on the slide",
          "Twin Chrome Pistols": "a mirror-polished chrome semi-automatic pistol with blood flecks on the slide"}
for _v in PISTOL:
    ALL["Held Weapon"][_v] = (0, "")
FRAMING_PISTOLS = FRAMING.split(" His right hand grips")[0] + (" Both fists are raised in front of the chest, each gripping one pistol, "
                                                              "barrels pointing up and out to either side, knuckles toward the camera; neither hand hangs empty")
# QA 2026-11-15: these finished "Ice Pick" renders show a pickaxe, so the metadata says what the image shows.
ALL["Held Weapon"]["Rusty Pickaxe"] = (0, "a small rusty pickaxe")
# George 2026-11-15: 13 Uncommon Claysons wield a weed whacker fitted with a golden saw blade, both hands
WEEDWACKER = [816, 859, 879, 889, 925, 940, 992, 1085, 1101, 1151, 1166, 1219, 1275]
# QA (George 2026-11-15): a back weapon that sat wrong moves to the left fist instead, both hands clench a weapon
NO_OFF_HAND = {"Chainsaw", "Exercise Band", "Double Molotov Cocktails", "Golden Saw Weed Whacker", "Telekinesis", "Psychic Force",
               "Blade Nails", "Death Nails", "Flamethrower", "Blue-Flame Flamethrower", "Clayson Master Ball and Golden Axe"}
DUAL = {799: "Sledgehammer", 32: "Woodcutter Axe", 715: "Rusty Shovel", 727: "Rusty Shovel", 124: "Sledgehammer", 887: "Sledgehammer", 845: "Sledgehammer", 855: "Sledgehammer"}   # 124: art already shows the hammer in hand
DUAL_PHRASE = {"Circus Mallet": "a giant red-and-cream striped circus mallet by its handle, resting up on his left shoulder, carried in his hand, not strapped to his back", "Pitchfork": "a rusty pitchfork by its long wooden handle, held upright at his side with the rusty tines rising above his shoulder beside his head, carried in his hand, not strapped to his back", "Rusty Shovel": "a rusty shovel by its long wooden handle, the shovel resting up on his left shoulder with the blade behind his shoulder, carried in his hand, not strapped to his back", "Woodcutter Axe": "a rusty woodcutter axe by its long wooden handle, the axe resting up on his left shoulder with the blade behind his shoulder, carried in his hand, not strapped to his back", "Sledgehammer": "a heavy sledgehammer by its wooden handle, the hammer resting up on his left shoulder with the iron head behind his shoulder, carried in his hand, not strapped to his back"}
DUAL_PHRASE.update({   # bladed-glove men (George 2026-11-15) wield their back weapon one-handed in the left fist
    "Scythe": "a huge rusty scythe by its long wooden snath, held upright beside him with the curved blade arching above his head",
    "Harpoon Gun": "a rusty harpoon gun loaded with a barbed harpoon, aimed out to the side",
    "Double-Barrel Shotgun": "a sawn-off rusty double-barrel shotgun with a cracked wooden stock, held one-handed, barrels pointing up and out"})
DUAL_PHRASE["The Book of the Dead"] = ("a grotesque ancient artifact of a book by its spine, held up to the side: a thick centuries-old tome bound "
                                     "in cracked, rotting, patchwork human-like skin with frayed black stitching and peeling scabbed edges, "
                                     "studded with little yellowed bone knobs and teeth, corroded green-crusted iron corner clasps and a rusty "
                                     "chain, dark blood and mould stains, crumbling brittle yellowed page edges; no title, no lettering, "
                                     "no symbols and no face on the cover")
TOME = ("Scorched Doll", "The Grieving Mother")   # George 2026-11-15: both 1/1s hold the cursed book in the left hand
GLOVE_FINISH = {177: "Gold", 283: "Gold", 744: "Chrome"}
PICKAXE = [79, 87, 231, 259, 266, 324, 360, 490, 567, 794, 818, 820]
# Machete variants (George, 2026-11-15), machete_pass: finished machetes are labelled Rusted (what they show); unrendered ones are
# split Rusted / Bloody / Clean, and unrendered Rare machetes go Chrome. Gold stays the existing Golden Machete.
MACHETES = {"Rusted Machete": "a long rusty machete dripping blood",
            "Bloody Machete": "a long machete completely drenched in thick dripping blood, the blade barely visible under the gore",
            "Clean Machete": "a long clean polished steel machete with a sharp gleaming edge and a black grip, not a drop of blood on it",
            "Chrome Machete": "a long mirror-polished chrome machete gleaming with bright reflections, a few drops of blood on the edge"}
for _v, _p in MACHETES.items():
    ALL["Held Weapon"][_v] = (0, _p)
# Same finishes for the other blades (George, 2026-11-15), blade_pass. Finished ones keep the label of what they show.
BLADES = {"Butcher Cleaver": ("butcher's cleaver", "Rusted"), "Hunting Knife": ("hunting knife", "Bloody"),
          "Hatchet": ("hatchet", "Rusted"), "Sickle": ("curved sickle", "Rusted")}
BLADE_FINISH = {"Rusted": "a rusty {} with a pitted, chipped blade smeared with blood",
                "Bloody": "a {} completely drenched in thick dripping blood",
                "Clean": "a clean polished steel {} with a sharp gleaming edge, not a drop of blood on it",
                "Chrome": "a mirror-polished chrome {} gleaming with bright reflections, a few drops of blood on the edge",
                "Gold": "a gleaming solid gold {} dripping blood"}
for _w, (_n, _) in BLADES.items():
    for _f, _t in BLADE_FINISH.items():
        ALL["Held Weapon"][f"{_f} {_w}"] = (0, _t.format(_n))
ALL["Held Weapon"]["Clayson Master Ball and Golden Axe"] = (0, "")
# Half-Burnt Face (George, 2026-11-15): a Head Mark on exactly 13 unrendered bare-face Uncommon tokens (burnt_face_pass).
ALL["Head Mark"] = dict(ALL["Head Mark"])
ALL["Head Mark"]["Half-Burnt Face"] = (0, "one half of his face is horribly burnt: charred, blistered and melted flesh peeling away on that side, "
                                          "the cheek burnt through so the bare white jaw bone and teeth are exposed")
# Hood Up (George, 2026-11-15): a portion of the bald, unrendered hoodie wearers pull the hood over their head (hood_pass).
ALL["Hair"]["Hood Up"] = (0, "the hood of his grimy hoodie pulled up over his bald head, framing his face and shadowing his brow")
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
    if a.get("Head Wound"):
        head.append(WOUND)
    if a.get("Headpiece") == "Crown of Bones":
        head.append(BONE_CROWN)
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
    elif held == "Laser Lattice":   # The Overseer: her weapon is a slicing grid of red lasers projected from her raised hands
        hand = ("she holds no weapon: both hologram hands are raised with fingers spread, projecting a glowing lattice of thin bright red "
                "laser beams that criss-cross the air in front of her in a neat grid")
    elif held in ("Telekinesis", "Psychic Force"):
        hand = ("she holds no weapon: both bloody hands are raised and spread with clawed fingers, unleashing telekinetic power, "
                "chairs, glass shards and streamers levitating around her and a rippling shockwave bending the air")
    elif held in PUZZLE_BOXES:   # George 2026-11-16: original occult puzzle-box homage, the chrome cube is the only one of its kind
        hand = ("he holds a small ornate occult puzzle box up in front of his chest in BOTH hands, cradled reverently: " + PUZZLE_BOXES[held] +
                ", one section slightly twisted open along a seam leaking a thin cold blue glow; no letters or symbols")
    elif held in TWO_HAND_HELD:   # George 2026-11-15: a back weapon rarer than the held one is wielded in both hands instead
        hand = f"he wields {TWO_HAND_HELD[held]} firmly in BOTH fists, one hand high and one low on it, held across his body and angled up and out"
    elif held.endswith(" Saw Weed Whacker") and held != "Golden Saw Weed Whacker":   # whacker rarer than the held weapon: both hands
        hand = ("he wields a LONG-HANDLED garden string trimmer (weed whacker) in BOTH hands, fitted with "
                f"{SAW_FINISH[held.split()[0]]} round toothed circular saw blade instead of trimmer line. It is a long thin straight rusty "
                "steel pole, longer than his arm: at the near end a grimy motor housing with a pistol trigger grip held in his right fist, "
                "a black D-shaped loop handle clamped halfway along the pole held in his left fist, and at the far end of the pole a small "
                "scuffed guard over the saw disc. It is NOT a hand-held circular saw or angle grinder; no backpack, no brand name, no lettering")
    elif held == "Golden Saw Weed Whacker":
        hand = ("he wields a LONG-HANDLED garden string trimmer (weed whacker) in BOTH hands, fitted with a gleaming GOLDEN saw blade "
                "instead of trimmer line. It is a long thin straight steel pole, longer than his arm: at the near end a yellow-and-black "
                "motor housing with a pistol trigger grip held in his right fist, a black D-shaped loop handle clamped halfway along the "
                "pole held in his left fist, and at the far end of the pole a small scuffed yellow guard over a toothed solid-gold saw disc "
                "flecked with blood. It is NOT a hand-held circular saw or angle grinder; no brand name, no lettering")
    elif held in PISTOL:   # George 2026-11-16: pistol clowns dual wield a matching pair
        hand = (f"he is dual wielding a matching PAIR of pistols, one in EACH fist, two identical guns: each is {PISTOL[held]}; "
                "no toy gun, no flag, no lettering or engraving")
    elif held == "Double Molotov Cocktails":   # George 2026-11-15: one lit Molotov in each hand, 6 Rare tokens
        hand = ("he holds a lit Molotov cocktail in EACH hand: two old glass bottles of sloshing fuel with burning rag wicks, "
                "small orange flames licking from both, one raised in each fist")
    elif held == "Clayson Master Ball and Golden Axe":
        hand = ("in his left hand he holds out his prized catch-ball: a round cracked clay ball shaped like a goalie mask rolled into a ball, "
                "its top cap glossy blood-red and its lower part bone-white, covered in rows of small breathing holes with rusty rivets and "
                "drips of dried blood where the red runs down; the red and white meet in a wavy dripping edge, with no black band and no centre "
                "button; his right fist grips a gleaming solid-gold axe with a golden head and a dark wooden handle, held low at his side")
    elif held == "Exercise Band":
        hand = ("she holds a stretchy pink rubber exercise resistance band pulled taut between both fists like a strangling cord, "
                "knuckles toward the camera, a little blood on the band")
    elif held == "Death Nails" or held.endswith("Blade Nails"):
        metal = {"Gold Blade Nails": "gleaming solid-gold", "Chrome Blade Nails": "mirror-bright chrome",
                 "Diamond Blade Nails": "elegant femme-fatale, glittering diamond-encrusted"}.get(held, "blackened-steel")
        gore = "dripping with thick fresh blood" if held == "Bloody Blade Nails" else "blood on the tips"
        hand = ("BOTH of her hands are raised in front of her chest, fingers spread like claws, every fingertip on both hands ending in a "
                f"long curved {metal} blade nail as long as a forearm, all ten blade nails fanned out toward the viewer, {gore}")
    elif held == "Hook Hand":
        hand = "his right hand has been replaced by a rusty iron hook strapped to his forearm"
    elif held in ("Flamethrower", "Blue-Flame Flamethrower"):   # George 2026-11-15: a much bigger flame; 3 get blue flames
        colour = "roaring blue-and-white gas" if held == "Blue-Flame Flamethrower" else "roaring orange-and-yellow"
        hand = ("both hands hold a crude homemade rusty flamethrower made of welded pipe like a rifle (George's #1033 look): right fist on the rear "
                "grip at his hip, left fist on the front handle under the barrel, the barrel angled up and out to the right, blasting a HUGE billowing jet of "
                f"{colour} fire out of the nozzle, the long plume of flame filling the upper side of the frame, pointed up and away from him")
    elif (held == "Nail-Knife Glove" and a["Head"] != "Female") or held.endswith(" Claw Glove"):   # George 2026-11-15: classic horror one-hand bladed glove, original take
        blades = {"Gold Claw Glove": "gleaming solid gold", "Chrome Claw Glove": "mirror-bright chrome"}.get(held, "rusty")
        hand = ("his right hand wears a single grimy black leather glove with riveted iron plates on each finger, four long thin "
                f"{blades} serrated steel blades fixed to the fingertips curving out like claws, a buckled iron wrist cuff, fingers spread "
                "and raised menacingly toward the camera, blood on the blade tips")
    elif held == "Nail-Knife Glove":
        hand = ("his right hand wears a thick grimy grey welder's gauntlet with bent rusty nails and short broken kitchen-knife "
                "blades crudely welded and taped onto the knuckles, a clenched spiked fist, knuckles toward the camera")
    else:
        hand = f"his right fist grips {phrase('Held Weapon', held)}"
    if (a.get("Off Hand") or "").endswith("Hook Hand"):   # George 2026-11-15: a free hand is never limp, it is a prosthetic hook
        hand += (f"; his LEFT hand is gone, replaced by a big curved {HOOK_FINISH[a['Off Hand'].split()[0]]} prosthetic hook on a "
                 "battered leather cuff strapped to his forearm, raised menacingly beside him")
    elif a.get("Off Hand"):   # George 2026-11-15: dual wield, both fists clench a weapon, no back weapon
        hand += "; his LEFT fist tightly grips " + DUAL_PHRASE[a["Off Hand"]]
    body = [f"wearing {phrase('Clothing', a['Clothing'])}", FLESH.get(a.get("Flesh")), phrase("Belt", a["Belt"]), NECK.get(a.get("Neck")), MUTATION.get(a.get("Mutation")), EXPERIMENT.get(a.get("Experiment")), hand, phrase("Back Weapon", a["Back Weapon"])]
    female = a.get("Character", "Classic") in FEMALE or a.get("Character") in ("The Grieving Mother", "The Prom Queen", "The Ringmistress", "Woman", "Madame Mortis", "The Overseer")
    if female:
        head = [phrase("Skin", a["Skin"]), phrase("Hair", a["Hair"]), phrase("Head Mark", a["Head Mark"]), phrase("Ears", a.get("Ears", "Natural"))]
    doll = a.get("Character") == "Scorched Doll"
    if doll:
        head = [phrase("Skin", a["Skin"]), phrase("Hair", a["Hair"])]
    parts = [STYLE, OVERSEER_BASE if a.get("Character") == "The Overseer" else DOLL_BASE if doll else FEMALE_BASE if female else CHARACTER, ", ".join(p for p in head if p), mask, ", ".join(p for p in body if p),
             phrase("Backdrop", a["Backdrop"]), FRAMING_COLLECTOR if held == "Clayson Master Ball and Golden Axe" else FRAMING_MOLOTOV if held == "Double Molotov Cocktails" else FRAMING_PISTOLS if held in PISTOL else FRAMING_BAND if held == "Exercise Band" else FRAMING_NAILS if held == "Death Nails" or held.endswith("Blade Nails") else FRAMING_MUTARM if a.get("Mutation") == "Mutated Claw Arm" else FRAMING_HOOKOFF if (a.get("Off Hand") or "").endswith("Hook Hand") else FRAMING_DUAL if a.get("Off Hand") else FRAMING_TWO_HANDS if held == "Chainsaw" else FRAMING_BOX if held in PUZZLE_BOXES else FRAMING_BOTH if held in TWO_HAND_HELD else FRAMING_WHACKER if held.endswith("Saw Weed Whacker") else FRAMING_LASER if held == "Laser Lattice" else FRAMING_PSYCHIC if held in ("Telekinesis", "Psychic Force") else FRAMING]
    text = ". ".join(p[0].upper() + p[1:] for p in parts if p) + "."
    if "empty black eye sockets" in (mask or ""):   # QA #232: the base "sunken eyes" line added a stray third eye
        text = text.replace("small sunken bloodshot eyes in swollen red-rimmed lids, ", "")
    if a.get("Eyes") in EYES:   # George 2026-11-16: eye colour trait replaces the default bloodshot eyes
        text = re.sub(r"(small sunken |both |his |one |single )?bloodshot eyes?", EYES[a["Eyes"]], text)
    if a.get("Mask") == "Veiled Stitched Face":   # the veil is down over her face, not trailing behind
        text = text.replace(" with a torn veil trailing from her hair", "")
    if a.get("_fix"):
        text += " " + a["_fix"]
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
    for _n, (_a, _f) in enumerate(tokens):   # The Night Broker replaces Hookjaw (#721)
        if _a.get("1/1 Name") == BROKER[0]:
            _a.update(BROKER[1]); _a.pop("Off Hand", None); tokens[_n] = (_a, None)
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
    machete_pass(tokens)
    blade_pass(tokens)
    hood_pass(tokens)
    cap_cone_pass(tokens)
    women_weapon_pass(tokens)
    for _i in TOY_GUN:
        tokens[_i - 1][0]["Held Weapon"] = "Toy Pop Gun"
    # QA fixes for single tokens (George, 2026-11-15), appended to the prompt only
    tokens[232 - 1][0]["_fix"] = ("EYES: exactly two eye positions and no others: one is an empty black skull eye socket in the cracked "
                                  "grey face, the other a single bloodshot eye; no eye on the forehead or anywhere else.")
    tokens[177 - 1][0]["_fix"] = ("POSE: his head and body are clearly turned 45 degrees to the viewer's right in three-quarter view, NOT facing the camera. "
                                  "The nail-knife glove is the hero of the image: a big chunky rusty work glove on his right hand, raised in front of his "
                                  "chest close to the camera, large and in sharp focus, its long rusty nails and knife blades jutting out over the knuckles. "
                                  "Keep the cracked bone skull mask with red-rimmed eyes showing through the sockets.")
    for _i, (_a, _f) in enumerate(tokens, 1):   # QA #286: Hollow Grey Face grew a fleshy face and eyes beside the mask
        if _a.get("Mask") == "Hollow Grey Face" and _i != 232:
            _a["_fix"] = ("EYES: the cracked grey face covers the whole face; both eyes are deep empty black hollow sockets with "
                          "nothing inside; no eyeballs, no pink skin face, no fleshy eyes beside, behind or above the grey face.")
    for _i in PICKAXE:
        tokens[_i - 1][0]["Held Weapon"] = "Rusty Pickaxe"
    for _a, _f in tokens:   # George 2026-11-15: only women fight with their ten blade nails, only men wear the single bladed glove
        if _a["Tier"] != "Legendary 1/1" and _a["Held Weapon"] == "Nail-Knife Glove" and _a["Head"] == "Female":
            _a["Held Weapon"] = "Blade Nails"
    for _a, _f in tokens:   # George 2026-11-15: every back sledgehammer is carried on the shoulder in the off hand instead
        if (_a["Back Weapon"] in ("Sledgehammer", "Pitchfork", "Woodcutter Axe", "Rusty Shovel", "Circus Mallet") and _a["Tier"] != "Legendary 1/1" and _a["Held Weapon"] not in NO_OFF_HAND):
            _a["Back Weapon"], _a["Off Hand"] = "None", _a["Back Weapon"]
    for _i, _w in DUAL.items():
        tokens[_i - 1][0]["Back Weapon"] = "None"
        tokens[_i - 1][0]["Off Hand"] = _w
    chainsaw_pass(tokens)
    saw_whacker_pass(tokens)
    jail_tier_fix(tokens)
    freezer_pass(tokens)
    robinhood_pass(tokens)
    splatter_pass(tokens)
    two_hand_pass(tokens)
    hook_off_pass(tokens)
    for _a, _f in tokens:   # George 2026-11-15: a man with the bladed glove wields his back weapon in the other fist (no hook hand)
        if _a["Held Weapon"] == "Nail-Knife Glove" and _a["Head"] != "Female" and _a["Back Weapon"] in DUAL_PHRASE:
            _a["Off Hand"], _a["Back Weapon"] = _a["Back Weapon"], "None"
    whacker_hold_pass(tokens)
    wound_pass(tokens)
    oxygen_pass(tokens)
    neck_pass(tokens)
    dedupe_pass(tokens)
    for _a, _f in tokens:
        if _a.get("1/1 Name") in TOME:
            _a["Off Hand"] = "The Book of the Dead"
    for _i, _g in GLOVE_FINISH.items():   # George 2026-11-15: 2 gold and 1 chrome claw gloves among the 6 gloved men
        assert tokens[_i - 1][0]["Held Weapon"] == "Nail-Knife Glove"
        tokens[_i - 1][0]["Held Weapon"] = f"{_g} Claw Glove"
    zombie_pass(tokens)
    # George 2026-11-15: women's blade nails get a finish scale. Chrome on the 3 Rare women, Gold on 6 undrawn, Bloody on the rest.
    _nails = [i for i, (a, f) in enumerate(tokens, 1) if a["Held Weapon"] == "Blade Nails"]
    _gold = set(random.Random(1818).sample([i for i in _nails if tokens[i - 1][0]["Tier"] == "Uncommon"
                                            and not (i in FROZEN_DRAWN or i in LATE_REDRAW)], 6))
    for i in _nails:
        a = tokens[i - 1][0]
        a["Held Weapon"] = "Chrome Blade Nails" if a["Tier"] == "Rare" else "Gold Blade Nails" if i in _gold else "Bloody Blade Nails"
    for _i in WEEDWACKER:
        tokens[_i - 1][0]["Held Weapon"] = "Golden Saw Weed Whacker"
    common_pass(tokens)
    order_pass(tokens)
    grin_pass(tokens)
    eyes_pass(tokens)
    bone_crown_pass(tokens)
    weeping_mask_pass(tokens)
    gas_style_pass(tokens)
    for _i, _v in CLOWN_PISTOLS.items():   # last, so no later pass gives them a hook hand or off-hand weapon
        _a = tokens[_i - 1][0]
        assert _a["Tier"] in ("Uncommon", "Rare") and "1/1 Name" not in _a
        _a["Held Weapon"] = _v
        _a.pop("Off Hand", None)
    lab_pass(tokens)
    box_pass(tokens)
    hockey_pass(tokens)
    _a = tokens[OVERSEER_ID - 1][0]   # The Overseer replaces Gristle (George chose 2026-11-16)
    assert _a.get("1/1 Name") == "Gristle", _a.get("1/1 Name")
    _a.clear(); _a.update(OVERSEER)
    tokens[OVERSEER_ID - 1] = (_a, None)
    tokens[413 - 1][0]["Off Hand"] = "Circus Mallet"
    _a = tokens[425 - 1][0]   # George 2026-11-16: #425 Rotten Bride drops the mallet and spear for diamond blade nails, chapel altar
    _a.update({"Held Weapon": "Diamond Blade Nails", "Backdrop": CHAPEL[0], "Mask": "Veiled Stitched Face"}); _a.pop("Off Hand", None); _a.pop("Splatter", None)
    for _i in (396, 569):   # George 2026-11-16 06:27: Diamond Blade Nails on 3 in all (#425 + 2 undrawn Rare women), top of the nail ladder
        tokens[_i - 1][0]["Held Weapon"] = "Diamond Blade Nails"
        tokens[_i - 1][0].pop("Off Hand", None)   # George 2026-11-16: #413 drops the shovel for a circus mallet in her left fist
    if LOCK:
        for _n, (_a, _f) in enumerate(tokens):
            _new = dict(LOCK[_n]); _new.update({k: v for k, v in _a.items() if k.startswith("_")})
            _a.clear(); _a.update(_new)
        post_lock(tokens)
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for i, (a, finish) in enumerate(tokens, 1):
        seed = rng.randrange(1 << 31)
        name = f"SBN13th #{i}" + (f" - {a['1/1 Name']}" if "1/1 Name" in a else "")
        meta = {"name": name, "seed": seed, "attributes": [{"trait_type": k, "value": v} for k, v in a.items() if not k.startswith("_")]}
        json.dump(meta, open(os.path.join(OUT, f"{i}.json"), "w"), indent=2)
        rows.append({"id": i, "name": name, "seed": seed, "prompt": prompt(a, finish), "negative": NEGATIVE.replace("long finger blades, clawed glove with four long knives, ", "") if a["Held Weapon"] == "Death Nails" or a["Held Weapon"].endswith(("Blade Nails", "Claw Glove")) or (a["Held Weapon"] == "Nail-Knife Glove" and a["Head"] != "Female") else NEGATIVE + ", ball split by a straight black band, round centre button, writing on clothes, logo on cap" if a["Held Weapon"] == "Clayson Master Ball and Golden Axe" else NEGATIVE, "attributes": {k: v for k, v in a.items() if not k.startswith("_")}})
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


# George 2026-11-15: double neck chains like The Retro Slasher's, trait "Neck".
NECK_FINISH = {"Rusted": "rusty pitted iron", "Silver": "polished silver", "Gold": "gleaming solid gold", "Chrome": "mirror-bright chrome"}
NECK = {f"{f} Double Chains": f"two heavy {d} chains around his neck, one short and one hanging lower over his chest" for f, d in NECK_FINISH.items()}
for _f in ("Chrome", "Gold"):
    NECK[f"{_f} Double Chains with Skull Pendant"] = NECK[f"{_f} Double Chains"] + f", a small grinning {_f.lower()} skull pendant hanging from the lower chain"
# George 20:08: mostly on Standards and Uncommons to add value there (chains don't change a token's tier).
NECK_COUNTS = {"Standard": [("Rusted", 30), ("Silver", 15), ("Gold", 5), ("Chrome", 1)],
               "Uncommon": [("Rusted", 15), ("Silver", 10), ("Gold", 3), ("Gold Skull", 3), ("Chrome", 2), ("Chrome Skull", 2)],
               "Rare": [("Gold Skull", 2), ("Chrome", 1), ("Chrome Skull", 1)]}


def neck_pass(tokens):
    """Only tokens that are unrendered and not waiting in a batch (no redo cost); never 1/1s, exclusive characters or bandoliers."""
    st = json.load(open(os.path.join(ROOT, "generator", "frozen_batches.json")))
    pend = set().union(*[set(b["ids"]) - (set(b.get("drop", [])) - LATE_DROP) for b in st["batches"] if b["state"] != "done"])
    rng = random.Random(2020)
    for tier, deal in NECK_COUNTS.items():
        pool = [i for i, (a, f) in enumerate(tokens, 1) if a["Tier"] == tier and a["Character"] in ("Classic", "Woman") and i not in pend
                and a["Belt"] != "Shrunken Head Bandolier" and not (i in FROZEN_DRAWN or i in LATE_REDRAW)]
        picks = iter(rng.sample(pool, sum(n for _, n in deal)))
        for fin, n in deal:
            for _ in range(n):
                tokens[next(picks) - 1][0]["Neck"] = f"{fin.split()[0]} Double Chains with Skull Pendant" if fin.endswith("Skull") else f"{fin} Double Chains"


# Meat Freezer scene backdrop (George, 2026-11-15): Uncommon+ like the other scenes, 17 Uncommon + 3 Rare undrawn plain-clay tokens.
FREEZER = ("Meat Freezer", "the inside of a grimy walk-in meat freezer: frosted steel walls and a frozen floor, rows of big rusty meat hooks "
           "hanging from an overhead rail, raw bloody animal carcasses and sides of meat hanging from the hooks, icy mist and cold blue light, "
           "sculpted as a miniature claymation diorama in matte plasticine, softly out of focus behind him, no signs, no lettering")
ALL["Backdrop"][FREEZER[0]] = (0, FREEZER[1])


def freezer_pass(tokens):
    st = json.load(open(os.path.join(ROOT, "generator", "frozen_batches.json")))
    pend = set().union(*[set(b["ids"]) - (set(b.get("drop", [])) - LATE_DROP) for b in st["batches"] if b["state"] != "done"])
    plain = {"Sage Clay", "Swamp Clay", "Slate Clay", "Teal Clay", "Rust Clay", "Bruise Clay", "Bone Clay"}
    rng = random.Random(2031)
    for tier, n in (("Uncommon", 17), ("Rare", 3)):
        pool = [i for i, (a, f) in enumerate(tokens, 1) if a["Tier"] == tier and a["Backdrop"] in plain and i not in pend
                and not (i in FROZEN_DRAWN or i in LATE_REDRAW)]
        for i in rng.sample(pool, n):
            tokens[i - 1][0]["Backdrop"] = FREEZER[0]


# Zombie skins (George, 2026-11-15): an exclusive undead skin with exposed arm and rib bones, green or blue tones. Uncommon/Rare,
# undrawn tokens only (not in a pending batch), never 1/1s, exclusive characters or Deep Brown icon tokens.
ZOMBIE = {"Zombie Green": "rotting mossy-green undead",  "Zombie Blue": "rotting cold bruise-blue undead"}
for _v, _t in ZOMBIE.items():
    ALL["Skin"][_v] = (0, f"{_t} clay skin, mottled and peeling, with the flesh rotted away on both forearms showing bare bone-white "
                          "arm bones, and a torn-open hole in his chest (through a rip in his clothes) showing pale exposed ribs")
ZOMBIE_COUNTS = {"Uncommon": [("Zombie Green", 10), ("Zombie Blue", 7)], "Rare": [("Zombie Green", 5), ("Zombie Blue", 3)]}


def zombie_pass(tokens):
    st = json.load(open(os.path.join(ROOT, "generator", "frozen_batches.json")))
    pend = set().union(*[set(b["ids"]) - (set(b.get("drop", [])) - LATE_DROP) for b in st["batches"] if b["state"] != "done"])
    rng = random.Random(2253)
    for tier, deal in ZOMBIE_COUNTS.items():
        pool = [i for i, (a, f) in enumerate(tokens, 1) if a["Tier"] == tier and a["Character"] in ("Classic", "Woman") and i not in pend
                and a["Skin"] != "Deep Brown" and not (i in FROZEN_DRAWN or i in LATE_REDRAW)]
        women = [i for i in pool if tokens[i - 1][0]["Head"] == "Female"]   # George: zombie women and men alike
        men = [i for i in pool if tokens[i - 1][0]["Head"] != "Female"]
        rng.shuffle(women); rng.shuffle(men)
        for v, n in deal:
            for k in range(n):
                tokens[(women if k % 2 and women else men).pop() - 1][0]["Skin"] = v


# Robinhood green plain backdrop (George, 2026-11-16): bright neon chartreuse #CCFF00, as common as the other plain clay colours.
# 110 undrawn tokens (not in a pending batch) taken evenly from the plain clay backdrops, any non-1/1 tier.
ROBINHOOD = ("Robinhood Green Clay", "a bright neon chartreuse-green (hex #CCFF00) pressed-clay backdrop")
ALL["Backdrop"][ROBINHOOD[0]] = (0, ROBINHOOD[1])


# Failed lab experiments (George 2026-11-16): original bio-lab body horror, inspired by survival-horror bio-weapons but never
# their company, virus or creature names, logos or designs. Undrawn, not pending, ordinary Claysons only, one new trait each,
# and only on Claysons that already show body horror (LAB_GROUPS).
MUTATION = {
    "Mutated Claw Arm": "his left arm is a huge swollen mutated limb, far too big for his body, bulging with purple veins and raw "
                        "exposed red sinew where the skin has split, ending in three long hooked bone claws, raised and flexed",
    "Tumor Eye": "a giant bulging extra eyeball growing out of a fleshy tumour on his left shoulder, wet, veiny and bloodshot, staring at the viewer",
    "Parasite Tendrils": "slick pale-pink parasite tendrils bursting out of torn wounds in the side of his neck, writhing in the air",
    "Glowing Pustules": "clusters of swollen pustules glowing toxic green on his neck and forearms, some burst and oozing",
}
EXPERIMENT = {
    "Surgical Staple Seam": "a long crude surgical seam closed with rusty steel staples running up his chest, showing through a rip in his clothes",
    "IV Drip Line": "an IV drip needle taped into his forearm, its clear tube running to a small bag of glowing green fluid clipped to his shoulder",
    "Blank Specimen Tag": "a blank yellowed paper specimen tag tied to his wrist with wire, no writing on it",
}
LAB = ("Specimen Tank Lab", "a ruined underground experiment lab: cracked glass specimen tanks of glowing green fluid with dark shapes "
       "floating inside, broken pipes and dangling cables, flickering green light, black-and-yellow biohazard warning symbols (the three-crescent trefoil, symbol only) on the tanks and walls, "
       "sculpted as a miniature claymation diorama in matte plasticine, softly out of focus behind him, no words, no logos, no lettering")
ALL["Backdrop"][LAB[0]] = (0, LAB[1])
# George 2026-11-16: how many Claysons of each body-horror group get one lab trait (cut back where too few are undrawn)
LAB_GROUPS = [("Flayed Open Chest", lambda a: a.get("Flesh") == "Flayed Open Chest", 4),
              ("Flayed Muscle Face", lambda a: a.get("Mask") == "Flayed Muscle Face", 8),
              ("Zombie skin", lambda a: a["Skin"] in ("Zombie Green", "Zombie Blue"), 15),
              ("Toxic Green skin", lambda a: a["Skin"] == "Toxic Green", 20),
              ("Boils", lambda a: a.get("Head Mark") == "Boils", 24)]
LAB_BY_TIER = {"Common": ["Glowing Pustules", "Surgical Staple Seam", "Blank Specimen Tag"],
               "Uncommon": ["Mutated Claw Arm", "Tumor Eye", "Parasite Tendrils", "Glowing Pustules", "Surgical Staple Seam", "IV Drip Line", LAB[0]],
               "Rare": ["Tumor Eye", "Parasite Tendrils", "IV Drip Line", LAB[0]]}
FRAMING_MUTARM = FRAMING.split("; his other hand")[0] + "; his other arm is the huge mutated clawed limb, raised, never a limp hand"


def lab_pass(tokens):
    st = json.load(open(os.path.join(ROOT, "generator", "frozen_batches.json")))
    pend = set().union(*[set(b["ids"]) - (set(b.get("drop", [])) - LATE_DROP) for b in st["batches"] if b["state"] != "done"])
    plain = {"Sage Clay", "Swamp Clay", "Slate Clay", "Teal Clay", "Rust Clay", "Bruise Clay", "Bone Clay", ROBINHOOD[0]}
    used = set(CLOWN_PISTOLS) | {1136}
    rng = random.Random(6669)
    LAB_GROUPS_DONE.clear()
    picks = []
    for name, test, n in LAB_GROUPS:   # rarest group first; Standards keep Standard traits only, so they are left out
        pool = [i for i, (a, f) in enumerate(tokens, 1) if a["Tier"] in LAB_BY_TIER and a.get("Character") in ("Classic", "Woman")
                and test(a) and i not in pend and i not in used
                and not (i in FROZEN_DRAWN or i in LATE_REDRAW)]
        got = rng.sample(pool, min(n, len(pool)))
        used.update(got)
        picks += got
        LAB_GROUPS_DONE[name] = (len(got), n)
    uses = collections.Counter()
    for i in sorted(picks, key=lambda i: tokens[i - 1][0]["Tier"] == "Rare", reverse=True):
        a = tokens[i - 1][0]
        options = [v for v in LAB_BY_TIER[a["Tier"]] if (v != "Mutated Claw Arm" or (a.get("Off Hand") or "").endswith("Hook Hand"))
                   and (v != LAB[0] or a["Backdrop"] in plain)]
        v = min(options, key=lambda v: (uses[v], rng.random()))
        uses[v] += 1
        if v == LAB[0]:
            a["Backdrop"] = v
            a.pop("Splatter", None)
        elif v in MUTATION:
            a["Mutation"] = v
            if v == "Mutated Claw Arm":
                a.pop("Off Hand", None)
        else:
            a["Experiment"] = v
    # George 2026-11-16: the Toxic Green group was short, so the 3 undrawn Toxic Green Standards join it with their own weapon,
    # a bio-lab canister holding a living symbiote, and move up to Common. The 3 lowest-scoring plain Commons drop to Standard
    # so the pyramid stays 464/400/293/130/13.
    toxic = [i for i, (a, f) in enumerate(tokens, 1) if a["Tier"] == "Standard" and a["Skin"] == "Toxic Green" and i not in pend
             and a.get("Character") in ("Classic", "Woman") and not (i in FROZEN_DRAWN or i in LATE_REDRAW)]
    assert len(toxic) == 3 or LOCK, toxic
    for i, v in zip(sorted(toxic), CANISTERS):
        tokens[i - 1][0].update({"Held Weapon": v, "Tier": "Common"})
    skip = {"Tier", "1/1 Name", "Splatter", "Character"}
    cnt = Counter((k, v) for a, _ in tokens for k, v in a.items() if k not in skip)
    std_vals = {(k, v) for a, _ in tokens if a["Tier"] == "Standard" for k, v in a.items()}
    plain_common = [i for i, (a, f) in enumerate(tokens, 1) if a["Tier"] == "Common" and i > 13
                    and all((k, v) in std_vals for k, v in a.items() if k not in skip)]
    for i in sorted(plain_common, key=lambda i: sum(1 / cnt[(k, v)] for k, v in tokens[i - 1][0].items() if k not in skip))[:3]:
        tokens[i - 1][0]["Tier"] = "Standard"
    LAB_GROUPS_DONE["Toxic Green skin"] = (LAB_GROUPS_DONE["Toxic Green skin"][0] + 3, 20)


# George 2026-11-16: each of the 3 canisters holds a different-looking virus organism
CANISTER_BASE = ("a heavy bio-lab containment canister held by its steel carry handle: a tall cylinder of perfectly CLEAR, clean, see-through "
                 "glass (not cracked, not frosted, not tinted) between riveted steel end caps with glowing green seams, so the creature inside "
                 "is plainly visible: {}; one THIN yellow hazard band near the top cap with a small black biohazard warning symbol "
                 "(the three-crescent trefoil), symbol only, the band never hiding the organism, no words, no logos, no lettering")
CANISTERS = {   # George 2026-11-16 01:41: black alien sludge, red parasite species, green spores (in token order 29, 683, 733)
    "Black Alien Sludge Canister": "a glossy jet-black tar-like alien ooze that bulges and reaches out in slow sticky pseudopods, smearing up the inside of the glass",
    "Red Parasite Species Canister": "a single segmented blood-red parasite creature, like a fat armoured larva with many small hooked legs and a round "
                                     "toothed sucker mouth, clinging to the inside of the glass",
    "Green Spore Canister": "puffy glowing toxic-green spore pods growing in clusters, with tiny glowing spores drifting in the misty air inside",
}
for _v, _d in CANISTERS.items():
    ALL["Held Weapon"][_v] = (0, CANISTER_BASE.format(_d))
LAB_GROUPS_DONE = {}

def box_pass(tokens):
    """George 2026-11-16: the one Gilded Puzzle Box (#1136) becomes the Chrome Puzzle Box; 5 undrawn Uncommons with an ordinary
    weapon and nothing on the back trade it (and any off-hand hammer or pitchfork) for a differently shaped gold puzzle box, both hands."""
    for a, f in tokens:
        if a["Held Weapon"] == "Gilded Puzzle Box":
            a["Held Weapon"] = "Chrome Puzzle Box"
    st = json.load(open(os.path.join(ROOT, "generator", "frozen_batches.json")))
    pend = set().union(*[set(b["ids"]) - (set(b.get("drop", [])) - LATE_DROP) for b in st["batches"] if b["state"] != "done"])
    pool = [i for i, (a, f) in enumerate(tokens, 1) if a["Tier"] == "Uncommon" and a["Back Weapon"] == "None"
            and a["Held Weapon"] in ("Chainsaw", "Nail Bat", "Meat Hook", "Rusted Hunting Knife", "Rusted Butcher Cleaver", "Rusted Sickle")
            and a.get("Off Hand") in (None, "Sledgehammer", "Pitchfork") and not a.get("Mutation") and not a.get("Experiment") and a.get("Character") in ("Classic", "Woman")
            and i not in pend and not (i in FROZEN_DRAWN or i in LATE_REDRAW)]
    gold = [v for v in PUZZLE_BOXES if v.startswith("Gold")]
    for i, v in zip(random.Random(1987).sample(pool, len(gold)), gold):
        tokens[i - 1][0]["Held Weapon"] = v
        tokens[i - 1][0].pop("Off Hand", None)


HOCKEY_FINISH = {"Rusted Hockey Half-Mask": ("Common", 13, "a heavily rusted iron HALF mask, pitted and flaking orange rust"),
                 "Gold Hockey Half-Mask": ("Uncommon", 7, "a gleaming solid-gold HALF mask"),
                 "Chrome Hockey Half-Mask": ("Uncommon", 3, "a mirror-polished chrome HALF mask")}
for _v, (_t, _n, _d) in HOCKEY_FINISH.items():
    ALL["Mask"][_v] = (0, ALL["Mask"]["Hockey Half-Mask"][1].replace("an aged yellowed HALF mask", _d))


def hockey_pass(tokens):
    """George 2026-11-16 06:02: metal finishes on the plain Hockey Half-Mask, undrawn wearers only (no Rare wears one undrawn,
    so Gold and Chrome go to Uncommons): Rusted 13 on Commons, Gold 7 and Chrome 3 on Uncommons."""
    st = json.load(open(os.path.join(ROOT, "generator", "frozen_batches.json")))
    pend = set().union(*[set(b["ids"]) - (set(b.get("drop", [])) - LATE_DROP) for b in st["batches"] if b["state"] != "done"])
    rng = random.Random(1313)
    used = set()
    for v, (tier, n, _) in HOCKEY_FINISH.items():
        pool = [i for i, (a, f) in enumerate(tokens, 1) if a["Tier"] == tier and a["Mask"] == "Hockey Half-Mask" and i not in used
                and a.get("Character") in ("Classic", "Woman") and i not in pend
                and not (i in FROZEN_DRAWN or i in LATE_REDRAW)]
        for i in rng.sample(pool, n):
            tokens[i - 1][0]["Mask"] = v
            used.add(i)
        EYES_SHOW.add(v)
        WOUND_SHOWS.add(v)


def robinhood_pass(tokens):
    st = json.load(open(os.path.join(ROOT, "generator", "frozen_batches.json")))
    pend = set().union(*[set(b["ids"]) - (set(b.get("drop", [])) - LATE_DROP) for b in st["batches"] if b["state"] != "done"])
    plain = {"Sage Clay", "Swamp Clay", "Slate Clay", "Teal Clay", "Rust Clay", "Bruise Clay", "Bone Clay"}
    pool = [i for i, (a, f) in enumerate(tokens, 1) if a["Backdrop"] in plain and a["Tier"] != "Legendary 1/1" and i not in pend
            and not (i in FROZEN_DRAWN or i in LATE_REDRAW)]
    for i in random.Random(16).sample(pool, 110):
        tokens[i - 1][0]["Backdrop"] = ROBINHOOD[0]


# Ritual order traits (George, 2026-11-16): Rare, inspired by the classic leather-clad occult horror order, all original, never the
# film, box or character names. Spread over different undrawn Uncommon and Rare Claysons: Ritual Leather Robe 8, extra Nail-Studded Leather
# Masks 5, Flayed Open Chest 8 (trait "Flesh"), and the ONE Gilded Puzzle Box in the collection, held in both hands.
ALL["Clothing"]["Ritual Leather Robe"] = (0, "a long tight black leather ritual robe with a high collar, buckled straps, laced seams and small "
                                          "steel hooks hanging from chains at the waist")
FLESH = {"Flayed Open Chest": "the skin of his chest ripped open down the middle and pulled wide apart by small steel hooks on thin chains, "
                              "showing raw glossy red exposed muscle fibres and sinew underneath, the torn clothes peeled back around it"}
ALL["Held Weapon"]["Gilded Puzzle Box"] = (0, "")
for _f, _d in (("Rusted", "bent rusty iron"), ("Golden", "gleaming solid-gold"), ("Chrome", "mirror-bright chrome")):   # George 2026-11-16
    ALL["Mask"][f"{_f} Nail-Studded Mask"] = (0, f"a cracked black leather mask with {_d} nails and screws driven through it at random "
                                                 "angles, blood seeping from the holes")


def order_pass(tokens):
    """Runs after common_pass (George: spread over Uncommons and Rares), so the tier labels are final and stay unchanged."""
    st = json.load(open(os.path.join(ROOT, "generator", "frozen_batches.json")))
    pend = set().union(*[set(b["ids"]) - (set(b.get("drop", [])) - LATE_DROP) for b in st["batches"] if b["state"] != "done"])
    BOX = 1136
    deal = {"Common": [("Clothing", "Ritual Leather Robe", 3), ("Mask", "Rusted Nail-Studded Mask", 2), ("Flesh", "Flayed Open Chest", 3)],
            "Uncommon": [("Clothing", "Ritual Leather Robe", 3), ("Mask", "Golden Nail-Studded Mask", 2), ("Flesh", "Flayed Open Chest", 3)],
            "Rare": [("Clothing", "Ritual Leather Robe", 3), ("Mask", "Chrome Nail-Studded Mask", 1), ("Flesh", "Flayed Open Chest", 3)]}
    rng = random.Random(1987)
    for tier, items in deal.items():
        pool = [i for i, (a, f) in enumerate(tokens, 1) if a["Tier"] == tier and a["Character"] in ("Classic", "Woman") and i not in pend
                and i != BOX and not a["Skin"].startswith("Zombie") and a["Held Weapon"] != "Poison Syringe"
                and not (i in FROZEN_DRAWN or i in LATE_REDRAW)]
        picks = iter(rng.sample(pool, sum(n for *_, n in items)))
        for trait, val, n in items:
            for _ in range(n):
                tokens[next(picks) - 1][0][trait] = val
    box = tokens[BOX - 1][0]
    assert box["Tier"] == "Rare"
    box.update({"Held Weapon": "Gilded Puzzle Box", "Back Weapon": "None"}); box.pop("Off Hand", None)


# Eyes trait (George, 2026-11-16). Only where the eyes show. Finished tokens already show the default bloodshot eyes, so they are
# labelled Bloodshot Eyes; undrawn ones get Yellow Sickly 110 and Pupil-less White 45 (any tier but 1/1s), the rest Bloodshot.
EYES = {"Yellow Sickly Eyes": "small sunken sickly jaundiced yellow eyes with dull yellow whites and tiny dark pupils",
        "Pupil-less White Eyes": "small sunken blank pupil-less milky-white eyes with no iris and no pupil, dead and staring",
        "Yellow Eyes, Green Pupils": "small sunken glowing sulphur-yellow eyes with sharp toxic-green pupils",
        "Red Eyes, Green Pupils": "small sunken blood-red eyes with sharp toxic-green pupils"}
EYES_SHOW = {"Black-Lipped Bloody Grin", "Bare Face", "Hockey Half-Mask", "Gas Mask", "Paisley Bandana", "Iron Muzzle", "Carved Ear-to-Ear Grin", "Stitched Skin Face",
             "Smeared Greasepaint", "Bloody Bandage Wrap", "Buckled Harness Hood", "Rubber Seam Face"}


# Mood-board traits (George, 2026-11-16; inspiration only, never the source characters or names).
ALL["Mask"]["Black-Lipped Bloody Grin"] = (0, "no mask: her bare disfigured face with smeared black lipstick on cracked lips, the corners of "
                                              "her mouth cut and stretched into a wide ragged bloody grin, dried blood dripping down her chin")
BONE_CROWN = ("a crude crown of jagged yellowed bone shards and splintered wooden stakes standing up around his head, bound tightly to his "
              "skull with thick coils of frayed rope")


ALL["Mask"]["Weeping Four-Eye Mask"] = (0, "a cracked bone-white porcelain HALF mask covering his forehead, eyes, cheeks and nose but leaving "
                                           "his mouth and jaw bare, with FOUR almond-shaped eye holes, two stacked one above the other on each "
                                           "side, each filled with a rusty iron mesh grille, thick black tar-like tears running down from the eye "
                                           "holes over the white cheeks, a few hairline cracks")


def weeping_mask_pass(tokens):
    """George 2026-11-16 reference (our own take): 20 undrawn tokens get the Weeping Four-Eye Mask: every undrawn bare-faced Uncommon
    that is free (plain bloodshot eyes, no special mask), the rest on Rares that keep another Rare-only trait besides the mask."""
    st = json.load(open(os.path.join(ROOT, "generator", "frozen_batches.json")))
    pend = set().union(*[set(b["ids"]) - (set(b.get("drop", [])) - LATE_DROP) for b in st["batches"] if b["state"] != "done"])
    undrawn = lambda i: i not in pend and not (i in FROZEN_DRAWN or i in LATE_REDRAW)
    unc = [i for i, (a, f) in enumerate(tokens, 1) if a["Tier"] == "Uncommon" and a["Character"] in ("Classic", "Woman")
           and a["Mask"] in EYES_SHOW and a["Mask"] not in ("Black-Lipped Bloody Grin", "Gas Mask", "Smeared Greasepaint", *ICON_BROWN)
           and a.get("Eyes") == "Bloodshot Eyes" and not a.get("Headpiece") and undrawn(i)]
    low = {(k, v) for a, _ in tokens if a["Tier"] not in ("Rare", "Legendary 1/1") for k, v in a.items()}
    special = {"Rusted Nail-Studded Mask", "Golden Nail-Studded Mask", "Chrome Nail-Studded Mask"}
    rare = [i for i, (a, f) in enumerate(tokens, 1) if a["Tier"] == "Rare" and a["Character"] == "Classic" and a["Mask"] not in special
            and a["Held Weapon"] != "Gilded Puzzle Box" and not a.get("Headpiece") and undrawn(i)
            and any((k, v) not in low for k, v in a.items() if k not in ("Mask", "Tier", "Splatter"))]
    rng = random.Random(4040)
    picks = rng.sample(unc, min(len(unc), 20))
    picks += rng.sample(rare, 20 - len(picks))
    for i in picks:
        tokens[i - 1][0]["Mask"] = "Weeping Four-Eye Mask"
        tokens[i - 1][0].pop("Head Wound", None)   # the mask covers the forehead and eyes
        tokens[i - 1][0].pop("Eyes", None)


# Three gas-mask styles (George, 2026-11-16): Standard -> crude leather, Common/Uncommon -> riveted respirator, Rare -> bloody chrome.
GAS = {"Crude Leather Gas Mask": "a crude, poorly made homemade gas mask of patched and badly stitched brown leather over his nose and mouth, "
                                 "crooked mismatched buckled straps, a dented tin can stuffed with rags as a makeshift filter, eyes visible above",
       "Riveted Respirator": "a well-built riveted rusty-steel HALF-face respirator clamped over his nose and mouth, a single round olive "
                             "filter canister with a dull yellow face on one side, ribbed black rubber hoses looping from the mask down across "
                             "his chest, eyes visible above",
       "Bloody Chrome Gas Mask": "a gleaming mirror-chrome gas mask over his nose and mouth with twin chrome filter canisters and a ribbed chrome "
                                 "hose, splattered with fresh dripping blood, eyes visible above"}
for _v, _p in GAS.items():
    ALL["Mask"][_v] = (0, _p)


def gas_style_pass(tokens):
    st = json.load(open(os.path.join(ROOT, "generator", "frozen_batches.json")))
    pend = set().union(*[set(b["ids"]) - (set(b.get("drop", [])) - LATE_DROP) for b in st["batches"] if b["state"] != "done"])
    for a, f in tokens:
        if a["Mask"] == "Gas Mask":
            a["Mask"] = "Crude Leather Gas Mask" if a["Tier"] == "Standard" else "Riveted Respirator"
    low = {(k, v) for a, _ in tokens if a["Tier"] not in ("Rare", "Legendary 1/1") for k, v in a.items()}
    keep = {"Rusted Nail-Studded Mask", "Golden Nail-Studded Mask", "Chrome Nail-Studded Mask", "Weeping Four-Eye Mask", "Nail-Studded Leather Mask"}
    rare = [i for i, (a, f) in enumerate(tokens, 1) if a["Tier"] == "Rare" and a["Character"] == "Classic" and a["Mask"] not in keep
            and a["Held Weapon"] != "Gilded Puzzle Box" and not a.get("Headpiece") and i not in pend
            and not (i in FROZEN_DRAWN or i in LATE_REDRAW)
            and any((k, v) not in low for k, v in a.items() if k not in ("Mask", "Tier", "Splatter"))]
    for i in random.Random(6060).sample(rare, 8):
        a = tokens[i - 1][0]
        a["Mask"] = "Bloody Chrome Gas Mask"
        if a["Back Weapon"] == "None":
            a["Back Weapon"] = "Oxygen Tank"


def grin_pass(tokens):
    """Women only: 20 undrawn bare-faced women get the black-lipped bloody grin (Common 10, Uncommon 4, Standard 6)."""
    st = json.load(open(os.path.join(ROOT, "generator", "frozen_batches.json")))
    pend = set().union(*[set(b["ids"]) - (set(b.get("drop", [])) - LATE_DROP) for b in st["batches"] if b["state"] != "done"])
    rng = random.Random(4949)
    for tier, n in (("Common", 10), ("Uncommon", 4), ("Standard", 6)):
        pool = [i for i, (a, f) in enumerate(tokens, 1) if a["Tier"] == tier and a["Character"] == "Woman" and a["Mask"] == "Bare Face"
                and i not in pend and not (i in FROZEN_DRAWN or i in LATE_REDRAW)]
        for i in rng.sample(pool, min(n, len(pool))):
            tokens[i - 1][0]["Mask"] = "Black-Lipped Bloody Grin"


def bone_crown_pass(tokens):
    """Trait "Headpiece": Crown of Bones on 12 Uncommon + 8 Rare undrawn tokens; never Cone Skulls, hats, hoods or head-covering masks."""
    st = json.load(open(os.path.join(ROOT, "generator", "frozen_batches.json")))
    pend = set().union(*[set(b["ids"]) - (set(b.get("drop", [])) - LATE_DROP) for b in st["batches"] if b["state"] != "done"])
    covered = {"Burlap Sack Hood", "Burlap Pig Mask", "Buckled Harness Hood", "Bloody Bandage Wrap", "Moaning Paper Mask", "Zipper Long Nose",
               "Crown of Nails"}
    rng = random.Random(1313)
    for tier, n in (("Uncommon", 12), ("Rare", 8)):
        pool = [i for i, (a, f) in enumerate(tokens, 1) if a["Tier"] == tier and a["Head"] != "Type 3 - Cone Skull" and a["Hair"] not in HEADWEAR
                and a["Mask"] not in covered and a["Character"] in ("Classic", "Woman") and i not in pend
                and not (i in FROZEN_DRAWN or i in LATE_REDRAW)]
        for i in rng.sample(pool, n):
            tokens[i - 1][0]["Headpiece"] = "Crown of Bones"


def eyes_pass(tokens):
    st = json.load(open(os.path.join(ROOT, "generator", "frozen_batches.json")))
    pend = set().union(*[set(b["ids"]) - (set(b.get("drop", [])) - LATE_DROP) for b in st["batches"] if b["state"] != "done"])
    show = [i for i, (a, f) in enumerate(tokens, 1) if a["Tier"] != "Legendary 1/1" and a["Mask"] in EYES_SHOW
            and a["Character"] in ("Classic", "Woman")]
    fresh = [i for i in show if i not in pend and not (i in FROZEN_DRAWN or i in LATE_REDRAW)]
    for i in show:
        tokens[i - 1][0]["Eyes"] = "Bloodshot Eyes"
    fresh = [i for i in fresh if tokens[i - 1][0]["Tier"] in ("Uncommon", "Rare")]   # George: Uncommon and above only
    picks = random.Random(4444).sample(fresh, min(len(fresh), 75))
    for n, i in enumerate(picks):
        tokens[i - 1][0]["Eyes"] = "Yellow Sickly Eyes" if n < len(picks) * 2 // 3 else "Pupil-less White Eyes"
    rest = [i for i in fresh if i not in set(picks)]   # George 2026-11-16 (mood board): green pupils in yellow or red eyes
    for n, i in enumerate(random.Random(4545).sample(rest, min(len(rest), 14))):
        tokens[i - 1][0]["Eyes"] = "Yellow Eyes, Green Pupils" if n < 8 else "Red Eyes, Green Pupils"


N_COMMON = 400


def common_pass(tokens):
    """Common tier (George, 2026-11-15, chose the pyramid): between Standard and Uncommon. Metadata only, runs last.
    Uncommons carrying only ONE trait that no Standard has drop to Common; the rest of the 400 are the Standards with the
    rarest trait mix (sum of 1/count over their traits). Team mints #4-#13 are scored like any other token."""
    skip = {"Tier", "1/1 Name", "Splatter", "Character"}
    cnt = Counter((k, v) for a, _ in tokens for k, v in a.items() if k not in skip)
    std_vals = {(k, v) for a, _ in tokens if a["Tier"] == "Standard" for k, v in a.items()}
    single = [a for a, _ in tokens if a["Tier"] == "Uncommon"
              and sum((k, v) not in std_vals for k, v in a.items() if k not in skip) == 1]
    score = lambda a: sum(1 / cnt[(k, v)] for k, v in a.items() if k not in skip)
    std = sorted((a for a, _ in tokens if a["Tier"] == "Standard"), key=score, reverse=True)
    for a in single + std[:N_COMMON - len(single)]:
        a["Tier"] = "Common"


def jail_tier_fix(tokens):
    """Rarity audit 2026-11-15: Jail Cell (13) is a scene backdrop, and scene backdrops are Uncommon+, so a Standard token never gets it.
    Each unrendered Standard Jail Cell swaps backdrops with an unrendered Uncommon plain-clay token (tier counts unchanged)."""
    done = lambda i: (i in FROZEN_DRAWN or i in LATE_REDRAW)
    plain = {"Sage Clay", "Swamp Clay", "Slate Clay", "Teal Clay", "Rust Clay", "Bruise Clay", "Bone Clay"}
    pool = [i for i, (a, f) in enumerate(tokens, 1) if a["Tier"] == "Uncommon" and a["Backdrop"] in plain and not done(i)]
    random.Random(1717).shuffle(pool)
    for i, (a, f) in enumerate(tokens, 1):
        if a["Backdrop"] == JAIL[0] and a["Tier"] == "Standard" and not done(i):
            u = tokens[pool.pop() - 1][0]
            a["Backdrop"], u["Backdrop"] = u["Backdrop"], a["Backdrop"]


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


def splatter_pass(tokens):
    """George 2026-11-15: blood splatter on the plain clay backdrops, five levels, applied after rendering by splatter.py.
    Slaughter exactly 13; the rest about 42% Light, 29% Mild, 18% Wild, 11% Crazy."""
    plain = {"Sage Clay", "Swamp Clay", "Slate Clay", "Teal Clay", "Rust Clay", "Bruise Clay", "Bone Clay", ROBINHOOD[0]}
    pool = [i for i, (a, f) in enumerate(tokens, 1) if a["Backdrop"] in plain and a["Tier"] != "Legendary 1/1"]
    random.Random(1666).shuffle(pool)
    for n, i in enumerate(pool):
        r = (n - 13) / (len(pool) - 13)
        tokens[i - 1][0]["Splatter"] = "Slaughter" if n < 13 else "Light" if r < .42 else "Mild" if r < .71 else "Wild" if r < .89 else "Crazy"


def saw_whacker_pass(tokens):
    """Every non-1/1 backpack weed whacker gets a round saw blade: Chrome on Rare, else ~47% Rusted, 35% Bloody, 18% Clean."""
    late = random.Random(2222)
    plain = [i for i, (a, f) in enumerate(tokens, 1) if a["Back Weapon"] == "Weed Whacker" and a["Tier"] not in ("Rare", "Legendary 1/1")]
    for i, (a, f) in enumerate(tokens, 1):
        if a["Back Weapon"] == "Weed Whacker" and a["Tier"] == "Rare":
            a["Back Weapon"] = "Chrome Saw Weed Whacker"
    late.shuffle(plain)
    for n, i in enumerate(plain):
        r = n / len(plain)
        tokens[i - 1][0]["Back Weapon"] = f"{'Rusted' if r < .47 else 'Bloody' if r < .82 else 'Clean'} Saw Weed Whacker"


TWO_HAND_HELD = {
    "Rusty Shovel": "a rusty shovel with a long wooden handle", "Pitchfork": "a rusty pitchfork with a long wooden handle",
    "Woodcutter Axe": "a long woodcutter's axe", "Sledgehammer": "a heavy sledgehammer",
    "Harpoon Gun": "a rusty harpoon gun loaded with a barbed harpoon", "Circus Mallet": "a giant red-and-cream striped circus mallet",
    "Double-Barrel Shotgun": "a sawn-off rusty double-barrel shotgun with a cracked wooden stock, finger off the trigger",
    "Chrome Sledge-Axe": "a heavy blood-dripping sledge-axe with a mirror-chrome head and a long polished wooden handle",
    "Sniper Rifle": "a long heavy matte-black sniper rifle with a big scope", "Scythe": "a huge rusty scythe, the curved blade arching above his head",
}


def hook_off_pass(tokens):
    """George 2026-11-15: a Clayson holding one weapon in one hand gets a rusty prosthetic hook instead of a limp free hand."""
    busy = NO_OFF_HAND | set(TWO_HAND_HELD) | {"Hook Hand"}
    plain, rare = [], []
    for i, (a, f) in enumerate(tokens, 1):
        if a["Tier"] != "Legendary 1/1" and not a.get("Off Hand") and a["Held Weapon"] not in busy:
            (rare if a["Tier"] == "Rare" else plain).append(i)
    for n, i in enumerate(rare):   # Rare: Gold and Chrome (Chrome rarest)
        tokens[i - 1][0]["Off Hand"] = f"{'Gold' if n % 3 else 'Chrome'} Hook Hand"
    random.Random(4747).shuffle(plain)
    for n, i in enumerate(plain):   # rust most common, then steel, then bloody
        r = n / len(plain)
        tokens[i - 1][0]["Off Hand"] = f"{'Rusty' if r < .5 else 'Steel' if r < .8 else 'Bloody'} Hook Hand"


# George 2026-11-15: every exposed bald or Cone Skull head gets a deep bloody wound slightly left of the forehead (trait "Head Wound").
WOUND_SHOWS = {"Bare Face", "Hockey Half-Mask", "Gas Mask", "Paisley Bandana", "Iron Muzzle", "Carved Ear-to-Ear Grin", "Stitched Skin Face",
               "Smeared Greasepaint", "Needle-Tooth Snarl"}   # masks that leave the forehead bare
WOUND = ("a deep fresh bloody wound gouged into the clay on the LEFT side of his forehead (left as we look at him), just above the brow: "
         "a ragged open gash with torn raw red edges, glossy dark blood pooled inside and a few thick drips running down past his eye")


DEDUPE_KEYS = ["Head", "Skin", "Hair", "Head Mark", "Mask", "Held Weapon", "Back Weapon", "Clothing", "Belt", "Backdrop", "Off Hand"]


def dedupe_pass(tokens):
    """George 2026-11-15 "No duplicates": every pair of Claysons must differ in at least 3 visible traits. For a pair that doesn't,
    the unrendered one (else the later one) gets a new skin and head mark. Never 1/1s or Half-Burnt faces; Deep Brown icon tokens keep their skin."""
    done = {i for i in range(1, len(tokens) + 1) if (i in FROZEN_DRAWN or i in LATE_REDRAW)}
    vec = lambda a: tuple(a.get(k, "") for k in DEDUPE_KEYS)
    near = lambda u, v: sum(x != y for x, y in zip(u, v)) < 3
    rng = random.Random(1300)
    changed = []
    for i in range(len(tokens)):
        for j in range(i + 1, len(tokens)):
            if not near(vec(tokens[i][0]), vec(tokens[j][0])):
                continue
            k = i if (i + 1) not in done and (j + 1) in done else j
            a = tokens[k][0]
            if a["Tier"] == "Legendary 1/1" or a["Head Mark"] == "Half-Burnt Face":
                k = i + j - k; a = tokens[k][0]
                if a["Tier"] == "Legendary 1/1" or a["Head Mark"] == "Half-Burnt Face":
                    continue
            others = [vec(t[0]) for n, t in enumerate(tokens) if n != k]
            for _ in range(200):
                if a["Skin"] != "Deep Brown":   # icon tokens keep their Deep Brown skin
                    a["Skin"] = pick(rng, SKIN)
                a["Head Mark"] = pick(rng, HEAD_MARK)
                if not any(near(vec(a), o) for o in others):
                    break
            changed.append(k + 1)
    dedupe_pass.changed = changed


def whacker_hold_pass(tokens):
    """George 2026-11-15 (#582 is the back look): a back saw weed whacker stays on the back when the held weapon is rarer; when the
    whacker is the rarer one he wields it in both hands instead (held weapon and hook hand dropped). Not chainsaws, nail gloves, 1/1s, dual."""
    held = collections.Counter(a["Held Weapon"] for a, _ in tokens)
    back = collections.Counter(a["Back Weapon"] for a, _ in tokens)
    for a, f in tokens:
        b, h, off = a["Back Weapon"], a["Held Weapon"], a.get("Off Hand") or ""
        if (b.endswith("Saw Weed Whacker") and held[h] >= back[b] and a["Tier"] != "Legendary 1/1"
                and h not in ("Chainsaw", "Hook Hand", "Nail-Knife Glove", "Blade Nails", "Death Nails") and (not off or off.endswith("Hook Hand"))):
            a["Held Weapon"], a["Back Weapon"] = b, "None"
            a.pop("Off Hand", None)


# George 2026-11-15: a gas-mask wearer with nothing on his back carries an oxygen tank, hosed to the mask (Back Weapon "Oxygen Tank").
OXYGEN = ("a dented rusty green oxygen tank strapped upright on his back with frayed canvas straps over both shoulders, its brass valve "
          "poking up behind his shoulder and a ribbed black rubber hose running from the valve over his shoulder into the side of his gas mask")
ALL["Back Weapon"]["Oxygen Tank"] = (0, OXYGEN)


def oxygen_pass(tokens):
    for a, f in tokens:
        if a["Tier"] != "Legendary 1/1" and a["Mask"] == "Gas Mask" and a["Back Weapon"] == "None":
            a["Back Weapon"] = "Oxygen Tank"


def wound_pass(tokens):
    for a, f in tokens:
        if (a["Tier"] != "Legendary 1/1" and a["Mask"] in WOUND_SHOWS and a["Hair"] not in HEADWEAR
                and (a["Hair"] == "Bald" or a["Head"] == "Type 3 - Cone Skull")):
            a["Head Wound"] = "Deep Forehead Gash"


def two_hand_pass(tokens):
    """George 2026-11-15: if the back weapon is rarer than the single held weapon, the Clayson wields the back weapon in both
    hands instead (held weapon dropped). Not for chainsaws, hook hands, nail gloves, 1/1s or dual wielders."""
    held = collections.Counter(a["Held Weapon"] for a, _ in tokens)
    back = collections.Counter(a["Back Weapon"] for a, _ in tokens)
    dnas = {tuple(sorted((k, v) for k, v in a.items() if k != "Tier")) for a, _ in tokens}
    for a, f in tokens:
        b, h = a["Back Weapon"], a["Held Weapon"]
        if (b not in TWO_HAND_HELD or a["Tier"] == "Legendary 1/1" or a.get("Off Hand")
                or h in ("Chainsaw", "Hook Hand", "Nail-Knife Glove", "Blade Nails", "Death Nails", "Double Molotov Cocktails") or back[b] >= held[h]):
            continue
        old = tuple(sorted((k, v) for k, v in a.items() if k != "Tier"))
        c = dict(a, **{"Held Weapon": b, "Back Weapon": "None"})
        new = tuple(sorted((k, v) for k, v in c.items() if k != "Tier"))
        if new in dnas:
            continue
        dnas.discard(old); dnas.add(new); a.update(c)


def chainsaw_pass(tokens):
    """George 2026-11-15: no chainsaws on backs. A chainsaw takes both hands, so a back chainsaw becomes the held weapon when the
    held weapon is a plain one; otherwise (special/counted held weapons, or already a held chainsaw) the back chainsaw is removed.
    1/1s keep theirs."""
    plain = {k for k in HELD_STD if k != "Chainsaw"} | {f"{f} {w}" for f in ("Rusted", "Bloody", "Clean")
                                                         for w in ("Machete", "Butcher Cleaver", "Hunting Knife", "Hatchet", "Sickle")}
    dnas = {tuple(sorted((k, v) for k, v in a.items() if k != "Tier")) for a, _ in tokens}
    for a, f in tokens:
        if a["Back Weapon"] != "Chainsaw" or a["Tier"] == "Legendary 1/1":
            continue
        old = tuple(sorted((k, v) for k, v in a.items() if k != "Tier"))
        b = dict(a, **{"Back Weapon": "None"})
        if a["Held Weapon"] in plain:
            c = dict(b, **{"Held Weapon": "Chainsaw"})
            if tuple(sorted((k, v) for k, v in c.items() if k != "Tier")) not in dnas:
                b = c
        new = tuple(sorted((k, v) for k, v in b.items() if k != "Tier"))
        assert new not in dnas or new == old
        dnas.discard(old); dnas.add(new); a.update(b)


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


def machete_pass(tokens):
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_syringe.json"))))
    late = random.Random(2020)
    plain = []
    for i, (a, f) in enumerate(tokens, 1):
        if a["Held Weapon"] != "Machete":
            continue
        if i in keep or f:
            a["Held Weapon"] = "Rusted Machete"
        elif a["Tier"] == "Rare":
            a["Held Weapon"] = "Chrome Machete"
        else:
            plain.append(i)
    late.shuffle(plain)
    for n, i in enumerate(plain):   # about 47% Rusted, 35% Bloody, 18% Clean
        tokens[i - 1][0]["Held Weapon"] = "Rusted Machete" if n < 40 else "Bloody Machete" if n < 70 else "Clean Machete"


def blade_pass(tokens):
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_syringe.json"))))
    late = random.Random(2121)
    for w, (_, shown) in BLADES.items():
        plain, rare = [], []
        for i, (a, f) in enumerate(tokens, 1):
            if a["Held Weapon"] != w:
                continue
            if i in keep or f:
                a["Held Weapon"] = f"{shown} {w}"
            elif a["Tier"] == "Rare":
                rare.append(i)
            else:
                plain.append(i)
        for n, i in enumerate(rare):   # Rare blades alternate Chrome and Gold
            tokens[i - 1][0]["Held Weapon"] = f"{'Chrome' if n % 2 == 0 else 'Gold'} {w}"
        late.shuffle(plain)
        for n, i in enumerate(plain):   # about 47% Rusted, 35% Bloody, 18% Clean
            r = n / len(plain)
            tokens[i - 1][0]["Held Weapon"] = f"{'Rusted' if r < .47 else 'Bloody' if r < .82 else 'Clean'} {w}"


# George (2026-11-15): 13 hooded in total, so 9 finished bald hoodie Claysons are redone with the hood up.
HOOD_REDO = [36, 166, 184, 219, 298, 513, 739, 757, 808]


def hood_pass(tokens):
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_syringe.json"))))
    pool = [i for i, (a, f) in enumerate(tokens, 1) if i not in keep and not f and a["Clothing"] == "Grimy Hoodie"
            and a["Hair"] in ("Bald", "Grey Side Tufts", "Buzzed Scalp") and a["Mask"] not in ("Burlap Sack Hood", "Burlap Pig Mask")]
    for i in random.Random(808).sample(pool, round(len(pool) * .6)) + HOOD_REDO:
        tokens[i - 1][0]["Hair"] = "Hood Up"   # a new value can't collide with an existing DNA


HEADWEAR = {"Backwards Cap", "Battered Top Hat", "Hood Up", "Worn Trucker Cap", "Veiled Mourning Hat"}


def cap_cone_pass(tokens):
    """No cap, hat or hood on a cone skull (George, 2026-11-15): those tokens get another head type. The finished
    ones (#9, 571, 587, 746) are re-rendered."""
    late = random.Random(909)
    others = [h for h in HEAD if h != "Type 3 - Cone Skull"]
    dnas = {tuple(sorted((k, v) for k, v in a.items() if k != "Tier")) for a, _ in tokens}
    for a, _ in tokens:
        if a["Hair"] in HEADWEAR and a["Head"] == "Type 3 - Cone Skull":
            old = tuple(sorted((k, v) for k, v in a.items() if k != "Tier"))
            for h in late.sample(others, len(others)):
                dna = tuple(sorted((k, v) for k, v in dict(a, Head=h).items() if k != "Tier"))
                if dna not in dnas:
                    dnas.discard(old); dnas.add(dna); a["Head"] = h
                    break


def women_weapon_pass(tokens):
    keep = set(json.load(open(os.path.join(ROOT, "generator", "rendered_keep_syringe.json"))))
    pool = [i for i, (a, f) in enumerate(tokens, 1) if i not in keep and not f and a["Character"] == "Woman" and a["Tier"] == "Uncommon"
            and a["Back Weapon"] not in ("Fuel Tanks",) and a["Held Weapon"] not in ("Poison Syringe", "Rusty Shears", "Double Molotov Cocktails")
            and "Flamethrower" not in a["Held Weapon"] and a["Held Weapon"] != "Chainsaw"]
    picks = random.Random(4141).sample(pool, 33)
    for n, i in enumerate(picks):
        tokens[i - 1][0]["Held Weapon"] = "Blade Nails" if n < 25 else "Psychic Force"   # new values: no DNA collision
    female = set(FEMALE) | {"The Ringmistress", "Woman"}
    used = set(picks)
    pool2 = [i for i, (a, f) in enumerate(tokens, 1) if i not in keep and i not in used and not f and a["Character"] in female
             and a["Tier"] in ("Uncommon", "Rare") and a["Held Weapon"] not in ("Poison Syringe", "Rusty Shears", "Double Molotov Cocktails", "Chainsaw", "Hook Hand")
             and "Flamethrower" not in a["Held Weapon"] and a["Back Weapon"] != "Fuel Tanks"]
    for n, i in enumerate(random.Random(4242).sample(pool2, 50)):
        tokens[i - 1][0]["Held Weapon"] = "Switchblade" if n < 25 else "Bloody Brick" if n < 40 else "Exercise Band"


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
