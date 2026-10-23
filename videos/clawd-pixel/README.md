# 小克 Clawd 像素冒险 (vertical 1080×1920, 27 s)

A pixel-art short starring Clawd, the Claude Code mascot (the half-block crab from the CLI banner,
rows doubled to square pixels). No narration; an 8-bit soundtrack with SFX on every beat.

| # | time | scene |
|---|------|-------|
| 1 | 0 – 4.7 | Terminal: `$ claude` is typed, the pixels fly out and assemble into Clawd |
| 2 | 4.6 – 9.9 | Night field, speech bubble: 你好！我是小克 / 一起写代码吧！ |
| 3 | 9.7 – 17.1 | Side-scroller WORLD 1-1: collects tokens, stomps two bugs → BUG 清零！ |
| 4 | 16.9 – 23.1 | Rocket falls together block by block, Clawd boards, 3-2-1 GO! |
| 5 | 22.9 – 27 | Lands on a clay planet, plants a flag, title 小克 / CLAWD / 今天也一起造点什么吧！ |

All sprites are ASCII maps in `index.html` rendered to crisp SVG; scene changes use a 9×16 pixel wipe.
The `<script id="cues">` JSON is the single timing source for both the timeline and the audio.

```bash
python3 scripts/make_audio.py                     # regenerate assets/audio/clawd-chiptune.mp3 (numpy + ffmpeg)
python3 scripts/subset_font.py fusion-pixel.ttf   # after changing text (needs fonttools + brotli)
npm run check && npm run render
```

Font: Fusion Pixel (SIL OFL 1.1), subset to the glyphs used.
