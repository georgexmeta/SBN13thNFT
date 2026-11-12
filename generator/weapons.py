"""Weapon trait layers.

Coordinates are body coordinates (the same space as the torso, before the
whole character is shifted up by 55px).

Hand-held weapons are drawn in a local frame with the grip at (0, 0) and the
business end pointing up (-y). A fist wraps the grip and a sleeved forearm
comes up from the bottom edge, in front of the near (viewer-left) shoulder.

Long weapons are slung across the back: they are drawn behind everything,
poke out above the near shoulder, and a strap crosses the chest.
"""
from traits import OUT, SW, shade

HELD = ["Machete", "Hunting Knife", "Butcher Knife", "Fish Hook", "Golden Machete"]
SLUNG = ["Pitchfork", "Weed Whacker"]
WEAPONS = ["None"] + HELD + SLUNG

STEEL = "#c7cdd2"
STEEL_DARK = "#8d959c"
RUST = "#8a4a22"
BLOOD = "#8e1414"
WOOD = "#7a4a25"

# where the fist sits and how the weapon leans (outward, away from the face)
HOLD_T = "translate(345 950) rotate(-6) scale(1.2)"
# back-slung weapons run from behind the far hip up past the near shoulder
SLING_T = {"Pitchfork": "translate(560 1120) rotate(-24)",
           "Weed Whacker": "translate(422 1411) rotate(-20)"}


def _blood(points):
    out = []
    for (x, y, r) in points:
        out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{BLOOD}"/>')
    return "".join(out)


def _wood_grip(y0, y1, w, color=WOOD, rivets=True):
    """Handle from y0 (bottom) to y1 (top), centred on x=0."""
    h = y0 - y1
    out = (f'<rect x="{-w / 2}" y="{y1}" width="{w}" height="{h}" rx="{w * 0.35}" fill="{color}" '
           f'stroke="{OUT}" stroke-width="6"/>'
           f'<path d="M {-w / 2 + 6} {y1 + 8} L {-w / 2 + 6} {y0 - 8}" stroke="{shade(color, 1.35)}" stroke-width="4" stroke-linecap="round"/>')
    if rivets:
        for y in (y1 + h * 0.2, y0 - h * 0.2):
            out += f'<circle cx="0" cy="{y:.0f}" r="5" fill="#d9d2b8" stroke="{OUT}" stroke-width="2.5"/>'
    return out


def _fist(skin, sleeve):
    """Character's RIGHT fist held in front of the chest, weapon pointing up.

    Matches George's reference photo: the forearm comes across the body
    from the near side (lower-left), the back of the hand and wrist face
    out on the left, the knuckles run along the top, the four fingers curl
    down the inside (right) of the grip toward the chest, and the thumb
    wraps over the top with its tip pointing in.
    """
    dark = shade(skin, 0.72)
    mid = shade(skin, 0.86)
    light = shade(skin, 1.2)
    vein = shade(skin, 0.7)
    vein = "#%02x%02x%02x" % (int(vein[1:3], 16) * 85 // 100, int(vein[3:5], 16) * 90 // 100,
                              min(255, int(vein[5:7], 16) * 120 // 100))
    # forearm crossing the chest from the lower-left
    arm = (f'<path d="M -100 -40 L -520 110 L -520 280 L -100 64 Z" fill="{skin}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
           # cel shadow along the underside, and the shadow the fist casts on the wrist
           f'<path d="M -100 26 C -200 70 -360 140 -520 200 L -520 280 L -100 64 Z" fill="{dark}"/>'
           f'<path d="M -100 -40 L -150 -22 C -146 0 -140 30 -128 52 L -100 64 Z" fill="{dark}" opacity="0.6"/>'
           # top-edge highlight
           f'<path d="M -150 -14 L -230 14" stroke="{light}" stroke-width="5" stroke-linecap="round"/>'
           # bulging veins
           f'<path d="M -230 40 C -200 30 -180 34 -150 20 C -136 14 -124 16 -112 8 M -180 32 C -170 46 -150 50 -130 46" '
           f'fill="none" stroke="{OUT}" stroke-width="7" stroke-linecap="round" opacity="0.7"/>'
           f'<path d="M -230 40 C -200 30 -180 34 -150 20 C -136 14 -124 16 -112 8 M -180 32 C -170 46 -150 50 -130 46" '
           f'fill="none" stroke="{vein}" stroke-width="3.5" stroke-linecap="round"/>'
           # wrist bone
           f'<path d="M -132 50 C -124 62 -112 66 -104 60" fill="none" stroke="{OUT}" stroke-width="3.5" stroke-linecap="round"/>'
           # scratched cut held shut with crude stitches
           f'<path d="M -200 86 C -180 80 -160 72 -140 66" fill="none" stroke="{BLOOD}" stroke-width="5" stroke-linecap="round"/>'
           + "".join(f'<path d="M {x - 4} {y - 9} L {x + 4} {y + 9}" stroke="{OUT}" stroke-width="3" stroke-linecap="round"/>'
                     for x, y in ((-190, 83), (-172, 77), (-154, 71)))
           # arm hair
           + "".join(f'<path d="M {x} {y} q -4 -8 -11 -9" fill="none" stroke="{OUT}" stroke-width="2.2" stroke-linecap="round"/>'
                     for x, y in ((-164, -4), (-190, 4), (-176, 16), (-204, 18)))
           )
    if sleeve:
        arm += (f'<path d="M -226 -10 C -220 40 -216 90 -208 138 L -560 340 L -560 40 Z" fill="{sleeve}" '
                f'stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<path d="M -226 -10 C -220 40 -216 90 -208 138 L -232 150 C -240 100 -244 50 -250 0 Z" fill="#000" opacity="0.28"/>'
                # rolled-up cuff fold and frayed threads
                f'<path d="M -244 -4 C -238 44 -234 92 -226 142" fill="none" stroke="{OUT}" stroke-width="4"/>'
                f'<path d="M -212 120 l 10 8 M -214 100 l 9 4 M -218 30 l 10 -2" stroke="{OUT}" stroke-width="2.5" stroke-linecap="round"/>')
    # back of the hand, wrist on the left, knuckle ridge along the top
    back_d = ("M 22 -60 C -10 -72 -60 -66 -96 -46 C -112 -38 -118 -26 -118 -12 "
              "L -114 58 C -80 70 -40 70 -6 60 Z")
    back = (f'<path d="{back_d}" fill="{skin}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
            f'<path d="M -118 20 L -114 58 C -80 70 -40 70 -6 60 L -4 34 C -40 40 -80 38 -118 20 Z" fill="{dark}"/>'
            # tendons running from the wrist to the knuckles
            f'<path d="M -100 -14 C -70 -26 -40 -36 -16 -42 M -100 8 C -70 0 -40 -8 -18 -12 M -98 26 C -70 22 -44 18 -20 16" '
            f'fill="none" stroke="{mid}" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M -80 -50 C -50 -62 -20 -64 6 -60" fill="none" stroke="{light}" stroke-width="5" stroke-linecap="round"/>'
            # wrinkles where the wrist bends
            f'<path d="M -108 -20 C -112 -6 -112 8 -108 20 M -100 -10 C -103 0 -103 10 -100 18" fill="none" stroke="{OUT}" stroke-width="2.5" stroke-linecap="round"/>'
            # grime, a scab, a bruise and hairs on the back of the hand
            f'<circle cx="-60" cy="20" r="6" fill="{BLOOD}" opacity="0.8"/>'
            f'<path d="M -66 14 l 12 12" stroke="#4a0e0e" stroke-width="2"/>'
            f'<ellipse cx="-40" cy="-20" rx="16" ry="10" fill="#6b4a7a" opacity="0.25"/>'
            f'<ellipse cx="-30" cy="44" rx="16" ry="6" fill="#3b2a18" opacity="0.4"/>'
            f'<ellipse cx="-84" cy="40" rx="10" ry="5" fill="#3b2a18" opacity="0.35"/>'
            + "".join(f'<path d="M {x} {y} q -3 -6 -9 -7" fill="none" stroke="{OUT}" stroke-width="2" stroke-linecap="round"/>'
                      for x, y in ((-88, -30), (-70, -34), (-78, -14), (-60, -24))))
    # fingers curled down the inside of the grip; each roll's rounded right
    # end is the bent middle joint, the fingertip is tucked out of sight
    fingers = [(30, 24, -16, 40), (4, 28, -14, 50), (-24, 30, -12, 54), (-54, 30, -10, 52)]
    f_svg = ""
    for i, (y, h, x0, x1) in enumerate(fingers):
        r = h / 2
        fill = mid if i == 0 else skin  # pinky sits in shadow
        f_svg += (f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="{h}" rx="{r:.1f}" fill="{fill}" '
                  f'stroke="{OUT}" stroke-width="6"/>'
                  f'<path d="M {x0 + 8} {y + h - 6} L {x1 - r:.0f} {y + h - 6}" stroke="{dark if i == 0 else mid}" stroke-width="7" stroke-linecap="round"/>'
                  # knuckle bump where the finger meets the back of the hand
                  f'<ellipse cx="{x0 + 2}" cy="{y + h * 0.35:.0f}" rx="5" ry="4" fill="{light}"/>'
                  # crease of the middle joint, with wrinkle lines
                  f'<path d="M {x0 + 26} {y + 6} C {x0 + 22} {y + h * 0.4:.0f} {x0 + 22} {y + h * 0.6:.0f} {x0 + 26} {y + h - 6}" '
                  f'fill="none" stroke="{OUT}" stroke-width="3.5" stroke-linecap="round"/>'
                  f'<path d="M {x0 + 38} {y + 7} L {x1 - 14} {y + 7}" stroke="{light}" stroke-width="4" stroke-linecap="round"/>'
                  # dirty nail of the tucked fingertip peeking out at the bottom of the curl
                  f'<path d="M {x1 - 16} {y + h - 2} C {x1 - 12} {y + h + 4} {x1 - 4} {y + h + 2} {x1 - 2} {y + h - 6}" '
                  f'fill="#c9a98a" stroke="{OUT}" stroke-width="2.5"/>'
                  f'<path d="M {x1 - 14} {y + h + 1} C {x1 - 10} {y + h + 3} {x1 - 6} {y + h + 2} {x1 - 4} {y + h - 2}" '
                  f'fill="none" stroke="#3b2a18" stroke-width="2.5"/>')
    # thumb wraps over the top of the grip, tip pointing in toward the chest
    thumb = (f'<path d="M -90 -44 C -70 -76 -10 -88 34 -76 C 56 -70 62 -56 52 -48 C 30 -44 0 -50 -30 -44 '
             f'C -50 -40 -70 -34 -84 -28 Z" fill="{skin}" stroke="{OUT}" stroke-width="6" stroke-linejoin="round"/>'
             # thumb's own shadow underside and the shadow it casts on the index finger
             f'<path d="M -84 -30 C -60 -40 -20 -50 20 -48 C 36 -48 48 -48 52 -48 C 30 -42 0 -46 -30 -42 C -50 -38 -70 -32 -84 -28 Z" fill="{mid}"/>'
             f'<path d="M -6 -46 C 14 -44 34 -44 50 -46 L 46 -38 C 30 -36 10 -38 -6 -40 Z" fill="#000" opacity="0.18"/>'
             f'<path d="M 30 -76 C 44 -76 56 -68 56 -58 C 46 -56 34 -60 26 -66 Z" fill="#c9a98a" stroke="{OUT}" stroke-width="3"/>'
             f'<path d="M 32 -70 C 40 -68 46 -64 50 -60" fill="none" stroke="#3b2a18" stroke-width="3.5"/>'
             f'<path d="M -50 -70 C -20 -80 10 -82 28 -78" fill="none" stroke="{light}" stroke-width="4" stroke-linecap="round"/>'
             # knuckle crease of the thumb
             f'<path d="M -6 -50 C -10 -58 -10 -66 -4 -74 M 2 -52 C -1 -60 -1 -66 3 -72" fill="none" stroke="{OUT}" stroke-width="2.5" stroke-linecap="round"/>'
             f'<ellipse cx="-50" cy="-60" rx="10" ry="4" fill="#3b2a18" opacity="0.35"/>')
    return arm, back + f_svg + thumb


def _golden_machete():
    gold = ('<defs><linearGradient id="goldblade" x1="0" x2="1"><stop offset="0" stop-color="#9c7414"/>'
            '<stop offset="0.5" stop-color="#ffd75a"/><stop offset="1" stop-color="#c99a24"/></linearGradient></defs>')
    svg = _machete().replace(f'fill="{STEEL}"', 'fill="url(#goldblade)"').replace(f'fill="{STEEL_DARK}"', 'fill="#a87c18"')
    svg = svg.replace('fill="#2f2f2f"', 'fill="#3a1414"').replace('fill="#3a3a3a"', 'fill="#d4a017"')
    sparkle = "".join(f'<path d="M {x} {y - 14} L {x + 4} {y - 4} L {x + 14} {y} L {x + 4} {y + 4} L {x} {y + 14} L {x - 4} {y + 4} L {x - 14} {y} L {x - 4} {y - 4} Z" fill="#fff8d0" stroke="#111" stroke-width="2"/>'
                      for x, y in ((40, -470), (-4, -250)))
    return gold + svg + sparkle


def _machete():
    blade = ("M -16 -70 L 22 -70 C 36 -200 44 -330 52 -430 C 40 -470 10 -500 -18 -505 "
             "C -20 -380 -18 -220 -16 -70 Z")
    return (f'<path d="{blade}" fill="{STEEL}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
            # spine shadow and a bright cutting edge
            f'<path d="M -16 -70 C -18 -220 -20 -380 -18 -505 C -8 -500 -2 -495 4 -488 C 0 -380 -2 -220 -2 -70 Z" fill="{STEEL_DARK}"/>'
            f'<path d="M 18 -90 C 30 -210 38 -330 44 -425" fill="none" stroke="#f4f6f7" stroke-width="5" stroke-linecap="round"/>'
            # rust and blood
            f'<ellipse cx="6" cy="-160" rx="9" ry="16" fill="{RUST}" opacity="0.7"/>'
            f'<ellipse cx="14" cy="-300" rx="7" ry="12" fill="{RUST}" opacity="0.6"/>'
            f'<path d="M 30 -380 C 44 -400 50 -420 46 -440 C 30 -430 20 -410 22 -390 Z" fill="{BLOOD}"/>'
            + _blood([(36, -350, 6), (26, -340, 4), (40, -330, 3)])
            + f'<rect x="-26" y="-80" width="56" height="16" rx="5" fill="#3a3a3a" stroke="{OUT}" stroke-width="5"/>'
            + _wood_grip(60, -66, 36, "#2f2f2f"))


def _hunting_knife():
    blade = ("M -16 -60 L 20 -60 C 26 -130 26 -190 18 -250 C 6 -262 -6 -265 -14 -268 "
             "C -6 -240 -2 -220 -6 -200 C -14 -150 -16 -100 -16 -60 Z")
    return (f'<path d="{blade}" fill="{STEEL}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
            f'<path d="M -14 -66 C -14 -110 -10 -160 -4 -200 L 4 -200 C 2 -150 0 -110 0 -66 Z" fill="{STEEL_DARK}"/>'
            # serrated spine
            f'<path d="M -16 -80 l -6 -8 l 6 -6 l -6 -8 l 6 -6 l -6 -8 l 6 -6" fill="none" stroke="{OUT}" stroke-width="4" stroke-linejoin="round"/>'
            f'<path d="M 16 -80 C 20 -140 20 -190 14 -240" fill="none" stroke="#f4f6f7" stroke-width="4" stroke-linecap="round"/>'
            + _blood([(10, -200, 7), (14, -180, 4), (6, -170, 3)])
            # brass guard and stacked-leather handle
            + f'<path d="M -40 -72 L 44 -72 L 40 -56 L -36 -56 Z" fill="#b8913a" stroke="{OUT}" stroke-width="5" stroke-linejoin="round"/>'
            + _wood_grip(58, -58, 34, "#6b4a2b", rivets=False)
            + "".join(f'<path d="M -17 {y} L 17 {y}" stroke="{OUT}" stroke-width="2.5"/>' for y in range(-44, 56, 12))
            + f'<circle cx="0" cy="66" r="12" fill="#b8913a" stroke="{OUT}" stroke-width="5"/>')


def _butcher_knife():
    blade = ("M -20 -64 L 30 -64 L 96 -80 C 102 -180 104 -280 96 -360 "
             "C 70 -378 20 -380 -20 -370 Z")
    return (f'<path d="{blade}" fill="{STEEL}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
            f'<path d="M -20 -64 L -20 -370 L -4 -372 L -4 -64 Z" fill="{STEEL_DARK}"/>'
            f'<path d="M 88 -95 C 94 -190 96 -270 90 -350" fill="none" stroke="#f4f6f7" stroke-width="5" stroke-linecap="round"/>'
            # hanging hole near the spine
            f'<circle cx="18" cy="-330" r="12" fill="#3a3a3a" stroke="{OUT}" stroke-width="5"/>'
            # rust bloom and blood smeared along the edge
            f'<ellipse cx="40" cy="-150" rx="22" ry="14" fill="{RUST}" opacity="0.55"/>'
            f'<path d="M 96 -200 C 70 -205 60 -230 70 -260 C 80 -280 98 -280 100 -260 Z" fill="{BLOOD}"/>'
            f'<path d="M 72 -258 C 66 -240 64 -225 70 -210" fill="none" stroke="{BLOOD}" stroke-width="7" stroke-linecap="round"/>'
            + _blood([(54, -280, 6), (40, -300, 4), (60, -312, 3), (30, -250, 5)])
            + _wood_grip(60, -66, 38))


def _fish_hook():
    """A huge rusty meat/fish hook held by its T-handle."""
    hook = "M 0 -60 L 0 -300 C 0 -375 -100 -385 -104 -300 C -106 -255 -84 -222 -58 -234"
    return (f'<path d="{hook}" fill="none" stroke="{OUT}" stroke-width="30" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{hook}" fill="none" stroke="#8f8c84" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M -4 -80 L -4 -290" stroke="#c9c6bc" stroke-width="5" stroke-linecap="round"/>'
            # barb
            f'<path d="M -58 -234 L -48 -272 L -80 -242 Z" fill="#8f8c84" stroke="{OUT}" stroke-width="6" stroke-linejoin="round"/>'
            # rust patches
            f'<path d="M 0 -140 L 0 -180 M -92 -340 C -98 -320 -101 -305 -101 -295" fill="none" stroke="{RUST}" stroke-width="14" stroke-linecap="round" opacity="0.8"/>'
            # something dripping off the point
            f'<path d="M -66 -232 C -72 -214 -68 -200 -74 -184" fill="none" stroke="{BLOOD}" stroke-width="7" stroke-linecap="round"/>'
            + _blood([(-74, -176, 6), (-84, -250, 5)])
            # wooden T-handle
            + f'<rect x="-14" y="-70" width="28" height="140" rx="10" fill="{WOOD}" stroke="{OUT}" stroke-width="6"/>'
            + f'<rect x="-48" y="58" width="96" height="26" rx="10" fill="{WOOD}" stroke="{OUT}" stroke-width="6"/>')


def held(kind, skin, sleeve):
    """Front layer: forearm, weapon, fist."""
    if kind not in HELD:
        return ""
    weapon = {"Machete": _machete, "Hunting Knife": _hunting_knife,
              "Butcher Knife": _butcher_knife, "Fish Hook": _fish_hook,
              "Golden Machete": _golden_machete}[kind]()
    arm, fist = _fist(skin, sleeve)
    return f'<g transform="{HOLD_T}">' + arm + weapon + fist + '</g>'


# --------------------------------------------------------------------------
# Back-slung weapons
# --------------------------------------------------------------------------
def _pitchfork():
    out = (f'<rect x="-13" y="-860" width="26" height="980" rx="12" fill="{WOOD}" stroke="{OUT}" stroke-width="{SW}"/>'
           f'<path d="M -5 -840 L -5 100" stroke="{shade(WOOD, 1.35)}" stroke-width="5"/>'
           # metal ferrule and crossbar
           f'<rect x="-20" y="-900" width="40" height="60" rx="6" fill="#6f716c" stroke="{OUT}" stroke-width="6"/>'
           f'<path d="M -95 -930 C -60 -905 60 -905 95 -930 L 95 -912 C 60 -885 -60 -885 -95 -912 Z" '
           f'fill="#6f716c" stroke="{OUT}" stroke-width="6" stroke-linejoin="round"/>')
    for x, bend in ((-88, -10), (-30, -4), (30, 4), (88, 10)):
        t = f"M {x} -915 C {x} -980 {x + bend} -1040 {x + bend * 1.6:.0f} -1090"
        out += (f'<path d="{t}" fill="none" stroke="{OUT}" stroke-width="20" stroke-linecap="round"/>'
                f'<path d="{t}" fill="none" stroke="#7d7f7a" stroke-width="10" stroke-linecap="round"/>')
    out += (f'<path d="M -30 -960 L -30 -1000 M 88 -940 L 92 -980" stroke="{RUST}" stroke-width="10" stroke-linecap="round" opacity="0.8"/>'
            + _blood([(-88, -1060, 7), (-34, -1030, 5), (90, -1000, 6)]))
    return out


def _weed_whacker():
    """String trimmer: long shaft, loop handle, bent neck with the spool head,
    half-moon guard and trimmer line at the top end (poking over the shoulder).
    The engine end hangs down behind the body."""
    shaft = (f'<rect x="-11" y="-830" width="22" height="960" rx="10" fill="#9aa0a6" stroke="{OUT}" stroke-width="{SW}"/>'
             f'<path d="M -3 -810 L -3 120" stroke="#e1e4e7" stroke-width="5"/>')
    # loop (bike) handle clamped onto the shaft
    loop = "M 0 -730 C -70 -760 -120 -710 -100 -660 C -86 -624 -30 -632 0 -660"
    handle = (f'<path d="{loop}" fill="none" stroke="{OUT}" stroke-width="26" stroke-linecap="round"/>'
              f'<path d="{loop}" fill="none" stroke="#2d2d2d" stroke-width="14" stroke-linecap="round"/>'
              f'<rect x="-18" y="-740" width="36" height="90" rx="8" fill="#e07a1f" stroke="{OUT}" stroke-width="5"/>')
    # gearbox and bent neck
    neck = (f'<rect x="-20" y="-860" width="40" height="50" rx="8" fill="#3a3a3a" stroke="{OUT}" stroke-width="6"/>'
            f'<path d="M 0 -846 L 42 -918" stroke="{OUT}" stroke-width="30" stroke-linecap="round"/>'
            f'<path d="M 0 -846 L 42 -918" stroke="#3a3a3a" stroke-width="18" stroke-linecap="round"/>')
    # cutter head in a frame rotated so the neck comes in along +y
    head = ('<g transform="translate(56 -940) rotate(30) scale(1.35)">'
            # half-moon guard on the shaft side
            f'<path d="M -80 0 A 80 46 0 0 0 80 0 L 80 -8 L -80 -8 Z" fill="#e07a1f" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
            f'<path d="M -64 10 A 64 32 0 0 0 64 10 M -30 6 L -26 38 M 30 6 L 26 38" fill="none" stroke="#000" stroke-width="8" opacity="0.2"/>'
            # trimmer line whipping out of the spool
            f'<path d="M -30 -10 C -60 -16 -80 -10 -100 -22 M 30 -10 C 60 -6 80 -18 102 -10" fill="none" stroke="{OUT}" stroke-width="11" stroke-linecap="round"/>'
            f'<path d="M -30 -10 C -60 -16 -80 -10 -100 -22 M 30 -10 C 60 -6 80 -18 102 -10" fill="none" stroke="#b5e61d" stroke-width="5" stroke-linecap="round"/>'
            # spool
            f'<ellipse cx="0" cy="-10" rx="38" ry="14" fill="#2d2d2d" stroke="{OUT}" stroke-width="6"/>'
            f'<ellipse cx="0" cy="-22" rx="22" ry="8" fill="#555" stroke="{OUT}" stroke-width="4"/>'
            f'<ellipse cx="0" cy="-30" rx="9" ry="4" fill="#9aa0a6" stroke="{OUT}" stroke-width="3"/>'
            '</g>')
    # grass clippings and blood stuck to the guard
    gunk = (_blood([(10, -880, 7), (70, -880, 5), (30, -950, 4)])
            + f'<path d="M -10 -900 l 10 -14 M 90 -900 l 8 -16 M 60 -870 l 14 -6" stroke="#5f8a2a" stroke-width="5" stroke-linecap="round"/>')
    return shaft + handle + neck + head + gunk


def slung(kind):
    """Back layer, drawn right after the background."""
    if kind not in SLUNG:
        return ""
    inner = _pitchfork() if kind == "Pitchfork" else _weed_whacker()
    return f'<g transform="{SLING_T[kind]}">{inner}</g>'


def sling_strap(kind):
    """Strap across the chest, drawn over the clothing."""
    if kind not in SLUNG:
        return ""
    d = "M 300 846 C 380 900 470 990 540 1080 L 600 1080 C 520 970 420 880 330 832 Z"
    if kind == "Pitchfork":
        # twisted rope
        rope = "M 312 840 C 390 900 480 990 568 1080"
        return (f'<path d="{rope}" fill="none" stroke="{OUT}" stroke-width="26" stroke-linecap="round"/>'
                f'<path d="{rope}" fill="none" stroke="#c9a96a" stroke-width="16" stroke-linecap="round"/>'
                f'<path d="{rope}" fill="none" stroke="#8a6f3c" stroke-width="16" stroke-dasharray="6 12"/>')
    return (f'<path d="{d}" fill="#2d2d2d" stroke="{OUT}" stroke-width="6" stroke-linejoin="round"/>'
            f'<rect x="402" y="900" width="40" height="30" rx="5" transform="rotate(42 422 915)" '
            f'fill="none" stroke="#b9b9b9" stroke-width="6"/>')
