"""Edit-in-place fixes from George's review of the finished renders (2026-11-16). Runs AFTER edit_pass.py results are in.
Per-token notes live in generator/review_fixes.json {"id": ["instruction", ...]}.
    python3 generator/edit_review.py [--submit]   (writes output/ai/edit-review.json either way)"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edit_pass import he, man, ROOT, IMG  # noqa: E402

GRIP = ("fix his grip on the weed whacker: his left hand firmly wraps the black loop handle in the middle of the shaft and his right fist "
        "grips the rear trigger handle next to the motor; no hand on the shaft up near the blade, no empty or limp hand, the whole tool stays "
        "inside the frame")
fix = {}
for i, a in man.items():   # George 2026-11-16: #3, #46 hold the held saw weed whacker wrong; standardise all of them
    if a.get("Held Weapon", "").endswith("Saw Weed Whacker"):
        fix.setdefault(i, []).append(GRIP)
for k, v in json.load(open(os.path.join(ROOT, "generator", "review_fixes.json"))).items():
    fix.setdefault(int(k), []).extend(v)
fix = {i: t for i, t in fix.items() if os.path.exists(os.path.join(IMG, f"{i}.png"))}
out = {i: he(man[i], "Edit this claymation image. Keep everything else exactly the same (pose, face, clay style, framing, colours, lighting, "
                     "every other detail). Changes: " + "; ".join(t) + ". No text, no logos.") for i, t in sorted(fix.items())}
json.dump(out, open(os.path.join(ROOT, "output", "ai", "edit-review.json"), "w"), indent=1)
print(len(out), "tokens to edit")
if "--submit" in sys.argv:
    import batch_generate as bg
    bg.edit_multi(out, label="review")
