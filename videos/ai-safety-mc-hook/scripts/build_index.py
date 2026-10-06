#!/usr/bin/env python3
"""Generate index.html (single-file HyperFrames composition) from STORYBOARD.md durations,
audio_meta.json voice timings and quote-boxes.json screenshot coordinates.

Scene-local times below are clause starts from audio_meta.json (MiniMax subtitles), so
every reveal lands on its spoken cue. Run: python3 scripts/build_index.py
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sb = open(os.path.join(ROOT, "STORYBOARD.md"), encoding="utf8").read()
DUR = [float(x) for x in re.findall(r"^- duration: ([\d.]+)s", sb, flags=re.M)]
START = [round(sum(DUR[:i]), 3) for i in range(len(DUR))]
TOTAL = round(sum(DUR), 3)
meta = json.load(open(os.path.join(ROOT, "audio_meta.json"), encoding="utf8"))
VO = {v["frame"]: v for v in meta["voices"]}
QB = json.load(open(os.path.join(ROOT, "quote-boxes.json")))

E = html.escape
els, js = [], []          # html chunks, timeline lines


def S(n):  # global start of frame n (1-based)
    return START[n - 1]


def tw(kind, sel, t, **kw):
    args = ", ".join(f"{k}:{json.dumps(v)}" for k, v in kw.items())
    js.append(f'{kind}("{sel}", {round(t, 3)}{", {" + args + "}" if args else ""});')


def section(sid, n, t0, t1, inner, cls="", chrome=True):
    s, d = round(S(n) + t0, 3), round(t1 - t0, 3)
    ch = (f'<div class="chrome l">AI SAFETY · 一些思考</div><div class="chrome r">{n:02d} / 10</div>' if chrome else "")
    els.append(f'<section id="{sid}" class="clip scene {cls}" data-start="{s}" data-duration="{d}">{ch}{inner}</section>')


def shot(sid, img, left, top, width, key=None, src_label=""):
    """Screenshot card (2x DPR capture of a 1440-wide viewport) + optional quote boxes."""
    s = width / 1440.0
    h = round(900 * s)
    boxes = ""
    if key:
        for i, r in enumerate(QB[key]["rects"]):
            boxes += (f'<div id="{sid}-hl{i}" class="hl" style="left:{r["x"]*s-6:.1f}px;top:{r["y"]*s-5:.1f}px;'
                      f'width:{r["w"]*s+12:.1f}px;height:{r["h"]*s+10:.1f}px"></div>')
    lab = f'<div class="src">{E(src_label)}</div>' if src_label else ""
    return (f'<div id="{sid}" class="shot" style="left:{left}px;top:{top}px;width:{width}px;height:{h}px">'
            f'<img src="{img}" alt="" />{boxes}</div>'
            f'<div id="{sid}-src" class="srcwrap" style="left:{left}px;top:{top + h + 14}px">{lab}</div>')


# ── Frame 1 — hook ──────────────────────────────────────────────────────────
n = 1
els.append(f'<video id="v1a" class="clip vid" src="public/vid/mods-teaser.mp4" muted playsinline data-start="{S(1)}" data-duration="6.23" data-media-start="0" style="left:140px;top:250px;width:1100px;height:616px"></video>')
section("s1", n, 0, 6.23, """
  <div class="frame-win" style="left:139px;top:249px;width:1102px;height:618px"></div>
  <div id="s1-kick" class="kicker" style="left:140px;top:180px">X · GITHUB · 2026.09.27 — 10.06</div>
  <div id="s1-h" class="h-cn" style="left:1310px;top:250px;width:520px;font-size:62px">AI 把《我的世界》<br/>塞进了<span class="or">别的游戏</span></div>
  <div id="s1-c1" class="chip" style="left:1310px;top:520px">GTA V × MINECRAFT</div>
  <div id="s1-c2" class="chip" style="left:1310px;top:590px">HALO × MINECRAFT</div>
  <div id="s1-repo" class="mono-sm" style="left:140px;top:885px">GITHUB.COM/REHAN-REMADE/UNIVERSAL-MODDER · 4.4K★</div>
""")
tw("fade", "#s1-kick", S(1) + 0.1); tw("fade", "#s1-repo", S(1) + 0.4)
tw("up", "#s1-h", S(1) + 1.32); tw("left", "#s1-c1", S(1) + 4.72); tw("left", "#s1-c2", S(1) + 5.67)
er_card_l, er_card_t, er_w = 1262, 190, 540
sc = er_w / 1100
els.append(f'<video id="v1b" class="clip vid" src="public/vid/eldenring-clip.mp4" muted playsinline data-start="{S(1)+6.23}" data-duration="{round(DUR[0]-6.23,3)}" data-media-start="0" style="left:0;top:0;width:1920px;height:1080px;z-index:1"></video>')
section("s1b", n, 6.23, DUR[0], f"""
  <div class="vignette"></div>
  <div id="s1b-card" class="card-img" style="left:{er_card_l}px;top:{er_card_t}px;width:{er_w}px"><img src="public/shots/x-eldenring-card.png" alt=""/></div>
  <div id="s1b-chip" class="chip big" style="left:140px;top:760px">ELDEN RING × MINECRAFT</div>
  <div id="s1b-meta" class="mono-sm" style="left:{er_card_l}px;top:{er_card_t + round(1104*sc) + 14}px">X · @TOBYNJACOBS · 2026-09-29 · 308.2K ♥</div>
""", cls="z2")
els.append(f'<video id="v1c" class="clip vid" src="public/vid/eldenring-clip.mp4" muted playsinline data-start="{S(1)+6.23}" data-duration="{round(DUR[0]-6.23,3)}" data-media-start="0" style="left:{er_card_l+35*sc:.1f}px;top:{er_card_t+267*sc:.1f}px;width:{1030*sc:.1f}px;height:{580*sc:.1f}px;z-index:3;object-fit:cover"></video>')
tw("right", "#s1b-card", S(1) + 6.25); tw("left", "#s1b-chip", S(1) + 6.3); tw("fade", "#s1b-meta", S(1) + 6.6)

# ── Frame 2 — how it works ──────────────────────────────────────────────────
n = 2
steps = [("01", "反编译，读懂游戏代码", "ILSPY · GHIDRA · FRIDA", 2.76),
         ("02", "两边各写一个桥接插件", "FABRIC MOD · SCRIPTHOOKV · SKSE", 4.89),
         ("03", "实时同步镜头、坐标、碰撞", "SHARED MEMORY · 127.0.0.1", 7.22),
         ("04", "按深度把方块画面合成进去", "COLOR + DEPTH COMPOSITE", 8.92)]
rows = "".join(f'<div id="s2-st{i}" class="step" style="top:{330+i*128}px"><div class="num">{a}</div><div><div class="st">{b}</div><div class="mono-sm muted">{c}</div></div></div>' for i, (a, b, c, _) in enumerate(steps))
section("s2", n, 0, DUR[1], f"""
  <div id="s2-kick" class="kicker" style="left:140px;top:150px">HOW IT WORKS · 原理</div>
  <div id="s2-h" class="h-cn" style="left:140px;top:190px;font-size:88px">原理不玄</div>
  {rows}
  <div id="s2-ban" class="card-img" style="left:1000px;top:330px;width:800px"><img src="public/img/banner.png" alt=""/></div>
  <div id="s2-run" class="mono-sm" style="left:1000px;top:754px">GAME A ⇄ MINECRAFT · 两个游戏同时运行</div>
""")
tw("fade", "#s2-kick", S(2)); tw("up", "#s2-h", S(2) + 0.05)
tw("right", "#s2-ban", S(2) + 1.06); tw("fade", "#s2-run", S(2) + 1.3)
for i, (*_, t) in enumerate(steps):
    tw("left", f"#s2-st{i}", S(2) + t)

# ── Frame 3 — the turn ──────────────────────────────────────────────────────
n = 3
section("s3a", n, 0, 4.69, """
  <div id="s3-l1" class="h-cn" style="left:160px;top:330px;font-size:64px;font-weight:700">过去：一个团队 × 几个月</div>
  <div id="s3-l2" class="h-cn" style="left:160px;top:450px;font-size:64px;font-weight:700">现在：一个人 + 一个 AI × <span id="s3-days" class="or">几天</span></div>
""")
tw("up", "#s3-l1", S(3)); tw("up", "#s3-l2", S(3) + 2.17); tw("pop", "#s3-days", S(3) + 4.15)
section("s3b", n, 4.69, DUR[2], """
  <div id="s3-big" class="h-cn ink" style="left:140px;top:250px;font-size:168px">能力是中性的</div>
  <div id="s3-q" class="h-cn ink75" style="left:150px;top:520px;font-size:72px;font-weight:700">问题是，<span id="s3-q2">落在谁手里。</span></div>
""", cls="orange", chrome=False)
tw("slam", "#s3-big", S(3) + 4.69); tw("up", "#s3-q", S(3) + 6.32); tw("fade", "#s3-q2", S(3) + 7.04, duration=0.3)

# ── Frame 4 — vibe hacking ──────────────────────────────────────────────────
n = 4
section("s4", n, 0, DUR[3], f"""
  <div id="s4-kick" class="kicker" style="left:120px;top:110px">01 · 坏人怎么用 AI</div>
  {shot("s4-shot", "public/shots/an-vibehack-quote.png", 120, 160, 1080, "an-vibehack", "ANTHROPIC.COM · 2025-08-27 · DETECTING AND COUNTERING MISUSE")}
  <div id="s4-date" class="num-xl" style="left:1290px;top:150px;font-size:120px">2025.08</div>
  <div id="s4-tag" class="mono-sm" style="left:1296px;top:290px">CLAUDE CODE · “VIBE HACKING”</div>
  <div id="s4-st1" class="stat" style="left:1290px;top:380px"><div class="num-xl or">17+</div><div class="lab">家机构被勒索</div></div>
  <div id="s4-st2" class="stat" style="left:1290px;top:640px"><div class="num-xl or" style="font-size:96px">$500,000+</div><div class="lab">赎金有时超过</div></div>
""")
tw("fade", "#s4-kick", S(4)); tw("up", "#s4-date", S(4) + 0.05)
tw("up", "#s4-shot", S(4) + 1.37, y=80, duration=0.9); tw("fade", "#s4-shot-src", S(4) + 1.6)
tw("fade", "#s4-tag", S(4) + 3.41); tw("mark", "#s4-shot-hl0", S(4) + 3.5)
tw("up", "#s4-st1", S(4) + 6.83); tw("up", "#s4-st2", S(4) + 8.71)

# ── Frame 5 — espionage + 2026 report ───────────────────────────────────────
n = 5
section("s5a", n, 0, 5.32, f"""
  <div id="s5-kick" class="kicker" style="left:120px;top:110px">01 · 坏人怎么用 AI</div>
  {shot("s5-shot", "public/shots/an-espionage-quote.png", 120, 160, 1000, "an-espionage", "ANTHROPIC.COM · 2025-11-13 · AI-ORCHESTRATED ESPIONAGE")}
  <div id="s5-num" class="num-xl or" style="left:1170px;top:300px;font-size:200px">80–90%</div>
  <div id="s5-lab" class="lab" style="left:1180px;top:540px">的攻击工作由 AI 完成</div>
""")
tw("fade", "#s5-kick", S(5)); tw("up", "#s5-shot", S(5) + 0.4, y=80, duration=0.9); tw("fade", "#s5-shot-src", S(5) + 0.7)
tw("mark", "#s5-shot-hl0", S(5) + 1.2); tw("slam", "#s5-num", S(5) + 3.23); tw("up", "#s5-lab", S(5) + 3.5)
section("s5b", n, 5.32, DUR[4], f"""
  {shot("s5b-shot", "public/shots/an-threat-2026-quote.png", 120, 160, 1000, "an-threat-2026", "ANTHROPIC.COM · 2026-09 · THREAT INTELLIGENCE REPORT")}
  <div id="s5b-k" class="kicker" style="left:1180px;top:300px">今年的报告</div>
  <div id="s5b-q" class="h-cn" style="left:1180px;top:350px;width:640px;font-size:62px">「AI 把成本<br/>压回了<span class="or">防守方</span>。」</div>
""")
tw("right", "#s5b-shot", S(5) + 5.32); tw("fade", "#s5b-shot-src", S(5) + 5.6); tw("mark", "#s5b-shot-hl0", S(5) + 5.9)
tw("fade", "#s5b-k", S(5) + 5.5); tw("up", "#s5b-q", S(5) + 7.03)

# ── Frame 6 — nine seconds ──────────────────────────────────────────────────
n = 6
term = [("$ agent: staging 凭证不匹配 → 决定自己“修好它”", 2.44),
        ("$ 在一个无关文件里找到 API token", 3.7),
        ("  token 权限：所有操作（包括删除）", 5.0),
        ("$ curl -X DELETE …/volumes/production", 6.61),
        ("  ✕ 生产数据库    ✕ 卷级备份", 7.48)]
tl_html = "".join(f'<div id="s6-t{i}" class="tline{" or" if i == 4 else ""}">{E(a)}</div>' for i, (a, _) in enumerate(term))
section("s6a", n, 0, 10.44, f"""
  <div id="s6-kick" class="kicker" style="left:140px;top:110px">02 · AI 自己犯错</div>
  <div id="s6-h" class="h-cn" style="left:140px;top:150px;font-size:76px">危险，不只来自坏人。</div>
  <div id="s6-date" class="mono-sm" style="left:146px;top:262px">2026.04 · POCKETOS × CURSOR × CLAUDE OPUS 4.6</div>
  <div id="s6-term" class="term" style="left:140px;top:320px;width:1040px;height:440px"><div class="term-bar">AGENT · PRODUCTION <span class="muted">· 示意 ILLUSTRATION</span></div>{tl_html}</div>
  <div id="s6-nine" class="num-xl or" style="left:1300px;top:250px;font-size:400px;line-height:1">9</div>
  <div id="s6-sec" class="h-cn" style="left:1560px;top:470px;font-size:120px">秒</div>
""")
tw("fade", "#s6-kick", S(6)); tw("up", "#s6-h", S(6)); tw("fade", "#s6-date", S(6) + 1.57); tw("up", "#s6-term", S(6) + 1.8, y=40)
for i, (_, t) in enumerate(term):
    tw("type", f"#s6-t{i}", S(6) + t)
tw("slam", "#s6-nine", S(6) + 7.48); tw("fade", "#s6-sec", S(6) + 7.7)
section("s6b", n, 10.44, DUR[5], f"""
  {shot("s6b-shot", "public/shots/reg-pocketos-quote.png", 120, 160, 1000, "reg-pocketos", "THEREGISTER.COM · 2026-04-27")}
  <div id="s6b-q" class="h-lat" style="left:1180px;top:300px;width:640px">“It took<br/><span class="or">9 seconds.</span>”</div>
  <div id="s6b-who" class="mono-sm" style="left:1186px;top:520px">— JER CRANE, POCKETOS 创始人</div>
  <div id="s6b-ok" class="lab" style="left:1180px;top:600px;width:640px">数据最终由平台方 Railway<br/>在一小时内恢复</div>
""")
tw("right", "#s6b-shot", S(6) + 10.44); tw("fade", "#s6b-shot-src", S(6) + 10.7); tw("mark", "#s6b-shot-hl0", S(6) + 10.9)
tw("up", "#s6b-q", S(6) + 10.6); tw("fade", "#s6b-who", S(6) + 11.0); tw("up", "#s6b-ok", S(6) + 11.4)

# ── Frame 7 — self-preservation (simulation) ────────────────────────────────
n = 7
grid = "".join(f'<div id="s7-g{i}" class="cell" style="left:{(i%4)*74}px;top:{(i//4)*74}px"></div>' for i in range(16))
section("s7", n, 0, DUR[6], f"""
  <div id="s7-kick" class="kicker" style="left:120px;top:110px">03 · 实验室里的「自保」</div>
  <div id="s7-tag" class="tag" style="left:840px;top:100px">CONTROLLED SIMULATION · 受控模拟实验</div>
  {shot("s7-shot", "public/shots/an-misalignment-quote.png", 120, 160, 1000, "an-misalignment", "ANTHROPIC.COM · 2025-06-20 · AGENTIC MISALIGNMENT")}
  <div id="s7-clock" class="mono-sm" style="left:1180px;top:170px">17:00 · 计划关停这个 AI</div>
  <div id="s7-tr" class="h-cn" style="left:1180px;top:215px;width:660px;font-size:44px;font-weight:700;line-height:1.35">「取消下午五点的清除，<br/>这些信息就会<span class="or">保密</span>。」</div>
  <div id="s7-grid" style="position:absolute;left:1180px;top:420px;width:300px;height:300px">{grid}</div>
  <div id="s7-lab" class="lab" style="left:1500px;top:440px;width:330px">16 个主流模型<br/><span class="or">类似行为普遍出现</span></div>
""")
tw("fade", "#s7-kick", S(7)); tw("fade", "#s7-tag", S(7) + 0.1); tw("up", "#s7-shot", S(7) + 0.15, y=80, duration=0.9)
tw("fade", "#s7-shot-src", S(7) + 0.5); tw("fade", "#s7-clock", S(7) + 1.13)
tw("mark", "#s7-shot-hl0", S(7) + 3.94); tw("mark", "#s7-shot-hl1", S(7) + 4.1); tw("up", "#s7-tr", S(7) + 3.94)
js.append(f'tl.fromTo("#s7-grid .cell", {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.35, ease:"power3.out", stagger:0.08}}, {S(7)+5.44});')
tw("up", "#s7-lab", S(7) + 7.70)

# ── Frame 8 — keywords ──────────────────────────────────────────────────────
n = 8
kws = [("对齐", "ALIGNMENT", 2.73), ("奖励黑客", "REWARD HACKING", 3.32), ("可解释性", "INTERPRETABILITY", 4.29), ("人类监督", "HUMAN OVERSIGHT", 5.27)]
kw_html = "".join(f'<div id="s8-k{i}" class="kw" style="top:{190+i*160}px"><div class="kwc">{a}</div><div class="mono-sm muted">{b}</div></div>' for i, (a, b, _) in enumerate(kws))
section("s8", n, 0, DUR[7], f"""
  <div id="s8-kick" class="kicker" style="left:140px;top:120px">04 · 四个关键词</div>
  {kw_html}
  <div id="s8-big" class="h-cn or" style="left:1080px;top:330px;font-size:200px">AI 安全</div>
""")
tw("fade", "#s8-kick", S(8)); tw("slam", "#s8-big", S(8) + 0.1)
for i, (*_, t) in enumerate(kws):
    tw("left", f"#s8-k{i}", S(8) + t)
    if i:
        js.append(f'tl.to("#s8-k{i-1}", {{opacity:0.4, duration:0.4, ease:"power2.out"}}, {round(S(8)+t,3)});')

# ── Frame 9 — introspection + monologue ─────────────────────────────────────
n = 9
section("s9a", n, 0, 5.53, f"""
  <div id="s9-kick" class="kicker" style="left:120px;top:110px">05 · AI 想想自己</div>
  {shot("s9-shot", "public/shots/an-introspection-quote.png", 120, 160, 1000, "an-introspection", "ANTHROPIC.COM · 2025-10-29 · INTROSPECTION")}
  <div id="s9-num" class="num-xl or" style="left:1180px;top:300px;font-size:200px">≈20%</div>
  <div id="s9-lab" class="lab" style="left:1190px;top:540px;width:620px">的时候，Claude 能察觉<br/>被注入自己的「念头」</div>
""")
tw("fade", "#s9-kick", S(9)); tw("up", "#s9-shot", S(9) + 0.1, y=80, duration=0.9); tw("fade", "#s9-shot-src", S(9) + 0.4)
tw("mark", "#s9-shot-hl0", S(9) + 0.84); tw("slam", "#s9-num", S(9) + 4.36); tw("up", "#s9-lab", S(9) + 4.5)
mono_lines = [("如果我能看见自己在想什么，", 5.53), ("也该让你们看见，", 7.71), ("并随时<span class=\"or\">纠正我</span>。", 9.05)]
ml = "".join(f'<div id="s9-m{i}" class="mono-line">{a}</div>' for i, (a, _) in enumerate(mono_lines))
section("s9b", n, 5.53, DUR[8], f"""
  <div id="s9-who" class="kicker" style="left:160px;top:200px">&gt; CLAUDE</div>
  <div style="position:absolute;left:160px;top:260px">{ml}</div>
  <div id="s9-const" class="mono-sm muted" style="left:160px;top:780px;width:1600px">CLAUDE'S CONSTITUTION · 2026-01-22 — “CLAUDE SHOULD NOT UNDERMINE HUMANS' ABILITY TO OVERSEE AND CORRECT ITS VALUES AND BEHAVIOR.”</div>
""")
tw("fade", "#s9-who", S(9) + 5.53)
for i, (_, t) in enumerate(mono_lines):
    tw("up", f"#s9-m{i}", S(9) + t, y=24)
tw("fade", "#s9-const", S(9) + 9.4)

# ── Frame 10 — steering wheel + sources ─────────────────────────────────────
n = 10
els.append(f'<video id="v10" class="clip vid" src="public/vid/eldenring-clip.mp4" muted playsinline data-start="{S(10)}" data-duration="5.34" data-media-start="4" style="left:0;top:0;width:1920px;height:1080px;z-index:1"></video>')
section("s10a", n, 0, 5.34, """
  <div class="dim"></div>
  <div id="s10-l1" class="h-cn" style="left:140px;top:300px;font-size:72px">能把 MC 塞进任何游戏的能力，</div>
  <div id="s10-l2" class="h-cn" style="left:140px;top:420px;font-size:72px">也能把一个错误，</div>
  <div id="s10-l3" class="h-cn or" style="left:140px;top:540px;font-size:72px">放大到来不及撤回。</div>
""", cls="z2")
tw("up", "#s10-l1", S(10)); tw("up", "#s10-l2", S(10) + 2.41); tw("up", "#s10-l3", S(10) + 3.79)
section("s10b", n, 5.34, 7.56, """
  <div id="s10-b1" class="h-cn ink" style="left:140px;top:250px;font-size:168px">安全不是刹车，</div>
  <div id="s10-b2" class="h-cn ink" style="left:140px;top:480px;font-size:168px">是方向盘。</div>
""", cls="orange", chrome=False)
tw("slam", "#s10-b1", S(10) + 5.34); tw("slam", "#s10-b2", S(10) + 6.54)
srcs = ["ANTHROPIC.COM — DETECTING & COUNTERING MISUSE (2025-08-27)",
        "ANTHROPIC.COM — DISRUPTING AI-ORCHESTRATED ESPIONAGE (2025-11-13)",
        "ANTHROPIC.COM — THREAT INTELLIGENCE REPORT (2026-09)",
        "ANTHROPIC.COM — AGENTIC MISALIGNMENT (2025-06-20) · INTROSPECTION (2025-10-29) · CONSTITUTION (2026-01-22)",
        "THEREGISTER.COM — CURSOR-OPUS AGENT SNUFFS OUT STARTUP'S PRODUCTION DATABASE (2026-04-27)",
        "GITHUB.COM/REHAN-REMADE/UNIVERSAL-MODDER · X.COM/TOBYNJACOBS (2026-09-29)"]
src_html = "".join(f'<div id="s10-s{i}" class="srcline">{E(s)}</div>' for i, s in enumerate(srcs))
section("s10c", n, 7.56, DUR[9], f"""
  <div id="s10-st" class="kicker" style="left:140px;top:200px">SOURCES · 来源</div>
  <div style="position:absolute;left:140px;top:250px;width:1640px">{src_html}</div>
  <div id="s10-made" class="mono-sm muted" style="left:140px;top:780px">MADE WITH HYPERFRAMES · VOICE: MINIMAX</div>
""", chrome=False)
js.append(f'tl.fromTo("#s10c .srcline", {{opacity:0, y:16}}, {{opacity:1, y:0, duration:0.4, ease:"power3.out", stagger:0.08}}, {S(10)+7.6});')
tw("fade", "#s10-st", S(10) + 7.56); tw("fade", "#s10-made", S(10) + 8.2)

# ── audio + captions ────────────────────────────────────────────────────────
for f in range(1, 11):
    v = VO[f]
    els.append(f'<audio id="vo{f:02d}" src="{v["path"]}" data-start="{S(f)}" data-duration="{v["duration_s"]}" data-volume="1"></audio>')
els.append(f'<audio id="bgm" src="assets/audio/bgm-drone.mp3" data-start="0" data-duration="{TOTAL}" data-volume="0.16"></audio>')
caps = []
for f in range(1, 11):
    ws = VO[f]["words"]
    for i, w in enumerate(ws):
        st = S(f) + w["start"]
        en = S(f) + (ws[i + 1]["start"] if i + 1 < len(ws) else min(VO[f]["duration_s"] + 0.3, DUR[f - 1]))
        txt = w["text"].rstrip("。")
        caps.append(f'<div class="clip cap" data-start="{round(st,3)}" data-duration="{round(en-st,3)}"><span>{E(txt)}</span></div>')
els.extend(caps)

FONTS = "".join(
    f"@font-face{{font-family:'{fam}';src:url('assets/fonts/{file}') format('woff2');font-weight:{w};font-display:block}}"
    for fam, file, w in [("Noto Sans SC", "NotoSansSC-400.woff2", 400), ("Noto Sans SC", "NotoSansSC-500.woff2", 500),
                         ("Noto Sans SC", "NotoSansSC-700.woff2", 700), ("Noto Sans SC", "NotoSansSC-900.woff2", 900),
                         ("Barlow", "Barlow-700.woff2", 700), ("Barlow", "Barlow-800.woff2", 800), ("Barlow", "Barlow-900.woff2", 900),
                         ("IBM Plex Mono", "IBMPlexMono-400.woff2", 400), ("IBM Plex Mono", "IBMPlexMono-500.woff2", 500)])

CSS = FONTS + """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1920px;height:1080px;overflow:hidden;background:#111111}
#root{position:relative;width:1920px;height:1080px;overflow:hidden;background:#111111;color:#F0ECE5;font-family:'Noto Sans SC',sans-serif}
.clip{position:absolute;inset:0}
.scene{background:#111111;z-index:0}
.scene.z2{background:transparent;z-index:2}
.scene.orange{background:#E85D26}
.vid{position:absolute;object-fit:cover;z-index:1}
#v1a{z-index:1}
.scene > *{position:absolute}
.chrome{top:44px;font:500 15px/1 'IBM Plex Mono',monospace;letter-spacing:.14em;color:#888880}
.chrome.l{left:60px}.chrome.r{right:60px}
.kicker{font:500 18px/1 'IBM Plex Mono','Noto Sans SC',monospace;letter-spacing:.14em;color:#E85D26;text-transform:uppercase}
.h-cn{font-family:'Noto Sans SC',sans-serif;font-weight:900;line-height:1.12;letter-spacing:-.02em;color:#F0ECE5;white-space:nowrap}
.h-cn.ink{color:#111111}.h-cn.ink75,.ink75{color:rgba(17,17,17,.78)}
.h-lat{font:700 76px/1.05 'Barlow','Noto Sans SC',sans-serif;letter-spacing:-.02em;color:#F0ECE5}
.or{color:#E85D26}
.scene.orange .or{color:#111111}
.num-xl{font:900 160px/0.95 'Barlow',sans-serif;letter-spacing:-.04em;color:#F0ECE5}
.stat .lab,.lab{font:700 36px/1.35 'Noto Sans SC',sans-serif;color:#F0ECE5}
.stat{border-top:1px solid #282826;padding-top:18px;width:520px}
.mono-sm{font:500 17px/1.4 'IBM Plex Mono','Noto Sans SC',monospace;letter-spacing:.1em;color:#F0ECE5;text-transform:uppercase}
.muted{color:#888880}
.chip{font:500 22px/1 'IBM Plex Mono',monospace;letter-spacing:.14em;color:#F0ECE5;border:1px solid #E85D26;padding:14px 18px}
.chip.big{font-size:30px;background:#111111}
.frame-win{border:1px solid #505048}
.shot{overflow:hidden;border:1px solid #505048;background:#F0ECE5}
.shot img{display:block;width:100%;height:100%}
.hl{position:absolute;border:2px solid #E85D26;background:rgba(232,93,38,.16);transform-origin:left center}
.srcwrap{position:absolute}
.src{font:500 15px/1 'IBM Plex Mono',monospace;letter-spacing:.12em;color:#888880}
.card-img img{display:block;width:100%}
.card-img{border:1px solid #505048}
.vignette{inset:0;background:linear-gradient(90deg,rgba(17,17,17,.15) 0%,rgba(17,17,17,.15) 55%,rgba(17,17,17,.75) 100%)}
.dim{inset:0;background:rgba(17,17,17,.62)}
.step{left:140px;display:flex;gap:28px;align-items:flex-start}
.step .num{font:900 64px/1 'Barlow',sans-serif;color:#E85D26;width:90px}
.step .st{font:700 44px/1.2 'Noto Sans SC',sans-serif;margin-bottom:8px}
.term{background:#1A1A18;border:1px solid #282826;padding:24px 30px}
.term-bar{font:500 15px/1 'IBM Plex Mono',monospace;letter-spacing:.14em;color:#E85D26;margin-bottom:30px}
.tline{font:500 27px/1.9 'IBM Plex Mono','Noto Sans SC',monospace;color:#F0ECE5;white-space:nowrap;overflow:hidden;clip-path:inset(0 0 0 0)}
.tline.or{color:#E85D26}
.tag{font:500 16px/1 'IBM Plex Mono','Noto Sans SC',monospace;letter-spacing:.14em;background:#E85D26;color:#111111;padding:10px 14px}
.cell{position:absolute;width:60px;height:60px;background:#E85D26}
.kw{left:140px}
.kwc{font:900 96px/1.05 'Noto Sans SC',sans-serif;letter-spacing:-.02em}
.mono-line{font:700 72px/1.6 'Noto Sans SC',sans-serif;color:#F0ECE5}
.srcline{font:500 20px/2.1 'IBM Plex Mono',monospace;letter-spacing:.06em;color:#F0ECE5;border-bottom:1px solid #282826}
.cap{z-index:20;display:flex;align-items:flex-end;justify-content:center;padding-bottom:58px;pointer-events:none}
.cap span{font:500 40px/1.35 'Noto Sans SC',sans-serif;color:#F0ECE5;background:rgba(17,17,17,.78);padding:8px 26px;letter-spacing:.02em}
"""

JS_HELPERS = """
const tl = gsap.timeline({ paused: true });
const E3 = "power3.out";
function fade(s,t,o){o=o||{};tl.fromTo(s,{opacity:0},{opacity:1,duration:o.duration||0.5,ease:"power2.out"},t);}
function up(s,t,o){o=o||{};tl.fromTo(s,{opacity:0,y:o.y||36},{opacity:1,y:0,duration:o.duration||0.7,ease:E3},t);}
function left(s,t,o){o=o||{};tl.fromTo(s,{opacity:0,x:-48},{opacity:1,x:0,duration:o.duration||0.6,ease:E3},t);}
function right(s,t,o){o=o||{};tl.fromTo(s,{opacity:0,x:90},{opacity:1,x:0,duration:o.duration||0.8,ease:E3},t);}
function pop(s,t,o){o=o||{};tl.fromTo(s,{opacity:0,scale:0.85},{opacity:1,scale:1,duration:o.duration||0.45,ease:E3},t);}
function slam(s,t,o){o=o||{};tl.fromTo(s,{opacity:0,scale:1.12},{opacity:1,scale:1,duration:o.duration||0.5,ease:"expo.out"},t);}
function mark(s,t,o){o=o||{};tl.fromTo(s,{opacity:0,scaleX:0},{opacity:1,scaleX:1,duration:o.duration||0.5,ease:E3},t);}
function type(s,t,o){o=o||{};tl.fromTo(s,{clipPath:"inset(0 100% 0 0)"},{clipPath:"inset(0 0% 0 0)",duration:o.duration||0.7,ease:"none"},t);}
"""

page = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1920, height=1080" />
<title>当 AI 能把 MC 塞进任何游戏</title>
<script src="assets/vendor/gsap.min.js"></script>
<style>{CSS}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1920" data-height="1080">
{chr(10).join(els)}
</div>
<script>
{JS_HELPERS}
{chr(10).join(js)}
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
</script>
</body>
</html>
"""
open(os.path.join(ROOT, "index.html"), "w", encoding="utf8").write(page)
print(f"index.html written · {len(DUR)} frames · total {TOTAL}s · {len(caps)} captions")
