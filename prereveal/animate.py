"""Render the SBN13th pre-reveal loop: a backlit grotesque head silhouette on camcorder footage.

Usage: python3 animate.py <silhouette_dir> <out_dir> [--preview]
Reads <i>_body.png / <i>_head.png alpha masks (rendered from the trait generator),
writes frames straight into ffmpeg -> prereveal.mp4 (+ audio).
"""
import math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

SIL, OUT = sys.argv[1], sys.argv[2]
PREVIEW = "--preview" in sys.argv
W = H = 1080
FPS = 24
DUR = 12.0
N = int(FPS * DUR)
HERO, VARIANTS = 1, [3, 4, 5, 2]
PIVOT = (585, 790)          # neck pivot in mask coords
SCALE, OX, OY = 0.9, 25, 125  # global placement of the figure

FONT = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf"
f_big = ImageFont.truetype(FONT, 54)


def fill_holes(a):
    """Solidify a mask: anything not reachable from the border is inside."""
    b = a.point(lambda v: 255 if v > 100 else 0).convert("L")
    pad = Image.new("L", (b.width + 2, b.height + 2), 0); pad.paste(b, (1, 1))
    ImageDraw.floodfill(pad, (0, 0), 128)
    inside = pad.crop((1, 1, b.width + 1, b.height + 1)).point(lambda v: 0 if v == 128 else 255)
    return ImageChops.lighter(a, inside)


def load(i):
    b = Image.open(f"{SIL}/{i}_body.png").split()[3]
    h = Image.open(f"{SIL}/{i}_head.png").split()[3]
    # the upper neck turns with the head; filling holes closes the slot between ear and neck
    neck_top = Image.new("L", b.size, 0)
    neck_top.paste(b.crop((0, 0, b.width, PIVOT[1] - 10)), (0, 0))
    return fill_holes(b), fill_holes(ImageChops.lighter(h, neck_top))


MASKS = {i: load(i) for i in [HERO] + VARIANTS}


def ease(x):
    return 0.5 - 0.5 * math.cos(math.pi * min(max(x, 0), 1))


def head_angle(t):
    """Degrees, positive = chin down (clockwise). Periodic over DUR."""
    bowed = 15.0
    if t < 2.5:
        a = bowed + 1.2 * math.sin(t * 2.1)
    elif t < 6.0:
        a = bowed * (1 - ease((t - 2.5) / 3.5))
    elif t < 8.0:
        a = 0.6 * math.sin((t - 6) * 3)
    elif t < 8.6:  # the twitch
        x = (t - 8.0) / 0.6
        a = -9 * math.sin(math.pi * x) + 3 * math.sin(x * 40) * (1 - x)
    elif t < 9.4:
        a = 0
    else:
        a = bowed * ease((t - 9.4) / 2.6) + 1.2 * math.sin(t * 2.1) * ease((t - 9.4) / 2.6)
    return a


# glitch windows (start, end, strength, variant-or-None)
GLITCHES = [(1.40, 1.62, 0.7, None), (3.9, 4.35, 1.0, 3), (5.3, 5.45, 0.5, None),
            (8.05, 8.25, 0.8, None), (9.9, 10.3, 1.0, 4), (11.2, 11.32, 0.6, 5)]


def glitch_at(t):
    for g in GLITCHES:
        if g[0] <= t < g[1]:
            return g
    return None


def figure_mask(t, idx):
    body, head = MASKS[idx]
    ang = head_angle(t)
    head_r = head.rotate(-ang, resample=Image.BICUBIC, center=PIVOT)
    m = ImageChops.lighter(body, head_r)
    # close the small notch where the ear lobe meets the neck
    box = (370, 500, 580, 700)
    m.paste(m.crop(box).filter(ImageFilter.MaxFilter(21)).filter(ImageFilter.MinFilter(21)), box[:2])
    # breathing + sway, then global placement
    breath = 1 + 0.008 * math.sin(2 * math.pi * t / 3.0)
    sway = 6 * math.sin(2 * math.pi * t / DUR)
    s = SCALE * breath
    # inverse affine: src = (dst - offset) / s
    ox, oy = OX + sway + (1 - breath) * 540 * SCALE, OY + (1 - breath) * 1000 * SCALE
    m = m.transform((W, H), Image.AFFINE, (1 / s, 0, -ox / s, 0, 1 / s, -oy / s), resample=Image.BICUBIC)
    return np.asarray(m, dtype=np.float32) / 255.0


yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
GLOW = np.exp(-(((xx - 545) / 430) ** 2 + ((yy - 520) / 470) ** 2))
VIGN = 1 - 0.55 * (((xx - W / 2) / (W * 0.72)) ** 2 + ((yy - H / 2) / (H * 0.72)) ** 2)
VIGN = np.clip(VIGN, 0, 1)[..., None]
SCAN = np.where((np.arange(H) % 3) == 0, 0.78, 1.0).astype(np.float32)[:, None, None]
DITHER = (((xx.astype(int) // 2) + (yy.astype(int) // 2)) % 2).astype(np.float32)
GREEN = np.array([0.18, 0.95, 0.42], np.float32)
RIM = np.array([0.80, 1.00, 0.86], np.float32)
DARK = np.array([0.012, 0.016, 0.030], np.float32)
BG = np.array([0.020, 0.060, 0.035], np.float32)


def blur(a, r):
    im = Image.fromarray((a * 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), dtype=np.float32) / 255.0


def streaks(rng, amount):
    small = rng.random((H, W // 60)).astype(np.float32)
    small = np.where(small > 0.86, small, 0) * amount
    im = Image.fromarray((small * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    return np.asarray(im, dtype=np.float32) / 255.0


def frame(n):
    t = n / FPS
    rng = np.random.default_rng(1300 + n)
    g = glitch_at(t)
    idx = g[3] if (g and g[3] and (n % 3 != 0)) else HERO
    M = figure_mask(t, idx)

    flick = 0.88 + 0.08 * math.sin(t * 17.3) * math.sin(t * 5.1) + 0.04 * rng.random()
    halo = blur(M, 26) * (1 - M)
    tight = blur(M, 5) * (1 - M)
    inner = M * (1 - blur(M, 3)) * 2.2

    img = BG + GREEN * (0.5 * GLOW * flick)[..., None]
    img = img + GREEN * (0.7 * halo * flick)[..., None] + RIM * (0.75 * tight * flick)[..., None]
    st = streaks(rng, 1.0)
    img = img + np.array([0.35, 0.55, 0.42], np.float32) * (st * (0.5 + 0.5 * GLOW))[..., None] * 0.6
    # silhouette on top
    img = img * (1 - M[..., None]) + DARK * M[..., None]
    img = img + RIM * (np.clip(inner, 0, 1) * 0.55 * flick)[..., None]
    img = img + np.array([0.12, 0.14, 0.2], np.float32) * (st * M * 0.25)[..., None]

    # glitch: bright green band, dithered silhouette, tearing
    if g:
        strength = g[2]
        rb = np.random.default_rng(int(g[0] * 100) + n // 2)
        y0 = int(rb.uniform(0.05, 0.55) * H)
        y1 = min(H, y0 + int(rb.uniform(0.18, 0.4) * H))
        band = np.zeros(H, np.float32); band[y0:y1] = strength
        bandm = band[:, None]
        sil = M * (0.55 + 0.45 * DITHER)
        bright = GREEN * 0.95 + 0.05
        bandimg = bright * (1 - 0.85 * sil[..., None]) + rng.random((H, W, 1)).astype(np.float32) * 0.18
        img = img * (1 - bandm[..., None]) + bandimg * bandm[..., None]
        # horizontal tearing
        rows = rng.integers(0, H, 6)
        for r in rows:
            h = rng.integers(8, 60)
            img[r:r + h] = np.roll(img[r:r + h], int(rng.integers(-60, 60)), axis=1)
    else:
        # subtle constant wobble on a couple of lines
        r = int((t * 230) % H)
        img[r:r + 4] = np.roll(img[r:r + 4], 5, axis=1)

    # chroma offset
    img[..., 0] = np.roll(img[..., 0], 3, axis=1)
    img[..., 2] = np.roll(img[..., 2], -3, axis=1)
    img = img + rng.normal(0, 0.035, (H, W, 1)).astype(np.float32)
    img = img * VIGN

    # OSD
    pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(pil)
    if (n // 12) % 2 == 0:
        d.ellipse((58, 62, 100, 104), fill=(235, 30, 30))
    d.text((115, 52), "REC", font=f_big, fill=(235, 240, 235))
    secs = int(t); fr = n % FPS
    tc = f"00:00:{secs:02d}:{fr:02d}"
    d.text((W - 60, H - 60), tc, font=f_big, fill=(235, 240, 235), anchor="rs")
    out = np.asarray(pil, dtype=np.float32) / 255.0
    out = out * SCAN
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)


def audio(path):
    sr = 48000
    t = np.arange(int(sr * DUR)) / sr
    rng = np.random.default_rng(13)
    hum = 0.05 * np.sin(2 * np.pi * 60 * t) + 0.025 * np.sin(2 * np.pi * 120 * t) + 0.012 * np.sin(2 * np.pi * 180 * t)
    drone = 0.11 * np.sin(2 * np.pi * 41.2 * t + 0.6 * np.sin(2 * np.pi * t / DUR)) * (0.7 + 0.3 * np.sin(2 * np.pi * t / DUR))
    drone += 0.05 * np.sin(2 * np.pi * 61.7 * t)  # dissonant fifth-ish
    hiss = rng.normal(0, 1, (2, t.size))
    hiss = np.cumsum(hiss, axis=1); hiss -= np.convolve(hiss[0], np.ones(40) / 40, "same")[None]  # crude hp
    hiss = rng.normal(0, 0.02, (2, t.size))
    sig = np.stack([hum + drone, hum + drone]) + hiss
    for g0, g1, s, _ in GLITCHES:
        a, b = int(g0 * sr), int(g1 * sr)
        burst = rng.normal(0, 0.35 * s, (2, b - a)) * (rng.random(b - a) > 0.4)
        burst += 0.25 * s * np.sign(np.sin(2 * np.pi * 900 * t[a:b]))
        sig[:, a:b] += burst
    # heartbeat thumps
    for beat in np.arange(0.4, DUR, 1.5):
        for off in (0, 0.22):
            a = int((beat + off) * sr); L = int(0.18 * sr)
            if a + L < t.size:
                env = np.exp(-np.linspace(0, 8, L))
                sig[:, a:a + L] += 0.35 * env * np.sin(2 * np.pi * 52 * np.linspace(0, 0.18, L))
    # click-free loop edges
    fade = int(0.02 * sr)
    sig[:, :fade] *= np.linspace(0, 1, fade); sig[:, -fade:] *= np.linspace(1, 0, fade)
    sig = np.clip(sig / np.max(np.abs(sig)) * 0.6, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((sig.T * 32767).astype(np.int16).tobytes())


def main():
    os.makedirs(OUT, exist_ok=True)
    if PREVIEW:
        for n in [0, 50, 96, 130, 170, 200, 240, 280]:
            Image.fromarray(frame(n)).save(f"{OUT}/f{n:03d}.png")
        return
    wav = f"{OUT}/prereveal.wav"
    audio(wav)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                          "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart",
                          f"{OUT}/prereveal.mp4"], stdin=subprocess.PIPE)
    for n in range(N):
        p.stdin.write(frame(n).tobytes())
    p.stdin.close(); p.wait()


if __name__ == "__main__":
    main()
