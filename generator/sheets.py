"""Contact sheets of finished Claysons, the token number printed UNDER each picture, 8 per row, 48 per sheet.

    python3 generator/sheets.py <out_dir>
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "output", "ai", "images-v2")
CELL, BAR, GAP, COLS, PER = 300, 40, 18, 8, 48
try:
    FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
except OSError:
    FONT = ImageFont.load_default()

out = sys.argv[1]; os.makedirs(out, exist_ok=True)
rows = {r["id"]: r["attributes"] for r in json.load(open(os.path.join(ROOT, "output", "ai", "manifest-v2.json")))}
ids = sorted(int(f[:-4]) for f in os.listdir(SRC) if f.endswith(".png") and f[:-4].isdigit())
for n in range(0, len(ids), PER):
    part = ids[n:n + PER]
    nrows = (len(part) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * (CELL + GAP) + GAP, nrows * (CELL + BAR + GAP) + GAP), (24, 24, 24))
    d = ImageDraw.Draw(sheet)
    for k, i in enumerate(part):
        x = GAP + (k % COLS) * (CELL + GAP); y = GAP + (k // COLS) * (CELL + BAR + GAP)
        sheet.paste(Image.open(os.path.join(SRC, f"{i}.png")).convert("RGB").resize((CELL, CELL)), (x, y))
        d.rectangle([x, y + CELL, x + CELL, y + CELL + BAR], fill=(0, 0, 0))
        t = rows[i].get("1/1 Name") or rows[i]["Tier"]
        d.text((x + 8, y + CELL + 7), f"#{i}  {t}"[:24], fill="white", font=FONT)
    sheet.save(os.path.join(out, f"claysons-{part[0]}-{part[-1]}.jpg"), quality=82)
    print(part[0], part[-1])
