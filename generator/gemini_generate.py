"""Generate token images with Gemini's image model, anchored to George's reference images.

    python3 generator/gemini_generate.py 1-20   # key from GEMINI_API_KEY or a network secret header          # writes output/ai/images/<id>.png
    python3 generator/gemini_generate.py 10,76 --refs refs/master.jpg refs/mask.jpg --force

Every call sends the reference image(s) plus the token's prompt from output/ai/manifest.json (run prompts.py
first). Existing images are skipped unless --force. Model can be changed with GEMINI_IMAGE_MODEL.
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from facing import facing   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.environ.get("MANIFEST", os.path.join(ROOT, "output", "ai", "manifest.json"))
OUTDIR = os.environ.get("OUTDIR", os.path.join(ROOT, "output", "ai", "images"))
MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
DEFAULT_REFS = [os.path.join(ROOT, "refs", "master-reference.jpg"), os.path.join(ROOT, "refs", "face-reference.png")]
MASK_REF = os.path.join(ROOT, "refs", "mask-reference.jpg")

LEAD = ("The first reference photo sets the sculpting style, clay finish, lighting and camera framing. The second "
        "reference photo is the character: keep the exact same face sculpt and head proportions. Change only what this "
        "description says: ")


def ids(spec):
    out = []
    for part in spec.split(","):
        a, _, b = part.partition("-")
        out += range(int(a), int(b or a) + 1)
    return out


def part_for(path):
    mime = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    return {"inline_data": {"mime_type": mime, "data": base64.b64encode(open(path, "rb").read()).decode()}}


def generate(row, refs, key):
    refs = list(refs)
    if str(row["attributes"].get("Mask", "None")).startswith(("Hockey", "Bloody", "Chrome")) and os.path.exists(MASK_REF) and MASK_REF not in refs:
        refs.append(MASK_REF)
    body = {"contents": [{"parts": [part_for(r) for r in refs] + [{"text": LEAD + row["prompt"] + " Avoid: " + row["negative"]}]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "seed": row["seed"], "imageConfig": {"aspectRatio": "1:1"}}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
                                 data=json.dumps(body).encode(), headers={"Content-Type": "application/json", **({"x-goog-api-key": key} if key else {})})
    spend_waits = 0
    for attempt in range(5 + 12):   # extra rounds are only used by spend-limit waits
        try:
            res = json.load(urllib.request.urlopen(req, timeout=180))
            for c in res.get("candidates", []):
                for p in c.get("content", {}).get("parts", []):
                    d = p.get("inline_data") or p.get("inlineData")
                    if d:
                        return base64.b64decode(d["data"])
            if "PROHIBITED" in json.dumps(res) and attempt - spend_waits < 4:   # safety filter false positive: try another seed
                body["generationConfig"]["seed"] += 1
                req.data = json.dumps(body).encode(); continue
            raise RuntimeError("no image in response: " + json.dumps(res)[:400])
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:400]
            if e.code == 429 and "spend" in msg and spend_waits < 12:   # account spend cap: wait it out, don't burn retries
                spend_waits += 1; print(f"  spend limit hit, waiting 5 min ({spend_waits}/12)", flush=True)
                time.sleep(300); continue
            if e.code in (429, 500, 503) and attempt - spend_waits < 4 and "limit: 0" not in msg:
                time.sleep(10 * 2 ** (attempt - spend_waits)); continue
            raise RuntimeError(f"HTTP {e.code}: {msg}")
        except urllib.error.URLError as e:   # proxy or network blip: wait and retry instead of skipping the token
            if attempt < 16:
                print(f"  network error ({e.reason}), retrying in 30s", flush=True); time.sleep(30); continue
            raise


def main():
    key = os.environ.get("GEMINI_API_KEY")   # optional: a network secret can add the x-goog-api-key header instead
    args = sys.argv[1:]
    force = "--force" in args
    refs = DEFAULT_REFS
    if "--refs" in args:
        i = args.index("--refs"); refs = []
        for a in args[i + 1:]:
            if a.startswith("--"): break
            refs.append(a)
    rows = {r["id"]: r for r in json.load(open(MANIFEST))}
    os.makedirs(OUTDIR, exist_ok=True)
    for i in ids(args[0] if args and not args[0].startswith("--") else "1-1300"):
        out = os.path.join(OUTDIR, f"{i}.png")
        if os.path.exists(out) and not force:
            continue
        try:
            row = dict(rows[i])
            for tries in range(3):   # every token must face ~45 degrees to the viewer's right
                img = generate(row, refs, key)
                tmp = out + ".check.png"; open(tmp, "wb").write(img)
                way = facing(tmp)
                if way == "RIGHT" or tries == 2:
                    break
                print(f"  #{i} faces {way}, re-rolling", flush=True); row["seed"] += 7
            os.replace(tmp, out); print(f"#{i} ok" + ("" if way == "RIGHT" else f" (facing {way}, needs review)"), flush=True)
            time.sleep(float(os.environ.get("THROTTLE", "0")))
        except Exception as e:
            print(f"#{i} failed: {e}", flush=True)
            if "HTTP 402" in str(e):   # prepaid credits are gone: stop instead of failing every token
                sys.exit("stopping: Gemini prepayment credits are depleted")


if __name__ == "__main__":
    main()
