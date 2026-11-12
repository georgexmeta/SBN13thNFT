"""Claymation look: turns the flat cartoon layers into lit, slightly lumpy clay.

Every drawn part (skull, ear, eyes, nose, mask, shirt, fist, weapon...) is wrapped
in its own filter, so each reads as a separate piece of modelling clay: edges
wobble a little, the piece is lit as a soft bevelled lump with a glossy
highlight, it gets a fingerprint-grain texture and casts a soft shadow. The hard
black ink outlines become faint pressed-in grooves.
"""
import re

FILTERS = """<defs>
<filter id="clay" x="-15%" y="-15%" width="130%" height="130%" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="0.018" numOctaves="2" seed="4" result="warp"/>
  <feDisplacementMap in="SourceGraphic" in2="warp" scale="7" xChannelSelector="R" yChannelSelector="G" result="src"/>
  <feGaussianBlur in="src" stdDeviation="1.3" result="soft"/>
  <feGaussianBlur in="src" stdDeviation="11" result="body"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.09" numOctaves="3" seed="11" result="dabs"/>
  <feColorMatrix in="dabs" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.18 0 0 0 0" result="dabsA"/>
  <feComposite in="dabsA" in2="src" operator="in" result="dabsIn"/>
  <feGaussianBlur in="src" stdDeviation="38" result="dome"/>
  <feComposite in="body" in2="dome" operator="arithmetic" k1="0" k2="0.55" k3="0.7" k4="0" result="form"/>
  <feComposite in="dabsIn" in2="form" operator="arithmetic" k1="0" k2="1" k3="1" k4="0" result="bump"/>
  <feDiffuseLighting in="bump" surfaceScale="16" diffuseConstant="1.1" lighting-color="#fff6ec" result="diff">
    <feDistantLight azimuth="300" elevation="46"/></feDiffuseLighting>
  <feSpecularLighting in="form" surfaceScale="16" specularConstant="0.22" specularExponent="12" lighting-color="#fff4e6" result="spec">
    <feDistantLight azimuth="300" elevation="55"/></feSpecularLighting>
  <feComposite in="soft" in2="diff" operator="arithmetic" k1="1.3" k2="0" k3="0" k4="0" result="lit"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" seed="9" result="noise"/>
  <feColorMatrix in="noise" type="saturate" values="0" result="grain"/>
  <feComposite in="lit" in2="grain" operator="arithmetic" k1="0" k2="1" k3="0.08" k4="-0.04" result="grainy"/>
  <feComposite in="grainy" in2="spec" operator="arithmetic" k1="0" k2="1" k3="0.5" k4="0" result="shiny"/>
  <feComposite in="shiny" in2="src" operator="in" result="piece"/>
  <feGaussianBlur in="src" stdDeviation="6" result="sb"/>
  <feOffset in="sb" dx="-6" dy="9" result="so"/>
  <feColorMatrix in="so" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.32 0" result="shadow"/>
  <feMerge><feMergeNode in="shadow"/><feMergeNode in="piece"/></feMerge>
</filter>
<filter id="claybg" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="0.6" numOctaves="2" seed="2" result="noise"/>
  <feColorMatrix in="noise" type="saturate" values="0" result="grain"/>
  <feGaussianBlur in="SourceGraphic" stdDeviation="2.5" result="sb"/>
  <feComposite in="sb" in2="grain" operator="arithmetic" k1="0" k2="1" k3="0.06" k4="-0.03"/>
</filter>
<radialGradient id="vignette" cx="0.55" cy="0.45" r="0.75">
  <stop offset="0.55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.45"/>
</radialGradient>
</defs>"""

_INK = re.compile(r'stroke="#111(?:111)?"')


def soften(s):
    # ink outlines -> faint grooves pressed into the clay
    return _INK.sub('stroke="#1a0f0a" stroke-opacity="0.22"', s)


def claify(layers):
    """layers[0] is the background; group markers ('<g ...>' / '</g>') pass through."""
    out = [FILTERS, f'<g filter="url(#claybg)">{soften(layers[0])}</g>']
    for part in layers[1:]:
        if not part:
            continue
        if part == "</g>" or (part.startswith("<g transform") and part.endswith(">") and part.count("<") == 1):
            out.append(part)
        else:
            out.append(f'<g filter="url(#clay)">{soften(part)}</g>')
    out.append('<rect width="1000" height="1000" fill="url(#vignette)" pointer-events="none"/>')
    return out
