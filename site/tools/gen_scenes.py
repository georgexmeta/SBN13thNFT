#!/usr/bin/env python3
"""Generate the clay scenes for the interactive cabin site with Gemini (George's credits).
python3 site/tools/gen_scenes.py <out_dir> [scene ...]"""
import base64, json, os, sys, urllib.request
MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
PF = "/mnt/project-files/website/"
STYLE = ("Handmade stop-motion claymation diorama: matte plasticine with visible thumbprints and sculpting tool marks, "
         "a miniature model set photographed with warm studio lighting and shallow depth of field, grim horror mood, night. "
         "Wide 16:9 composition. No text, no letters, no logos, no watermark.")
SCENES = {
 "exterior": ("A lonely crooked wooden cabin sculpted from clay on the shore of a dark lake at night, glowing amber windows, "
              "a front porch with a hanging lantern and the front door slightly open spilling warm light, clay pine trees, low fog, "
              "a low red moon over the water. The cabin sits in the centre of the frame.", None),
 "inside": ("Inside a rustic clay cabin, one-point perspective looking straight ahead at a back door standing open, showing a moonlit "
            "wooden dock and lake beyond it. On the LEFT wall, an open side doorway glowing with warm orange candlelight. "
            "On the RIGHT wall, an open side doorway glowing with eerie green and red Christmas lights. Clay floorboards, a rag rug, "
            "a cold fireplace, mounted antlers, cobwebs, oil lamp. Three clear exits: left, straight ahead, right.", None),
 "peddler": ("The SAME character as the FIRST reference image (keep his face, third eye, rusty halo, gold teeth, rings and black nails exactly), "
             "seen wider at his candlelit merchant stall in a dark wooden lean-to room. There is NO gold or silver block: instead, with both hands he "
             "is wrapping a gift box exactly like the SECOND reference image (black-and-white striped and swirled paper, red-and-green ribbon, rusty "
             "chains, padlock, skull tag), pulling the ribbon tight while a tentacle pokes out of the half-wrapped box. Spools of striped paper, "
             "ribbon and rusty chain on the counter. Behind him, crooked shelves stacked with finished chained Nightmare Boxes. He grins at the viewer.",
             ["melding-peddler.jpeg", "nightmare-box.jpeg"]),
 "tree": ("A creepy Christmas tree sculpted from clay standing in a small cabin room: twisted black branches, ornaments made of tiny skulls, "
          "eyeballs, rusty hooks and padlocks, tangled green and red fairy lights, a broken star on top. Under the tree sits ONE gift box exactly "
          "like the reference image (striped box, rusty chains, padlock, tentacles, yellow eyes). Dim red glow, snow drifting through a cracked window.",
          "nightmare-box.jpeg"),
 "dock": ("View from the end of a wooden clay dock looking out over a scenic clay-model lake at night: glassy dark water, misty clay mountains, "
          "a pine forest shoreline, a big low red moon with its reflection, a rowboat tied to the dock, a lone tentacle breaking the surface far away.", None),
}
def gen(name, out):
    prompt, ref = SCENES[name]
    parts = [{"text": STYLE + "\n\n" + prompt}]
    for r in reversed([ref] if isinstance(ref, str) else (ref or [])):
        parts.insert(0, {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(open(PF + r, "rb").read()).decode()}})
    body = {"contents": [{"parts": parts}], "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "16:9"}}}
    req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": "dummy"})
    r = json.load(urllib.request.urlopen(req, timeout=180))
    for p in r["candidates"][0]["content"]["parts"]:
        d = p.get("inlineData") or p.get("inline_data")
        if d:
            open(os.path.join(out, name + ".png"), "wb").write(base64.b64decode(d["data"])); return True
    print(name, "no image", json.dumps(r)[:400]); return False
if __name__ == "__main__":
    out = sys.argv[1]; names = sys.argv[2:] or list(SCENES)
    for n in names:
        try: print(n, gen(n, out))
        except urllib.error.HTTPError as e: print(n, e.code, e.read()[:300])
