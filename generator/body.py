"""Flag renders whose BODY isn't turned toward the viewer's right (the head check alone misses these).

    python3 generator/body.py output/ai/images-v2   -> prints "<id> {"body": ...}" and writes output/ai/body.json
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anatomy  # noqa: E402

anatomy.Q = ("Look at this clay figure's BODY (torso, shoulders and chest), ignoring the head. From the viewer's point of view, which way "
             "is the body turned? Reply with JSON only: {\"body\": \"RIGHT\" | \"LEFT\" | \"FRONT\" | \"BACK\"} where RIGHT means the "
             "chest is turned toward the right side of the image.")

if __name__ == "__main__":
    d, out = sys.argv[1], {}
    for f in sorted(os.listdir(d), key=lambda f: int(f[:-4]) if f[:-4].isdigit() else 0):
        if f.endswith(".png") and f[:-4].isdigit():
            r = anatomy.check(os.path.join(d, f)); out[f[:-4]] = r
            print(f[:-4], json.dumps(r), flush=True)
    json.dump(out, open("output/ai/body.json", "w"), indent=1)
