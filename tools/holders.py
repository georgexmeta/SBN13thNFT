"""Snapshot holder wallets of the WL communities on Robinhood Chain, merged and deduped.

    python3 tools/holders.py        -> output/wl/holders.csv, plus a per-collection count
Reads ownership straight from the chain over JSON-RPC (ownerOf for every token id), so it needs
rpc.mainnet.chain.robinhood.com reachable. The Blockscout API sits behind a bot check and can't be used.
"""
import json, os, sys, time, urllib.request
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RPC = os.environ.get("RPC", "https://rpc.mainnet.chain.robinhood.com")
COLLECTIONS = {
    "Clay Stonks": "0xde0acefc89d4cf5f4ce45a4fb8a51aa355091b44",
    "CCFF00": "0x505a22ffed8d37ebe580ffd98d2cdb0021189146",
    "SKNOTS": "0x496f1e53ef6c1af48341b9d0a03249108cf26543",
    "Hood Vandalz": "0x05780625aec3b8dd36f1260c05d6d43d8040feab",
    "Pixelhood Minis": "0x8215824669c453136cabe59a079c32aca2f87cd5",
}
BURN = {"0x0000000000000000000000000000000000000000", "0x000000000000000000000000000000000000dead"}
TOTAL_SUPPLY, OWNER_OF = "0x18160ddd", "0x6352211e"


def rpc(batch):
    req = urllib.request.Request(RPC, data=json.dumps(batch).encode(), headers={"Content-Type": "application/json", "User-Agent": "sbn13th-snapshot/1.0"})
    for attempt in range(10):
        try:
            return json.load(urllib.request.urlopen(req, timeout=60))
        except Exception as e:
            err = e; time.sleep(10 * (attempt + 1))   # public RPC rate-limits; back off
    raise RuntimeError(f"RPC failed: {err}")


def call(to, data, i=1):
    return {"jsonrpc": "2.0", "id": i, "method": "eth_call", "params": [{"to": to, "data": data}, "latest"]}


def holders(addr):
    supply = int(rpc([call(addr, TOTAL_SUPPLY)])[0]["result"], 16)
    owners, misses, tid = Counter(), 0, 0
    # ids usually run 0..supply or 1..supply; keep going until a long run of missing ids past the supply
    while tid <= supply or misses < 100:
        batch = [call(addr, OWNER_OF + format(t, "064x"), t) for t in range(tid, tid + 25)]
        time.sleep(0.4)
        for res in rpc(batch):
            r = res.get("result")
            if r and len(r) >= 66:
                owners["0x" + r[-40:].lower()] += 1; misses = 0
            else:
                misses += 1
        tid += 25
        if tid > supply * 3 + 1000:
            break
    for b in BURN:
        owners.pop(b, None)
    return supply, owners


def main():
    os.makedirs(os.path.join(ROOT, "output", "wl"), exist_ok=True)
    MIN = int(os.environ.get("MIN_HELD", "3"))   # a wallet qualifies with MIN+ NFTs from any ONE collection
    every, counts = set(), {}
    for name, addr in COLLECTIONS.items():
        supply, h = holders(addr); counts[name] = dict(h)
        ok = {a for a, n in h.items() if n >= MIN}; every |= ok
        print(f"{name}: supply {supply}, {len(h)} holders, {len(ok)} hold {MIN}+", flush=True)
    json.dump(counts, open(os.path.join(ROOT, "output", "wl", "counts.json"), "w"))
    with open(os.path.join(ROOT, "output", "wl", "holders.csv"), "w") as f:
        f.write("address\n" + "\n".join(sorted(every)) + "\n")
    print(f"merged unique wallets: {len(every)}")


if __name__ == "__main__":
    main()
