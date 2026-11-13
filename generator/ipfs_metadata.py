"""Build IPFS-ready OpenSea metadata for the 1,300 v2 tokens.

    python3 generator/ipfs_metadata.py <IMAGES_CID> [royalty_wallet] [royalty_bps]

Step 1: upload output/ai/images-v2 (1.png ... 1300.png) to Pinata as one folder and copy its CID.
Step 2: run this script with that CID. It writes output/ipfs/metadata/<id>.json and output/ipfs/collection.json.
Step 3: upload output/ipfs/metadata as a second folder. Its CID gives the contract baseURI: ipfs://<CID>/
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = os.environ.get("COLLECTION_NAME", "SBN13th")
DESC = os.environ.get("COLLECTION_DESC", "1,300 hand-sculpted-look claymation slashers. 1,157 Standard, 130 Rare and 13 Legendary 1/1s.")


def main():
    cid, wallet, bps = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else ""), int(sys.argv[3]) if len(sys.argv) > 3 else 500
    out = os.path.join(ROOT, "output", "ipfs", "metadata"); os.makedirs(out, exist_ok=True)
    rows = json.load(open(os.path.join(ROOT, "output", "ai", "manifest-v2.json")))
    missing = [r["id"] for r in rows if not os.path.exists(os.path.join(ROOT, "output", "ai", "images-v2", f"{r['id']}.png"))]
    if missing:
        sys.exit(f"{len(missing)} images missing, e.g. {missing[:10]}")
    for r in rows:
        meta = {"name": r["name"], "description": DESC, "image": f"ipfs://{cid}/{r['id']}.png",
                "attributes": [{"trait_type": k, "value": v} for k, v in r["attributes"].items()]}
        json.dump(meta, open(os.path.join(out, f"{r['id']}.json"), "w"), indent=1)
    coll = {"name": NAME, "description": DESC, "image": f"ipfs://{cid}/1.png",
            "seller_fee_basis_points": bps, "fee_recipient": wallet}
    json.dump(coll, open(os.path.join(ROOT, "output", "ipfs", "collection.json"), "w"), indent=1)
    print(f"wrote {len(rows)} metadata files to {out}")


if __name__ == "__main__":
    main()
