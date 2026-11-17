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
KEYS = ("Head", "Character", "Held Weapon", "Back Weapon", "Off Hand", "Mask", "Clothing", "Headpiece", "Neck", "Mutation")

Q = """You are QA-checking a picture from a claymation NFT collection. IMAGE 1 is the house-standard reference; IMAGE 2 is the token to check. Compare IMAGE 2 against IMAGE 1: body angle, head angle, how big the figure is in the frame. The house standard: ONE clay figure, body and head turned about
45 degrees toward the viewer's right (three-quarter view), framed from the waist up with backdrop visible above the head and on both sides,
holding the listed weapons. Exactly two arms and two hands (or a hook prosthetic in place of one hand when listed), every hand attached to
an arm. A held weapon must be gripped in a fist, not floating or standing loose. No text or lettering anywhere except a '666' jumpsuit patch or a 'TICKETS' sign on a circus ticket booth.
Listed traits: %s
Answer for IMAGE 2. "facing" is right45 only if BOTH the torso/shoulders and the head turn toward the viewer's right like IMAGE 1; a chest squarely facing the camera is "front". "framing" is too_close if the head/figure is noticeably bigger in the frame than in IMAGE 1 or the head nearly touches the top edge. "clipping" = any weapon/tool passing through the body, face or mask, or growing out of the body instead of being held.
Reply JSON: {"facing": "right45"|"front"|"left"|"profile", "framing": "ok"|"too_close"|"too_far"|"cropped",
"extra_or_floating_limbs": bool, "loose_weapon": bool, "missing_listed_item": [names], "unlisted_extra_weapon": bool,
"text_or_logo": bool, "clipping": bool, "wrong_character": bool (true if IMAGE 2 clearly does not match the listed traits, e.g. a man when Head is Female, or a different mask/outfit/character), "notes": "short, only real problems"}"""


_r = Image.open(os.path.join(ROOT, "refs", "master-reference.jpg")).convert("RGB").resize((640, 640)); _b = io.BytesIO(); _r.save(_b, "JPEG", quality=88)
REF = {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(_b.getvalue()).decode()}}


def check(i):
    im = Image.open(os.path.join(IMG, f"{i}.png")).convert("RGB").resize((640, 640))
    b = io.BytesIO(); im.save(b, "JPEG", quality=88)
    traits = {k: man[i][k] for k in KEYS if man[i].get(k) not in (None, "None")}
    body = {"contents": [{"parts": [REF, {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(b.getvalue()).decode()}},
                                    {"text": Q % json.dumps(traits)}]}],
            "generationConfig": {"responseMimeType": "application/json"}}
    r = bg._req(bg.API + f"/v1beta/models/{MODEL}:generateContent", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    res = json.loads(r["candidates"][0]["content"]["parts"][-1]["text"])
    return res[-1] if isinstance(res, list) else res


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
    v.get(f) for f in ("extra_or_floating_limbs", "loose_weapon", "missing_listed_item", "unlisted_extra_weapon", "text_or_logo", "clipping", "wrong_character"))}
print(len(done), "checked;", len(bad), "flagged")
