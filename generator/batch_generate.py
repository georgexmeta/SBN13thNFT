"""Render tokens through the Gemini Batch API (about half the price of live calls, results within hours).

    python3 generator/batch_generate.py submit 1-1300 [--chunk 200]   # every missing image, in batches
    python3 generator/batch_generate.py poll                          # save finished batches, re-roll bad facings
    python3 generator/batch_generate.py status

Same model, prompts, references and checks as gemini_generate.py. The reference photos are uploaded once to the
Files API and referenced by URI, so each request line is small. Finished images go through the same head/body
facing check; a failure is re-submitted with a new seed (up to 2 times), then kept and flagged "needs review".
State lives in output/ai/batches.json.
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gemini_generate as g   # noqa: E402

API = "https://generativelanguage.googleapis.com"
STATE = os.path.join(g.ROOT, "output", "ai", "batches.json")
KEY = os.environ.get("GEMINI_API_KEY")
REFS = [os.path.join(g.ROOT, "refs", "master-reference.jpg"), os.path.join(g.ROOT, "refs", "goal-pig.jpg")]


def _req(url, data=None, headers=None, method=None, raw=False):
    h = dict(headers or {})
    if KEY:
        h["x-goog-api-key"] = KEY
    for attempt in range(6):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h, method=method), timeout=600)
            return r if raw else json.load(r)
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:800]
            if e.code in (429, 500, 503) and attempt < 5:
                time.sleep(15 * 2 ** attempt); continue
            raise RuntimeError(f"HTTP {e.code}: {msg}")
        except urllib.error.URLError:
            if attempt < 5:
                time.sleep(30); continue
            raise


def upload(path, mime, name):
    size = os.path.getsize(path)
    start = _req(f"{API}/upload/v1beta/files", data=json.dumps({"file": {"display_name": name}}).encode(), raw=True,
                 headers={"X-Goog-Upload-Protocol": "resumable", "X-Goog-Upload-Command": "start",
                          "X-Goog-Upload-Header-Content-Length": str(size), "X-Goog-Upload-Header-Content-Type": mime,
                          "Content-Type": "application/json"})
    url = start.headers["x-goog-upload-url"]
    res = _req(url, data=open(path, "rb").read(), headers={"Content-Length": str(size), "X-Goog-Upload-Offset": "0",
                                                           "X-Goog-Upload-Command": "upload, finalize"})
    return res["file"]


def load():
    return json.load(open(STATE)) if os.path.exists(STATE) else {"refs": {}, "batches": [], "tries": {}}


def save(st):
    """Merge with what is on disk first, so a long poll never wipes batches or drops added meanwhile by another process."""
    if os.path.exists(STATE):
        disk = json.load(open(STATE))
        mine = {b["name"]: b for b in st["batches"]}
        for b in disk["batches"]:
            if b["name"] not in mine:
                st["batches"].append(b)
            else:
                m = mine[b["name"]]
                m["drop"] = sorted(set(m.get("drop", [])) | set(b.get("drop", [])))
                if b["state"] != "running":
                    m["state"] = b["state"]
        for k, v in disk.get("refs", {}).items():
            st["refs"].setdefault(k, v)
    tmp = STATE + ".tmp"
    json.dump(st, open(tmp, "w"), indent=1)
    os.replace(tmp, STATE)


def ref_parts(st, row):
    refs = list(REFS)
    if str(row["attributes"].get("Mask", "")).startswith(("Hockey", "Bloody", "Chrome")) and os.path.exists(g.MASK_REF):
        refs.append(g.MASK_REF)
    parts = []
    for r in refs:
        f = st["refs"].get(r)
        if not f or f["expires"] < time.time() + 6 * 3600:   # Files API keeps uploads 48 h
            up = upload(r, "image/png" if r.endswith(".png") else "image/jpeg", os.path.basename(r))
            f = st["refs"][r] = {"uri": up["uri"], "mime": up["mimeType"], "expires": time.time() + 46 * 3600}
            save(st)
        parts.append({"file_data": {"mime_type": f["mime"], "file_uri": f["uri"]}})
    return parts


def submit(id_list, chunk=200, st=None, force=False):
    st = st or load()
    rows = {r["id"]: r for r in json.load(open(g.MANIFEST))}
    pending = {i for b in st["batches"] if b["state"] == "running" for i in b["ids"]}
    todo = [i for i in id_list if not os.path.exists(os.path.join(g.OUTDIR, f"{i}.png")) and (force or i not in pending)]
    for n in range(0, len(todo), chunk):
        part = todo[n:n + chunk]
        path = os.path.join(g.ROOT, "output", "ai", f"batch-{int(time.time())}-{n}.jsonl")
        with open(path, "w") as f:
            for i in part:
                row = rows[i]
                seed = row["seed"] + g.SEED_BUMP.get(str(i), 0) + 7 * st["tries"].get(str(i), 0)
                body = {"contents": [{"parts": ref_parts(st, row) + [{"text": g.LEAD + row["prompt"] + " Avoid: " + row["negative"]}]}],
                        "generationConfig": {"responseModalities": ["IMAGE"], "seed": seed, "imageConfig": {"aspectRatio": "1:1"}}}
                f.write(json.dumps({"key": str(i), "request": body}) + "\n")
        up = upload(path, "application/jsonl", os.path.basename(path))
        op = _req(f"{API}/v1beta/models/{g.MODEL}:batchGenerateContent", headers={"Content-Type": "application/json"},
                  data=json.dumps({"batch": {"display_name": os.path.basename(path), "input_config": {"file_name": up["name"]}}}).encode())
        st["batches"].append({"name": op["name"], "ids": part, "state": "running", "submitted": time.time()})
        save(st)
        print(f"submitted {op['name']} with {len(part)} tokens", flush=True)
    return st


def edit(id_list, instruction, st=None):
    """Fix finished images in place: send the image itself with an edit instruction (keeps the art, changes one detail)."""
    st = st or load()
    path = os.path.join(g.ROOT, "output", "ai", f"edit-{int(time.time())}.jsonl")
    with open(path, "w") as f:
        for i in id_list:
            img = base64.b64encode(open(os.path.join(g.OUTDIR, f"{i}.png"), "rb").read()).decode()
            body = {"contents": [{"parts": [{"inline_data": {"mime_type": "image/png", "data": img}}, {"text": instruction}]}],
                    "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "1:1"}}}
            f.write(json.dumps({"key": str(i), "request": body}) + "\n")
    up = upload(path, "application/jsonl", os.path.basename(path))
    op = _req(f"{API}/v1beta/models/{g.MODEL}:batchGenerateContent", headers={"Content-Type": "application/json"},
              data=json.dumps({"batch": {"display_name": os.path.basename(path), "input_config": {"file_name": up["name"]}}}).encode())
    st["batches"].append({"name": op["name"], "ids": list(id_list), "state": "running", "submitted": time.time(), "edit": True})
    save(st)
    print(f"submitted edit {op['name']} with {len(id_list)} tokens", flush=True)
    return st


def _find(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            r = _find(v, key)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = _find(v, key)
            if r is not None:
                return r
    return None


def poll():
    st = load()
    retry = []
    for b in st["batches"]:
        if b["state"] != "running":
            continue
        info = _req(f"{API}/v1beta/{b['name']}")
        state = _find(info, "state") or ""
        if not info.get("done") and "SUCCEEDED" not in state and "FAILED" not in state and "CANCELLED" not in state and "EXPIRED" not in state:
            print(f"{b['name']}: {state or 'running'}", flush=True)
            continue
        if "SUCCEEDED" not in state and not _find(info, "responsesFile"):
            print(f"{b['name']}: ended {state} {json.dumps(info)[:300]}", flush=True)
            b["state"] = "failed"; retry += b["ids"]; save(st); continue
        fname = _find(info, "responsesFile")
        lines = _req(f"{API}/download/v1beta/{fname}:download?alt=media", raw=True).read().decode().splitlines()
        got = set()
        for line in lines:
            item = json.loads(line)
            i = int(item.get("key") or _find(item, "key"))
            img = None
            for c in (item.get("response") or {}).get("candidates", []):
                for p in c.get("content", {}).get("parts", []):
                    d = p.get("inline_data") or p.get("inlineData")
                    if d:
                        img = base64.b64decode(d["data"])
            if i in b.get("drop", []):   # superseded by a newer request for the same token
                got.add(i); print(f"#{i} superseded, dropped", flush=True); continue
            if i in st.get("redo", []) and b["submitted"] < st.get("redo_since", 0):   # traits changed after this request was sent: render again with the new prompt
                st["redo"].remove(i); retry.append(i); print(f"#{i} prompt changed, re-rendering", flush=True); continue
            if img is None:
                print(f"#{i} no image: {json.dumps(item)[:200]}", flush=True); retry.append(i); continue
            got.add(i)
            out = os.path.join(g.OUTDIR, f"{i}.png"); tmp = out + ".check.png"
            open(tmp, "wb").write(img)
            way = g.facing(tmp)
            if way == "RIGHT":
                bd = g._check(tmp).get("body", "RIGHT")
                way = "RIGHT" if bd == "RIGHT" else f"body {bd}"
            tries = st["tries"].get(str(i), 0)
            if way == "RIGHT" or tries >= 2:
                os.replace(tmp, out); print(f"#{i} ok" + ("" if way == "RIGHT" else f" (facing {way}, needs review)"), flush=True)
            else:
                st["tries"][str(i)] = tries + 1; os.remove(tmp); retry.append(i)
                print(f"  #{i} faces {way}, re-rolling", flush=True)
        retry += [i for i in b["ids"] if i not in got and i not in retry]
        if b["submitted"] < st.get("redo_since", 0):
            st["redo"] = [i for i in st.get("redo", []) if i not in b["ids"]]
        b["state"] = "done"; save(st)
    if retry:
        submit(sorted(set(retry)), st=st)
    return st


def status():
    st = load()
    for b in st["batches"]:
        print(b["name"], b["state"], len(b["ids"]), time.strftime("%H:%M", time.gmtime(b["submitted"])))
    print("images:", len([f for f in os.listdir(g.OUTDIR) if f.endswith(".png") and "check" not in f]))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "submit":
        a = sys.argv[2:]
        chunk = int(a[a.index("--chunk") + 1]) if "--chunk" in a else 200
        submit(g.ids(a[0]), chunk)
    elif cmd == "poll":
        poll()
    else:
        status()
