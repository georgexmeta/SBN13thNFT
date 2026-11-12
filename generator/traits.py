"""Trait layers for the grotesque PFP collection.

Every function returns an SVG fragment drawn on a 1000x1000 canvas.
The character is drawn in a three-quarter view, head turned ~45 degrees
to the viewer's right: the back of the skull and the near ear sit on the
left, the face features crowd toward the right contour.
"""
import math

OUT = "#111111"   # outline colour
SW = 8            # main stroke width


def shade(hex_color, f):
    """Darken (f<1) or lighten (f>1) a hex colour."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    if f < 1:
        r, g, b = (int(c * f) for c in (r, g, b))
    else:
        r, g, b = (int(c + (255 - c) * (f - 1)) for c in (r, g, b))
    return "#%02x%02x%02x" % (r, g, b)


# --------------------------------------------------------------------------
# Palettes
# --------------------------------------------------------------------------
BACKGROUNDS = {
    "Swamp Green": "#7fa36b",
    "Mustard": "#d9b44a",
    "Dusty Teal": "#5fa3a0",
    "Rust": "#c96b3c",
    "Bruise Purple": "#8a76a8",
    "Fog Grey": "#a9b0ad",
    "Bone": "#e3d6b4",
    "Blood Orange": "#e0603f",
}

SKINS = {
    "Pink Flesh": "#e9b49a",
    "Sallow": "#d8c08c",
    "Ruddy": "#d9917a",
    "Corpse Grey": "#b6b79a",
    "Leather": "#a8735a",
    "Pale Wax": "#efd7c3",
}

HAIR_COLORS = {
    "Ginger": "#c8622c",
    "Dirty Blonde": "#b89a55",
    "Greasy Black": "#2b2522",
    "Ash Grey": "#8d8a84",
    "Mud Brown": "#5e4430",
}


# --------------------------------------------------------------------------
# Background
# --------------------------------------------------------------------------
def background(color):
    return f'<rect width="1000" height="1000" fill="{color}"/>'


# --------------------------------------------------------------------------
# Body / clothing
# --------------------------------------------------------------------------
TORSO = ("M 120 1010 C 130 900 190 840 300 815 C 360 800 410 790 440 775 "
         "L 600 770 C 660 790 740 805 800 830 C 880 860 900 930 905 1010 Z")


def neck(skin):
    d = "M 410 620 C 420 700 410 760 390 815 L 625 815 C 610 760 610 720 620 660 Z"
    return (f'<path d="{d}" fill="{skin}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
            # neck shadow under jaw
            f'<path d="M 430 655 C 500 720 560 720 607 690 L 604 740 C 560 760 480 755 428 720 Z" fill="{shade(skin, 0.78)}"/>'
            f'<path d="M 470 760 C 500 775 540 776 570 765" fill="none" stroke="{OUT}" stroke-width="4" stroke-linecap="round"/>')


def _grime(rng, x0, x1, y0, y1, n, color, opacity=0.35):
    out = []
    for _ in range(n):
        cx, cy = rng.uniform(x0, x1), rng.uniform(y0, y1)
        rx, ry = rng.uniform(5, 20), rng.uniform(3, 11)
        rot = rng.uniform(0, 180)
        out.append(f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" '
                   f'transform="rotate({rot:.0f} {cx:.0f} {cy:.0f})" fill="{color}" opacity="{opacity}"/>')
    return "".join(out)


def clothing(kind, rng):
    clip = '<clipPath id="torso"><path d="' + TORSO + '"/></clipPath>'
    inner_tee = ('<path d="M 410 800 L 470 905 L 560 905 L 615 800 Z" fill="#2a2a2a" '
                 f'stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>')
    if kind == "Denim Shirt":
        base = "#4f6fa3"
        body = (f'<path d="{TORSO}" fill="{base}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<g clip-path="url(#torso)">'
                f'<path d="M 120 1010 C 130 900 190 840 300 815 L 330 1010 Z" fill="{shade(base, 0.75)}"/>'
                + _grime(rng, 150, 880, 840, 1000, 14, "#3b2a18")
                + '</g>' + inner_tee +
                # collar flaps
                f'<path d="M 410 790 L 330 820 L 395 900 L 470 905 Z" fill="{shade(base, 1.12)}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<path d="M 610 785 L 720 815 L 640 905 L 560 905 Z" fill="{shade(base, 1.12)}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                # placket + buttons + pocket
                f'<path d="M 515 905 L 525 1010" stroke="{OUT}" stroke-width="5"/>'
                f'<circle cx="535" cy="950" r="8" fill="#d8d0b8" stroke="{OUT}" stroke-width="4"/>'
                f'<path d="M 640 930 L 770 925 L 775 1010 M 640 930 L 642 1010 M 640 960 L 772 955" fill="none" stroke="{OUT}" stroke-width="5"/>'
                f'<path d="M 230 900 C 250 940 260 980 262 1010" fill="none" stroke="{shade(base, 1.35)}" stroke-width="3" stroke-dasharray="8 7"/>')
        return clip + body
    if kind == "Red Flannel" or kind == "Green Flannel":
        base = "#a8322d" if kind == "Red Flannel" else "#3f6b3a"
        dark = shade(base, 0.55)
        pid = "plaid" + base[1:]
        pat = (f'<pattern id="{pid}" width="70" height="70" patternUnits="userSpaceOnUse" patternTransform="rotate(-4)">'
               f'<rect width="70" height="70" fill="{base}"/>'
               f'<rect x="0" y="22" width="70" height="22" fill="{dark}" opacity="0.8"/>'
               f'<rect x="22" y="0" width="22" height="70" fill="{dark}" opacity="0.8"/>'
               f'<rect x="0" y="52" width="70" height="4" fill="#1c1c1c" opacity="0.7"/>'
               f'<rect x="52" y="0" width="4" height="70" fill="#1c1c1c" opacity="0.7"/>'
               f'<rect x="0" y="8" width="70" height="3" fill="#e8d9b0" opacity="0.5"/>'
               '</pattern>')
        body = (f'<defs>{pat}</defs>'
                f'<path d="{TORSO}" fill="url(#{pid})" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<g clip-path="url(#torso)"><path d="M 120 1010 C 130 900 190 840 300 815 L 340 1010 Z" fill="#000" opacity="0.28"/>'
                + _grime(rng, 150, 880, 840, 1000, 10, "#3b2a18", 0.3) + '</g>'
                + inner_tee +
                f'<path d="M 410 790 L 340 825 L 400 895 L 470 905 Z" fill="url(#{pid})" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<path d="M 610 785 L 715 818 L 635 900 L 560 905 Z" fill="url(#{pid})" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<circle cx="535" cy="955" r="8" fill="#e5dcc4" stroke="{OUT}" stroke-width="4"/>')
        return clip + body
    if kind == "Chore Coat":
        base = "#3e4752"
        body = (f'<path d="{TORSO}" fill="{base}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<g clip-path="url(#torso)"><path d="M 120 1010 C 130 900 190 840 300 815 L 340 1010 Z" fill="#000" opacity="0.3"/>'
                + _grime(rng, 150, 880, 830, 1000, 22, "#6b5638", 0.45) + '</g>'
                # plaid shirt underneath
                '<path d="M 420 795 L 470 905 L 560 905 L 605 795 Z" fill="#8e8e8e" stroke="#111" stroke-width="8" stroke-linejoin="round"/>'
                '<path d="M 440 815 L 590 815 M 455 850 L 580 850 M 470 885 L 565 885 M 480 800 L 500 905 M 530 800 L 525 905" stroke="#3a3a3a" stroke-width="7"/>'
                # big corduroy collar
                f'<path d="M 415 780 L 300 815 L 360 920 L 470 905 Z" fill="#5a4630" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<path d="M 605 778 L 740 810 L 660 920 L 560 905 Z" fill="#5a4630" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<circle cx="585" cy="960" r="10" fill="#9a9a9a" stroke="{OUT}" stroke-width="4"/>'
                f'<path d="M 650 950 L 790 945 L 795 1010 M 650 950 L 652 1010" fill="none" stroke="{OUT}" stroke-width="5"/>')
        return clip + body
    if kind == "Stained Undershirt":
        base = "#e6e1cf"
        body = (f'<path d="{TORSO}" fill="{base}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<g clip-path="url(#torso)"><path d="M 120 1010 C 130 900 190 840 300 815 L 340 1010 Z" fill="#000" opacity="0.15"/>'
                + _grime(rng, 150, 880, 830, 1000, 18, "#8a6a2c", 0.45)
                + _grime(rng, 400, 700, 860, 1000, 5, "#7a1f1a", 0.55) + '</g>'
                f'<path d="M 410 790 C 450 860 570 860 610 785" fill="none" stroke="{OUT}" stroke-width="{SW}"/>'
                # suspenders
                f'<path d="M 330 820 L 360 1010 M 690 815 L 660 1010" stroke="#5b3a22" stroke-width="34"/>'
                f'<path d="M 330 820 L 360 1010 M 690 815 L 660 1010" stroke="{OUT}" stroke-width="4" fill="none" transform="translate(-17 0)"/>'
                f'<path d="M 330 820 L 360 1010 M 690 815 L 660 1010" stroke="{OUT}" stroke-width="4" fill="none" transform="translate(17 0)"/>')
        return clip + body
    raise ValueError(kind)


# --------------------------------------------------------------------------
# Head
# --------------------------------------------------------------------------
def _lumpy_cranium(rng, swell):
    """Build the head outline. The back/top of the skull gets random lumps."""
    # anchor points along the skull from the ear (back) over the top to the brow
    pts = [(395, 560), (330, 470), (300, 360), (325, 255), (395, 175),
           (500, 135), (610, 145), (700, 195), (750, 290)]
    lumped = []
    for i, (x, y) in enumerate(pts):
        if 1 <= i <= 7:
            # push outward from the skull centre by a random swelling
            cx, cy = 520, 420
            dx, dy = x - cx, y - cy
            m = math.hypot(dx, dy)
            k = rng.uniform(0, 1) * swell
            x, y = x + dx / m * k, y + dy / m * k
        lumped.append((x, y))
    d = f"M {lumped[0][0]:.0f} {lumped[0][1]:.0f} "
    for (x0, y0), (x1, y1) in zip(lumped, lumped[1:]):
        # bulge each segment outward to make lumps
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        nx, ny = mx - 520, my - 420
        m = math.hypot(nx, ny)
        b = rng.uniform(10, 18 + swell * 0.6)
        d += f"Q {mx + nx / m * b:.0f} {my + ny / m * b:.0f} {x1:.0f} {y1:.0f} "
    # far-side face contour: brow ridge, eye dip, cheekbone, cheek, chin, jaw
    d += ("C 770 330 790 370 785 410 "     # brow ridge
          "C 778 440 762 450 765 470 "     # eye socket dip
          "C 790 500 795 540 780 570 "     # cheekbone
          "C 772 620 760 660 720 690 "     # cheek -> jaw
          "C 690 715 640 725 600 715 "     # chin
          "C 520 700 450 650 395 560 Z")   # jaw line back to ear
    return d


def head(skin, rng, swell):
    d = _lumpy_cranium(rng, swell)
    dark = shade(skin, 0.78)
    darker = shade(skin, 0.62)
    light = shade(skin, 1.25)
    parts = [f'<clipPath id="headclip"><path d="{d}"/></clipPath>',
             f'<path d="{d}" fill="{skin}"/>',
             '<g clip-path="url(#headclip)">',
             # cel shadow on the back half (light comes from front-right)
             f'<path d="M 250 100 C 420 160 450 300 455 420 C 460 520 520 600 560 760 L 250 760 Z" fill="{dark}"/>',
             # under-jaw shadow
             f'<path d="M 420 600 C 520 690 640 700 760 650 L 760 760 L 400 760 Z" fill="{dark}"/>',
             # highlight on the forehead
             f'<path d="M 560 190 C 640 200 700 250 715 300 C 660 270 600 245 545 240 Z" fill="{light}" opacity="0.8"/>',
             ]
    # lumps / swellings: filled bulges with a cel-shaded crescent underneath
    for _ in range(int(3 + swell / 10)):
        cx, cy = rng.uniform(380, 650), rng.uniform(175, 330)
        r = rng.uniform(28, 55)
        parts.append(f'<path d="M {cx - r:.0f} {cy:.0f} A {r:.0f} {r * 0.75:.0f} 0 0 0 {cx + r:.0f} {cy:.0f} '
                     f'A {r * 1.1:.0f} {r * 0.95:.0f} 0 0 1 {cx - r:.0f} {cy:.0f} Z" fill="{darker}" opacity="0.85"/>')
        parts.append(f'<path d="M {cx - r:.0f} {cy:.0f} A {r:.0f} {r * 0.75:.0f} 0 0 0 {cx + r * 0.6:.0f} {cy + r * 0.6:.0f}" '
                     f'fill="none" stroke="{OUT}" stroke-width="4" stroke-linecap="round" opacity="0.8"/>')
        parts.append(f'<ellipse cx="{cx + r * 0.25:.0f}" cy="{cy - r * 0.45:.0f}" rx="{r * 0.35:.0f}" ry="{r * 0.18:.0f}" '
                     f'transform="rotate(-20 {cx:.0f} {cy:.0f})" fill="{light}" opacity="0.9"/>')
    # forehead wrinkles / folds above the brow
    parts.append(f'<path d="M 560 365 C 610 340 680 340 745 360" fill="none" stroke="{darker}" stroke-width="6" stroke-linecap="round"/>')
    parts.append(f'<path d="M 590 335 C 640 318 690 320 730 330" fill="none" stroke="{darker}" stroke-width="5" stroke-linecap="round"/>')
    # cheek folds
    parts.append(f'<path d="M 600 545 C 585 590 600 625 615 650" fill="none" stroke="{darker}" stroke-width="6" stroke-linecap="round"/>')
    parts.append('</g>')
    parts.append(f'<path d="{d}" fill="none" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>')
    return "".join(parts)


def ear(skin, kind):
    dark = shade(skin, 0.7)
    if kind == "Cauliflower":
        d = ("M 405 470 C 370 420 320 430 318 480 C 300 500 315 540 335 545 "
             "C 320 575 350 610 385 600 C 400 590 410 570 405 540 C 418 515 418 490 405 470 Z")
        inner = (f'<path d="M 390 480 C 360 460 340 480 350 500 C 335 520 355 545 375 540 C 360 560 380 580 395 570" '
                 f'fill="none" stroke="{OUT}" stroke-width="5" stroke-linecap="round"/>'
                 f'<circle cx="345" cy="515" r="10" fill="{dark}"/><circle cx="365" cy="560" r="8" fill="{dark}"/>')
    elif kind == "Torn":
        d = ("M 405 470 C 370 430 330 440 325 480 L 345 490 L 322 510 "
             "C 320 560 345 600 385 600 C 400 590 410 570 405 540 C 418 515 418 490 405 470 Z")
        inner = (f'<path d="M 390 490 C 360 480 350 520 370 540 C 360 560 380 575 395 570" fill="none" '
                 f'stroke="{OUT}" stroke-width="5" stroke-linecap="round"/>'
                 '<path d="M 330 495 L 345 490" stroke="#7a1f1a" stroke-width="5"/>')
    else:  # "Normal"
        d = "M 405 470 C 370 430 325 440 325 495 C 325 560 355 605 390 600 C 405 590 410 570 405 540 C 418 515 418 490 405 470 Z"
        inner = (f'<path d="M 390 485 C 355 475 350 520 370 540 C 360 560 380 575 395 568" fill="none" '
                 f'stroke="{OUT}" stroke-width="5" stroke-linecap="round"/>')
    return ('<g transform="translate(-22 6)">'
            f'<path d="{d}" fill="{skin}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
            f'<path d="M 400 480 C 380 470 350 470 345 500 C 345 540 360 570 385 580 L 400 560 Z" fill="{dark}" opacity="0.6"/>'
            + inner + '</g>')


# --------------------------------------------------------------------------
# Eyes
# --------------------------------------------------------------------------
def _eye(cx, cy, rx, ry, lid, pupil_dx, pupil_r, iris, skin, droop):
    """Single eye: white, iris, heavy upper lid covering `lid` fraction."""
    dark = shade(skin, 0.72)
    eid = f"e{cx}{cy}"
    top = cy - ry + 2 * ry * lid
    return (
        # socket shadow and under-eye bag
        f'<ellipse cx="{cx}" cy="{cy + 4}" rx="{rx + 18}" ry="{ry + 16}" fill="{dark}" opacity="0.7"/>'
        f'<path d="M {cx - rx - 8} {cy + ry + 2} Q {cx} {cy + ry + 32 + droop} {cx + rx + 6} {cy + ry - 2}" '
        f'fill="none" stroke="{OUT}" stroke-width="4" stroke-linecap="round"/>'
        f'<clipPath id="{eid}"><ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"/></clipPath>'
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#f1ecd8"/>'
        f'<g clip-path="url(#{eid})">'
        f'<circle cx="{cx + pupil_dx}" cy="{cy + 4}" r="{pupil_r + 7}" fill="{iris}"/>'
        f'<circle cx="{cx + pupil_dx}" cy="{cy + 4}" r="{pupil_r}" fill="#111"/>'
        f'<circle cx="{cx + pupil_dx + 4}" cy="{cy - 1}" r="3" fill="#fff"/>'
        # bloodshot veins
        f'<path d="M {cx - rx} {cy + 3} l 14 -3 l 6 4 M {cx + rx} {cy + 6} l -12 -2" stroke="#c0392b" stroke-width="2" fill="none"/>'
        # heavy lid
        f'<rect x="{cx - rx - 2}" y="{cy - ry - 2}" width="{2 * rx + 4}" height="{top - (cy - ry) + 2}" fill="{skin}"/>'
        f'<path d="M {cx - rx - 2} {top} L {cx + rx + 2} {top + droop * 0.4}" stroke="{OUT}" stroke-width="6"/>'
        '</g>'
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{OUT}" stroke-width="6"/>'
        # lid crease
        f'<path d="M {cx - rx - 4} {top - 10} Q {cx} {top - 22} {cx + rx + 2} {top - 8 + droop * 0.4}" fill="none" stroke="{OUT}" stroke-width="4" stroke-linecap="round"/>'
    )


def eyes(kind, skin, rng):
    iris = rng.choice(["#6e9ec9", "#7a8b4a", "#6b4a2b", "#9aa3a6"])
    if kind == "Droopy Mismatch":
        return (_eye(585, 478, 38, 26, 0.42, 14, 8, iris, skin, 8)
                + _eye(712, 462, 24, 20, 0.30, 8, 6, iris, skin, 0))
    if kind == "Swollen Shut":
        # near eye bulging swollen and closed, far eye staring
        dark = shade(skin, 0.7)
        return (f'<ellipse cx="585" cy="478" rx="58" ry="40" fill="{shade(skin, 0.9)}" stroke="{OUT}" stroke-width="6"/>'
                f'<path d="M 545 485 Q 585 500 625 482" fill="none" stroke="{OUT}" stroke-width="6" stroke-linecap="round"/>'
                f'<path d="M 555 455 Q 585 440 615 455" fill="none" stroke="{shade(skin, 1.3)}" stroke-width="6" stroke-linecap="round"/>'
                f'<ellipse cx="585" cy="478" rx="58" ry="40" fill="#7b4a6b" opacity="0.25"/>'
                + _eye(712, 458, 26, 22, 0.18, 10, 7, iris, skin, 0)
                + f'<path d="M 690 500 Q 712 510 735 498" fill="none" stroke="{dark}" stroke-width="5"/>')
    if kind == "Lazy Eye":
        return (_eye(585, 472, 34, 26, 0.35, -16, 8, iris, skin, 4)
                + _eye(714, 470, 24, 20, 0.35, 10, 6, iris, skin, 4))
    if kind == "Sunken Socket":
        # near eye drooped way down the face with a sagging fold
        return (_eye(588, 500, 34, 24, 0.40, 12, 7, iris, skin, 14)
                + f'<path d="M 545 440 C 570 465 610 465 640 445" fill="none" stroke="{OUT}" stroke-width="6" stroke-linecap="round"/>'
                + _eye(712, 456, 24, 20, 0.28, 8, 6, iris, skin, 0))
    if kind == "Pinprick":
        return (_eye(585, 472, 36, 28, 0.25, 10, 3, "#d8d0b0", skin, 3)
                + _eye(713, 465, 25, 21, 0.25, 8, 3, "#d8d0b0", skin, 3))
    raise ValueError(kind)


def brows(kind, hair):
    if kind == "None":
        return ""
    if kind == "Bushy":
        return (f'<path d="M 538 432 C 560 405 610 400 640 418 L 632 432 C 600 420 565 425 540 445 Z" fill="{hair}" stroke="{OUT}" stroke-width="4" stroke-linejoin="round"/>'
                f'<path d="M 680 420 C 700 405 735 405 752 420 L 745 430 C 725 422 700 422 684 432 Z" fill="{hair}" stroke="{OUT}" stroke-width="4" stroke-linejoin="round"/>')
    # "Scarred" - one brow split by a scar
    return (f'<path d="M 540 435 C 560 418 585 412 600 414 L 598 426 C 580 426 560 432 544 446 Z" fill="{hair}" stroke="{OUT}" stroke-width="4"/>'
            f'<path d="M 612 412 C 625 412 635 415 640 420 L 632 430 C 625 426 618 425 612 425 Z" fill="{hair}" stroke="{OUT}" stroke-width="4"/>'
            f'<path d="M 682 422 C 700 410 735 410 750 422 L 744 431 C 725 424 700 424 686 433 Z" fill="{hair}" stroke="{OUT}" stroke-width="4"/>')


# --------------------------------------------------------------------------
# Nose
# --------------------------------------------------------------------------
def nose(kind, skin):
    dark = shade(skin, 0.68)
    light = shade(skin, 1.2)
    if kind == "Split Nostril":
        # like the reference: bulbous tip with the near nostril torn open
        d = ("M 650 430 C 660 470 680 500 715 520 C 760 535 770 565 750 585 "
             "C 735 598 715 595 700 590 C 685 602 660 602 640 588 C 625 580 625 560 640 548 Z")
        return (f'<path d="{d}" fill="{skin}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<path d="M 650 445 C 655 480 670 505 690 520 L 660 545 C 645 520 640 480 650 445 Z" fill="{dark}"/>'
                f'<path d="M 700 525 C 725 528 745 540 748 555" fill="none" stroke="{light}" stroke-width="6" stroke-linecap="round"/>'
                # torn open nostril
                f'<path d="M 650 560 C 665 548 690 556 700 590 C 680 595 660 590 650 580 Z" fill="#5a1a1a" stroke="{OUT}" stroke-width="5"/>'
                f'<path d="M 662 565 L 672 590 M 678 562 L 685 588" stroke="#c46d6d" stroke-width="3"/>'
                f'<ellipse cx="730" cy="585" rx="10" ry="6" fill="#2a1414"/>')
    if kind == "Bulbous":
        d = ("M 650 430 C 665 470 680 490 700 505 C 770 500 790 560 765 590 "
             "C 745 612 715 605 700 598 C 680 612 640 608 628 585 C 618 562 630 545 650 540 Z")
        return (f'<path d="{d}" fill="{shade(skin, 0.95)}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<path d="M 650 445 C 658 480 668 500 685 512 L 655 540 C 645 515 642 480 650 445 Z" fill="{dark}"/>'
                f'<circle cx="740" cy="540" r="14" fill="{light}" opacity="0.8"/>'
                f'<circle cx="715" cy="560" r="5" fill="{dark}"/><circle cx="755" cy="565" r="4" fill="{dark}"/>'
                f'<ellipse cx="672" cy="590" rx="16" ry="8" fill="#2a1414"/>'
                f'<ellipse cx="740" cy="596" rx="9" ry="5" fill="#2a1414"/>')
    if kind == "Smashed Flat":
        d = ("M 660 470 C 670 500 700 520 730 540 C 755 555 750 580 730 588 "
             "C 700 596 660 596 635 585 C 620 575 630 555 650 545 Z")
        return (f'<path d="{d}" fill="{skin}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<path d="M 662 480 L 690 512 L 672 520 Z" fill="{dark}"/>'
                f'<path d="M 668 490 L 700 482 M 676 505 L 712 500" stroke="{OUT}" stroke-width="4"/>'
                f'<ellipse cx="660" cy="575" rx="14" ry="7" fill="#2a1414"/>'
                f'<ellipse cx="722" cy="578" rx="10" ry="6" fill="#2a1414"/>'
                f'<path d="M 690 535 C 700 545 715 548 725 545" fill="none" stroke="#7a2a2a" stroke-width="4"/>')
    if kind == "Missing":
        # nasal cavity exposed
        return (f'<path d="M 655 470 C 690 500 730 530 740 575 C 710 595 660 595 640 580 C 650 550 650 510 655 470 Z" '
                f'fill="{dark}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                '<path d="M 668 515 C 690 530 710 560 712 580 L 690 585 C 685 560 675 540 668 515 Z" fill="#2a1010" stroke="#111" stroke-width="4"/>'
                '<path d="M 690 520 C 715 540 728 560 730 578 L 718 582 C 712 560 700 540 690 520 Z" fill="#2a1010" stroke="#111" stroke-width="4"/>'
                '<path d="M 700 548 L 708 580" stroke="#c46d6d" stroke-width="3"/>')
    raise ValueError(kind)


# --------------------------------------------------------------------------
# Mouth
# --------------------------------------------------------------------------
def _teeth(rng, x0, x1, y, h, style):
    out = []
    x = x0
    i = 0
    while x < x1 - 6:
        w = rng.uniform(16, 26)
        if style == "gappy" and rng.random() < 0.3:
            x += w
            i += 1
            continue
        hh = h * rng.uniform(0.6, 1.1)
        tilt = rng.uniform(-10, 10)
        col = rng.choice(["#f0e3b0", "#e4cf86", "#d6bb6a", "#f5ecd0", "#c9a85a"])
        if style == "rotten" and rng.random() < 0.3:
            col = "#6b5a33"
        out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w - 2:.0f}" height="{hh:.0f}" rx="4" fill="{col}" '
                   f'stroke="#111" stroke-width="3.5" transform="rotate({tilt:.0f} {x + w / 2:.0f} {y:.0f})"/>')
        x += w
        i += 1
    return "".join(out)


def mouth(kind, skin, rng):
    lip = shade(skin, 0.82)
    if kind == "Snarl":
        clip = ('<clipPath id="mclip"><path d="M 585 625 C 620 610 680 600 745 618 '
                'C 740 650 700 668 650 668 C 615 666 590 650 585 625 Z"/></clipPath>')
        return (clip +
                '<path d="M 585 625 C 620 610 680 600 745 618 C 740 650 700 668 650 668 C 615 666 590 650 585 625 Z" fill="#3a0f12"/>'
                '<g clip-path="url(#mclip)">' + _teeth(rng, 590, 745, 608, 28, "gappy")
                + _teeth(rng, 600, 735, 640, 26, "rotten") + '</g>'
                f'<path d="M 575 628 C 620 600 690 590 755 612 C 720 600 640 605 585 640 Z" fill="{lip}" stroke="#111" stroke-width="5"/>'
                f'<path d="M 585 625 C 620 610 680 600 745 618 C 740 650 700 668 650 668 C 615 666 590 650 585 625 Z" fill="none" stroke="#111" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<path d="M 600 672 C 640 690 700 685 730 668" fill="none" stroke="#111" stroke-width="5" stroke-linecap="round"/>')
    if kind == "Slack Jaw":
        clip = '<clipPath id="mclip"><path d="M 595 625 C 640 615 700 615 740 628 C 735 670 700 695 660 695 C 620 690 598 665 595 625 Z"/></clipPath>'
        return (clip +
                '<path d="M 595 625 C 640 615 700 615 740 628 C 735 670 700 695 660 695 C 620 690 598 665 595 625 Z" fill="#3a0f12"/>'
                '<g clip-path="url(#mclip)">' + _teeth(rng, 600, 740, 615, 22, "gappy")
                + '<ellipse cx="665" cy="690" rx="45" ry="22" fill="#b8505a"/></g>'
                f'<path d="M 595 625 C 640 615 700 615 740 628 C 735 670 700 695 660 695 C 620 690 598 665 595 625 Z" fill="none" stroke="#111" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<path d="M 610 705 C 650 718 700 712 725 698" fill="none" stroke="{lip}" stroke-width="10" stroke-linecap="round"/>'
                # drool
                '<path d="M 615 680 C 612 700 618 720 612 735 C 608 745 620 748 622 738 C 624 720 622 700 625 685 Z" fill="#cfe6ea" stroke="#111" stroke-width="3" opacity="0.9"/>')
    if kind == "Crooked Grin":
        clip = '<clipPath id="mclip"><path d="M 580 640 C 630 640 690 625 750 600 C 745 630 720 660 670 665 C 630 668 595 660 580 640 Z"/></clipPath>'
        return (clip +
                '<path d="M 580 640 C 630 640 690 625 750 600 C 745 630 720 660 670 665 C 630 668 595 660 580 640 Z" fill="#3a0f12"/>'
                '<g clip-path="url(#mclip)">' + _teeth(rng, 585, 750, 612, 34, "rotten") + '</g>'
                f'<path d="M 580 640 C 630 640 690 625 750 600 C 745 630 720 660 670 665 C 630 668 595 660 580 640 Z" fill="none" stroke="#111" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<path d="M 570 630 C 575 640 580 648 590 652" fill="none" stroke="#111" stroke-width="5" stroke-linecap="round"/>'
                f'<path d="M 745 592 C 755 598 760 606 758 615" fill="none" stroke="#111" stroke-width="5" stroke-linecap="round"/>')
    if kind == "Lipless":
        # exposed gums, no lips (like the reference's pulled-back mouth)
        clip = '<clipPath id="mclip"><path d="M 590 620 C 640 605 700 605 745 620 C 740 655 705 672 660 672 C 620 670 595 652 590 620 Z"/></clipPath>'
        return (clip +
                '<path d="M 590 620 C 640 605 700 605 745 620 C 740 655 705 672 660 672 C 620 670 595 652 590 620 Z" fill="#3a0f12"/>'
                '<g clip-path="url(#mclip)">'
                '<path d="M 580 600 L 760 600 L 760 628 C 700 618 640 618 580 632 Z" fill="#b8505a"/>'
                + _teeth(rng, 592, 745, 618, 24, "rotten")
                + '<path d="M 580 680 L 760 680 L 760 655 C 700 662 640 662 580 652 Z" fill="#b8505a"/>'
                + _teeth(rng, 605, 735, 640, 18, "gappy") + '</g>'
                f'<path d="M 590 620 C 640 605 700 605 745 620 C 740 655 705 672 660 672 C 620 670 595 652 590 620 Z" fill="none" stroke="#111" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<path d="M 595 612 L 588 600 M 620 605 L 616 592 M 735 612 L 742 600" stroke="#111" stroke-width="4"/>')
    raise ValueError(kind)


# --------------------------------------------------------------------------
# Skin details
# --------------------------------------------------------------------------
def skin_details(kinds, skin, rng):
    out = ['<g clip-path="url(#headclip)">']
    # grime is always present
    out.append(_grime(rng, 330, 780, 200, 700, 16, "#4a3a22", 0.22))
    for _ in range(40):
        x, y = rng.uniform(560, 780), rng.uniform(600, 710)
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="2" fill="#2a2018" opacity="0.6"/>')  # stubble
    if "Stitches" in kinds:
        out.append('<path d="M 420 250 C 470 300 500 330 520 400" fill="none" stroke="#7a2a2a" stroke-width="6" stroke-linecap="round"/>')
        for t in range(6):
            x = 425 + t * 18
            y = 255 + t * 26
            out.append(f'<path d="M {x - 12} {y + 6} L {x + 14} {y - 6}" stroke="#111" stroke-width="4" stroke-linecap="round"/>')
    if "Veins" in kinds:
        out.append('<path d="M 360 320 C 390 300 400 270 440 260 C 470 250 480 230 500 215 M 440 260 C 450 280 470 290 480 300" '
                   'fill="none" stroke="#6b7fa8" stroke-width="5" stroke-linecap="round" opacity="0.8"/>')
    if "Boils" in kinds:
        for (x, y, r) in [(575, 300, 14), (520, 560, 11), (745, 640, 9), (470, 420, 12)]:
            out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#d97a6a" stroke="#111" stroke-width="4"/>'
                       f'<circle cx="{x - r * 0.3:.0f}" cy="{y - r * 0.3:.0f}" r="{r * 0.35:.0f}" fill="#f6e3a0"/>')
    if "Burn Scar" in kinds:
        out.append(f'<path d="M 470 470 C 520 450 560 520 545 600 C 520 640 470 620 450 580 C 430 530 440 490 470 470 Z" '
                   f'fill="#c98a8a" opacity="0.75" stroke="#111" stroke-width="4"/>')
        out.append('<path d="M 480 500 C 500 520 510 560 495 590 M 515 490 C 525 520 528 560 520 600" fill="none" stroke="#9a5a5a" stroke-width="4"/>')
    if "Wart" in kinds:
        out.append(f'<circle cx="760" cy="620" r="12" fill="{shade(skin, 0.75)}" stroke="#111" stroke-width="4"/>'
                   '<path d="M 760 608 l 4 -14 M 765 610 l 12 -8" stroke="#111" stroke-width="2"/>')
    out.append('</g>')
    return "".join(out)


# --------------------------------------------------------------------------
# Hair
# --------------------------------------------------------------------------
def hair(kind, color, rng):
    if kind == "Bald":
        return ""
    dark = shade(color, 0.65)
    if kind == "Stringy Long":
        # front: a greasy cap of hair over the crown with a few strands on the forehead
        out = [f'<path d="M 300 420 C 280 250 370 120 510 112 C 640 108 730 180 750 280 '
               f'C 720 250 690 240 660 250 C 640 300 620 330 600 345 C 600 300 590 270 570 255 '
               f'C 520 260 470 290 440 340 C 420 400 400 470 395 520 C 360 500 320 470 300 420 Z" '
               f'fill="{color}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>',
               f'<path d="M 330 330 C 350 230 410 170 490 150 M 380 360 C 400 270 450 210 540 185 M 600 160 C 650 175 690 200 715 240" '
               f'fill="none" stroke="{dark}" stroke-width="6" stroke-linecap="round"/>',
               f'<path d="M 450 165 C 500 145 560 140 610 150" fill="none" stroke="{shade(color, 1.4)}" stroke-width="6" stroke-linecap="round"/>']
        return "".join(out)
    if kind == "Patchy Tufts":
        out = []
        for (x, y, n) in [(400, 210, 7), (560, 150, 6), (340, 330, 5), (660, 190, 4)]:
            for j in range(n):
                a = -math.pi / 2 + rng.uniform(-0.7, 0.7)
                L = rng.uniform(30, 60)
                out.append(f'<path d="M {x + j * 6} {y} q {math.cos(a) * L / 2 + 10:.0f} {math.sin(a) * L / 2:.0f} {math.cos(a) * L:.0f} {math.sin(a) * L:.0f}" '
                           f'fill="none" stroke="{OUT}" stroke-width="11" stroke-linecap="round"/>'
                           f'<path d="M {x + j * 6} {y} q {math.cos(a) * L / 2 + 10:.0f} {math.sin(a) * L / 2:.0f} {math.cos(a) * L:.0f} {math.sin(a) * L:.0f}" '
                           f'fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round"/>')
        return "".join(out)
    if kind == "Greasy Comb-over":
        return (f'<path d="M 310 380 C 300 260 360 170 460 140 C 560 120 650 140 700 200 '
                f'C 640 190 580 195 520 215 C 450 240 400 300 380 380 C 370 420 340 430 310 380 Z" '
                f'fill="{color}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<path d="M 340 330 C 380 230 470 175 600 170 M 360 360 C 400 270 470 210 640 185 M 330 280 C 380 200 440 165 520 150" '
                f'fill="none" stroke="{dark}" stroke-width="6" stroke-linecap="round"/>'
                f'<path d="M 420 200 C 470 175 520 165 560 162" fill="none" stroke="{shade(color, 1.5)}" stroke-width="6" stroke-linecap="round"/>')
    if kind == "Trucker Cap":
        cap = rng.choice(["#2f4f3a", "#7a2f2a", "#c9b27a", "#2a3550"])
        return (f'<path d="M 285 345 C 270 180 390 75 525 75 C 660 75 760 170 770 300 L 285 345 Z" '
                f'fill="{cap}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<path d="M 285 345 C 275 200 340 120 410 95 C 370 180 360 260 375 335 Z" fill="#000" opacity="0.25"/>'
                f'<path d="M 470 85 C 440 170 440 260 460 330 M 610 85 C 625 170 630 250 625 312" fill="none" stroke="#e8e0c8" stroke-width="5" stroke-dasharray="6 6"/>'
                f'<path d="M 720 290 C 790 280 870 295 910 325 C 870 345 790 340 730 325 Z" fill="{shade(cap, 0.8)}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                + _grime(rng, 350, 700, 150, 300, 6, "#3b2a18", 0.35)
                + f'<path d="M 300 345 C 290 390 295 430 310 470" fill="none" stroke="{OUT}" stroke-width="16" stroke-linecap="round"/>'
                + f'<path d="M 300 345 C 290 390 295 430 310 470" fill="none" stroke="{rng.choice(list(HAIR_COLORS.values()))}" stroke-width="9" stroke-linecap="round"/>')
    raise ValueError(kind)


def hair_back(kind, color, rng):
    """Hair drawn behind the head (long hair hanging down the back)."""
    if kind != "Stringy Long":
        return ""
    dark = shade(color, 0.65)
    out = [f'<path d="M 320 220 C 250 330 240 520 230 700 C 228 760 250 800 270 810 '
           f'C 300 760 330 740 360 760 C 380 720 400 690 430 680 C 420 600 400 450 420 300 Z" '
           f'fill="{dark}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>']
    for i in range(9):
        x0 = 300 + i * 14 + rng.uniform(-4, 4)
        L = rng.uniform(420, 560)
        x1 = x0 - rng.uniform(30, 80)
        out.append(f'<path d="M {x0:.0f} 260 C {x0 - 30:.0f} {260 + L * 0.4:.0f} {x1 + 15:.0f} {260 + L * 0.7:.0f} {x1:.0f} {260 + L:.0f}" '
                   f'fill="none" stroke="{OUT}" stroke-width="17" stroke-linecap="round"/>'
                   f'<path d="M {x0:.0f} 260 C {x0 - 30:.0f} {260 + L * 0.4:.0f} {x1 + 15:.0f} {260 + L * 0.7:.0f} {x1:.0f} {260 + L:.0f}" '
                   f'fill="none" stroke="{color if i % 3 else dark}" stroke-width="9" stroke-linecap="round"/>')
    return "".join(out)
