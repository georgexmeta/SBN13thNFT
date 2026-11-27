#!/usr/bin/env python3
"""Generate the clay scenes for the interactive cabin site with Gemini (George's credits).
python3 site/tools/gen_scenes.py <out_dir> [scene ...]"""
import base64, json, os, sys, urllib.request
MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
PF = "/mnt/project-files/website/"
STYLE = ("STYLE REFERENCE is the FIRST image: copy its look exactly. The whole scene is a pressed-plasticine bas-relief, like a "
         "hand-made clay wall panel: soft rounded shallow-relief shapes pushed out of a flat clay slab, thumb-smoothed surfaces with "
         "fine fingerprint texture and tool lines, puffy pillow-like clay clouds, chunky simplified forms, soft even frontal light "
         "with gentle shadows, a limited pastel palette built on dusty lavender and violet with muted accents. Cute-spooky storybook "
         "mood, not photoreal, no realistic textures, no deep 3D perspective. Wide 16:9 composition. No text, no letters, no logos, no watermark.")
STYLE_REF = "style-721-clay.jpg"
SCENES = {
 "exterior": ("A lonely crooked wooden cabin sculpted from clay on the shore of a dark lake at night, glowing amber windows, "
              "a front porch with a hanging lantern and the front door slightly open spilling warm light, clay pine trees, low fog, "
              "a low red moon over the water. The cabin sits in the centre of the frame.", None),
 "inside": ("Inside a rustic clay cabin, one-point perspective looking straight ahead at a back door standing open, showing a moonlit "
            "wooden dock and lake beyond it. On the LEFT wall, an open side doorway glowing with warm orange candlelight. "
            "On the RIGHT wall, an open side doorway glowing with eerie green and red Christmas lights. Clay floorboards, a rag rug, "
            "a crackling fireplace, mounted antlers, cobwebs. LOTS of warm candle light: dripping clay candles with glowing flames on the mantel, "
            "shelves, floor and window sills, warm amber glow pooling on the floor and walls. Three clear exits: left, straight ahead, right.", None),
 "peddler": ("The SAME character as the SECOND reference image, sculpted as a rounded clay figure that pops out of the relief (keep his face, third eye, rusty halo, gold teeth, rings, black nails and the box he is wrapping exactly), "
             "at his candlelit merchant stall: a lean-to of lavender relief clay planks. There is NO gold, NO silver, NO molten metal anywhere: with both hands he "
             "is wrapping a gift box exactly like the THIRD reference image (black-and-white striped and swirled paper, red-and-green ribbon, rusty "
             "chains, padlock, skull tag), pulling the ribbon tight while a tentacle pokes out of the half-wrapped box. Spools of striped paper, "
             "ribbon and rusty chain on the counter. Behind him, crooked shelves stacked with finished chained Nightmare Boxes. He grins at the viewer.",
             ["peddler-wrapping-ref.png", "nightmare-box.jpeg"]),
 "tree": ("A creepy Christmas tree sculpted from clay standing in a small cabin room: twisted black branches, ornaments made of tiny skulls, "
          "eyeballs, rusty hooks and padlocks, tangled green and red fairy lights, a broken star on top. Under the tree sits ONE gift box exactly "
          "like the SECOND reference image (striped box, rusty chains, padlock, tentacles, yellow eyes). Dim red glow, snow drifting through a cracked window.",
          "nightmare-box.jpeg"),
 "dock": ("The view from the end of a wooden clay dock looking out over a lake at night, built entirely as LAYERED clay: many flat "
          "cut-out plasticine layers stacked one in front of another like a paper-theatre diorama, each layer with a thick soft rounded edge "
          "and its own drop shadow on the layer behind. Back to front: lavender sky slab with puffy pillow clouds and a big flat red clay moon; "
          "three overlapping bands of rolling mountains in lavender, violet and dusty plum; a band of chunky pine trees; the lake made of "
          "wavy stacked strips of blue-violet clay with pressed ripple lines and a red moon reflection made of clay dabs; a lone purple tentacle "
          "rising from the water; a rowboat; and the dock planks in the foreground. Clearly visible depth from the stacked layers.", None),
}
def gen(name, out):
    prompt, ref = SCENES[name]
    parts = [{"text": STYLE + "\n\n" + prompt}]
    refs = [STYLE_REF] + ([ref] if isinstance(ref, str) else (ref or []))
    for r in reversed(refs):
        parts.insert(0, {"inline_data": {"mime_type": "image/png" if r.endswith(".png") else "image/jpeg", "data": base64.b64encode(open(PF + r, "rb").read()).decode()}})
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
