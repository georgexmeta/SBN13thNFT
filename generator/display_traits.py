"""Published trait layout (George 2026-11-17 17:47: keep the art, but give every trait a clearly defined category).

The render pipeline (v2.py, prompts, tiers, dedupe) keeps its internal attribute names. This module only regroups them
for the OpenSea metadata, the trait sheet and the review page, so each category holds one kind of thing:

  Gender       Male / Female (was hidden inside Head = "Female" and Character = "Woman"/"Classic")
  Character    only real named archetypes (Classic / Woman dropped)
  Hair         hair only; caps, hats, veils, bonnets, hoods and crowns move to Headwear (hair under them = "Covered")
  Headwear     Backwards Cap, Top Hat, Hood Up, veils, bonnets, Crown of Bones, Crown of Nails ...
  Mask         worn masks only
  Face         bare faces, face paint, grins and face conditions that are not a worn mask
  Held Weapon  objects held in the hand(s)
  Hands        hands that are the weapon: blade nails, claw gloves, bare fist, tentacle arms
  Power        Psychic Force, Telekinesis, Laser Lattice
  Prosthetic   hook hands (left hook finishes, and the right Iron Hook Hand)
  Off Hand     weapon or object carried in the left hand / on the shoulder
  Back Weapon  weapons on the back;  Back Gear: oxygen tank, fuel tanks, wings
  Neck         chains plus the two necklaces that used to sit under Belt
  Mutation     lab mutations plus the Elder Tentacle Arm
"""

HEADWEAR = {"Backwards Cap", "Battered Top Hat", "Hood Up", "Black Veil", "Straw Sun Bonnet", "Lace Bonnet",
            "Wilted Flower Crown", "Trainer Cap", "Retro Purple Beanie", "Veiled Mourning Hat"}
FACE = {"Bare Face", "Smeared Greasepaint", "Cracked Clown Paint", "Fanged Killer Clown", "Flayed Muscle Face", "Hollow Grey Face",
        "Waterlogged Face", "Manic Grin", "Black-Lipped Bloody Grin", "Carved Ear-to-Ear Grin", "Needle-Tooth Snarl",
        "Bearded Bulging Stare", "Psychic Glare", "Cold Digital Stare", "Mad Mother's Face", "Blood-Red Smile", "Psycho Yuppie Grin",
        "Writhing Face Tentacles", "Hinged Puppet Jaw", "Melted Doll Face", "Stitched Bride Face", "Veiled Stitched Face",
        "Cracked Porcelain Face", "Split Faceplate"}
HANDS = {"Bare Fist", "Death Nails", "Nail-Knife Glove", "Squid Tentacle Arms"}
POWER = {"Psychic Force", "Telekinesis", "Laser Lattice"}
BACK_GEAR = {"Oxygen Tank", "Fuel Tanks", "Leathery Bat Wings", "Leathery Elder Wings"}
NECKLACE = {"Golden Neck Chains", "Garnet Choker"}
FEMALE_CHARS = {"Woman", "Hollow Sister", "Farmhouse Smile", "Glitch Android", "Cursed Porcelain Doll", "The Ringmistress",
                "Rotten Bride", "Drowned Well Girl", "The Prom Queen", "The Overseer", "The Grieving Mother", "Madame Mortis",
                "The Trial Puppet"}

ORDER = ["Tier", "1/1 Name", "Character", "Gender", "Head", "Skin", "Eyes", "Ears", "Hair", "Headwear", "Head Mark", "Head Wound",
         "Mask", "Face", "Held Weapon", "Hands", "Power", "Prosthetic", "Off Hand", "Back Weapon", "Back Gear", "Clothing", "Neck",
         "Belt", "Flesh", "Mutation", "Experiment", "Backdrop", "Splatter"]


def remap(a):
    a = {k: v for k, v in a.items() if v not in (None, "", "None")}
    if a.get("Tier") == "Legendary 1/1":   # George 2026-11-17 17:54: 1/1s show only Tier + name, so their one-off traits stay off the trait lists
        return {"Tier": a["Tier"], "1/1 Name": a["1/1 Name"]}
    o = dict(a)
    o["Gender"] = "Female" if a.get("Head") == "Female" or a.get("Character") in FEMALE_CHARS else "Male"
    if o.get("Head") == "Female":
        o["Head"] = "Female Head"
    if a.get("Character") in ("Classic", "Woman"):
        del o["Character"]
    # headwear
    hw = []
    if a.get("Hair") in HEADWEAR:
        hw.append(a["Hair"]); o["Hair"] = "Covered"
    if a.get("Headpiece"):
        hw.append(o.pop("Headpiece"))
    if a.get("Mask") == "Crown of Nails":
        hw.append("Crown of Nails"); o["Mask"] = "None"
    if hw:
        o["Headwear"] = " + ".join(hw)
    # face vs mask
    if a.get("Mask") in FACE:
        o["Face"] = a["Mask"]; o["Mask"] = "None"
    if o.get("Mask") == "None":
        del o["Mask"]
    # hands, powers, prosthetics
    held = a.get("Held Weapon")
    if held in POWER:
        o["Power"] = held; del o["Held Weapon"]
    elif held in HANDS or (held or "").endswith("Blade Nails") or (held or "").endswith("Claw Glove"):
        o["Hands"] = held; del o["Held Weapon"]
    elif held == "Hook Hand":
        o["Prosthetic"] = "Iron Hook Hand (Right)"; del o["Held Weapon"]
    off = a.get("Off Hand")
    if off and off.endswith("Hook Hand"):
        o["Prosthetic"] = off; del o["Off Hand"]
    elif off == "Elder Tentacle Arm":
        o["Mutation"] = off; del o["Off Hand"]
    # back gear, necklaces
    if a.get("Back Weapon") in BACK_GEAR:
        o["Back Gear"] = a["Back Weapon"]; del o["Back Weapon"]
    if a.get("Belt") in NECKLACE:
        o["Neck"] = a["Belt"]; del o["Belt"]
    return {k: o[k] for k in ORDER if o.get(k) not in (None, "", "None")} | {k: v for k, v in o.items() if k not in ORDER and v not in (None, "", "None")}
