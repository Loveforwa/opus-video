"""hfkit — shared builder for the single-file HyperFrames explainers in this repo.

Design v2 (after review of video 1): low-saturation ink palette with a sparing brass accent,
Noto Serif SC display type, official HyperFrames CSS transition recipes between every scene
(blur crossfade / focus pull / zoom-through / color dip), 3D screenshot cards, per-character
headline reveals, film grain + vignette, shadowed captions without a pill.

A video script imports Kit, declares scenes with scene-local times taken from the narration's
clause timings (audio_meta.json), then calls kit.write().
"""
import html, json, os, re, shutil

E = html.escape
SHARED = os.path.dirname(os.path.abspath(__file__))

PAL = {
    "ink": "#0B0D12", "ink2": "#11141B", "panel": "#161A22", "line": "rgba(233,230,223,.12)",
    "paper": "#E9E6DF", "muted": "#8D919B", "faint": "#5A5F6A",
    "brass": "#C9A46C", "brass_soft": "rgba(201,164,108,.22)", "steel": "#8FA3B8",
}

TRANS = {
    # official recipes from hyperframes-animation/transitions (css-dissolve, css-blur, css-scale)
    "blur": """tl.to(O,{filter:"blur(14px)",scale:1.04,opacity:0,duration:0.6,ease:"power2.inOut"},T);
tl.fromTo(N,{filter:"blur(14px)",scale:0.97,opacity:0},{filter:"blur(0px)",scale:1,opacity:1,duration:0.6,ease:"power2.inOut"},T+0.1);""",
    "focus": """tl.to(O,{filter:"blur(26px)",duration:0.7,ease:"power1.in"},T);
tl.to(O,{opacity:0,duration:0.45,ease:"power1.in"},T+0.45);
tl.fromTo(N,{opacity:0,filter:"blur(18px)"},{opacity:1,filter:"blur(18px)",duration:0.3,ease:"power1.inOut"},T+0.5);
tl.to(N,{filter:"blur(0px)",duration:0.6,ease:"power1.out"},T+0.8);""",
    "zoom": """tl.to(O,{scale:2.1,filter:"blur(12px)",opacity:0,duration:0.55,ease:"power3.in"},T);
tl.fromTo(N,{scale:0.72,filter:"blur(12px)",opacity:0},{scale:1,filter:"blur(0px)",opacity:1,duration:0.7,ease:"power3.out"},T+0.3);""",
    "dip": """tl.to(O,{opacity:0,duration:0.45,ease:"power2.in"},T);
tl.fromTo(N,{opacity:0},{opacity:1,duration:0.6,ease:"power2.out"},T+0.5);""",
    "cut": "",
}
OVERLAP = 1.4  # seconds an outgoing scene stays mounted past the next scene's start


class Kit:
    def __init__(self, root, title, pad=0.6, tail=3.0, chrome_left="", total_scenes=None):
        self.root, self.title, self.chrome_left = root, title, chrome_left
        meta = json.load(open(os.path.join(root, "audio_meta.json"), encoding="utf8"))
        self.vo = {v["frame"]: v for v in meta["voices"]}
        frames = sorted(self.vo)
        self.dur = {f: round(self.vo[f]["duration_s"] + pad, 3) for f in frames}
        self.dur[frames[-1]] = round(self.dur[frames[-1]] + tail, 3)
        acc, self.start = 0.0, {}
        for f in frames:
            self.start[f] = round(acc, 3); acc += self.dur[f]
        self.total = round(acc, 3)
        self.n_frames = total_scenes or len(frames)
        qb = os.path.join(root, "quote-boxes.json")
        self.qb = json.load(open(qb)) if os.path.exists(qb) else {}
        self.els, self.js, self.scenes = [], [], []
        self._ids = 0
        self._sync_assets()

    # ── timing ────────────────────────────────────────────────────────────────
    def S(self, f): return self.start[f]
    def D(self, f): return self.dur[f]
    def W(self, f, i): return self.vo[f]["words"][i]["start"]  # clause start (scene-local)

    # ── assets ────────────────────────────────────────────────────────────────
    def _sync_assets(self):
        dst = os.path.join(self.root, "assets", "fonts"); os.makedirs(dst, exist_ok=True)
        for fn in os.listdir(os.path.join(SHARED, "fonts")):
            shutil.copy2(os.path.join(SHARED, "fonts", fn), os.path.join(dst, fn))
        shutil.copy2(os.path.join(SHARED, "grain.png"), os.path.join(self.root, "assets", "grain.png"))

    # ── tween helpers (emit JS) ───────────────────────────────────────────────
    def tw(self, kind, sel, t, **kw):
        args = ", ".join(f"{k}:{json.dumps(v)}" for k, v in kw.items())
        self.js.append(f'{kind}("{sel}", {round(t, 3)}{", {" + args + "}" if args else ""});')

    def raw(self, line): self.js.append(line)

    # ── scenes ────────────────────────────────────────────────────────────────
    def scene(self, sid, f, t0, t1, inner, trans="blur", bg="ink", chrome=True, z=None, glow=False):
        """A timed full-frame scene. t0/t1 are scene-local seconds within frame f.
        It stays mounted OVERLAP s past t1 so the next scene's transition can play over it."""
        s = round(self.S(f) + t0, 3)
        is_last = abs((self.S(f) + t1) - self.total) < 1e-3
        d = round(t1 - t0 + (0 if is_last else OVERLAP), 3)
        zi = z if z is not None else 10 + 2 * len(self.scenes)
        ch = ""
        if chrome:
            ch = (f'<div class="chrome l">{E(self.chrome_left)}</div>'
                  f'<div class="chrome r">{f:02d} <span class="faint">/ {self.n_frames:02d}</span></div>')
        g = '<div class="glow"></div>' if glow else ""
        self.els.append(f'<section id="{sid}" class="clip scene bg-{bg}" style="z-index:{zi}" data-start="{s}" '
                        f'data-duration="{d}"><div class="sc-in" id="{sid}-in">{g}{ch}{inner}</div></section>')
        self.scenes.append({"id": sid, "start": s, "trans": trans, "z": zi, "bg": bg})
        return zi

    def video(self, vid, src, f, t0, t1, style, media_start=0, z=None, fade_in=0.6):
        zi = z if z is not None else 10 + 2 * len(self.scenes) - 1
        st = round(self.S(f) + t0, 3)
        self.els.append(f'<video id="{vid}" class="clip vid" src="{src}" muted playsinline data-start="{st}" '
                        f'data-duration="{round(t1-t0,3)}" data-media-start="{media_start}" style="{style};z-index:{zi}"></video>')
        if fade_in:
            self.js.append(f'tl.fromTo("#{vid}",{{opacity:0}},{{opacity:1,duration:{fade_in},ease:"power2.out"}},{st});')

    # ── building blocks ───────────────────────────────────────────────────────
    def shot(self, sid, img, left, top, width, key=None, src_label="", crop_x=0, view_w=1440, crop_y=0, view_h=900):
        """3D screenshot card from a 2x capture of a 1440x900 viewport, cropped to the css-px window
        (crop_x, crop_y, view_w, view_h). Quote boxes come from quote-boxes.json[key]."""
        s = width / view_w
        h = round(view_h * s)
        boxes = ""
        if key and key in self.qb:
            for i, r in enumerate(self.qb[key]["rects"]):
                boxes += (f'<div id="{sid}-hl{i}" class="hl" style="left:{(r["x"]-crop_x)*s-5:.1f}px;top:{(r["y"]-crop_y)*s-4:.1f}px;'
                          f'width:{r["w"]*s+10:.1f}px;height:{r["h"]*s+8:.1f}px"></div>')
        lab = f'<div class="src">{E(src_label)}</div>' if src_label else ""
        return (f'<div id="{sid}" class="shot" style="left:{left}px;top:{top}px;width:{width}px;height:{h}px">'
                f'<img src="{img}" alt="" style="width:{1440*s:.1f}px;left:{-crop_x*s:.1f}px;top:{-crop_y*s:.1f}px"/>{boxes}</div>'
                f'<div id="{sid}-src" class="srcwrap" style="left:{left}px;top:{top + h + 18}px">{lab}</div>')

    def hls(self, sid, key, t, gap=0.15):
        for i in range(len(self.qb.get(key, {}).get("rects", []))):
            self.tw("mark", f"#{sid}-hl{i}", t + i * gap)

    def chars(self, text, cls=""):
        """Wrap each character in a span for per-character reveals (keeps <span class=acc> markup)."""
        out, i = [], 0
        for part in re.split(r"(<[^>]+>)", text):
            if part.startswith("<"):
                out.append(part); continue
            for ch in part:
                out.append(" " if ch == " " else f'<span class="ch">{E(ch)}</span>')
        return f'<span class="chars {cls}">{"".join(out)}</span>'

    # ── output ────────────────────────────────────────────────────────────────
    def captions(self):
        caps = []
        for f, v in sorted(self.vo.items()):
            ws = v["words"]
            for i, w in enumerate(ws):
                st = self.S(f) + w["start"]
                en = self.S(f) + (ws[i + 1]["start"] if i + 1 < len(ws) else min(v["duration_s"] + 0.25, self.D(f)))
                txt = w["text"].rstrip("。")
                caps.append(f'<div class="clip cap" data-start="{round(st,3)}" data-duration="{round(en-st,3)}"><span>{E(txt)}</span></div>')
        return caps

    def audio(self, bgm=None, bgm_vol=0.14):
        out = [f'<audio id="vo{f:02d}" src="{v["path"]}" data-start="{self.S(f)}" data-duration="{v["duration_s"]}" data-volume="1"></audio>'
               for f, v in sorted(self.vo.items())]
        if bgm:
            out.append(f'<audio id="bgm" src="{bgm}" data-start="0" data-duration="{self.total}" data-volume="{bgm_vol}"></audio>')
        return out

    def transitions(self):
        for prev, nxt in zip(self.scenes, self.scenes[1:]):
            code = TRANS[nxt["trans"]]
            if not code:
                continue
            self.js.append("{ const O=\"#%s-in\", N=\"#%s-in\", T=%s;\n%s }" % (prev["id"], nxt["id"], nxt["start"], code))
            # incoming scene background fades with its content so the outgoing scene shows through
            if nxt.get("bg") == "none":
                continue
            self.js.append(f'tl.fromTo("#{nxt["id"]}", {{backgroundColor:"rgba(11,13,18,0)"}}, {{backgroundColor:"rgba(11,13,18,1)", duration:0.5, ease:"power1.inOut"}}, {nxt["start"]+0.15});')

    def grain(self):
        # deterministic grain shimmer: step the texture offset every 2 frames (15 Hz)
        steps, t, k = [], 0.0, 0
        while t < self.total:
            x, y = (k * 197) % 480, (k * 131) % 270
            steps.append(f'tl.set("#grain",{{backgroundPosition:"{-x}px {-y}px"}},{round(t,3)});')
            t += 1 / 15; k += 1
        self.js.extend(steps)

    def write(self, bgm=None, bgm_vol=0.14):
        self.transitions()
        self.grain()
        body = self.els + self.audio(bgm, bgm_vol) + self.captions()
        page = PAGE.format(title=E(self.title), css=CSS, total=self.total, body="\n".join(body),
                           helpers=JS_HELPERS, js="\n".join(self.js))
        open(os.path.join(self.root, "index.html"), "w", encoding="utf8").write(page)
        print(f"index.html · {len(self.scenes)} scenes · {self.total}s")


FONTS = "".join(
    f"@font-face{{font-family:'{fam}';src:url('assets/fonts/{file}') format('woff2');font-weight:{w};font-display:block}}"
    for fam, file, w in [
        ("Noto Serif SC", "NotoSerifSC-500.woff2", 500), ("Noto Serif SC", "NotoSerifSC-700.woff2", 700),
        ("Noto Serif SC", "NotoSerifSC-900.woff2", 900),
        ("Noto Sans SC", "NotoSansSC-400.woff2", 400), ("Noto Sans SC", "NotoSansSC-500.woff2", 500),
        ("Noto Sans SC", "NotoSansSC-700.woff2", 700),
        ("IBM Plex Mono", "IBMPlexMono-400.woff2", 400), ("IBM Plex Mono", "IBMPlexMono-500.woff2", 500)])

CSS = FONTS + """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1920px;height:1080px;overflow:hidden;background:#0B0D12}
#root{position:relative;width:1920px;height:1080px;overflow:hidden;background:#0B0D12;color:#E9E6DF;
  font-family:'Noto Sans SC',sans-serif;-webkit-font-smoothing:antialiased;text-rendering:geometricPrecision}
.clip{position:absolute;inset:0}
.scene{background:#0B0D12}
.scene.bg-none{background:transparent}
.sc-in{position:absolute;inset:0;transform-origin:50% 45%}
.bg-ink .sc-in::before{content:"";position:absolute;inset:0;background:radial-gradient(120% 90% at 30% 20%,#151925 0%,#0B0D12 60%,#07080B 100%)}
.glow{position:absolute;inset:0;background:radial-gradient(40% 40% at 70% 55%,rgba(201,164,108,.10),transparent 70%)}
.sc-in > *{position:absolute}
.vid{position:absolute;object-fit:cover}
.chrome{top:46px;font:500 14px/1 'IBM Plex Mono',monospace;letter-spacing:.18em;color:#8D919B;text-transform:uppercase}
.chrome.l{left:72px}.chrome.r{right:72px}
.faint{color:#5A5F6A}
.kicker{font:500 16px/1 'IBM Plex Mono','Noto Sans SC',monospace;letter-spacing:.2em;color:#C9A46C;text-transform:uppercase}
.kicker::before{content:"";display:inline-block;width:28px;height:1px;background:#C9A46C;vertical-align:middle;margin-right:14px}
.h{font-family:'Noto Serif SC',serif;font-weight:900;line-height:1.18;letter-spacing:.01em;color:#E9E6DF;white-space:nowrap}
.h.md{font-weight:700}
.lead{font:500 34px/1.6 'Noto Sans SC',sans-serif;color:#C9C6BF}
.acc{color:#C9A46C}
.steel{color:#8FA3B8}
.muted{color:#8D919B}
.num{font-family:'Noto Serif SC',serif;font-weight:900;line-height:1;letter-spacing:-.01em;color:#E9E6DF;font-variant-numeric:lining-nums}
.unit{font:700 30px/1.3 'Noto Sans SC',sans-serif;color:#C9C6BF}
.mono{font:500 16px/1.5 'IBM Plex Mono','Noto Sans SC',monospace;letter-spacing:.12em;color:#8D919B;text-transform:uppercase}
.rule{height:1px;background:rgba(233,230,223,.16)}
.chars{display:inline}
.ch{display:inline-block;will-change:transform,opacity,filter}
.shot{overflow:hidden;border-radius:12px;background:#F4F2EE;box-shadow:0 40px 90px rgba(0,0,0,.6),0 0 0 1px rgba(255,255,255,.08);transform-origin:50% 60%}
.shot img{position:absolute;top:0;display:block;height:auto}
.hl{position:absolute;background:rgba(201,164,108,.28);border-bottom:3px solid #C9A46C;transform-origin:left center;mix-blend-mode:multiply}
.srcwrap{position:absolute}
.src{font:500 14px/1 'IBM Plex Mono',monospace;letter-spacing:.14em;color:#8D919B;text-transform:uppercase}
.card{background:rgba(22,26,34,.86);border:1px solid rgba(233,230,223,.10);border-radius:14px;padding:28px 32px}
.pill{font:500 18px/1 'IBM Plex Mono','Noto Sans SC',monospace;letter-spacing:.12em;color:#E9E6DF;border:1px solid rgba(233,230,223,.22);border-radius:999px;padding:12px 20px;background:rgba(11,13,18,.55)}
.pill.acc{border-color:rgba(201,164,108,.6);color:#C9A46C}
.shade{inset:0;background:linear-gradient(90deg,rgba(11,13,18,.88) 0%,rgba(11,13,18,.55) 45%,rgba(11,13,18,.15) 100%)}
.shade-b{inset:0;background:linear-gradient(0deg,rgba(11,13,18,.92) 0%,rgba(11,13,18,.2) 55%,rgba(11,13,18,.1) 100%)}
#grain{position:absolute;inset:-10px;z-index:900;pointer-events:none;background:url('assets/grain.png');background-size:960px 540px;opacity:.07;mix-blend-mode:overlay}
#vignette{position:absolute;inset:0;z-index:899;pointer-events:none;background:radial-gradient(120% 100% at 50% 45%,transparent 55%,rgba(0,0,0,.55) 100%)}
#capband{position:absolute;left:0;right:0;bottom:0;height:220px;z-index:898;pointer-events:none;background:linear-gradient(0deg,rgba(0,0,0,.55),transparent)}
.cap{z-index:950;display:flex;align-items:flex-end;justify-content:center;padding-bottom:62px;pointer-events:none}
.cap span{font:500 38px/1.4 'Noto Sans SC',sans-serif;color:#F1EEE8;letter-spacing:.04em;text-shadow:0 2px 3px rgba(0,0,0,.7),0 0 24px rgba(0,0,0,.65)}
"""

JS_HELPERS = """
const tl = gsap.timeline({ paused: true });
const E3 = "power3.out";
function fade(s,t,o){o=o||{};tl.fromTo(s,{opacity:0},{opacity:1,duration:o.duration||0.6,ease:"power2.out"},t);}
function up(s,t,o){o=o||{};tl.fromTo(s,{opacity:0,y:o.y||30,filter:"blur(6px)"},{opacity:1,y:0,filter:"blur(0px)",duration:o.duration||0.8,ease:E3},t);}
function left(s,t,o){o=o||{};tl.fromTo(s,{opacity:0,x:-40,filter:"blur(6px)"},{opacity:1,x:0,filter:"blur(0px)",duration:o.duration||0.7,ease:E3},t);}
function right(s,t,o){o=o||{};tl.fromTo(s,{opacity:0,x:70,filter:"blur(6px)"},{opacity:1,x:0,filter:"blur(0px)",duration:o.duration||0.8,ease:E3},t);}
function pop(s,t,o){o=o||{};tl.fromTo(s,{opacity:0,scale:0.9,filter:"blur(8px)"},{opacity:1,scale:1,filter:"blur(0px)",duration:o.duration||0.7,ease:E3},t);}
function chars(s,t,o){o=o||{};tl.fromTo(s+" .ch",{opacity:0,y:o.y||26,filter:"blur(10px)"},{opacity:1,y:0,filter:"blur(0px)",duration:o.duration||0.7,ease:E3,stagger:o.stagger||0.035},t);}
function card3d(s,t,o){o=o||{};tl.fromTo(s,{opacity:0,rotationX:16,rotationY:o.ry||-14,z:-260,y:60,transformPerspective:1800},{opacity:1,rotationX:4,rotationY:o.ry2||-5,z:0,y:0,transformPerspective:1800,duration:o.duration||1.3,ease:"power3.out"},t);}
function mark(s,t,o){o=o||{};tl.fromTo(s,{opacity:0,scaleX:0},{opacity:1,scaleX:1,duration:o.duration||0.6,ease:"power2.out"},t);}
function wipe(s,t,o){o=o||{};tl.fromTo(s,{clipPath:"inset(0 100% 0 0)"},{clipPath:"inset(0 0% 0 0)",duration:o.duration||0.8,ease:"power2.inOut"},t);}
function dim(s,t,o){o=o||{};tl.to(s,{opacity:o.to||0.35,duration:o.duration||0.5,ease:"power2.out"},t);}
"""

PAGE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1920, height=1080" />
<title>{title}</title>
<script src="assets/vendor/gsap.min.js"></script>
<style>{css}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1920" data-height="1080">
{body}
<div id="capband"></div><div id="vignette"></div><div id="grain"></div>
</div>
<script>
{helpers}
{js}
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
</script>
</body>
</html>
"""
