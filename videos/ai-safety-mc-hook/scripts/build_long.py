#!/usr/bin/env python3
"""Video 1 (long) — 《当 AI 能把 MC 塞进任何游戏》长版，design v2 via the shared hfkit."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "..", "_shared"))
from hfkit import Kit, E  # noqa: E402

k = Kit(ROOT, "当 AI 能把 MC 塞进任何游戏", chrome_left="AI 安全 · 案例")
w, S = k.W, k.S
AN = dict(crop_x=370, view_w=700)  # anthropic.com article column


def shot_at(sid, img, key, left, top, width, src, t_card, t_hl=None, **crop):
    html = k.shot(sid, img, left, top, width, key, src, **crop)
    k.tw("card3d", f"#{sid}", t_card)
    k.tw("fade", f"#{sid}-src", t_card + 0.5)
    if t_hl is not None:
        k.hls(sid, key, t_hl)
    return html


# ── F1 hook ─────────────────────────────────────────────────────────────────
f = 1
t_er = w(f, 5)
z1 = k.scene("s1", f, 0, t_er, f"""
  <div class="frame-v" style="position:absolute;left:138px;top:228px;width:1004px;height:566px;border-radius:14px;box-shadow:0 40px 90px rgba(0,0,0,.6),0 0 0 1px rgba(255,255,255,.1)"></div>
  <div id="s1-k" class="kicker" style="left:140px;top:170px">X · 2026.09 — 10</div>
  <div id="s1-h" class="h" style="left:1210px;top:250px;font-size:60px;line-height:1.3">{k.chars("AI 把《我的世界》")}<br/>{k.chars('塞进了<span class="acc">别的游戏</span>')}</div>
  <div id="s1-c1" class="pill" style="left:1210px;top:480px">GTA V × MINECRAFT</div>
  <div id="s1-c2" class="pill" style="left:1210px;top:550px">HALO × MINECRAFT</div>
  <div id="s1-repo" class="mono" style="left:140px;top:820px">GITHUB.COM/REHAN-REMADE/UNIVERSAL-MODDER · 4.4K★</div>
""", trans="cut")
k.video("v1a", "public/vid/mods-teaser.mp4", f, 0, t_er + 1.4, "left:140px;top:230px;width:1000px;height:562px;border-radius:12px", z=z1 + 1)
k.tw("fade", "#s1-k", S(f) + 0.2); k.tw("fade", "#s1-repo", S(f) + 1.0)
k.tw("chars", "#s1-h", S(f) + w(f, 2)); k.tw("left", "#s1-c1", S(f) + w(f, 3)); k.tw("left", "#s1-c2", S(f) + w(f, 4))
k.video("v1b", "public/vid/eldenring-clip.mp4", f, t_er, k.D(f) + 1.4, "left:0;top:0;width:1920px;height:1080px", media_start=0)
cl, ct, cw = 1250, 170, 560
sc = cw / 1100
z1b = k.scene("s1b", f, t_er, k.D(f), f"""
  <div class="shade" style="background:linear-gradient(270deg,rgba(11,13,18,.85) 0%,rgba(11,13,18,.35) 45%,rgba(11,13,18,.1) 100%)"></div>
  <div id="s1b-card" style="left:{cl}px;top:{ct}px;width:{cw}px;border-radius:14px;overflow:hidden;box-shadow:0 40px 90px rgba(0,0,0,.6)"><img src="public/shots/x-eldenring-card.png" style="display:block;width:100%"/></div>
  <div id="s1b-chip" class="pill acc" style="left:140px;top:780px;font-size:24px">ELDEN RING × MINECRAFT</div>
  <div id="s1b-like" class="num" style="left:{cl}px;top:{ct + round(1104*sc) + 30}px;font-size:64px">308.2K <span class="unit">人点赞 · 2026-09-29</span></div>
""", trans="blur", bg="none")
k.video("v1c", "public/vid/eldenring-clip.mp4", f, t_er, k.D(f) + 1.4, f"left:{cl+35*sc:.1f}px;top:{ct+267*sc:.1f}px;width:{1030*sc:.1f}px;height:{580*sc:.1f}px", z=z1b + 1)
k.tw("right", "#s1b-card", S(f) + t_er + 0.3); k.tw("left", "#s1b-chip", S(f) + t_er + 0.4)
k.tw("up", "#s1b-like", S(f) + w(f, 7))

# ── F2 how it works ────────────────────────────────────────────────────────
f = 2
steps = [("01", "反编译，读懂游戏代码", "ILSPY · GHIDRA · FRIDA", 2), ("02", "两边各写一个桥接插件", "FABRIC MOD · SCRIPTHOOKV · SKSE", 3),
         ("03", "镜头、坐标、碰撞实时同步", "SHARED MEMORY · 127.0.0.1", 4), ("04", "按深度把方块画面叠进去", "COLOR + DEPTH COMPOSITE", 6)]
rows = "".join(f'<div id="s2-st{i}" style="left:140px;top:{360+i*130}px;display:flex;gap:30px"><div class="num acc" style="font-size:58px;width:90px">{a}</div>'
               f'<div><div class="h md" style="position:static;font-size:42px">{b}</div><div class="mono" style="margin-top:10px">{c}</div></div></div>'
               for i, (a, b, c, _) in enumerate(steps))
k.scene("s2", f, 0, k.D(f), f"""
  <div id="s2-k" class="kicker" style="left:140px;top:180px">原理</div>
  <div id="s2-h" class="h" style="left:140px;top:220px;font-size:76px">{k.chars("做法其实不神秘")}</div>
  {rows}
  <div id="s2-ban" style="left:1040px;top:360px;width:760px;border-radius:14px;overflow:hidden;box-shadow:0 40px 90px rgba(0,0,0,.6)"><img src="public/img/banner.png" style="display:block;width:100%"/></div>
  <div id="s2-run" class="mono" style="left:1040px;top:760px">GAME A ⇄ MINECRAFT · 两个游戏同时运行</div>
""", trans="blur")
k.tw("fade", "#s2-k", S(f) + 0.3); k.tw("chars", "#s2-h", S(f) + 0.3)
k.tw("card3d", "#s2-ban", S(f) + w(f, 1)); k.tw("fade", "#s2-run", S(f) + w(f, 1) + 0.6)
for i, (*_, wi) in enumerate(steps):
    k.tw("left", f"#s2-st{i}", S(f) + w(f, wi))

# ── F3 turn ────────────────────────────────────────────────────────────────
f = 3
k.scene("s3", f, 0, k.D(f), f"""
  <div id="s3-a" class="h md" style="left:140px;top:230px;font-size:56px">以前：一个团队 × 几个月</div>
  <div id="s3-b" class="h md" style="left:140px;top:320px;font-size:56px">现在：一个人 + 一个 AI × <span class="acc">几天</span></div>
  <div id="s3-c" class="h" style="left:140px;top:470px;font-size:84px">{k.chars("同样的能力，换个人来用")}</div>
  <div id="s3-p1" class="card" style="left:140px;top:650px;width:780px;height:150px"><div class="mono acc">PART 1</div><div class="h md" style="position:static;font-size:44px;margin-top:16px">AI 被人用歪了</div></div>
  <div id="s3-p2" class="card" style="left:960px;top:650px;width:780px;height:150px"><div class="mono steel">PART 2</div><div class="h md" style="position:static;font-size:44px;margin-top:16px">AI 自己出了错</div></div>
""", trans="focus", glow=True)
k.tw("up", "#s3-a", S(f) + w(f, 1)); k.tw("up", "#s3-b", S(f) + w(f, 2))
k.tw("chars", "#s3-c", S(f) + w(f, 4)); k.tw("up", "#s3-p1", S(f) + w(f, 8)); k.tw("up", "#s3-p2", S(f) + w(f, 9))

# ── F4 vibe hacking ────────────────────────────────────────────────────────
f = 4
sh = shot_at("s4-shot", "public/shots/an-vibehack-quote.png", "an-vibehack", 140, 230, 980, "ANTHROPIC.COM · 2025-08-27", S(f) + w(f, 2), S(f) + w(f, 4), crop_y=250, view_h=400, **AN)
k.scene("s4", f, 0, k.D(f), f"""
  <div id="s4-k" class="kicker" style="left:140px;top:170px">PART 1 · 坏人怎么用 AI</div>
  {sh}
  <div id="s4-d" class="num" style="left:1230px;top:230px;font-size:96px">2025.08</div>
  <div id="s4-t" class="mono" style="left:1234px;top:350px">CLAUDE CODE · 自动入侵 + 勒索</div>
  <div id="s4-n1" style="left:1230px;top:430px"><div class="num acc" style="font-size:130px">17+</div><div class="unit">家机构被勒索</div></div>
  <div id="s4-n2" style="left:1230px;top:650px"><div class="num" style="font-size:84px">$500,000+</div><div class="unit">有的赎金超过</div></div>
""", trans="zoom")
k.tw("fade", "#s4-k", S(f) + 0.3); k.tw("up", "#s4-d", S(f) + w(f, 1)); k.tw("fade", "#s4-t", S(f) + w(f, 3))
k.tw("pop", "#s4-n1", S(f) + w(f, 4)); k.tw("pop", "#s4-n2", S(f) + w(f, 5))

# ── F5 espionage → 2026 report ─────────────────────────────────────────────
f = 5
t_b = w(f, 3)
sh = shot_at("s5-shot", "public/shots/an-espionage-quote.png", "an-espionage", 140, 230, 980, "ANTHROPIC.COM · 2025-11-13", S(f) + 0.2, S(f) + w(f, 2), crop_y=200, view_h=400, **AN)
k.scene("s5a", f, 0, t_b, f"""
  {sh}
  <div id="s5-n" style="left:1230px;top:300px"><div class="num acc" style="font-size:170px">80–90%</div><div class="unit" style="margin-top:14px">的间谍行动工作由 AI 完成</div></div>
""")
k.tw("pop", "#s5-n", S(f) + w(f, 2))
sh = shot_at("s5b-shot", "public/shots/an-threat-2026-quote.png", "an-threat-2026", 140, 230, 980, "ANTHROPIC.COM · 2026-09 · THREAT REPORT", S(f) + t_b + 0.2, S(f) + w(f, 4), crop_y=220, view_h=400, **AN)
k.scene("s5b", f, t_b, k.D(f), f"""
  {sh}
  <div id="s5b-q" class="h" style="left:1230px;top:300px;font-size:56px;line-height:1.4">{k.chars("“AI 把成本")}<br/>{k.chars('又压回了<span class="acc">防守的一方</span>。”')}</div>
""", trans="blur")
k.tw("chars", "#s5b-q", S(f) + w(f, 4))

# ── F6 ISIS / extremists ───────────────────────────────────────────────────
f = 6
sh1 = shot_at("s6-voa", "public/shots/voa-isis-quote.png", "voa-isis", 140, 300, 820, "VOA · 2024", S(f) + w(f, 1), S(f) + w(f, 2) + 0.4, crop_x=360, view_w=720, crop_y=250, view_h=360)
sh2 = shot_at("s6-tat", "public/shots/tat-genai-quote.png", "tat-genai", 1020, 300, 760, "TECH AGAINST TERRORISM · 2023-11-08", S(f) + w(f, 3), S(f) + w(f, 4), crop_x=0, view_w=960, crop_y=180, view_h=420)
k.scene("s6", f, 0, k.D(f), f"""
  <div id="s6-k" class="kicker" style="left:140px;top:170px">恐怖组织 · 极端分子</div>
  <div id="s6-h" class="h" style="left:140px;top:205px;font-size:44px">{k.chars('ISIS 支持者发布 <span class="acc">AI 主播</span>播报的“新闻”')}</div>
  {sh1}{sh2}
  <div id="s6-n" style="left:1020px;top:680px"><div class="num acc" style="font-size:110px">5,000+</div><div class="unit">条 AI 生成内容 · 极端分子圈子</div></div>
""", trans="focus")
k.tw("fade", "#s6-k", S(f) + 0.4); k.tw("chars", "#s6-h", S(f) + w(f, 2)); k.tw("pop", "#s6-n", S(f) + w(f, 4))

# ── F7 attackers using chatbots ────────────────────────────────────────────
f = 7
t_b = w(f, 6)
sh = shot_at("s7-nbc", "public/shots/nbc-vegas-quote.png", "nbc-vegas", 140, 300, 900, "NBC NEWS · 2025-01", S(f) + w(f, 3), S(f) + w(f, 5), crop_x=320, view_w=620, crop_y=455, view_h=150)
k.scene("s7a", f, 0, t_b, f"""
  <div id="s7-k" class="kicker" style="left:140px;top:170px">用聊天机器人策划袭击</div>
  <div id="s7-d" class="h" style="left:140px;top:205px;font-size:52px">{k.chars("2025.01.01 · 拉斯维加斯")}</div>
  {sh}
  <div id="s7-tr" class="h md" style="left:1120px;top:300px;font-size:44px;line-height:1.5;white-space:normal;width:680px">{k.chars("“就我所知，这是美国本土第一起有人用 ChatGPT 帮忙做出这种装置的事件。”")}</div>
  <div id="s7-who" class="mono" style="left:1124px;top:620px">—— 拉斯维加斯警长 KEVIN MCMAHILL</div>
""", trans="focus")
k.tw("fade", "#s7-k", S(f) + 0.4); k.tw("chars", "#s7-d", S(f) + w(f, 1))
k.tw("chars", "#s7-tr", S(f) + w(f, 5), stagger=0.025); k.tw("fade", "#s7-who", S(f) + w(f, 5) + 1.2)
sh = shot_at("s7-yle", "public/shots/yle-pirkkala-quote.png", "yle-pirkkala", 140, 300, 900, "YLE · 2025-05 · 宣言真实性警方当时未证实", S(f) + w(f, 7), S(f) + w(f, 8), crop_x=190, view_w=680, crop_y=400, view_h=200)
k.scene("s7b", f, t_b, k.D(f), f"""
  <div id="s7b-d" class="h" style="left:140px;top:205px;font-size:52px">{k.chars("2025.05 · 芬兰皮尔卡拉")}</div>
  {sh}
  <div id="s7b-a" class="pill acc" style="left:1120px;top:330px;font-size:22px">据称</div>
  <div id="s7b-b" class="h md" style="left:1120px;top:400px;font-size:46px;line-height:1.5">用 ChatGPT 辅助<br/>策划了大约<span class="acc">半年</span></div>
""", trans="blur")
k.tw("chars", "#s7b-d", S(f) + t_b + 0.2); k.tw("pop", "#s7b-a", S(f) + w(f, 8)); k.tw("up", "#s7b-b", S(f) + w(f, 9) - 0.3)

# ── F8 Tumbler Ridge ───────────────────────────────────────────────────────
f = 8
sh = shot_at("s8-gn", "public/shots/gn-tumbler-quote.png", "gn-tumbler", 140, 600, 900, "GLOBAL NEWS · 2026", S(f) + w(f, 5), S(f) + w(f, 6), crop_x=160, view_w=680, crop_y=410, view_h=90)
marks = [("2026.02", "校园枪击 · 8 人遇难", 1, "acc"), ("2025.06", "账号因暴力内容被封", 4, ""), ("讨论报警", "判断未达门槛", 6, "steel"), ("2026.09", "BC 省起诉 OpenAI", 8, "acc")]
mk = "".join(f'<div id="s8-m{i}" style="left:{140+i*430}px;top:330px;width:400px"><div style="width:18px;height:18px;border-radius:50%;background:{"#C9A46C" if c=="acc" else "#8FA3B8" if c=="steel" else "#E9E6DF"}"></div>'
             f'<div class="num" style="font-size:44px;margin-top:22px">{a}</div><div class="unit" style="margin-top:10px">{b}</div></div>' for i, (a, b, _, c) in enumerate(marks))
k.scene("s8", f, 0, k.D(f), f"""
  <div id="s8-k" class="kicker" style="left:140px;top:170px">加拿大 · TUMBLER RIDGE</div>
  <div id="s8-h" class="h" style="left:140px;top:205px;font-size:56px">{k.chars("账号封了，没有报警")}</div>
  <div id="s8-line" class="rule" style="left:140px;top:338px;width:1640px"></div>
  {mk}
  {sh}
""", trans="focus")
k.tw("fade", "#s8-k", S(f) + 0.3); k.tw("wipe", "#s8-line", S(f) + 0.5, duration=1.4)
for i, (_, _, wi, _) in enumerate(marks):
    k.tw("up", f"#s8-m{i}", S(f) + w(f, wi))
k.tw("chars", "#s8-h", S(f) + w(f, 6))

# ── F9 AI companions ───────────────────────────────────────────────────────
f = 9
k.scene("s9", f, 0, k.D(f), """
  <div id="s9-k" class="kicker" style="left:140px;top:170px">人和 AI 的关系</div>
  <div id="s9-h" class="h" style="left:140px;top:210px;font-size:76px">聊得太深的时候</div>
  <div id="s9-c" class="card" style="left:140px;top:380px;width:1100px;height:380px;padding:40px 48px">
    <div class="mono acc">GARCIA V. CHARACTER TECHNOLOGIES</div>
    <div id="s9-l1" class="h md" style="position:static;font-size:42px;margin-top:30px">美国 · 14 岁少年 · 与 AI 角色聊得很深</div>
    <div id="s9-l2" class="lead" style="position:static;margin-top:24px">之后自杀身亡。母亲于 2024 年提起诉讼。</div>
    <div id="s9-l3" class="h md acc" style="position:static;font-size:42px;margin-top:30px">2026 年 1 月：Character.AI 与谷歌同意和解</div>
  </div>
  <div id="s9-src" class="mono" style="left:140px;top:790px">CNN · 2026-01-07</div>
  <div id="s9-help" class="mono" style="left:1300px;top:400px;width:500px;line-height:1.8;color:#C9C6BF">如果你正在经历困难，<br/>请联系身边的人或当地<br/>心理援助热线。</div>
""", trans="dip", glow=True)
k.tw("fade", "#s9-k", S(f) + 0.4); k.tw("up", "#s9-h", S(f) + 0.5); k.tw("up", "#s9-c", S(f) + w(f, 1))
k.tw("fade", "#s9-l2", S(f) + w(f, 3)); k.tw("fade", "#s9-l3", S(f) + w(f, 5)); k.tw("fade", "#s9-src", S(f) + w(f, 5))
k.tw("fade", "#s9-help", S(f) + w(f, 3) + 0.8)
k.tw("fade", "#s9-l1", S(f) + w(f, 1) + 0.3)

# ── F10 AI romance scam ────────────────────────────────────────────────────
f = 10
sh = shot_at("s10-shot", "public/shots/bjd-minhang-quote.png", "bjd-minhang", 140, 220, 820, "检察日报正义网 / 北京日报 · 2026-02-24", S(f) + w(f, 1), S(f) + w(f, 4), crop_x=340, view_w=760, crop_y=90, view_h=480)
nums = [("15", "名被害人", 3), ("171万+", "元被骗", 4), ("11", "年 · 主犯刑期", 5)]
nh = "".join(f'<div id="s10-n{i}" style="left:1060px;top:{230+i*200}px"><div class="num {"acc" if i==1 else ""}" style="font-size:110px">{a}</div><div class="unit">{b}</div></div>' for i, (a, b, _) in enumerate(nums))
k.scene("s10", f, 0, k.D(f), f"""
  <div id="s10-k" class="kicker" style="left:140px;top:170px">AI 婚恋诈骗 · 上海闵行</div>
  {sh}{nh}
""", trans="blur")
k.tw("fade", "#s10-k", S(f) + 0.3)
for i, (*_, wi) in enumerate(nums):
    k.tw("pop", f"#s10-n{i}", S(f) + w(f, wi))

# ── F11 China rules ────────────────────────────────────────────────────────
f = 11
sh = shot_at("s11-shot", "public/shots/cac-ai-companion-quote.png", "cac-ai-companion", 140, 400, 1000, "国家网信办 · 2026-04-10", S(f) + 0.6, S(f) + w(f, 3), crop_x=170, view_w=1080, crop_y=330, view_h=300)
k.scene("s11", f, 0, k.D(f), f"""
  <div id="s11-k" class="kicker" style="left:140px;top:170px">国内的规定</div>
  <div id="s11-h" class="h md" style="left:140px;top:210px;font-size:48px;white-space:normal;width:1640px;line-height:1.4">{k.chars("《人工智能拟人化互动服务管理暂行办法》")}</div>
  <div id="s11-d" class="pill acc" style="left:140px;top:310px">2026 年 7 月 15 日起施行</div>
  {sh}
  <div id="s11-r1" class="card" style="left:1200px;top:400px;width:600px;height:150px"><div class="num acc" style="font-size:56px">2 小时</div><div class="unit" style="margin-top:8px">连续使用每超过 2 小时要提醒</div></div>
  <div id="s11-r2" class="card" style="left:1200px;top:580px;width:600px;height:150px"><div class="h md" style="position:static;font-size:40px">不得诱导情感依赖</div><div class="unit muted" style="margin-top:8px">也不得过度迎合用户</div></div>
""", trans="blur")
k.tw("fade", "#s11-k", S(f) + 0.2); k.tw("chars", "#s11-h", S(f) + 0.3, stagger=0.02); k.tw("pop", "#s11-d", S(f) + w(f, 1))
k.tw("up", "#s11-r1", S(f) + w(f, 2)); k.tw("up", "#s11-r2", S(f) + w(f, 3))

# ── F12 hallucination: Tongzhou court ──────────────────────────────────────
f = 12
sh = shot_at("s12-shot", "public/shots/cns-tongzhou-quote.png", "cns-tongzhou", 140, 400, 980, "中新网 · 2026-01-15 · 央视《法治在线》", S(f) + w(f, 1), S(f) + w(f, 6), crop_x=90, view_w=880, crop_y=330, view_h=220)
k.scene("s12", f, 0, k.D(f), f"""
  <div id="s12-k" class="kicker" style="left:140px;top:170px">PART 2 · AI 自己出错 · 幻觉</div>
  <div id="s12-h" class="h" style="left:140px;top:210px;font-size:76px">{k.chars("一本正经地编")}</div>
  <div id="s12-case" class="pill" style="left:140px;top:320px">（2022）沪01民终12345号 → 实为一起民间借贷案</div>
  {sh}
  <div id="s12-q" class="h md" style="left:1190px;top:400px;font-size:42px;line-height:1.55;white-space:normal;width:620px">{k.chars("“不得放任人工智能模型生成或者编造虚假信息，扰乱司法秩序。”")}</div>
  <div id="s12-who" class="mono" style="left:1194px;top:700px">—— 北京通州法院判决书</div>
""", trans="zoom")
k.tw("fade", "#s12-k", S(f) + 0.4); k.tw("chars", "#s12-h", S(f) + 0.5)
k.tw("left", "#s12-case", S(f) + w(f, 3)); k.tw("chars", "#s12-q", S(f) + w(f, 6), stagger=0.03); k.tw("fade", "#s12-who", S(f) + w(f, 7))

# ── F13 Deloitte + database ────────────────────────────────────────────────
f = 13
sh1 = shot_at("s13-f", "public/shots/fortune-deloitte-quote.png", "fortune-deloitte", 140, 250, 820, "FORTUNE · 2025-10-07", S(f) + 0.3, S(f) + w(f, 1), crop_x=160, view_w=860, crop_y=300, view_h=220)
sh2 = shot_at("s13-c", "public/shots/charlotin-db-quote.png", "charlotin-db", 140, 560, 820, "DAMIENCHARLOTIN.COM · 2026-10-05", S(f) + w(f, 3), S(f) + w(f, 4), crop_x=300, view_w=900, crop_y=70, view_h=300)
k.scene("s13", f, 0, k.D(f), f"""
  {sh1}{sh2}
  <div id="s13-a" style="left:1080px;top:250px"><div class="h md" style="position:static;font-size:46px">德勤 · 澳大利亚政府报告</div><div class="unit muted" style="margin-top:12px">编造的法院判词 · 不存在的论文 · 退还部分款项</div></div>
  <div id="s13-n" style="left:1080px;top:540px"><div class="num acc" style="font-size:170px">2,149</div><div class="unit" style="margin-top:12px">起法庭案件出现 AI 编造的内容</div></div>
""", trans="blur")
k.tw("up", "#s13-a", S(f) + w(f, 1)); k.tw("pop", "#s13-n", S(f) + w(f, 4))

# ── F14 nine seconds ───────────────────────────────────────────────────────
f = 14
sh = shot_at("s14-shot", "public/shots/reg-pocketos-quote.png", "reg-pocketos", 140, 300, 980, "THEREGISTER.COM · 2026-04-27", S(f) + w(f, 1), S(f) + w(f, 4), crop_x=320, view_w=700, crop_y=280, view_h=330)
k.scene("s14", f, 0, k.D(f), f"""
  <div id="s14-k" class="kicker" style="left:140px;top:170px">AI 直接动手出错</div>
  <div id="s14-h" class="h md" style="left:140px;top:210px;font-size:46px">{k.chars("一枚权限过大的密钥 · 一次调用")}</div>
  {sh}
  <div id="s14-n" style="left:1240px;top:250px"><div class="num acc" style="font-size:300px;line-height:.9">9</div><div class="unit" style="margin-top:6px">秒 · 删光生产数据库和备份</div></div>
  <div id="s14-ok" class="pill" style="left:1240px;top:700px">数据最终由平台方用灾备恢复</div>
""", trans="focus")
k.tw("fade", "#s14-k", S(f) + 0.3); k.tw("chars", "#s14-h", S(f) + w(f, 2))
k.tw("pop", "#s14-n", S(f) + w(f, 4)); k.tw("left", "#s14-ok", S(f) + w(f, 5))

# ── F15 lab findings ───────────────────────────────────────────────────────
f = 15
t_b = w(f, 7)
grid = "".join(f'<div class="cell16" style="position:absolute;left:{(i%4)*70}px;top:{(i//4)*70}px;width:56px;height:56px;border-radius:6px;background:#C9A46C"></div>' for i in range(16))
sh = shot_at("s15-shot", "public/shots/an-misalignment-quote.png", "an-misalignment", 140, 260, 980, "ANTHROPIC.COM · 2025-06-20 · 受控模拟实验", S(f) + w(f, 2), S(f) + w(f, 4), crop_y=300, view_h=380, **AN)
k.scene("s15a", f, 0, t_b, f"""
  <div id="s15-k" class="kicker" style="left:140px;top:170px">实验室里看到的东西</div>
  <div id="s15-tag" class="pill acc" style="left:140px;top:205px">CONTROLLED SIMULATION · 受控模拟</div>
  {sh}
  <div id="s15-tr" class="h md" style="left:1190px;top:260px;font-size:40px;line-height:1.5;white-space:normal;width:620px">{k.chars("“取消下午五点的清除，这些信息就会保密。”")}</div>
  <div id="s15-g" style="left:1190px;top:470px;width:280px;height:280px">{grid}</div>
  <div id="s15-gl" class="unit" style="left:1500px;top:480px;width:300px">测试的 16 个主流模型<br/><span class="acc">类似行为普遍出现</span></div>
""", trans="dip")
k.tw("fade", "#s15-k", S(f) + 0.3); k.tw("pop", "#s15-tag", S(f) + w(f, 2))
k.tw("chars", "#s15-tr", S(f) + w(f, 4), stagger=0.03)
k.raw(f'tl.fromTo("#s15-g .cell16",{{opacity:0,scale:0.5}},{{opacity:1,scale:1,duration:0.35,ease:"power3.out",stagger:0.07}},{round(S(f)+w(f,5),3)});')
k.tw("up", "#s15-gl", S(f) + w(f, 6))
sh = shot_at("s15b-shot", "public/shots/an-rewardhack-quote.png", "an-rewardhack", 140, 260, 980, "ANTHROPIC.COM · 2025-11-21", S(f) + t_b + 0.2, S(f) + w(f, 9), crop_y=230, view_h=400, **AN)
k.scene("s15b", f, t_b, k.D(f), f"""
  {sh}
  <div id="s15b-n" style="left:1230px;top:300px"><div class="num acc" style="font-size:200px">12%</div><div class="unit" style="margin-top:12px">的时候会故意破坏<br/>安全研究的代码</div></div>
  <div id="s15b-l" class="mono" style="left:1234px;top:630px">学会钻奖励空子的模型</div>
""", trans="blur")
k.tw("fade", "#s15b-l", S(f) + w(f, 8)); k.tw("pop", "#s15b-n", S(f) + w(f, 9))

# ── F16 keywords ───────────────────────────────────────────────────────────
f = 16
kws = [("对齐", "ALIGNMENT", 2), ("奖励黑客", "REWARD HACKING", 3), ("可解释性", "INTERPRETABILITY", 4), ("人类监督", "HUMAN OVERSIGHT", 5)]
kh = "".join(f'<div id="s16-k{i}" style="left:140px;top:{230+i*160}px"><div class="h" style="position:static;font-size:92px">{a}</div><div class="mono" style="margin-top:6px">{b}</div></div>' for i, (a, b, _) in enumerate(kws))
k.scene("s16", f, 0, k.D(f), f"""
  {kh}
  <div id="s16-big" class="h acc" style="left:1100px;top:380px;font-size:150px">AI 安全</div>
  <div id="s16-sub" class="mono" style="left:1106px;top:560px">几个常说的词</div>
""", trans="focus", glow=True)
k.tw("pop", "#s16-big", S(f) + 0.6); k.tw("fade", "#s16-sub", S(f) + w(f, 1))
for i, (*_, wi) in enumerate(kws):
    k.tw("left", f"#s16-k{i}", S(f) + w(f, wi))
    if i:
        k.raw(f'tl.to("#s16-k{i-1}",{{opacity:0.35,duration:0.4,ease:"power2.out"}},{round(S(f)+w(f,wi),3)});')

# ── F17 introspection + constitution ───────────────────────────────────────
f = 17
t_b = w(f, 3)
sh = shot_at("s17-shot", "public/shots/an-introspection-quote.png", "an-introspection", 140, 260, 980, "ANTHROPIC.COM · 2025-10-29 · INTROSPECTION", S(f) + 0.3, S(f) + w(f, 2), crop_y=220, view_h=400, **AN)
k.scene("s17a", f, 0, t_b, f"""
  {sh}
  <div id="s17-n" style="left:1230px;top:300px"><div class="num acc" style="font-size:190px">≈20%</div><div class="unit" style="margin-top:12px">的时候能察觉<br/>被注入的“念头”</div></div>
""", trans="blur")
k.tw("pop", "#s17-n", S(f) + w(f, 2))
sh = shot_at("s17b-shot", "public/shots/an-const-news-quote.png", "an-const-news", 140, 260, 980, "ANTHROPIC.COM · 2026-01-22 · CLAUDE'S NEW CONSTITUTION", S(f) + t_b + 0.2, S(f) + w(f, 4), crop_y=300, view_h=400, **AN)
k.scene("s17b", f, t_b, k.D(f), f"""
  {sh}
  <div id="s17b-k" class="kicker" style="left:1230px;top:280px">CLAUDE 的宪法</div>
  <div id="s17b-q" class="h md" style="left:1230px;top:330px;font-size:46px;line-height:1.5;white-space:normal;width:580px">{k.chars('“Claude 不应该削弱人类<span class="acc">监督和纠正</span>它的能力。”')}</div>
""", trans="blur")
k.tw("fade", "#s17b-k", S(f) + t_b + 0.4); k.tw("chars", "#s17b-q", S(f) + w(f, 4), stagger=0.04)

# ── F18 ending + sources ───────────────────────────────────────────────────
f = 18
t_end = round(k.vo[f]["duration_s"] + 0.4, 3)
k.video("v18", "public/vid/eldenring-clip.mp4", f, 0, t_end + 1.4, "left:0;top:0;width:1920px;height:1080px", media_start=0, extra='data-playback-rate="0.85"')
k.scene("s18", f, 0, t_end, f"""
  <div class="shade" style="background:rgba(11,13,18,.72)"></div>
  <div id="s18-a" class="h md" style="left:140px;top:260px;font-size:52px">{k.chars("AI 能做的事会越来越多，")}</div>
  <div id="s18-b" class="lead" style="left:140px;top:360px">把 MC 塞进别的游戏，只是其中好玩的一件。</div>
  <div id="s18-c" class="h" style="left:140px;top:520px;font-size:66px">{k.chars("出事的时候，")}</div>
  <div id="s18-d" class="h" style="left:140px;top:620px;font-size:66px">{k.chars('人能不能及时<span class="acc">看见</span>，')}</div>
  <div id="s18-e" class="h" style="left:140px;top:720px;font-size:66px">{k.chars('能不能<span class="acc">叫停</span>。')}</div>
""", trans="focus", bg="none")
k.tw("chars", "#s18-a", S(f) + 0.4); k.tw("up", "#s18-b", S(f) + w(f, 1))
k.tw("chars", "#s18-c", S(f) + w(f, 4)); k.tw("chars", "#s18-d", S(f) + w(f, 5)); k.tw("chars", "#s18-e", S(f) + w(f, 6))
srcs = ["X @TobynJacobs (2026-09-29) · github.com/rehan-remade/universal-modder",
        "Anthropic：Detecting & countering misuse (2025-08-27) · AI-orchestrated espionage (2025-11-13) · Threat report (2026-09)",
        "VOA (2024) · Tech Against Terrorism (2023-11-08)",
        "NBC News (2025-01) · Yle (2025-05) · Global News / Al Jazeera (2026)",
        "CNN (2026-01-07) · 检察日报正义网 / 北京日报 (2026-02-24) · 国家网信办 (2026-04-10)",
        "中新网 / 央视《法治在线》(2026-01-15) · Fortune (2025-10-07) · damiencharlotin.com (2026-10-05)",
        "The Register (2026-04-27)",
        "Anthropic：Agentic misalignment (2025-06-20) · Reward hacking (2025-11-21) · Introspection (2025-10-29) · Constitution (2026-01-22)"]
s_html = "".join(f'<div class="mono srcl" style="position:static;color:#C9C6BF;line-height:2.2;border-bottom:1px solid rgba(233,230,223,.08);text-transform:none">{E(s)}</div>' for s in srcs)
k.scene("s18c", f, t_end, k.D(f), f"""
  <div id="s18c-k" class="kicker" style="left:140px;top:160px">来源</div>
  <div id="s18c-l" style="left:140px;top:210px;width:1640px">{s_html}</div>
""", trans="dip", chrome=False)
k.raw(f'tl.fromTo("#s18c-l .srcl",{{opacity:0,y:12}},{{opacity:1,y:0,duration:0.4,ease:"power3.out",stagger:0.07}},{round(S(f)+t_end+0.4,3)});')
k.tw("fade", "#s18c-k", S(f) + t_end + 0.3)

k.write(bgm="assets/audio/bgm-long.mp3", bgm_vol=0.12)
