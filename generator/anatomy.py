"""Flag renders with extra or missing arms/hands, using a cheap Gemini vision call.

    python3 generator/anatomy.py output/ai/images-v2   -> prints "<id> <ARMS> <HANDS>" and writes output/ai/anatomy.json
"""
import base64, json, os, sys, time, urllib.request

MODEL = os.environ.get("GEMINI_CHECK_MODEL", "gemini-3.8-flash")
Q = ("This is a clay figure of one character. Count only the character's own arms and hands (not hands drawn on clothing, "
     "not weapons). Reply with JSON only: {\"arms\": <number of arms attached to the body>, \"hands\": <number of hands>, "
     "\"extra_limb\": <true if any arm, hand or set of fingers looks duplicated or comes from the wrong place>}")


def check(path):
    body = {"contents": [{"parts": [{"inline_data": {"mime_type": "image/png", "data": base64.b64encode(open(path, "rb").read()).decode()}},
                                    {"text": Q}]}], "generationConfig": {"temperature": 0, "responseMimeType": "application/json"}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
                                 data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    for attempt in range(4):
        try:
            res = json.load(urllib.request.urlopen(req, timeout=60))
            return json.loads(res["candidates"][0]["content"]["parts"][0]["text"])
        except Exception as e:
            err = e; time.sleep(5 * (attempt + 1))
    return {"error": str(err)[:200]}


if __name__ == "__main__":
    d = sys.argv[1]
    out = {}
    for f in sorted(os.listdir(d), key=lambda f: int(f[:-4]) if f[:-4].isdigit() else 0):
        if not (f.endswith(".png") and f[:-4].isdigit()):
            continue
        r = check(os.path.join(d, f)); out[f[:-4]] = r
        print(f[:-4], json.dumps(r), flush=True)
    json.dump(out, open("output/ai/anatomy.json", "w"), indent=1)
