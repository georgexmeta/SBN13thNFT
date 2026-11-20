#!/usr/bin/env python3
"""Build the post-reveal per-token data for claysons.xyz/clayson/N.

Run ONLY after the reveal is live (the art must not be public before then):

  python3 site/tools/build_art.py <claysons-traits.csv> <png dir or zip> [<zip> ...]

Writes site/data/tokens.json (name, tier, traits per token) and site/art/<N>.png
(full-size art, copied byte for byte). Both folders are git-ignored; deploy them
with the rest of site/.
"""
import csv, json, os, shutil, sys, zipfile

here = os.path.dirname(os.path.abspath(__file__))
site = os.path.dirname(here)
csv_path, sources = sys.argv[1], sys.argv[2:]
if not sources:
    sys.exit(__doc__)

tokens = {}
for row in csv.DictReader(open(csv_path, newline='', encoding='utf-8')):
    tid = int(row['tokenID'])
    traits = []
    for k, v in row.items():
        if k.startswith('attributes[') and v and k != 'attributes[Tier]':
            traits.append([k[11:-1], v])
    tokens[tid] = {'name': row['name'], 'tier': row.get('attributes[Tier]', ''), 'traits': traits}
assert len(tokens) == 1300, f'expected 1300 rows, got {len(tokens)}'

os.makedirs(os.path.join(site, 'data'), exist_ok=True)
art = os.path.join(site, 'art'); os.makedirs(art, exist_ok=True)
json.dump(tokens, open(os.path.join(site, 'data', 'tokens.json'), 'w'), separators=(',', ':'))

found = set()
for src in sources:
    if zipfile.is_zipfile(src):
        with zipfile.ZipFile(src) as z:
            for n in z.namelist():
                b = os.path.basename(n)
                if b.endswith('.png') and b[:-4].isdigit():
                    with z.open(n) as f, open(os.path.join(art, b), 'wb') as o:
                        shutil.copyfileobj(f, o)
                    found.add(int(b[:-4]))
    else:
        for b in os.listdir(src):
            if b.endswith('.png') and b[:-4].isdigit():
                shutil.copyfile(os.path.join(src, b), os.path.join(art, b)); found.add(int(b[:-4]))
missing = sorted(set(tokens) - found)
print(f'tokens.json: {len(tokens)} tokens; art: {len(found)} PNGs' + (f'; MISSING {missing[:20]}' if missing else ''))
