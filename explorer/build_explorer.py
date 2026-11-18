#!/usr/bin/env python3
"""Build the Claysons trait explorer.

usage: python3 build_explorer.py <traits.csv> <images.zip|dir> <out_dir>

Writes out_dir/index.html (data embedded) plus sprite sheets
out_dir/s/<k>.jpg (140px, 10x10) and out_dir/l/<k>.jpg (280px, for the
piece view). Sheet k holds tokens k*100+1 .. k*100+100.
Rerun with the new CSV and zip when traits change (e.g. the Body trait).
"""
import csv, io, json, os, sys, zipfile
from collections import Counter
from PIL import Image

csv_path, img_src, out = sys.argv[1:4]
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html")

# keep_default_na off: read raw strings, so "None" stays a real trait
rows = list(csv.DictReader(open(csv_path, newline="", encoding="utf-8")))
cats = [c[len("attributes["):-1] for c in rows[0] if c.startswith("attributes[")]
rows.sort(key=lambda r: int(r["tokenID"]))
ids = [int(r["tokenID"]) for r in rows]
supply = len(rows)
assert ids == list(range(1, supply + 1)), "token ids must be 1..N"

values, index = [], {}
for c in cats:
    cnt = Counter(r[f"attributes[{c}]"] for r in rows)
    vals = sorted(cnt, key=lambda v: (-cnt[v], v))
    values.append([[v, cnt[v]] for v in vals])
    index[c] = {v: i for i, v in enumerate(vals)}
    assert sum(cnt.values()) == supply
tokens = [[index[c][r[f"attributes[{c}]"]] for c in cats] for r in rows]

# images
def opener():
    if os.path.isdir(img_src):
        return lambda n: open(os.path.join(img_src, n), "rb").read()
    z = zipfile.ZipFile(img_src)
    names = {os.path.basename(n): n for n in z.namelist()}
    return lambda n: z.read(names[n])
read = opener()
for sub, px, q in (("s", 140, 72), ("l", 280, 74)):
    os.makedirs(os.path.join(out, sub), exist_ok=True)
    for k in range((supply + 99) // 100):
        sheet = Image.new("RGB", (px * 10, px * 10), (20, 16, 18))
        for j in range(100):
            t = k * 100 + j + 1
            if t > supply:
                break
            im = Image.open(io.BytesIO(read(f"{t}.jpg"))).convert("RGB")
            im = im.resize((px, px), Image.LANCZOS)
            sheet.paste(im, ((j % 10) * px, (j // 10) * px))
        sheet.save(os.path.join(out, sub, f"{k}.jpg"), quality=q, optimize=True, progressive=True)

data = {
    "csv": os.path.basename(csv_path),
    "supply": supply,
    "cats": cats,
    "vals": values,
    "tok": tokens,
}
html = open(TEMPLATE, encoding="utf-8").read().replace(
    "__DATA__", json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/"))
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(html)
print(f"{supply} tokens, {len(cats)} categories, {sum(len(v) for v in values)} traits -> {out}")
