"""Add a touch of blood splatter to the plain clay backdrops, on the backdrop only (never the figure). No API calls.

    python3 generator/splatter.py out_dir id [id ...]      # writes <out_dir>/<id>.png from output/ai/images-v2/<id>.png

The backdrop is found as the region connected to the image border whose colour is close to the border's median colour,
shrunk by a safety margin. Splats are drawn procedurally (blob + droplets + drips), lightly embossed so they read as
glossy clay, and seeded by token id so a re-run gives the same result.
"""
import os
import sys

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "output", "ai", "images-v2")


def backdrop_mask(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    h, w = lab.shape[:2]
    border = np.concatenate([lab[:8].reshape(-1, 3), lab[:, :8].reshape(-1, 3), lab[:, -8:].reshape(-1, 3)])
    ref = np.median(border, axis=0)
    dist = np.linalg.norm(lab - ref, axis=2)
    close = (cv2.GaussianBlur(dist, (0, 0), 3) < 22).astype(np.uint8)
    n, lbl = cv2.connectedComponents(close)
    edge = set(np.unique(np.concatenate([lbl[0], lbl[:, 0], lbl[:, -1]]))) - {0}
    m = np.isin(lbl, list(edge)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    return cv2.erode(m, np.ones((31, 31), np.uint8))   # stay well clear of the figure's outline


def splats(h, w, mask, rng):
    a = np.zeros((h, w), np.float32)
    room = cv2.distanceTransform(mask, cv2.DIST_L2, 5)   # only start a splat with open backdrop around it
    room[int(h * .7):] = 0
    ys, xs = np.nonzero(room > 80)
    if len(xs) < 500:
        return a
    for _ in range(rng.integers(1, 3)):
        k = rng.integers(len(xs)); cx, cy = int(xs[k]), int(ys[k])
        r = rng.uniform(28, 60)
        # irregular main blob: a wobbly polygon
        t = np.linspace(0, 2 * np.pi, 90, endpoint=False)
        wob = 1 + sum(rng.uniform(-.18, .18) * np.sin(f * t + rng.uniform(0, 6)) for f in (2, 3, 5, 7, 11))
        pts = np.stack([cx + np.cos(t) * r * wob, cy + np.sin(t) * r * wob * .85], 1).astype(np.int32)
        cv2.fillPoly(a, [pts], 1, cv2.LINE_AA)
        spray = rng.uniform(0, 2 * np.pi)   # direction the blood was flung
        for _ in range(rng.integers(5, 9)):   # thick arms reaching out of the blob
            ang = spray + rng.normal(0, .9); ln = r * rng.uniform(1.2, 2.2)
            x2, y2 = int(cx + np.cos(ang) * ln), int(cy + np.sin(ang) * ln)
            cv2.line(a, (cx, cy), (x2, y2), 1, max(3, int(r * rng.uniform(.12, .3))), cv2.LINE_AA)
            cv2.circle(a, (x2, y2), max(3, int(r * rng.uniform(.12, .22))), 1, -1, cv2.LINE_AA)
        for _ in range(rng.integers(18, 34)):   # flung droplets, smaller further out, stretched along the spray
            ang = spray + rng.normal(0, .8); d = r * rng.uniform(1.4, 4.5)
            rr = max(1.5, r * rng.uniform(.04, .18) / (d / r) ** .6)
            cv2.ellipse(a, (int(cx + np.cos(ang) * d), int(cy + np.sin(ang) * d)), (int(rr * 1.8), int(rr)), np.degrees(ang), 0, 360, 1, -1, cv2.LINE_AA)
        for _ in range(rng.integers(2, 5)):   # drips running down from the bottom of the blob
            x0 = int(cx + rng.uniform(-.8, .8) * r); y0 = int(cy + r * .5); ln = int(r * rng.uniform(1, 3.5)); wd = max(3, int(r * rng.uniform(.1, .2)))
            cv2.line(a, (x0, y0), (x0, y0 + ln), 1, wd, cv2.LINE_AA)
            cv2.circle(a, (x0, y0 + ln), int(wd * .8), 1, -1, cv2.LINE_AA)
    return cv2.GaussianBlur(a, (0, 0), 1.0)


def apply(path, out, seed):
    img = cv2.imread(path)
    h, w = img.shape[:2]
    mask = backdrop_mask(img)
    rng = np.random.default_rng(seed)
    a = splats(h, w, mask, rng) * cv2.GaussianBlur(mask.astype(np.float32), (0, 0), 4)
    if a.max() == 0:
        cv2.imwrite(out, img); return False
    # light emboss so the splat reads as glossy raised clay, lit from the upper left like the figures
    hgt = cv2.GaussianBlur(a, (0, 0), 3)
    gy, gx = np.gradient(hgt)
    shade = np.clip(-(gx + gy) * 6, -1, 1)
    base = np.array([18, 14, 120], np.float32) * (0.85 + 0.3 * rng.random())   # BGR deep blood red
    col = base[None, None, :] * (1 + 0.35 * shade[..., None]) + 90 * np.clip(shade, 0, 1)[..., None] ** 3
    tex = img.astype(np.float32).mean(axis=2, keepdims=True) / 255   # keep the clay texture showing through
    col = col * (0.75 + 0.5 * tex)
    alpha = (a * 0.9)[..., None]
    res = img.astype(np.float32) * (1 - alpha) + col * alpha
    cv2.imwrite(out, np.clip(res, 0, 255).astype(np.uint8))
    return True


if __name__ == "__main__":
    out_dir = sys.argv[1]; os.makedirs(out_dir, exist_ok=True)
    for i in sys.argv[2:]:
        print(i, apply(os.path.join(SRC, f"{i}.png"), os.path.join(out_dir, f"{i}.png"), int(i)))
