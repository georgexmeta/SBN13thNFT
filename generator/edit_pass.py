"""Combined edit-in-place pass for finished Claysons (George approved 2026-11-16): one instruction per token covering every
fix that applies. python3 generator/edit_pass.py [--submit]  (writes output/ai/edit-pass.json either way)"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v2

ROOT = v2.ROOT
IMG = os.path.join(ROOT, "output", "ai", "images-v2")
man = {i: r["attributes"] for i, r in enumerate(json.load(open(os.path.join(ROOT, "output", "ai", "manifest-v2.json"))), 1)}
lst = lambda n: set(json.load(open(os.path.join(ROOT, "generator", f"{n}_finished.json"))))
fix = {}


def add(i, text):
    if os.path.exists(os.path.join(IMG, f"{i}.png")):
        fix.setdefault(i, []).append(text)


def he(a, t):   # pronouns for women
    if a.get("Head") == "Female" or a.get("Character") not in (None, "Classic"):
        for m, f in [(r"\bhis\b", "her"), (r"\bHis\b", "Her"), (r"\bhim\b", "her"), (r"\bhe\b", "she")]:
            t = re.sub(m, f, t)
    return t


for i in lst("hookoff"):
    oh = man[i].get("Off Hand") or ""
    if oh.endswith("Hook Hand"):
        fin = v2.HOOK_FINISH[oh.split()[0]]
        add(i, f"his free left hand is replaced by a prosthetic hook of {fin} strapped to his forearm, raised, never a limp hand or bare stump")
for i in lst("wound"):
    if man[i].get("Head Wound"):
        add(i, "add " + v2.WOUND)
for i in lst("oxygen"):
    if man[i].get("Back Weapon") == "Oxygen Tank":
        add(i, "add " + v2.OXYGEN)
for i in lst("gasmask"):
    mk = man[i]["Mask"]
    if "Gas Mask" in mk or "Respirator" in mk:
        add(i, "change his gas mask to " + v2.ALL["Mask"][mk][1])
for i in lst("bloodmoon"):
    if man[i]["Backdrop"] == "Blood Moon":
        add(i, "replace the backdrop with " + v2.ALL["Backdrop"]["Blood Moon"][1])
for i in lst("cone"):
    if man[i]["Head"] == "Type 3 - Cone Skull":
        add(i, "where the top of his head shows, make the cone-shaped skull only SUBTLY cone-shaped: slightly elongated with a soft rounded "
               "crown, not a sharp point or tall exaggerated cone (leave any mask, hat or hood as it is)")
for i in (141, 178, 212, 618):
    b = man[i]["Back Weapon"]
    if b.endswith("Saw Weed Whacker"):
        add(i, "the weed whacker on his back must have " + v2.SAW_FINISH[b.split()[0]] + " round toothed circular saw blade under a small "
               "guard as its cutting head, rising above and behind his shoulder")

out = {i: he(man[i], "Edit this claymation image. Keep everything else exactly the same (pose, face, clay style, framing, colours, lighting, "
                 "every other detail). Changes: " + "; ".join(t) + ". No text, no logos.") for i, t in sorted(fix.items())}
json.dump(out, open(os.path.join(ROOT, "output", "ai", "edit-pass.json"), "w"), indent=1)
if __name__ == "__main__":
    print(len(out), "tokens to edit")
if __name__ == "__main__" and "--submit" in sys.argv:
    import batch_generate as bg
    bg.edit_multi(out, label="editpass")
