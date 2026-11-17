"""Trait spreadsheet from the OpenSea CSV: Tokens sheet + Trait Summary (count, share, tier split per value), rarest first."""
import csv, os, sys
from collections import Counter, defaultdict
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIERS = ["Common", "Uncommon", "Rare", "Epic", "Legendary 1/1"]
rows = list(csv.DictReader(open(os.path.join(ROOT, "output", "opensea", "metadata.csv"))))
traits = [k[11:-1] for k in rows[0] if k.startswith("attributes[")]
out = sys.argv[1]
wb = Workbook()
hdr = Font(bold=True, color="FFFFFF"); fill = PatternFill("solid", fgColor="3A2A2A")

ws = wb.active; ws.title = "Trait Summary"
ws.append(["Trait", "Value", "Count", "Share", "Rarity Tier"] + TIERS)
summary = []
for t in traits:
    c = Counter(); tc = defaultdict(Counter)
    for r in rows:
        v = r[f"attributes[{t}]"] or "None"
        c[v] += 1; tc[v][r["attributes[Tier]"]] += 1
    for v, n in sorted(c.items(), key=lambda x: (x[1], x[0])):
        low = next((x for x in TIERS if tc[v][x]), "")   # the most common tier this value appears in = its rarity floor
        ws.append([t, v, n, n / len(rows), "1/1 only" if low == "Legendary 1/1" else (low + (" and up" if low != "Legendary 1/1" and sum(1 for x in TIERS if tc[v][x]) > 1 else " only"))] + [tc[v][x] or None for x in TIERS])
        if v != "None": summary.append((n, t, v))
for c in ws[1]: c.font, c.fill = hdr, fill
for r in ws.iter_rows(min_row=2, min_col=4, max_col=4):
    r[0].number_format = "0.0%"
for i, w in enumerate([14, 40, 8, 8, 18, 10, 10, 10, 8, 13], 1): ws.column_dimensions[get_column_letter(i)].width = w
ws.freeze_panes = "C2"; ws.auto_filter.ref = ws.dimensions

ws0 = wb.create_sheet("Overview", 0)
ws0.append(["Trait", "Distinct values", "Tokens with it (not None)"])
for t in traits:
    vals = Counter(r[f"attributes[{t}]"] or "None" for r in rows)
    ws0.append([t, sum(1 for v in vals if v != "None"), sum(n for v, n in vals.items() if v != "None")])
ws0.append([]); ws0.append(["Tier", "Tokens"])
for x in TIERS: ws0.append([x, sum(1 for r in rows if r["attributes[Tier]"] == x)])
for c in ws0[1]: c.font, c.fill = hdr, fill
for i, w in enumerate([18, 16, 24], 1): ws0.column_dimensions[get_column_letter(i)].width = w

ws2 = wb.create_sheet("Tokens")
ws2.append(["Token", "Name"] + traits)
for r in rows: ws2.append([int(r["tokenID"]), r["name"]] + [r[f"attributes[{t}]"] for t in traits])
for c in ws2[1]: c.font, c.fill = hdr, fill
ws2.freeze_panes = "C2"; ws2.auto_filter.ref = ws2.dimensions
for i in range(1, len(traits) + 3): ws2.column_dimensions[get_column_letter(i)].width = 18
wb.save(out)
n_vals = sum(1 for _ in summary)
print(len(traits), "traits;", n_vals, "values (excluding None)")
