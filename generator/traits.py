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
    "Blood Red": "#8e1c1c",
    "Midnight": "#232637",
    "Toxic Slime": "#9bd23a",
    "Gold": "#d4a017",
    # 1/1 exclusives (drawn by background())
    "Full Moon": "#1b2033",
    "Cornfield": "#e39b48",
    "Blood Drip": "#efe6d2",
}

SKINS = {
    "Pink Flesh": "#e9b49a",
    "Sallow": "#d8c08c",
    "Ruddy": "#d9917a",
    "Corpse Grey": "#b6b79a",
    "Leather": "#a8735a",
    "Pale Wax": "#efd7c3",
    "Bloodless Blue": "#a9c3cf",
    "Radioactive": "#a8d870",
    # 1/1 exclusives
    "Charred": "#5a4a42",
    "Gilded": "#e2b84a",
    "Albino": "#f7f1ec",
}

HAIR_COLORS = {
    "Ginger": "#c8622c",
    "Dirty Blonde": "#b89a55",
    "Greasy Black": "#2b2522",
    "Ash Grey": "#8d8a84",
    "Mud Brown": "#5e4430",
    "Blood-Matted": "#7a1a14",
}


# --------------------------------------------------------------------------
# Background
# --------------------------------------------------------------------------
def background(name):
    color = BACKGROUNDS[name]
    out = f'<rect width="1000" height="1000" fill="{color}"/>'
    if name == "Full Moon":
        out += ('<circle cx="760" cy="200" r="150" fill="#f3ecc8" stroke="#111" stroke-width="8"/>'
                '<circle cx="710" cy="160" r="26" fill="#d9cf9f"/><circle cx="820" cy="250" r="34" fill="#d9cf9f"/>'
                '<circle cx="790" cy="140" r="14" fill="#d9cf9f"/>'
                '<path d="M 0 760 C 120 700 220 740 300 700 C 380 660 460 690 520 650 L 520 1000 L 0 1000 Z" fill="#11141f"/>'
                '<path d="M 120 720 L 120 560 M 120 600 L 80 560 M 120 630 L 160 590" stroke="#11141f" stroke-width="12" stroke-linecap="round"/>')
    elif name == "Cornfield":
        out += '<rect y="620" width="1000" height="380" fill="#b8742f"/>'
        for x in range(-20, 1040, 46):
            out += (f'<path d="M {x} 1000 L {x + 6} 600 M {x + 4} 700 L {x - 26} 660 M {x + 5} 760 L {x + 34} 716 M {x + 6} 640 L {x - 18} 600" '
                    f'stroke="#6f5a22" stroke-width="9" stroke-linecap="round"/>')
        out += '<path d="M 60 120 l 30 -14 l 30 14 M 900 90 l 24 -12 l 24 12 M 840 160 l 18 -9 l 18 9" fill="none" stroke="#111" stroke-width="6" stroke-linecap="round"/>'
    elif name == "Blood Drip":
        d = "M 0 0 L 1000 0 L 1000 60"
        for x in range(1000, -1, -50):
            h = 60 + (x * 37 % 170)
            d += f" L {x} 60 C {x - 6} {h - 20} {x - 14} {h} {x - 22} {h} C {x - 30} {h} {x - 36} {h - 20} {x - 40} 60"
        d += " L 0 60 Z"
        out += f'<path d="{d}" fill="#9a1414" stroke="#111" stroke-width="6" stroke-linejoin="round"/>'
    return out


# --------------------------------------------------------------------------
# Body / clothing  (canvas coordinates; the body is turned 3/4 like the head)
# --------------------------------------------------------------------------
# Torso: near (viewer-left) shoulder is broad and close, far shoulder is
# foreshortened. The top edge dips in front of the neck (the neckline), so the
# torso, drawn over the neck, hides the base of the neck.
NECKLINE = "C 450 880 600 900 690 845"
TORSO = ("M 40 1075 C 50 925 110 872 230 852 C 300 840 350 822 398 800 "
         + NECKLINE + " C 760 860 840 876 890 910 C 940 945 960 980 965 1075 Z")
# Undershirt showing in the V between the collar points
OPENING = "M 405 806 C 450 880 600 900 688 846 L 612 912 L 582 975 L 525 908 Z"
# Collars: each starts behind the neck, wraps the neck base and folds down
# to a point at the V.
NEAR_COLLAR = ("M 392 786 C 425 850 472 886 525 908 L 490 972 "
               "C 438 934 382 884 346 852 C 360 826 374 804 392 786 Z")
FAR_COLLAR = ("M 690 838 C 668 874 642 898 612 912 L 642 972 "
              "C 682 936 716 902 740 872 C 724 858 708 846 690 838 Z")


def neck(skin):
    """Thick neck: back edge drops from behind the ear and flares into the
    trapezius, front edge comes out from under the jaw. The base is hidden
    by the clothing."""
    dark = shade(skin, 0.75)
    d = ("M 392 600 C 402 690 402 760 385 815 C 360 840 320 856 290 868 L 720 920 "
         "C 700 880 690 850 684 826 C 688 812 684 798 672 790 C 664 770 660 745 662 720 Z")
    return (f'<path d="{d}" fill="{skin}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
            '<clipPath id="neckclip"><path d="' + d + '"/></clipPath><g clip-path="url(#neckclip)">'
            # shadow cast by the jaw, following the jaw line
            f'<path d="M 380 630 C 450 735 540 800 690 795 L 690 832 C 540 845 440 790 380 715 Z" fill="{dark}"/>'
            # back of the neck in shadow
            f'<path d="M 380 600 C 425 700 435 790 430 900 L 280 900 L 280 600 Z" fill="{dark}"/>'
            '</g>'
            # neck muscle running from behind the ear toward the collarbone
            f'<path d="M 520 805 C 545 825 565 845 578 870" fill="none" stroke="{OUT}" stroke-width="4" stroke-linecap="round"/>')


def _grime(rng, x0, x1, y0, y1, n, color, opacity=0.35):
    out = []
    for _ in range(n):
        cx, cy = rng.uniform(x0, x1), rng.uniform(y0, y1)
        rx, ry = rng.uniform(5, 20), rng.uniform(3, 11)
        rot = rng.uniform(0, 180)
        out.append(f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" '
                   f'transform="rotate({rot:.0f} {cx:.0f} {cy:.0f})" fill="{color}" opacity="{opacity}"/>')
    return "".join(out)


def _plaid(pid, base, rotate, skew=0, size=56):
    dark = shade(base, 0.55)
    s, t = size, size * 0.32
    return (f'<pattern id="{pid}" width="{s}" height="{s}" patternUnits="userSpaceOnUse" '
            f'patternTransform="rotate({rotate}) skewY({skew})">'
            f'<rect width="{s}" height="{s}" fill="{base}"/>'
            f'<rect x="0" y="{t:.0f}" width="{s}" height="{t:.0f}" fill="{dark}" opacity="0.8"/>'
            f'<rect x="{t:.0f}" y="0" width="{t:.0f}" height="{s}" fill="{dark}" opacity="0.8"/>'
            f'<rect x="0" y="{s * 0.75:.0f}" width="{s}" height="3" fill="#1c1c1c" opacity="0.7"/>'
            f'<rect x="{s * 0.75:.0f}" y="0" width="3" height="{s}" fill="#1c1c1c" opacity="0.7"/>'
            f'<rect x="0" y="{s * 0.1:.0f}" width="{s}" height="2" fill="#e8d9b0" opacity="0.5"/>'
            '</pattern>')


def _shirt_folds(base):
    """Shoulder seams, armpit creases and the shadow side of the torso."""
    return ('<g clip-path="url(#torso)">'
            # near side turned away from the light
            '<path d="M 40 1075 C 50 925 110 872 230 852 C 262 900 280 960 292 1075 Z" fill="#000" opacity="0.28"/>'
            # shadow the head and neck throw on the chest
            '<path d="M 370 812 C 420 880 560 900 700 852 L 720 900 C 560 950 420 930 360 860 Z" fill="#000" opacity="0.22"/>'
            '</g>'
            # shoulder seams
            f'<path d="M 232 852 C 252 905 258 960 252 1075" fill="none" stroke="{OUT}" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M 862 896 C 850 940 850 978 856 1075" fill="none" stroke="{OUT}" stroke-width="5" stroke-linecap="round"/>'
            # fabric creases
            f'<path d="M 300 930 C 330 950 350 975 360 1000 M 150 930 C 170 950 180 975 182 1000 M 800 960 C 815 975 825 990 830 1005" '
            f'fill="none" stroke="{OUT}" stroke-width="4" stroke-linecap="round"/>')


def _collared_shirt(fill_body, fill_near, fill_far, inner, rng, grime_n=12, pocket=True):
    """Back layer (torso + collar band) and front layer (opening + collars)."""
    back = (f'<clipPath id="torso"><path d="{TORSO}"/></clipPath>'
            f'<path d="{TORSO}" fill="{fill_body}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
            + _shirt_folds(fill_body)
            + '<g clip-path="url(#torso)">' + _grime(rng, 80, 920, 870, 1000, grime_n, "#3b2a18", 0.32) + '</g>')
    front = (inner
             + f'<path d="{NEAR_COLLAR}" fill="{fill_near}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
             # fold line where the collar turns over
             + f'<path d="M 392 800 C 418 846 452 878 500 904" fill="none" stroke="{OUT}" stroke-width="3.5" stroke-linecap="round" opacity="0.7"/>'
             + f'<path d="{FAR_COLLAR}" fill="{fill_far}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
             # placket and buttons following the turned chest
             + f'<path d="M 602 968 C 606 985 608 998 609 1075" fill="none" stroke="{OUT}" stroke-width="5"/>'
             + f'<circle cx="618" cy="992" r="8" fill="#e5dcc4" stroke="{OUT}" stroke-width="4"/>')
    if pocket:
        front += (f'<path d="M 690 948 L 800 958 L 796 1075 M 690 948 L 688 1075 M 690 972 L 798 980" '
                  f'fill="none" stroke="{OUT}" stroke-width="5" stroke-linejoin="round"/>')
    return back, front


def _tee(color="#2a2a2a"):
    return (f'<path d="{OPENING}" fill="{color}" stroke="{OUT}" stroke-width="6" stroke-linejoin="round"/>'
            f'<path d="M 418 832 C 465 892 600 910 680 866" fill="none" stroke="{shade(color, 1.4)}" stroke-width="5"/>')


def _clothing_base(kind, rng):
    """Returns (back, front): back goes under the neck, front over it."""
    if kind == "Denim Shirt":
        base = "#4f6fa3"
        back, front = _collared_shirt(base, shade(base, 1.1), shade(base, 0.92), _tee(), rng, 14)
        front += (f'<path d="M 120 940 C 140 960 150 985 152 1075" fill="none" stroke="{shade(base, 1.4)}" stroke-width="3" stroke-dasharray="8 7"/>'
                  f'<path d="M 362 856 C 400 896 440 930 482 955" fill="none" stroke="{shade(base, 1.45)}" stroke-width="3" stroke-dasharray="7 6"/>')
        return back, front
    if kind in FLANNELS:
        base = FLANNELS[kind]
        pid = "plaid" + base[1:]
        defs = ('<defs>' + _plaid(pid + "b", base, -8, 6)
                + _plaid(pid + "n", base, 34, 0, 40) + _plaid(pid + "f", base, -40, 0, 36) + '</defs>')
        back, front = _collared_shirt(f"url(#{pid}b)", f"url(#{pid}n)", f"url(#{pid}f)", _tee(), rng, 10)
        return defs + back, front
    if kind == "Chore Coat":
        base = "#3e4752"
        cord = "#5a4630"
        # grey plaid work shirt shows in the opening
        inner = ('<defs>' + _plaid("plaidgrey", "#8e8e8e", -8, 0, 34) + '</defs>'
                 f'<path d="{OPENING}" fill="url(#plaidgrey)" stroke="{OUT}" stroke-width="6" stroke-linejoin="round"/>'
                 f'<path d="M 455 868 L 552 950 L 562 902 Z M 668 860 L 604 944 L 596 902 Z" fill="#7a7a7a" stroke="{OUT}" stroke-width="5" stroke-linejoin="round"/>')
        back, front = _collared_shirt(base, cord, shade(cord, 0.85), inner, rng, 24)
        return back, front
    if kind == "Stained Undershirt":
        base = "#e6e1cf"
        back = (f'<clipPath id="torso"><path d="{TORSO}"/></clipPath>'
                f'<path d="{TORSO}" fill="{base}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                '<g clip-path="url(#torso)">'
                '<path d="M 40 1075 C 50 925 110 872 230 852 C 262 900 280 960 292 1075 Z" fill="#000" opacity="0.15"/>'
                + _grime(rng, 80, 920, 860, 1000, 18, "#8a6a2c", 0.45)
                + _grime(rng, 450, 750, 900, 1000, 5, "#7a1f1a", 0.55) + '</g>')
        front = ( # crew neckline sitting on the neck base
                 f'<path d="M 398 800 C 450 880 600 900 690 845 L 702 868 C 600 928 432 908 382 822 Z" fill="{shade(base, 0.9)}" stroke="{OUT}" stroke-width="6" stroke-linejoin="round"/>'
                 # suspenders follow the turned torso
                 f'<path d="M 300 862 C 320 920 335 970 340 1075 L 378 1075 C 372 965 358 915 338 858 Z" fill="#5b3a22" stroke="{OUT}" stroke-width="5" stroke-linejoin="round"/>'
                 f'<path d="M 760 868 C 748 920 735 970 730 1075 L 762 1075 C 768 970 778 925 790 876 Z" fill="#5b3a22" stroke="{OUT}" stroke-width="5" stroke-linejoin="round"/>')
        return back, front
    raise ValueError(kind)


FLANNELS = {
    "Red Flannel": "#a8322d", "Green Flannel": "#3f6b3a", "Blue Flannel": "#2f4f8a",
    "Mustard Flannel": "#c9a227", "Purple Flannel": "#5b3d7a", "Orange Flannel": "#c4621f",
    "Grey Flannel": "#8a8a8a",
}
TRENCH = {"Khaki Trench Coat": "#b89a66", "Black Trench Coat": "#2b2b2e", "Olive Trench Coat": "#5b5f3a"}
HOODIE = {"Grey Hoodie": "#8d9096", "Black Hoodie": "#2c2c30", "Maroon Hoodie": "#6e2230"}
TORN_TEE = {"Torn White Tee": "#e8e4d8", "Torn Black Tee": "#2f2f33", "Torn Army Tee": "#5d6b45"}


def _plain_torso(base, rng, grime_color="#3b2a18", n=14):
    return (f'<clipPath id="torso"><path d="{TORSO}"/></clipPath>'
            f'<path d="{TORSO}" fill="{base}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
            + _shirt_folds(base)
            + '<g clip-path="url(#torso)">' + _grime(rng, 80, 920, 870, 1000, n, grime_color, 0.32) + '</g>')


def _crew_neck(base):
    return (f'<path d="M 398 800 C 450 880 600 900 690 845 L 702 868 C 600 928 432 908 382 822 Z" '
            f'fill="{shade(base, 0.85)}" stroke="{OUT}" stroke-width="6" stroke-linejoin="round"/>')


def _trench(base, rng):
    lapel = shade(base, 1.12)
    behind = (  # popped collar standing up behind the neck
        f'<path d="M 318 884 C 318 806 344 744 396 708 L 432 752 C 410 796 404 840 408 884 Z" fill="{shade(base, 0.85)}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
        f'<path d="M 690 868 C 706 806 728 766 760 742 L 776 800 C 766 830 752 858 736 884 Z" fill="{shade(base, 0.85)}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>')
    back = _plain_torso(base, rng, n=18)
    inner = (f'<path d="{OPENING}" fill="#d9d4c4" stroke="{OUT}" stroke-width="6" stroke-linejoin="round"/>'
             f'<path d="M 560 905 L 584 930 L 576 975 L 590 990 L 604 975 L 598 930 L 616 905 Z" fill="#4a2a2a" stroke="{OUT}" stroke-width="4" stroke-linejoin="round"/>')
    front = (inner
             # wide lapels
             + f'<path d="M 392 786 C 425 850 472 886 525 908 L 520 1075 L 420 1075 C 380 990 340 920 300 872 C 330 834 360 806 392 786 Z" fill="{lapel}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
             + f'<path d="M 360 860 L 330 900 L 380 905 Z" fill="{base}" stroke="{OUT}" stroke-width="5" stroke-linejoin="round"/>'
             + f'<path d="M 690 838 C 668 874 642 898 612 912 L 640 1075 L 712 1075 C 730 980 750 920 770 880 C 744 862 716 848 690 838 Z" fill="{shade(base, 0.95)}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
             # double-breasted buttons, gun flap, epaulette
             + "".join(f'<circle cx="{x}" cy="{y}" r="9" fill="{shade(base, 0.6)}" stroke="{OUT}" stroke-width="4"/>' for x, y in ((548, 1030), (650, 1035)))
             + f'<path d="M 760 900 L 880 920 L 870 990 L 770 980 Z" fill="{shade(base, 1.05)}" stroke="{OUT}" stroke-width="5" stroke-linejoin="round"/>'
             + f'<path d="M 150 900 L 290 868 L 296 892 L 158 926 Z" fill="{shade(base, 1.05)}" stroke="{OUT}" stroke-width="5" stroke-linejoin="round"/>'
             + f'<circle cx="276" cy="882" r="6" fill="{shade(base, 0.6)}" stroke="{OUT}" stroke-width="3"/>')
    return behind, back, front


def _hoodie(base, rng):
    behind = (  # hood bunched up behind the neck
        f'<path d="M 286 880 C 270 790 320 720 410 700 C 520 680 640 720 730 800 C 760 830 760 860 740 880 Z" '
        f'fill="{shade(base, 0.82)}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
        f'<path d="M 320 840 C 320 780 360 740 420 726" fill="none" stroke="{OUT}" stroke-width="4" stroke-linecap="round"/>')
    back = _plain_torso(base, rng, n=16)
    rim = "M 380 796 C 440 890 600 912 704 842 L 724 868 C 600 950 420 930 352 818 Z"
    front = (f'<path d="{rim}" fill="{shade(base, 0.9)}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
             f'<path d="M 372 812 C 440 905 600 928 712 856" fill="none" stroke="{OUT}" stroke-width="3" stroke-dasharray="6 6"/>'
             # drawstrings with metal tips
             + "".join(f'<path d="M {x} {y} C {x - 4} {y + 40} {x + 6} {y + 80} {x + 2} {y + 120}" fill="none" stroke="{OUT}" stroke-width="10" stroke-linecap="round"/>'
                       f'<path d="M {x} {y} C {x - 4} {y + 40} {x + 6} {y + 80} {x + 2} {y + 120}" fill="none" stroke="#e8e2cf" stroke-width="5" stroke-linecap="round"/>'
                       f'<rect x="{x - 5}" y="{y + 116}" width="14" height="22" rx="3" fill="#9aa0a6" stroke="{OUT}" stroke-width="3"/>'
                       for x, y in ((512, 900), (604, 902)))
             + f'<circle cx="512" cy="900" r="7" fill="#9aa0a6" stroke="{OUT}" stroke-width="3"/>'
             + f'<circle cx="604" cy="902" r="7" fill="#9aa0a6" stroke="{OUT}" stroke-width="3"/>')
    return behind, back, front


def _torn_tee(base, rng, skin):
    back = _plain_torso(base, rng, n=14)
    holes = ""
    spots = [(rng.uniform(130, 300), rng.uniform(930, 1010)), (rng.uniform(430, 560), rng.uniform(960, 1030)),
             (rng.uniform(700, 860), rng.uniform(930, 1010))]
    for cx, cy in spots:
        pts = []
        for k in range(9):
            import math as _m
            a = k / 9 * 2 * _m.pi
            r = rng.uniform(16, 34) if k % 2 else rng.uniform(8, 16)
            pts.append(f"{cx + _m.cos(a) * r * 1.4:.0f} {cy + _m.sin(a) * r:.0f}")
        holes += (f'<path d="M {" L ".join(pts)} Z" fill="{skin}" stroke="{OUT}" stroke-width="5" stroke-linejoin="round"/>'
                  f'<path d="M {cx - 10:.0f} {cy + 4:.0f} l 6 -10 M {cx + 12:.0f} {cy - 2:.0f} l 4 8" stroke="{shade(skin, 0.7)}" stroke-width="3"/>')
    front = (_crew_neck(base)
             # ripped collar and frayed threads
             + f'<path d="M 470 890 L 488 922 L 500 896 L 512 930 L 522 900" fill="none" stroke="{OUT}" stroke-width="4" stroke-linejoin="round"/>'
             + f'<path d="M 470 890 L 488 922 L 500 896 L 512 930 L 522 900 Z" fill="{skin}"/>'
             + "".join(f'<path d="M {x} {y} l {dx} 14" stroke="{OUT}" stroke-width="2.5" stroke-linecap="round"/>'
                       for x, y, dx in ((430, 880, -4), (560, 912, 3), (640, 888, 5), (690, 860, 4)))
             + holes
             + '<g clip-path="url(#torso)">' + _grime(rng, 400, 800, 900, 1000, 4, "#7a1f1a", 0.5) + '</g>')
    return "", back, front


def _butcher_apron(rng):
    back, front = _clothing_base("Stained Undershirt", rng)
    apron = "#ddd6c2"
    bib = "M 430 905 C 520 925 640 925 740 895 L 770 1075 L 400 1075 Z"
    front += (f'<path d="M 440 910 C 420 870 400 830 392 800 M 730 900 C 716 870 704 850 694 840" fill="none" stroke="{OUT}" stroke-width="16" stroke-linecap="round"/>'
              f'<path d="M 440 910 C 420 870 400 830 392 800 M 730 900 C 716 870 704 850 694 840" fill="none" stroke="#b9ae94" stroke-width="9" stroke-linecap="round"/>'
              f'<path d="{bib}" fill="{apron}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
              f'<clipPath id="bib"><path d="{bib}"/></clipPath><g clip-path="url(#bib)">'
              f'<path d="M 400 905 L 470 905 L 450 1075 L 400 1075 Z" fill="#000" opacity="0.12"/>'
              '<path d="M 520 930 C 560 960 540 1000 600 1020 C 640 1035 620 1060 660 1075 L 560 1075 C 540 1040 500 1010 520 930 Z" fill="#8e1414" opacity="0.85"/>'
              '<path d="M 680 930 C 690 960 700 990 690 1020" fill="none" stroke="#8e1414" stroke-width="10" stroke-linecap="round"/>'
              + _grime(rng, 430, 760, 920, 1070, 8, "#8e1414", 0.6) + '</g>')
    return "", back, front


def clothing(kind, rng, skin):
    """Returns (behind, back, front): behind goes under the neck too (hoods,
    popped collars), back under the neck, front over it."""
    if kind in TRENCH:
        return _trench(TRENCH[kind], rng)
    if kind in HOODIE:
        return _hoodie(HOODIE[kind], rng)
    if kind in TORN_TEE:
        return _torn_tee(TORN_TEE[kind], rng, skin)
    if kind == "Butcher Apron":
        return _butcher_apron(rng)
    back, front = _clothing_base(kind, rng)
    return "", back, front


def sleeve_fill(kind):
    """Fill for the sleeve of the arm holding a weapon (None = bare arm)."""
    if kind in FLANNELS:
        return f"url(#plaid{FLANNELS[kind][1:]}b)"
    return {**TRENCH, **HOODIE, "Denim Shirt": "#4f6fa3", "Chore Coat": "#3e4752"}.get(kind)


# --------------------------------------------------------------------------
# Head
# --------------------------------------------------------------------------
# Head shapes: anchor points along the skull from behind the jaw (back), over
# the top, to the start of the brow. Points listed in NOLUMP stay put (notches).
HEAD_SHAPES = {
    "Swollen Dome": [(395, 560), (330, 470), (300, 360), (325, 255), (395, 175),
                     (500, 135), (610, 145), (700, 195), (750, 290)],
    "Cone Head": [(395, 560), (330, 470), (300, 370), (318, 268), (366, 160),
                  (440, 62), (560, 112), (680, 192), (750, 290)],
    "Lopsided": [(395, 560), (288, 500), (212, 380), (236, 238), (338, 150),
                 (480, 130), (610, 150), (700, 200), (750, 290)],
    "Flat Top": [(395, 560), (330, 470), (296, 360), (312, 246), (382, 204),
                 (500, 212), (620, 198), (705, 216), (750, 290)],
    "Split Skull": [(395, 560), (330, 470), (300, 360), (325, 255), (395, 165),
                    (478, 124), (532, 218), (590, 128), (700, 195), (750, 290)],
    "Brow Bulge": [(395, 560), (330, 470), (300, 360), (325, 255), (395, 175),
                   (500, 140), (620, 138), (742, 178), (818, 292)],
    "Tumor Cluster": [(395, 560), (330, 470), (300, 360), (325, 255), (395, 175),
                      (500, 135), (610, 145), (700, 195), (750, 290)],
}
NOLUMP = {"Split Skull": {6}}
CAP_OK = {"Swollen Dome", "Flat Top", "Split Skull", "Brow Bulge"}
# the last head drawn, so hair can follow its outline
_HEAD = {}


def _lumpy_cranium(rng, swell, shape="Swollen Dome"):
    """Build the head outline for a head shape; the back/top gets random lumps."""
    pts = HEAD_SHAPES[shape]
    k_scale = 0.35 if shape == "Flat Top" else 1.0
    lumped = []
    for i, (x, y) in enumerate(pts):
        if 1 <= i <= len(pts) - 2 and i not in NOLUMP.get(shape, ()):
            # push outward from the skull centre by a random swelling
            cx, cy = 520, 420
            dx, dy = x - cx, y - cy
            m = math.hypot(dx, dy)
            k = rng.uniform(0, 1) * swell * k_scale
            x, y = x + dx / m * k, y + dy / m * k
        lumped.append((x, y))
    d = f"M {lumped[0][0]:.0f} {lumped[0][1]:.0f} "
    for j, ((x0, y0), (x1, y1)) in enumerate(zip(lumped, lumped[1:])):
        # bulge each segment outward to make lumps (not into a notch)
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        nx, ny = mx - 520, my - 420
        m = math.hypot(nx, ny)
        b = rng.uniform(10, 18 + swell * 0.6) * k_scale
        if shape == "Split Skull" and j in (5, 6):
            b = 4
        d += f"Q {mx + nx / m * b:.0f} {my + ny / m * b:.0f} {x1:.0f} {y1:.0f} "
    # far-side face contour: brow ridge, eye dip, cheekbone, cheek, chin, jaw
    brow = "C 846 340 812 402 785 414 " if shape == "Brow Bulge" else "C 770 330 790 370 785 410 "
    d += (brow +
          "C 778 440 762 450 765 470 "     # eye socket dip
          "C 790 500 795 540 780 570 "     # cheekbone
          "C 772 620 760 660 720 690 "     # cheek -> jaw
          "C 690 715 640 725 600 715 "     # chin
          "C 520 700 450 650 395 560 Z")   # jaw line back to ear
    _HEAD.update(d=d, pts=lumped, shape=shape)
    return d


def head(skin, rng, swell, shape="Swollen Dome"):
    d = _lumpy_cranium(rng, swell, shape)
    dark = shade(skin, 0.78)
    darker = shade(skin, 0.62)
    light = shade(skin, 1.25)
    parts = [f'<clipPath id="headclip"><path d="{d}"/></clipPath>',
             f'<path d="{d}" fill="{skin}"/>',
             '<g clip-path="url(#headclip)">',
             # cel shadow on the back half (light comes from front-right)
             f'<path d="M 120 0 L 300 30 C 420 160 450 300 455 420 C 460 520 520 600 560 760 L 120 760 Z" fill="{dark}"/>',
             # under-jaw shadow
             f'<path d="M 420 600 C 520 690 640 700 760 650 L 760 760 L 400 760 Z" fill="{dark}"/>',
             # highlight on the forehead
             f'<path d="M 560 190 C 640 200 700 250 715 300 C 660 270 600 245 545 240 Z" fill="{light}" opacity="0.8"/>',
             ]
    lump_y = (175, 330)
    if shape == "Cone Head":
        lump_y = (110, 320)
        parts.append(f'<path d="M 470 90 C 520 140 600 200 690 230" fill="none" stroke="{light}" stroke-width="8" stroke-linecap="round" opacity="0.8"/>')
    # lumps / swellings: filled bulges with a cel-shaded crescent underneath
    for _ in range(int(3 + swell / 10)):
        cx, cy = rng.uniform(380, 650), rng.uniform(*lump_y)
        r = rng.uniform(28, 55)
        parts.append(f'<path d="M {cx - r:.0f} {cy:.0f} A {r:.0f} {r * 0.75:.0f} 0 0 0 {cx + r:.0f} {cy:.0f} '
                     f'A {r * 1.1:.0f} {r * 0.95:.0f} 0 0 1 {cx - r:.0f} {cy:.0f} Z" fill="{darker}" opacity="0.85"/>')
        parts.append(f'<path d="M {cx - r:.0f} {cy:.0f} A {r:.0f} {r * 0.75:.0f} 0 0 0 {cx + r * 0.6:.0f} {cy + r * 0.6:.0f}" '
                     f'fill="none" stroke="{OUT}" stroke-width="4" stroke-linecap="round" opacity="0.8"/>')
        parts.append(f'<ellipse cx="{cx + r * 0.25:.0f}" cy="{cy - r * 0.45:.0f}" rx="{r * 0.35:.0f}" ry="{r * 0.18:.0f}" '
                     f'transform="rotate(-20 {cx:.0f} {cy:.0f})" fill="{light}" opacity="0.9"/>')
    if shape == "Lopsided":
        # the swollen back lobe, with a deep fold where it meets the skull
        parts.append(f'<path d="M 380 160 C 330 260 320 380 360 480" fill="none" stroke="{OUT}" stroke-width="5" stroke-linecap="round"/>')
        parts.append(f'<path d="M 386 168 C 340 262 332 380 368 476 L 300 476 L 300 168 Z" fill="{darker}" opacity="0.5"/>')
        parts.append(f'<path d="M 260 280 C 270 240 300 210 330 200" fill="none" stroke="{light}" stroke-width="7" stroke-linecap="round"/>')
    if shape == "Flat Top":
        # crushed top: a dent and crease across the crown
        parts.append(f'<path d="M 330 250 C 420 236 560 240 690 236" fill="none" stroke="{OUT}" stroke-width="5" stroke-linecap="round"/>')
        parts.append(f'<path d="M 330 254 C 420 240 560 244 690 240 L 690 270 C 560 270 420 268 330 280 Z" fill="{darker}" opacity="0.6"/>')
    if shape == "Split Skull":
        # cleft running down the crown, held together with staples
        parts.append(f'<path d="M 532 214 C 540 250 552 290 566 340" fill="none" stroke="{OUT}" stroke-width="7" stroke-linecap="round"/>')
        parts.append(f'<path d="M 510 200 C 520 240 532 290 546 340 L 566 340 C 552 290 540 250 532 214 Z" fill="{darker}"/>')
        parts += [f'<path d="M {x - 16} {y + 4} L {x - 16} {y - 6} L {x + 16} {y - 12} L {x + 16} {y - 2}" fill="none" stroke="#9aa0a6" stroke-width="5" stroke-linejoin="round"/>'
                  for x, y in ((540, 240), (548, 278), (558, 316))]
    if shape == "Brow Bulge":
        # heavy overhanging forehead casting a shadow over the eyes
        parts.append(f'<path d="M 560 400 C 640 420 720 420 800 400 L 800 440 C 720 450 640 450 560 430 Z" fill="{darker}" opacity="0.55"/>')
        parts.append(f'<path d="M 620 230 C 700 230 780 260 805 300" fill="none" stroke="{light}" stroke-width="9" stroke-linecap="round"/>')
    # forehead wrinkles / folds above the brow
    parts.append(f'<path d="M 560 365 C 610 340 680 340 745 360" fill="none" stroke="{darker}" stroke-width="6" stroke-linecap="round"/>')
    parts.append(f'<path d="M 590 335 C 640 318 690 320 730 330" fill="none" stroke="{darker}" stroke-width="5" stroke-linecap="round"/>')
    # cheek folds
    parts.append(f'<path d="M 600 545 C 585 590 600 625 615 650" fill="none" stroke="{darker}" stroke-width="6" stroke-linecap="round"/>')
    parts.append('</g>')
    parts.append(f'<path d="{d}" fill="none" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>')
    if shape == "Tumor Cluster":
        # knobbly growths bursting out of the skull
        for (x, y), r in zip([_HEAD["pts"][i] for i in (2, 3, 5, 6)], (40, 56, 46, 34)):
            parts.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{skin}" stroke="{OUT}" stroke-width="{SW}"/>'
                         f'<path d="M {x - r * 0.8:.0f} {y + r * 0.3:.0f} A {r} {r} 0 0 0 {x + r * 0.7:.0f} {y + r * 0.6:.0f}" fill="none" stroke="{darker}" stroke-width="8" stroke-linecap="round"/>'
                         f'<ellipse cx="{x + r * 0.25:.0f}" cy="{y - r * 0.4:.0f}" rx="{r * 0.3:.0f}" ry="{r * 0.17:.0f}" fill="{light}"/>'
                         f'<path d="M {x - r * 0.3:.0f} {y - r * 0.1:.0f} l 8 6 M {x + r * 0.1:.0f} {y + r * 0.2:.0f} l -6 8" stroke="#6b7fa8" stroke-width="3" stroke-linecap="round"/>')
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
    if kind in ("Glowing Red", "Glowing Green"):
        c = "#ff2a1a" if kind == "Glowing Red" else "#7dff3a"
        glow = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" opacity="{o}"/>'
                       for x, y in ((599, 482), (722, 466)) for r, o in ((46, 0.18), (30, 0.25)))
        return (_eye(585, 478, 36, 26, 0.35, 14, 7, c, skin, 6)
                + _eye(712, 462, 24, 20, 0.28, 10, 5, c, skin, 0) + glow)
    if kind == "Hollow Sockets":
        dark = shade(skin, 0.6)
        return "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx + 14}" ry="{ry + 12}" fill="{dark}"/>'
                       f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#120808" stroke="{OUT}" stroke-width="6"/>'
                       f'<circle cx="{x + 8}" cy="{y + 2}" r="4" fill="#d43a2a"/>'
                       f'<path d="M {x - rx + 6} {y + ry - 2} C {x - 8} {y + ry + 14} {x - 2} {y + ry + 26} {x - 6} {y + ry + 40}" fill="none" stroke="#3a1010" stroke-width="5" stroke-linecap="round"/>'
                       for x, y, rx, ry in ((588, 478, 34, 28), (713, 464, 22, 22)))
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
    if kind == "Stitched Shut":
        d = "M 588 632 C 630 620 690 614 748 624"
        return (f'<path d="M 584 626 C 630 604 700 600 752 616 C 740 650 700 662 660 662 C 620 660 594 648 584 626 Z" fill="{lip}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<path d="{d}" fill="none" stroke="#3a1010" stroke-width="7" stroke-linecap="round"/>'
                + "".join(f'<path d="M {x} {y - 18} L {x + 6} {y + 18}" stroke="#111" stroke-width="4" stroke-linecap="round"/>'
                          f'<circle cx="{x}" cy="{y - 18}" r="2.5" fill="#7a1a14"/><circle cx="{x + 6}" cy="{y + 18}" r="2.5" fill="#7a1a14"/>'
                          for x, y in ((604, 628), (630, 624), (656, 620), (682, 618), (708, 618), (732, 620)))
                + f'<path d="M 650 662 C 652 680 646 694 650 708" fill="none" stroke="#8e1414" stroke-width="5" stroke-linecap="round"/>')
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
        pts = _HEAD.get("pts") or HEAD_SHAPES["Swollen Dome"]
        anchors = []
        for i, n in ((3, 5), (4, 7), (5, 6), (len(pts) - 2, 4)):
            px, py = pts[i]
            anchors.append((px + (520 - px) * 0.06, py + (420 - py) * 0.06, n))
        for (x, y, n) in anchors:
            for j in range(n):
                a = -math.pi / 2 + rng.uniform(-0.7, 0.7)
                L = rng.uniform(30, 60)
                out.append(f'<path d="M {x + j * 6} {y} q {math.cos(a) * L / 2 + 10:.0f} {math.sin(a) * L / 2:.0f} {math.cos(a) * L:.0f} {math.sin(a) * L:.0f}" '
                           f'fill="none" stroke="{OUT}" stroke-width="11" stroke-linecap="round"/>'
                           f'<path d="M {x + j * 6} {y} q {math.cos(a) * L / 2 + 10:.0f} {math.sin(a) * L / 2:.0f} {math.cos(a) * L:.0f} {math.sin(a) * L:.0f}" '
                           f'fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round"/>')
        return "".join(out)
    if kind == "Greasy Comb-over":
        # plastered to the scalp: clipped to the head so it follows any head shape
        hp = ("M 290 420 C 200 220 300 -20 480 -30 C 640 -40 760 60 790 210 "
              "C 700 190 600 196 520 215 C 450 240 400 300 380 380 C 370 420 340 440 290 420 Z")
        return ('<g clip-path="url(#headclip)">'
                f'<path d="{hp}" fill="{color}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<path d="M 340 330 C 380 230 470 175 600 170 M 360 360 C 400 270 470 210 640 185 M 330 280 C 380 200 440 165 520 150 M 330 220 C 400 140 480 100 600 110" '
                f'fill="none" stroke="{dark}" stroke-width="6" stroke-linecap="round"/>'
                f'<path d="M 420 200 C 470 175 520 165 560 162" fill="none" stroke="{shade(color, 1.5)}" stroke-width="6" stroke-linecap="round"/>'
                '</g>'
                f'<path d="{_HEAD.get("d", "")}" fill="none" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>')
    if kind == "Backwards Cap":
        cap = rng.choice(["#2f4f3a", "#7a2f2a", "#c9b27a", "#2a3550"])
        mesh = rng.choice(["#e8e2cf", "#1f1f1f", shade(cap, 1.35)])
        dark = shade(cap, 0.7)
        hair_c = color
        crown = ("M 288 372 C 262 200 385 78 528 78 C 670 78 770 175 778 312 "
                 "C 610 322 440 345 288 372 Z")
        # front panels (now facing the back) are solid; mesh panels face forward
        mesh_area = ("M 560 82 C 660 92 760 180 778 312 C 700 316 620 320 548 326 "
                     "C 560 250 565 160 560 82 Z")
        out = [
            '<defs><pattern id="capmesh" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(20)">'
            f'<rect width="12" height="12" fill="{mesh}"/><circle cx="6" cy="6" r="3.2" fill="{shade(mesh, 0.55)}"/></pattern>'
            f'<clipPath id="capclip"><path d="{crown}"/></clipPath></defs>',
            # brim sticking out behind the head, seen from below-side
            f'<path d="M 372 352 C 300 334 205 340 140 372 C 175 404 270 410 362 392 Z" '
            f'fill="{dark}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>',
            f'<path d="M 362 380 C 290 392 210 392 160 378" fill="none" stroke="{shade(cap, 1.2)}" stroke-width="5" stroke-linecap="round"/>',
            f'<path d="{crown}" fill="{cap}"/>',
            '<g clip-path="url(#capclip)">',
            f'<path d="{mesh_area}" fill="url(#capmesh)"/>',
            f'<path d="M 560 82 C 565 160 560 250 548 326" fill="none" stroke="{OUT}" stroke-width="5"/>',
            # back-of-head shadow side
            f'<path d="M 280 380 C 270 220 340 120 420 92 C 385 180 378 280 392 360 Z" fill="#000" opacity="0.25"/>',
            # stitched panel seams converging on the top button
            f'<path d="M 528 80 C 450 140 420 250 430 352 M 528 80 C 640 120 700 200 720 316" fill="none" stroke="{shade(cap, 1.4)}" stroke-width="4" stroke-dasharray="7 6"/>',
            # snapback opening over the forehead showing skin/hair
            f'<path d="M 626 326 C 628 240 718 214 756 314 Z" fill="{hair_c}" stroke="{OUT}" stroke-width="6" stroke-linejoin="round"/>',
            f'<path d="M 646 300 l 8 20 M 664 268 l 8 44 M 690 254 l 4 56 M 716 262 l -2 46 M 738 288 l -6 22" stroke="{shade(hair_c, 0.6)}" stroke-width="4" stroke-linecap="round"/>',
            # adjustable strap with snaps
            f'<path d="M 624 308 L 756 298 L 758 316 L 626 326 Z" fill="{dark}" stroke="{OUT}" stroke-width="5" stroke-linejoin="round"/>',
            f'<circle cx="660" cy="316" r="5" fill="{shade(cap, 1.5)}" stroke="{OUT}" stroke-width="2.5"/>'
            f'<circle cx="685" cy="314" r="5" fill="{shade(cap, 1.5)}" stroke="{OUT}" stroke-width="2.5"/>'
            f'<circle cx="710" cy="312" r="5" fill="{shade(cap, 1.5)}" stroke="{OUT}" stroke-width="2.5"/>',
            _grime(rng, 330, 560, 140, 340, 6, "#3b2a18", 0.35),
            '</g>',
            f'<path d="{crown}" fill="none" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>',
            # sweat band edge
            f'<path d="M 296 362 C 450 336 610 318 772 306" fill="none" stroke="{OUT}" stroke-width="4"/>',
            f'<ellipse cx="528" cy="80" rx="18" ry="9" fill="{cap}" stroke="{OUT}" stroke-width="5"/>',
            # greasy tuft of hair poking out over the ear
            f'<path d="M 292 368 C 284 410 290 450 304 486 L 316 452 L 330 474 L 336 428 L 352 446 L 352 362 Z" '
            f'fill="{hair_c}" stroke="{OUT}" stroke-width="6" stroke-linejoin="round"/>',
            f'<path d="M 306 380 C 302 410 306 440 312 456 M 330 378 C 328 400 330 415 334 424" fill="none" stroke="{shade(hair_c, 0.6)}" stroke-width="4" stroke-linecap="round"/>',
        ]
        return "".join(out)
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


# --------------------------------------------------------------------------
# Bandana (face covering, worn over the nose and mouth like an outlaw)
# --------------------------------------------------------------------------
BANDANAS = {"Red Bandana": "#b8322e", "Black Bandana": "#232326",
            "Blue Bandana": "#2d4f8f", "Faded Paisley": "#cf6f6c"}


def bandana(kind, rng):
    if kind not in BANDANAS:
        return ""
    base = BANDANAS[kind]
    ink = shade(base, 1.6) if kind != "Black Bandana" else "#d9d4c4"
    dark = shade(base, 0.7)
    pid = "bandana" + base[1:]
    # paisley-ish print: teardrops, rings and dots
    pat = (f'<pattern id="{pid}" width="64" height="64" patternUnits="userSpaceOnUse" patternTransform="rotate(-12)">'
           f'<rect width="64" height="64" fill="{base}"/>'
           f'<path d="M 18 30 C 6 22 10 6 24 8 C 34 10 34 24 26 30 C 22 34 26 40 30 38" fill="none" stroke="{ink}" stroke-width="2.5"/>'
           f'<circle cx="22" cy="18" r="4" fill="none" stroke="{ink}" stroke-width="2"/>'
           f'<circle cx="48" cy="46" r="7" fill="none" stroke="{ink}" stroke-width="2"/>'
           f'<circle cx="48" cy="46" r="2" fill="{ink}"/>'
           + "".join(f'<circle cx="{x}" cy="{y}" r="1.8" fill="{ink}"/>' for x, y in ((40, 12), (54, 22), (8, 50), (30, 56), (58, 6)))
           + '</pattern>')
    shape = ("M 418 516 C 520 504 680 500 792 512 C 808 540 814 570 802 592 "
             "C 792 640 772 680 746 700 C 722 760 684 820 642 872 "
             "C 600 800 522 722 472 652 C 442 612 426 562 418 516 Z")
    out = [f'<defs>{pat}<clipPath id="bandclip"><path d="{shape}"/></clipPath></defs>',
           # knot and tails behind the near ear
           f'<path d="M 420 520 C 392 520 378 540 382 560 C 360 580 352 610 360 640 L 380 636 C 378 610 386 590 400 576 '
           f'C 396 600 404 630 418 650 L 434 640 C 424 612 422 584 432 560 Z" fill="{dark}" stroke="{OUT}" stroke-width="6" stroke-linejoin="round"/>',
           f'<path d="{shape}" fill="url(#{pid})" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>',
           '<g clip-path="url(#bandclip)">',
           # cloth tented over the nose, shadow on the side turned away
           f'<path d="M 418 516 C 470 520 520 560 560 640 C 590 700 620 790 642 872 L 400 872 L 400 516 Z" fill="#000" opacity="0.22"/>',
           f'<path d="M 790 512 C 770 560 740 600 700 620 C 660 640 630 700 620 760" fill="none" stroke="#000" stroke-width="10" opacity="0.18"/>',
           # folds hanging from the nose and chin
           f'<path d="M 760 595 C 720 640 690 700 668 790 M 700 590 C 670 640 650 700 645 760 M 560 560 C 590 620 610 690 620 760" '
           f'fill="none" stroke="{OUT}" stroke-width="3.5" stroke-linecap="round"/>',
           f'<path d="M 800 560 C 790 540 770 528 740 524" fill="none" stroke="{shade(base, 1.35)}" stroke-width="6" stroke-linecap="round"/>',
           # grime and a blood stain soaking through
           _grime(rng, 480, 760, 560, 760, 6, "#3b2a18", 0.3),
           f'<ellipse cx="{rng.uniform(640, 720):.0f}" cy="{rng.uniform(640, 700):.0f}" rx="22" ry="14" fill="#5e0e0e" opacity="0.45"/>',
           '</g>',
           # rolled top hem
           f'<path d="M 420 520 C 520 508 680 504 792 516" fill="none" stroke="{OUT}" stroke-width="3" stroke-dasharray="7 6"/>']
    return "".join(out)
