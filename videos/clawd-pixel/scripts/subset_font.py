#!/usr/bin/env python3
"""Subset Fusion Pixel (OFL, 12px bitmap-style CJK font) to the glyphs index.html uses.

Source TTF: `npm pack @fontpkg/fusion-pixel` → package/fusion-pixel.ttf
Usage: python3 scripts/subset_font.py /path/to/fusion-pixel.ttf
Re-run after adding new text. The font is drawn on a 12px grid (1200 upm / 100 per pixel),
so keep every font-size a multiple of 12 to land glyph pixels on whole screen pixels.
"""
import os, re, sys
from fontTools import subset

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html = open(os.path.join(ROOT, "index.html"), encoding="utf8").read()
text = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>|<[^>]+>", "", html)
# strings the timeline script injects as text (scenery code glyphs)
text += "{ }</>fn()=>[ ]//" + "".join(chr(c) for c in range(0x20, 0x7F))
chars = sorted(set(text) - {"\n", "\r", "\t"})
opts = subset.Options(); opts.flavor = "woff2"; opts.layout_features = ["*"]
font = subset.load_font(sys.argv[1], opts)
sub = subset.Subsetter(opts); sub.populate(text="".join(chars)); sub.subset(font)
out = os.path.join(ROOT, "assets", "fonts", "fusion-pixel-sub.woff2")
subset.save_font(font, out, opts)
print(f"{len(chars)} glyphs -> {out} ({os.path.getsize(out)} bytes)")
