"""Classify which way a render's face points, with a cheap Gemini vision call.

    python3 generator/facing.py <png> [...]        prints id RIGHT|LEFT|FRONT
Every token should face about 45 degrees toward the viewer's RIGHT, like refs/master-reference.jpg.
"""
import base64, json, os, sys, time, urllib.request

MODEL = os.environ.get("GEMINI_CHECK_MODEL", "gemini-3.8-flash")
Q = ("Look at the clay figure's head. Which way is the face pointing, from the viewer's point of view? "
     "Judge by where the nose and eyes point relative to the centre of the head. "
     "Answer with exactly one word: RIGHT (the face is turned toward the right side of the image), "
     "LEFT (turned toward the left side of the image), or FRONT (looking straight at the camera).")


def facing(path):
    body = {"contents": [{"parts": [{"inline_data": {"mime_type": "image/png", "data": base64.b64encode(open(path, "rb").read()).decode()}},
                                    {"text": Q}]}],
            "generationConfig": {"temperature": 0}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
                                 data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    for attempt in range(4):
        try:
            res = json.load(urllib.request.urlopen(req, timeout=60))
            txt = res["candidates"][0]["content"]["parts"][0]["text"].upper()
            for w in ("RIGHT", "LEFT", "FRONT"):
                if w in txt:
                    return w
            return "UNKNOWN"
        except Exception:
            time.sleep(5 * (attempt + 1))
    return "UNKNOWN"


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(os.path.basename(p).split(".")[0], facing(p), flush=True)
