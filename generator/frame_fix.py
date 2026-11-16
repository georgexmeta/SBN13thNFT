"""Queue the standard-framing edit for tokens George flags as 'not positioned like the others'.
    python3 generator/frame_fix.py <id> [...]   then edit_review.py --submit"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
man = {r["id"]: r["attributes"] for r in json.load(open(os.path.join(ROOT, "output", "ai", "manifest-v2.json")))}
P = os.path.join(ROOT, "generator", "review_fixes.json")
d = json.load(open(P))
for i in map(int, sys.argv[1:]):
    a = man[i]; she = a.get("Head") == "Female" or a.get("Character") not in (None, "Classic")
    his = "her" if she else "his"
    held, off, back = a.get("Held Weapon"), a.get("Off Hand"), a.get("Back Weapon")
    t = ("zoom out to the standard framing of the collection: the whole figure smaller and centred, clear backdrop above "
         f"{his} head and on both sides, torso visible down to the waist, body and head turned about 45 degrees to the viewer's right")
    if held and held not in ("Bare Fist",):
        t += f"; {his} right fist holds the {held.lower()} in front of {his} chest"
    if off:
        t += f"; {his} left hand keeps the {off.lower()}"
    if back and back != "None":
        t += f"; the {back.lower()} stays on {his} back"
    d[str(i)] = [x for x in d.get(str(i), []) if not x.startswith("zoom out to the standard framing")] + [t]
    print(i, t)
json.dump(d, open(P, "w"), indent=1)
