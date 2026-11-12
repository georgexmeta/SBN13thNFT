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
HOLD_T = "translate(250 965) rotate(-12) scale(1.3)"
# back-slung weapons run from behind the far hip up past the near shoulder
SLING_T = {"Pitchfork": "translate(560 1120) rotate(-24)",
           "Weed Whacker": "translate(502 1337) rotate(-28)"}


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
    """Fist around a vertical grip at the origin, forearm and sleeve below."""
    dark = shade(skin, 0.75)
    arm = (f'<path d="M -48 30 C -55 90 -62 160 -66 260 L 70 260 C 66 160 60 90 52 30 Z" '
           f'fill="{skin}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
           f'<path d="M -48 30 C -55 90 -62 160 -66 260 L -30 260 C -28 160 -26 90 -20 40 Z" fill="{dark}"/>')
    if sleeve:
        arm += (f'<path d="M -78 120 C -70 112 70 112 82 120 L 92 260 L -88 260 Z" fill="{sleeve}" '
                f'stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<path d="M -78 120 C -70 112 70 112 82 120 L 84 142 C 60 134 -60 134 -80 142 Z" fill="#000" opacity="0.25"/>')
    fist = (f'<path d="M -52 -38 C -60 -10 -58 30 -46 46 C -10 56 30 56 58 44 C 70 20 70 -20 60 -40 '
            f'C 30 -50 -20 -50 -52 -38 Z" fill="{skin}" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
            # knuckle shading on the back of the hand
            f'<path d="M -52 -38 C -60 -10 -58 30 -46 46 C -36 48 -30 40 -32 20 C -36 0 -36 -20 -30 -42 Z" fill="{dark}"/>'
            # curled fingers on the front of the grip
            + "".join(f'<path d="M 18 {y} C 50 {y - 4} 64 {y + 4} 62 {y + 18}" fill="none" stroke="{OUT}" '
                      f'stroke-width="5" stroke-linecap="round"/>' for y in (-34, -12, 10, 30))
            # thumb wrapped over the top
            + f'<path d="M -46 -30 C -30 -54 10 -56 34 -40 C 40 -30 30 -24 18 -26 C 0 -30 -24 -24 -40 -16 Z" '
              f'fill="{skin}" stroke="{OUT}" stroke-width="6" stroke-linejoin="round"/>'
            # dirty fingernail and a scab
            + f'<path d="M 22 -40 C 30 -44 38 -40 36 -32" fill="none" stroke="#5a4a2a" stroke-width="4"/>'
            + f'<circle cx="-20" cy="20" r="6" fill="{BLOOD}" opacity="0.7"/>')
    return arm, fist


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
    shaft = (f'<rect x="-11" y="-760" width="22" height="900" rx="10" fill="#9aa0a6" stroke="{OUT}" stroke-width="{SW}"/>'
             f'<path d="M -3 -740 L -3 120" stroke="#e1e4e7" stroke-width="5"/>')
    # D-handle sticking off the shaft
    handle = (f'<path d="M 0 -520 C 70 -540 110 -500 100 -440 C 92 -400 40 -400 0 -420" fill="none" '
              f'stroke="{OUT}" stroke-width="26" stroke-linecap="round"/>'
              f'<path d="M 0 -520 C 70 -540 110 -500 100 -440 C 92 -400 40 -400 0 -420" fill="none" '
              f'stroke="#2d2d2d" stroke-width="14" stroke-linecap="round"/>')
    # engine at the top end, poking up above the shoulder
    engine = (f'<path d="M -70 -760 C -80 -830 -60 -900 0 -910 C 60 -905 90 -850 80 -770 C 60 -745 -50 -742 -70 -760 Z" '
              f'fill="#e07a1f" stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round"/>'
              f'<path d="M -70 -760 C -80 -830 -60 -900 0 -910 C -30 -880 -40 -820 -36 -752 Z" fill="#000" opacity="0.2"/>'
              f'<rect x="-38" y="-870" width="70" height="60" rx="10" fill="#2d2d2d" stroke="{OUT}" stroke-width="5"/>'
              + "".join(f'<path d="M -30 {y} L 24 {y}" stroke="#555" stroke-width="5"/>' for y in (-858, -842, -826))
              # fuel cap, pull cord
              + f'<circle cx="52" cy="-800" r="14" fill="#2d2d2d" stroke="{OUT}" stroke-width="5"/>'
              f'<path d="M -66 -800 C -100 -800 -110 -780 -112 -760" fill="none" stroke="{OUT}" stroke-width="4"/>'
              f'<rect x="-130" y="-764" width="38" height="16" rx="8" fill="#2d2d2d" stroke="{OUT}" stroke-width="4"/>'
              # grime and a splash of blood on the housing
              f'<ellipse cx="30" cy="-880" rx="18" ry="8" fill="#3b2a18" opacity="0.4"/>'
              + _blood([(-50, -790, 7), (-36, -776, 4)]))
    return shaft + handle + engine


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
