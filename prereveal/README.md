# Pre-reveal loop

12-second, 1080x1080, 24 fps camcorder-style loop: a backlit, black silhouette of a
lumpy, swollen head (sample #1's skull, ear and nose from the trait generator) on green
VHS footage with REC/timecode overlay, scanlines, streaks and glitch bands. During two
glitches the silhouette flickers to other heads (patchy tufts, backwards cap, comb-over)
to hint at the variety. Audio: mains hum, a low drone, a heartbeat and glitch static.

```bash
mkdir -p /tmp/sil /tmp/pre
python3 prereveal/make_silhouettes.py generator /tmp/sil   # head/body SVG masks per sample
node prereveal/render_masks.js /tmp/sil                    # -> transparent PNG masks
python3 prereveal/animate.py /tmp/sil /tmp/pre             # -> /tmp/pre/prereveal.mp4
python3 prereveal/animate.py /tmp/sil /tmp/pre --preview   # a few still frames only
```
The committed `output/prereveal/prereveal.mp4` is that render re-encoded at CRF 26 (~8 MB).
