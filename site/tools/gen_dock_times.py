#!/usr/bin/env python3
"""Relight the dock lake view for different times of day, keeping the same clay scene.
python3 site/tools/gen_dock_times.py <dock.jpg> <out_dir> [phase ...]"""
import base64, json, os, sys, urllib.request
MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
KEEP = ("Edit this image. Keep EXACTLY the same layered pressed-plasticine clay scene, composition, camera, every layer, the dock, "
        "rowboat, tentacle, trees, mountains and clouds in the same places and the same handmade clay style. Change ONLY the time of day, "
        "lighting and colours of sky, water and layers: ")
PHASES = {
 "dawn": "early dawn: a pale peach-pink clay sun just peeking over the mountain layers on the left, sky graded from soft lavender to peach, "
         "cool misty light, light pink reflections on the water strips, no moon.",
 "day": "bright midday: a soft pale-yellow clay sun high in a light periwinkle sky, white puffy clay clouds, crisp even daylight, "
        "the water strips light blue-lilac with white highlight lines, no moon.",
 "night": "full night after the sun has set: deep indigo and navy sky, tiny pressed white clay stars, and the moon as a flat matte pressed-plasticine disc of pale cream clay exactly like the stars, "
          "with thumb-pressed craters and a small drop shadow, NO glow, NO halo, NO bloom, mountain layers in dark violet-navy silhouettes, water strips dark blue with a shimmering silver moon reflection made of clay dabs, "
          "the tentacle and rowboat dimly lit by moonlight, cool blue light everywhere, no sun.",
 "moonfix": "keep it night exactly as it is. Change ONLY the moon: make it a flat, matte pressed-plasticine disc like the little clay stars, "
            "pale cream clay with a few thumb-pressed craters and fingerprint texture, a soft raised edge and a small drop shadow on the sky layer. "
            "NO glow, NO halo, NO bloom, NO light rays around it. Keep the moonlight reflection on the water as clay dabs.",
 "closed": "keep the time of day and lighting exactly as they are. Change ONLY this: REMOVE the purple tentacle completely (just calm clay water "
           "there). At the end of the dock, a rusty clay chain hangs across between the two front posts with a padlock, and a crooked hand-made "
           "wooden clay sign is nailed to the right post, with the words LAKE IS CLOSED pressed into it in big chunky clay capital letters, "
           "spelled exactly L-A-K-E  I-S  C-L-O-S-E-D, nothing else written.",
 "open": "keep the time of day and lighting exactly as they are. Change ONLY this: REMOVE the rusty chain, the padlock and the LAKE IS CLOSED sign completely, so the end of the dock is open and the two posts stand bare. The water is calm and empty, no creature, no tentacle, no text anywhere.",
 "dusk": "sunset dusk: a big orange-red clay sun half sunk behind the mountain layers, sky graded from deep violet at the top to hot "
         "orange and magenta near the mountains, mountains in dark silhouette layers, orange reflection on the water strips, no moon.",
}
def gen(src, phase, out):
    body = {"contents": [{"parts": [{"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(open(src, "rb").read()).decode()}},
                                    {"text": KEEP + PHASES[phase] + ("" if phase in ("closed","open") else " Keep the LAKE IS CLOSED sign and chain exactly as they are, same letters. No other text, no logos.")}]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "16:9"}}}
    req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": "dummy"})
    r = json.load(urllib.request.urlopen(req, timeout=180))
    for p in r["candidates"][0]["content"]["parts"]:
        d = p.get("inlineData") or p.get("inline_data")
        if d: open(os.path.join(out, f"dock-{phase}-{os.path.basename(src).split('.')[0]}.png"), "wb").write(base64.b64decode(d["data"])); return True
    print(phase, "no image"); return False
if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    for ph in (sys.argv[3:] or list(PHASES)): print(ph, gen(src, ph, out))
