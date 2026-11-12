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

HELD = ["Machete", "Hunting Knife", "Butcher Knife", "Fish Hook"]
SLUNG = ["Pitchfork", "Weed Whacker"]
WEAPONS = ["None"] + HELD + SLUNG

STEEL = "#c7cdd2"
STEEL_DARK = "#8d959c"
RUST = "#8a4a22"
BLOOD = "#8e1414"
WOOD = "#7a4a25"

# where the fist sits and how the weapon leans (outward, away from the face)
HOLD_T = "translate(250 930) rotate(-8) scale(1.3)"
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
    """Fist wrapped around a vertical grip at the origin.

    We see the front of the fist: four stacked fingers curl around the
    handle, their tips tucked in on the left, the thumb locks over the index
    finger, and the back of the hand runs right into the wrist. The forearm
    angles down and to the right, back toward the body.
    """
    dark = shade(skin, 0.74)
    light = shade(skin, 1.18)
    # forearm runs from the wrist down-right toward the body
    arm_d = "M 28 40 L 44 270 L 158 270 L 98 10 Z"
    arm = (f'<path d="{arm_d}" fill="{skin}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
           f'<path d="M 28 40 L 44 270 L 80 270 L 56 34 Z" fill="{dark}"/>'
           f'<path d="M 70 80 C 76 120 80 150 84 180" fill="none" stroke="{dark}" stroke-width="5" stroke-linecap="round"/>')
    if sleeve:
        arm += (f'<path d="M 22 96 C 62 80 104 74 128 82 L 172 270 L 34 270 Z" fill="{sleeve}" '
                f'stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<path d="M 22 96 C 62 80 104 74 128 82 L 134 100 C 106 92 64 98 28 116 Z" fill="#000" opacity="0.28"/>')
    # back of the hand / palm mass behind the fingers, flowing into the wrist
    back = (f'<path d="M 18 -60 C 60 -66 92 -44 98 -6 C 102 26 92 44 70 52 L 30 50 Z" '
            f'fill="{skin}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
            f'<path d="M 60 -40 C 80 -20 84 10 74 40 L 92 30 C 100 6 96 -26 80 -48 Z" fill="{dark}"/>')
    # fingers: (top y, height, left end) from pinky (bottom) up to index (top)
    fingers = [(26, 26, -30), (0, 28, -40), (-28, 29, -44), (-56, 30, -44)]
    f_svg = ""
    for y, h, x0 in fingers:
        x1 = 62
        r = h / 2
        f_svg += (f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="{h}" rx="{r}" fill="{skin}" '
                  f'stroke="{OUT}" stroke-width="6"/>'
                  # knuckle crease and the shadow where the finger rolls under
                  f'<path d="M {x0 + 26} {y + 5} C {x0 + 22} {y + h * 0.4:.0f} {x0 + 22} {y + h * 0.6:.0f} {x0 + 26} {y + h - 5}" '
                  f'fill="none" stroke="{OUT}" stroke-width="3.5" stroke-linecap="round"/>'
                  f'<path d="M {x0 + 8} {y + h - 6} L {x1 - 8} {y + h - 6}" stroke="{dark}" stroke-width="6" stroke-linecap="round"/>'
                  f'<path d="M {x0 + 34} {y + 7} L {x1 - 10} {y + 7}" stroke="{light}" stroke-width="4" stroke-linecap="round"/>'
                  # grimy fingernail on the tucked-in tip
                  f'<path d="M {x0 + 5} {y + 6} C {x0 + 12} {y + 4} {x0 + 15} {y + h * 0.5:.0f} {x0 + 10} {y + h - 6}" '
                  f'fill="#6b5a3a" stroke="{OUT}" stroke-width="2.5"/>')
    # thumb comes from the back of the hand and locks over the index finger
    thumb = (f'<path d="M 92 -40 C 80 -74 40 -84 0 -74 C -22 -68 -30 -54 -20 -46 C -8 -38 20 -46 46 -42 '
             f'C 62 -40 74 -30 84 -20 Z" fill="{skin}" stroke="{OUT}" stroke-width="6" stroke-linejoin="round"/>'
             f'<path d="M -18 -66 C -10 -72 0 -72 6 -66 C 2 -58 -8 -54 -18 -58 Z" fill="#6b5a3a" stroke="{OUT}" stroke-width="2.5"/>'
             f'<path d="M 30 -70 C 50 -72 66 -66 76 -54" fill="none" stroke="{light}" stroke-width="4" stroke-linecap="round"/>'
             # scab and dirt
             f'<circle cx="40" cy="-14" r="6" fill="{BLOOD}" opacity="0.75"/>'
             f'<ellipse cx="78" cy="10" rx="10" ry="6" fill="#3b2a18" opacity="0.35"/>')
    return arm, back + f_svg + thumb


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
              "Butcher Knife": _butcher_knife, "Fish Hook": _fish_hook}[kind]()
    arm, fist = _fist(skin, sleeve)
    # the fist is drawn as a left hand and mirrored: right hand, knuckles
    # facing out (viewer-left), fingertips curling in toward the body
    m = '<g transform="scale(-1 1)">'
    return f'<g transform="{HOLD_T}">' + m + arm + '</g>' + weapon + m + fist + '</g></g>'


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
