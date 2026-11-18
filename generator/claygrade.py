"""Free local 'refined clay' colour grade (George 2026-11-18): softer, warmer, matte, unified palette.
python3 generator/claygrade.py in.png out.png"""
import sys
import numpy as np
from PIL import Image, ImageFilter

def grade(im, sat=0.86, warm=0.035, lift=0.035, contrast=0.93, grain=0.012, seed=0):
    im = im.convert("RGB")
    a = np.asarray(im).astype(np.float32) / 255.0
    lum = (a * [0.299, 0.587, 0.114]).sum(2, keepdims=True)
    a = lum + (a - lum) * sat                       # gentle desaturation, keeps hue
    a = (a - 0.5) * contrast + 0.5                  # soften contrast (matte)
    a = lift + a * (1 - lift)                       # lift blacks a touch
    a[..., 0] *= 1 + warm; a[..., 1] *= 1 + warm * 0.35; a[..., 2] *= 1 - warm   # warm clay cast
    # tame hot highlights / neon so the palette reads as plasticine, not paint
    hi = np.clip((a.max(2, keepdims=True) - 0.82) / 0.18, 0, 1)
    a = a * (1 - 0.25 * hi) + lum * 0.25 * hi
    rng = np.random.default_rng(seed)
    g = rng.normal(0, grain, a.shape[:2])[..., None]
    a = np.clip(a + g, 0, 1)
    out = Image.fromarray((a * 255 + 0.5).astype(np.uint8))
    return out.filter(ImageFilter.UnsharpMask(radius=1.2, percent=35, threshold=3))   # crisp sculpt edges

if __name__ == "__main__":
    grade(Image.open(sys.argv[1])).save(sys.argv[2])
