"""Build the OpenSea Studio drop upload: output/opensea/metadata.csv plus images named <tokenID>.png.

    python3 generator/opensea_csv.py           # writes the CSV and copies the finished images

Columns follow OpenSea's drop template: tokenID, name, description, file_name, external_url, attributes[<trait>].
Only string traits are used (Studio CSV uploads don't support numeric traits).
"""
import csv, json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESC = "SBN13th: 1,300 hand-sculpted-look claymation slashers. 1,157 Standard, 130 Rare and 13 Legendary 1/1s."
TRAITS = ["Tier", "1/1 Name", "Head", "Skin", "Hair", "Head Mark", "Mask", "Held Weapon", "Back Weapon", "Clothing", "Belt", "Backdrop"]


def main():
    rows = json.load(open(os.path.join(ROOT, "output", "ai", "manifest-v2.json")))
    out = os.path.join(ROOT, "output", "opensea"); img = os.path.join(out, "images")
    os.makedirs(img, exist_ok=True)
    missing = []
    with open(os.path.join(out, "metadata.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tokenID", "name", "description", "file_name", "external_url"] + [f"attributes[{t}]" for t in TRAITS])
        for r in rows:
            a = r["attributes"]
            w.writerow([r["id"], r["name"], DESC, f"{r['id']}.png", ""] + [a.get(t, "") for t in TRAITS])
            src = os.path.join(ROOT, "output", "ai", "images-v2", f"{r['id']}.png")
            if os.path.exists(src):
                shutil.copyfile(src, os.path.join(img, f"{r['id']}.png"))
            else:
                missing.append(r["id"])
    print(f"wrote {len(rows)} rows; {len(rows) - len(missing)} images ready, {len(missing)} still missing")


if __name__ == "__main__":
    main()
