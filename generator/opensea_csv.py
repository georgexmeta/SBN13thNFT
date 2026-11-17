"""Build the OpenSea Studio drop upload: output/opensea/metadata.csv plus images named <tokenID>.png.

    python3 generator/opensea_csv.py           # writes the CSV and copies the finished images

Columns follow OpenSea's drop template: tokenID, name, description, file_name, external_url, attributes[<trait>].
Only string traits are used (Studio CSV uploads don't support numeric traits).
"""
import csv, json, os, re, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "Claysons"
DESC = "Claysons: 1,300 hand-sculpted-look claymation slashers. 464 Common, 400 Uncommon, 293 Rare, 130 Epic and 13 Legendary 1/1s. Three Legendary 1/1s (#1 to #3) are held by the team."
TRAITS = ["Tier", "1/1 Name", "Character", "Head", "Skin", "Hair", "Head Mark", "Ears", "Mask", "Held Weapon", "Back Weapon", "Clothing", "Belt", "Backdrop", "Splatter", "Off Hand", "Head Wound", "Neck", "Flesh", "Eyes", "Headpiece", "Mutation", "Experiment"]


LEGEND_IDS = [1, 3, 13, 31, 103, 131, 301, 313, 1003, 1013, 1031, 1133, 1300]
LEGEND_FIXED = {"Old Gilded": 1, "Diamond Wraith": 3, "The Sleeper Below": 13}


LEGEND_RENUMBER = False   # George 2026-11-17 15:32: hold the renumbering until he says so; team keeps Legendaries on #1-#3
TEAM_LEGENDS = ["Old Gilded", "Diamond Wraith", "The Sleeper Below"]


def team_swap(rows):
    """Previous rule (2026-11-13): three flagship Legendaries swap places with IDs 1-3."""
    by_name = {r["attributes"].get("1/1 Name"): r["id"] for r in rows}
    swap = {r["id"]: r["id"] for r in rows}
    for new, nm in enumerate(TEAM_LEGENDS, 1):
        old = by_name[nm]; swap[old], swap[new] = new, old
    return swap


def legend_swap(rows):
    """internal id -> published tokenID"""
    legs = {r["attributes"]["1/1 Name"]: r["id"] for r in rows if r["attributes"].get("Tier") == "Legendary 1/1"}
    assert len(legs) == 13 and len(LEGEND_IDS) == 13
    place = {legs[n]: t for n, t in LEGEND_FIXED.items()}
    for i in sorted(legs.values()):
        if i not in place and i in LEGEND_IDS and i not in place.values():
            place[i] = i
    free = [t for t in LEGEND_IDS if t not in place.values()]
    for i in sorted(i for i in legs.values() if i not in place):
        place[i] = free.pop(0)
    displaced = sorted(t for t in LEGEND_IDS if t not in legs.values())          # non-Legendary tokens sitting on a Legendary number
    vacated = sorted(i for i in legs.values() if i not in LEGEND_IDS)            # Legendary old numbers now free
    swap = {r["id"]: r["id"] for r in rows}
    swap.update(place)
    swap.update(dict(zip(displaced, vacated)))
    assert sorted(swap.values()) == sorted(swap) and len(set(swap.values())) == len(rows)
    return swap


def main():
    rows = json.load(open(os.path.join(ROOT, "output", "ai", "manifest-v2.json")))
    from collections import Counter
    n = Counter(r["attributes"]["Tier"] for r in rows)
    desc = (f"Claysons: 1,300 hand-sculpted-look claymation slashers. {n['Common']:,} Common, {n['Uncommon']:,} Uncommon, {n['Rare']:,} Rare, "
            f"{n['Epic']:,} Epic and {n['Legendary 1/1']} Legendary 1/1s. " + ("The creator's wallets hold Legendary #1, #3, #13 and #1300." if LEGEND_RENUMBER else "Three Legendary 1/1s (#1 to #3) are held by the team."))
    out = os.path.join(ROOT, "output", "opensea"); img = os.path.join(out, "images")
    os.makedirs(img, exist_ok=True)
    # Legendary numbers (George 2026-11-17): the 13 Legendary 1/1s publish on these token IDs. The three flagship team
    # Legendaries take 1, 3 and 13; a Legendary whose own id is already on the list keeps it; the rest fill the remaining
    # numbers in id order. The tokens that sat on those numbers move to the Legendaries' old numbers. Internal ids (renders,
    # manifest, batches) never change; only the published tokenID, name number and image file move.
    swap = legend_swap(rows) if LEGEND_RENUMBER else team_swap(rows)
    rows = sorted(rows, key=lambda r: swap[r["id"]])
    missing = []
    with open(os.path.join(out, "metadata.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tokenID", "name", "description", "file_name", "external_url"] + [f"attributes[{t}]" for t in TRAITS])
        for r in rows:
            a = r["attributes"]
            tid = swap[r["id"]]
            name = re.sub(r"#\d+", f"#{tid}", r["name"].replace("SBN13th", NAME), count=1)
            w.writerow([tid, name, desc, f"{tid}.png", ""] + [a.get(t, "") for t in TRAITS])
            src = os.path.join(ROOT, "output", "ai", "images-v2", f"{r['id']}.png")
            if os.path.exists(src):
                shutil.copyfile(src, os.path.join(img, f"{tid}.png"))
            else:
                missing.append(r["id"])
    print(f"wrote {len(rows)} rows; {len(rows) - len(missing)} images ready, {len(missing)} still missing")


if __name__ == "__main__":
    main()
