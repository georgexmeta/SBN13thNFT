"""Snapshot holder wallets of the WL communities on Robinhood Chain via Blockscout, merged and deduped.

    python3 tools/holders.py        -> output/wl/holders.csv (one address per line) and a per-collection count
Needs robinhoodchain.blockscout.com reachable.
"""
import json, os, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://robinhoodchain.blockscout.com/api/v2"
COLLECTIONS = {
    "Clay Stonks": "0xde0acefc89d4cf5f4ce45a4fb8a51aa355091b44",
    "CCFF00": "0x505a22ffed8d37ebe580ffd98d2cdb0021189146",
    "SKNOTS": "0x496f1e53ef6c1af48341b9d0a03249108cf26543",
    "Hood Vandalz": "0x05780625aec3b8dd36f1260c05d6d43d8040feab",
}
BURN = {"0x0000000000000000000000000000000000000000", "0x000000000000000000000000000000000000dead"}


def get(url):
    for attempt in range(5):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json"}), timeout=60))
        except Exception:
            time.sleep(3 * (attempt + 1))
    raise RuntimeError("failed: " + url)


def holders(addr):
    out, params = set(), None
    while True:
        url = f"{API}/tokens/{addr}/holders" + ("?" + urllib.parse.urlencode(params) if params else "")
        page = get(url)
        for item in page.get("items", []):
            a = item["address"]["hash"].lower()
            if a not in BURN and int(item.get("value", "1") or 1) > 0:
                out.add(a)
        params = page.get("next_page_params")
        if not params:
            return out


def main():
    os.makedirs(os.path.join(ROOT, "output", "wl"), exist_ok=True)
    every = set()
    for name, addr in COLLECTIONS.items():
        h = holders(addr); every |= h
        print(f"{name}: {len(h)} holders", flush=True)
    with open(os.path.join(ROOT, "output", "wl", "holders.csv"), "w") as f:
        f.write("address\n" + "\n".join(sorted(every)) + "\n")
    print(f"merged unique wallets: {len(every)}")


if __name__ == "__main__":
    main()
