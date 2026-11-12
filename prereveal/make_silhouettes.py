import sys, os, random
sys.path.insert(0, sys.argv[1])
import traits as T, generate as G
out = sys.argv[2]
def parts(attrs, seed):
    rng = random.Random(seed)
    skin = T.SKINS[attrs["Skin Tone"]]; hc = T.HAIR_COLORS[attrs["Hair Color"]]
    cb, cf = T.clothing(attrs["Clothing"], rng)
    sw = min(G.SWELL[attrs["Swelling"]], 34) if attrs["Hair"] == "Backwards Cap" else G.SWELL[attrs["Swelling"]]
    hb = T.hair_back(attrs["Hair"], hc, rng)
    body = T.neck(skin) + cb + cf
    head = (T.head(skin, rng, sw) + T.ear(skin, attrs["Ear"]) + T.nose(attrs["Nose"], skin)
            + T.mouth(attrs["Mouth"], skin, rng) + T.hair(attrs["Hair"], hc, rng))
    wrap = lambda inner: ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1080" height="1080">'
                          '<g transform="translate(0 -55)">' + inner + '</g></svg>')
    return wrap(body), wrap(f'<g transform="{G.HEAD_T}">' + hb + head + '</g>')
for i, a in enumerate(G.SAMPLES, 1):
    b, h = parts(a, 1300 + i)
    open(f"{out}/{i}_body.svg", "w").write(b); open(f"{out}/{i}_head.svg", "w").write(h)
