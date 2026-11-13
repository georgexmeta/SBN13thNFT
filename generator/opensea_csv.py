"""Build the OpenSea Studio drop upload: output/opensea/metadata.csv plus images named <tokenID>.png.

    python3 generator/opensea_csv.py           # writes the CSV and copies the finished images

Columns follow OpenSea's drop template: tokenID, name, description, file_name, external_url, attributes[<trait>].
Only string traits are used (Studio CSV uploads don't support numeric traits).
"""
import csv, json, os, re, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "Claysons"
DESC = "Claysons: 1,300 hand-sculpted-look claymation slashers. 1,157 Standard, 130 Rare and 13 Legendary 1/1s. Three Legendary 1/1s (#1 to #3) are held by the team."
TRAITS = ["Tier", "1/1 Name", "Character", "Head", "Skin", "Hair", "Head Mark", "Ears", "Mask", "Held Weapon", "Back Weapon", "Clothing", "Belt", "Backdrop"]


def main():
    rows = json.load(open(os.path.join(ROOT, "output", "ai", "manifest-v2.json")))
    out = os.path.join(ROOT, "output", "opensea"); img = os.path.join(out, "images")
    os.makedirs(img, exist_ok=True)
    # Team stage (George, 2026-11-13): the Team wallet mints first and receives token IDs 1-13. Three flagship Legendaries
    # swap places with IDs 1-3; IDs 4-13 keep their own Standard/Rare tokens and the other 10 Legendaries stay where they
    # were. Internal ids (renders, manifest) are unchanged; only the published tokenID, name number and image file move.
    TEAM_LEGENDS = ["Old Gilded", "Diamond Wraith", "The Frontman"]
    by_name = {r["attributes"].get("1/1 Name"): r["id"] for r in rows}
    swap = {r["id"]: r["id"] for r in rows}
    for new, nm in enumerate(TEAM_LEGENDS, 1):
        old = by_name[nm]; swap[old], swap[new] = new, old
    rows = sorted(rows, key=lambda r: swap[r["id"]])
    missing = []
    with open(os.path.join(out, "metadata.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tokenID", "name", "description", "file_name", "external_url"] + [f"attributes[{t}]" for t in TRAITS])
        for r in rows:
            a = r["attributes"]
            tid = swap[r["id"]]
            name = re.sub(r"#\d+", f"#{tid}", r["name"].replace("SBN13th", NAME), count=1)
            w.writerow([tid, name, DESC, f"{tid}.png", ""] + [a.get(t, "") for t in TRAITS])
            src = os.path.join(ROOT, "output", "ai", "images-v2", f"{r['id']}.png")
            if os.path.exists(src):
                shutil.copyfile(src, os.path.join(img, f"{tid}.png"))
            else:
                missing.append(r["id"])
    print(f"wrote {len(rows)} rows; {len(rows) - len(missing)} images ready, {len(missing)} still missing")


if __name__ == "__main__":
    main()
