"""Vision QA of finished Claysons with a cheap Gemini text model (George 2026-11-16: framing, facing, hands, weapons).
    python3 generator/qa_scan.py <ids|1-1300> [--model gemini-3.5-flash]   -> output/ai/qa-scan.json (resumable)"""
import base64, io, json, os, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import batch_generate as bg  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "output", "ai", "images-v2")
OUT = os.path.join(ROOT, "output", "ai", "qa-scan.json")
MODEL = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else "gemini-3.5-flash"
man = {r["id"]: r["attributes"] for r in json.load(open(os.path.join(ROOT, "output", "ai", "manifest-v2.json")))}
KEYS = ("Held Weapon", "Back Weapon", "Off Hand", "Mask", "Headpiece", "Neck", "Mutation")

Q = """You are QA-checking one picture from a claymation NFT collection. The house standard: ONE clay figure, body and head turned about
45 degrees toward the viewer's right (three-quarter view), framed from the waist up with backdrop visible above the head and on both sides,
holding the listed weapons. Exactly two arms and two hands (or a hook prosthetic in place of one hand when listed), every hand attached to
an arm. A held weapon must be gripped in a fist, not floating or standing loose. No text or lettering anywhere except a '666' jumpsuit patch.
Listed traits: %s
Reply JSON: {"facing": "right45"|"front"|"left"|"profile", "framing": "ok"|"too_close"|"too_far"|"cropped",
"extra_or_floating_limbs": bool, "loose_weapon": bool, "missing_listed_item": [names], "unlisted_extra_weapon": bool,
"text_or_logo": bool, "clipping": bool, "notes": "short, only real problems"}"""


def check(i):
    im = Image.open(os.path.join(IMG, f"{i}.png")).convert("RGB").resize((640, 640))
    b = io.BytesIO(); im.save(b, "JPEG", quality=88)
    traits = {k: man[i][k] for k in KEYS if man[i].get(k) not in (None, "None")}
    body = {"contents": [{"parts": [{"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(b.getvalue()).decode()}},
                                    {"text": Q % json.dumps(traits)}]}],
            "generationConfig": {"responseMimeType": "application/json"}}
    r = bg._req(bg.API + f"/v1beta/models/{MODEL}:generateContent", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    return json.loads(r["candidates"][0]["content"]["parts"][0]["text"])


def ids_arg(s):
    out = []
    for p in s.split(","):
        a, _, b = p.partition("-"); out += range(int(a), int(b or a) + 1)
    return out


done = json.load(open(OUT)) if os.path.exists(OUT) else {}
todo = [i for i in ids_arg(sys.argv[1]) if str(i) not in done and os.path.exists(os.path.join(IMG, f"{i}.png"))]
def safe(i):
    try:
        return i, check(i)
    except Exception as e:  # noqa: BLE001
        return i, {"error": repr(e)[:300]}


with ThreadPoolExecutor(6) as ex:
    for n, (i, res) in enumerate(ex.map(safe, todo), 1):
        if "error" in res:
            print(i, res["error"][:160], flush=True)
            if "402" in res["error"]:
                break
            continue
        done[str(i)] = res
        if n % 25 == 0:
            json.dump(done, open(OUT, "w"), indent=0); print(n, "checked", flush=True)
json.dump(done, open(OUT, "w"), indent=0)
bad = {k: v for k, v in done.items() if v.get("facing") != "right45" or v.get("framing") != "ok" or any(
    v.get(f) for f in ("extra_or_floating_limbs", "loose_weapon", "missing_listed_item", "unlisted_extra_weapon", "text_or_logo", "clipping"))}
print(len(done), "checked;", len(bad), "flagged")
