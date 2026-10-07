#!/usr/bin/env python3
"""Video 3 — 《两百个“理论”是怎么来的》. Shared hfkit design; scene-local times = narration clause starts."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "..", "_shared"))
from hfkit import Kit, E  # noqa: E402

k = Kit(ROOT, "两百个理论是怎么来的", chrome_left="XX 理论 · 观察")
w, S = k.W, k.S
QQ = dict(crop_x=180, view_w=720)


def shot_at(sid, img, key, left, top, width, src, t_card, t_hl=None, **crop):
    html = k.shot(sid, img, left, top, width, key, src, **crop)
    k.tw("card3d", f"#{sid}", t_card)
    k.tw("fade", f"#{sid}-src", t_card + 0.5)
    if t_hl is not None:
        k.hls(sid, key, t_hl)
    return html


def phase(label, sub):
    return (f'<div class="pill acc" style="left:140px;top:150px;font-size:18px">{label}</div>'
            f'<div class="mono" style="left:{150 + 24 * len(label) + 60}px;top:162px">{sub}</div>')


# ── F1 hook ────────────────────────────────────────────────────────────────
f = 1
words = [("普信男", 0), ("雌竞", 1), ("性压抑论", 2), ("苹果安卓", 3)]
cells = "".join(f'<div id="s1-w{i}" class="h" style="left:{220 + (i % 2) * 760}px;top:{230 + (i // 2) * 220}px;font-size:120px">{t}</div>' for i, (t, _) in enumerate(words))
k.scene("s1", f, 0, k.D(f), f"""
  {cells}
  <div id="s1-x" class="rule" style="left:960px;top:230px;width:1px;height:400px;background:rgba(233,230,223,.18)"></div>
  <div id="s1-c" class="pill acc" style="left:220px;top:720px;font-size:22px">随便说一个 · 评论区吵上几百楼</div>
""", trans="cut", glow=True)
for i, (_, wi) in enumerate(words):
    k.tw("pop", f"#s1-w{i}", S(f) + w(f, wi))
k.tw("fade", "#s1-x", S(f) + 0.4); k.tw("left", "#s1-c", S(f) + w(f, 5))

# ── F2 two hundred → two eras ──────────────────────────────────────────────
f = 2
names = ["晚学", "甄学", "冰学", "明学", "六学", "白学", "柯学", "雷学", "珂学", "麦学", "佐学", "孙学", "赢学", "抽象", "躺平", "内卷", "牛马", "班味",
         "普信男", "雌竞", "力工思维", "性压抑论", "苹果安卓", "薄肌理论", "骨相理论", "松弛感", "情绪价值", "原生家庭", "讨好型人格", "NPD", "回避型", "MBTI",
         "熵增定律", "达克效应", "显化", "高能量", "草台班子", "长期主义", "斩杀线", "县城婆罗门", "耍起主义", "大压抑", "人类丰容", "豆包型人格", "断舍离", "九紫离火"]
wall = "".join(f'<span style="display:inline-block;margin:0 26px 14px 0">{n}</span>' for n in names)
k.scene("s2", f, 0, k.D(f), f"""
  <div id="s2-wall" style="left:120px;top:150px;width:1680px;font:700 34px/1.5 'Noto Serif SC',serif;color:rgba(233,230,223,.13)">{wall}</div>
  <div id="s2-n" style="left:140px;top:300px"><div class="num acc" style="font-size:180px">200+</div><div class="unit" style="margin-top:10px">个“理论”和“学”</div></div>
  <div id="s2-a" class="card" style="left:760px;top:330px;width:1000px;height:150px"><div class="mono">早些年</div><div class="h md" style="position:static;font-size:46px;margin-top:16px">网友给<span class="acc">别人</span>起名字</div></div>
  <div id="s2-b" class="card" style="left:760px;top:510px;width:1000px;height:150px;border-color:rgba(201,164,108,.5)"><div class="mono acc">最近几年</div><div class="h md" style="position:static;font-size:46px;margin-top:16px">有人给<span class="acc">自己</span>造理论</div></div>
""", trans="blur")
k.tw("fade", "#s2-wall", S(f) + 0.2, duration=1.4); k.tw("pop", "#s2-n", S(f) + w(f, 1))
k.tw("up", "#s2-a", S(f) + w(f, 5)); k.tw("up", "#s2-b", S(f) + w(f, 7))

# ── F3 晚学 ────────────────────────────────────────────────────────────────
f = 3
sh = shot_at("s3-shot", "public/shots/qq-wanxue-quote.png", "qq-wanxue", 140, 260, 900, "每日人物 / 腾讯新闻 · 2024-10-24", S(f) + w(f, 1), S(f) + w(f, 2), crop_y=290, view_h=300, **QQ)
k.scene("s3", f, 0, k.D(f), f"""
  {phase("前期 · 被研究", "约 2009 — 2019 · 豆瓣 / 贴吧")}
  {sh}
  <div id="s3-h" class="h" style="left:1130px;top:250px;font-size:110px">晚学</div>
  <div id="s3-d" class="unit muted" style="left:1136px;top:400px">研究对象：初代网红晚晚和她的丈夫</div>
  <div id="s3-a" class="card" style="left:1130px;top:480px;width:640px;height:110px"><span class="h md" style="position:static;font-size:40px">被拉黑 = <span class="acc">毕业</span></span></div>
  <div id="s3-b" class="card" style="left:1130px;top:610px;width:640px;height:110px"><span class="h md" style="position:static;font-size:40px">被删评论 = <span class="acc">延毕</span></span></div>
""", trans="focus")
k.tw("chars", "#s3-h", S(f) + w(f, 1)); k.tw("fade", "#s3-d", S(f) + w(f, 2))
k.tw("up", "#s3-a", S(f) + w(f, 4)); k.tw("up", "#s3-b", S(f) + w(f, 5))

# ── F4 冰学 / naming power ─────────────────────────────────────────────────
f = 4
sh = shot_at("s4-shot", "public/shots/qq-bingxue-quote.png", "qq-bingxue", 140, 230, 900, "每日人物 / 腾讯新闻 · 2023-11-26", S(f) + w(f, 3), S(f) + w(f, 5), crop_y=130, view_h=420, **QQ)
k.scene("s4", f, 0, k.D(f), f"""
  <div id="s4-a" class="h md" style="left:1130px;top:240px;font-size:44px;line-height:1.5">晚晚在经营人设，<br/>“晚学”是网友起的名字</div>
  {sh}
  <div id="s4-q" class="h" style="left:1130px;top:430px;font-size:48px;line-height:1.5;white-space:normal;width:660px">{k.chars("“多年前他们有多少拥趸，如今听来就有多少讽刺。”")}</div>
  <div id="s4-p" class="pill acc" style="left:1130px;top:690px;font-size:22px">起名字的权力 · 在观众手里</div>
""", trans="blur")
k.tw("up", "#s4-a", S(f) + 0.2); k.tw("chars", "#s4-q", S(f) + w(f, 5), stagger=0.03); k.tw("left", "#s4-p", S(f) + w(f, 8))

# ── F5 中期 ────────────────────────────────────────────────────────────────
f = 5
sh = shot_at("s5-shot", "public/shots/qq-leixue-quote.png", "qq-leixue", 140, 300, 900, "每日人物 / 腾讯新闻 · 2024-04-20", S(f) + w(f, 5), S(f) + w(f, 8), crop_y=340, view_h=260, **QQ)
k.scene("s5", f, 0, k.D(f), f"""
  {phase("中期 · 被认领", "约 2024 · 抖音 / B站 / 小红书")}
  <div id="s5-h" class="h" style="left:140px;top:210px;font-size:64px">{k.chars('被研究，就是<span class="acc">流量</span>')}</div>
  {sh}
  <div id="s5-n" style="left:1130px;top:300px"><div class="num acc" style="font-size:150px">14.3亿</div><div class="unit" style="margin-top:10px">次播放 · 叶珂模仿大赛</div><div class="mono" style="margin-top:8px">新浪舆情通数据 · 转引自搜狐 2024-12</div></div>
  <div id="s5-q" class="h md" style="left:1130px;top:600px;font-size:46px">“分一瓢<span class="acc">泼天的流量</span>”</div>
""", trans="zoom")
k.tw("chars", "#s5-h", S(f) + w(f, 1)); k.tw("pop", "#s5-n", S(f) + w(f, 4)); k.tw("up", "#s5-q", S(f) + w(f, 9))

# ── F6 后期: 三大理论 ──────────────────────────────────────────────────────
f = 6
cards = [("性压抑论", "峰哥", "中国男性的精神问题，都源于性压抑", 4), ("力工思维", "戴梦", "只会埋头付出的男人，没有魅力", 6), ("苹果安卓相对论", "户晨风", "用手机把人分成两个阶层", 8)]
ch = "".join(f'<div id="s6-c{i}" class="card" style="left:{140 + i * 560}px;top:400px;width:520px;height:330px;padding:34px 36px">'
             f'<div class="mono acc">{who}</div><div class="h" style="position:static;font-size:50px;margin-top:20px">{n}</div>'
             f'<div class="lead" style="position:static;font-size:30px;margin-top:26px">{d}</div></div>' for i, (n, who, d, _) in enumerate(cards))
k.scene("s6", f, 0, k.D(f), f"""
  {phase("后期 · 主动造论", "2025 — 2026 · 直播间 / 短视频")}
  <div id="s6-h" class="h" style="left:140px;top:220px;font-size:72px">{k.chars('2025 · “三大理论”')}</div>
  {ch}
  <div id="s6-src" class="mono" style="left:140px;top:770px">据网络公开报道（2025-09）整理</div>
""", trans="focus")
k.tw("chars", "#s6-h", S(f) + w(f, 3))
for i, (*_, wi) in enumerate(cards):
    k.tw("up", f"#s6-c{i}", S(f) + w(f, wi))
k.tw("fade", "#s6-src", S(f) + w(f, 4))

# ── F7 普信男 ↔ 雌竞 ───────────────────────────────────────────────────────
f = 7
sh = shot_at("s7-shot", "public/shots/ccnu-puxin-quote.png", "ccnu-puxin", 140, 610, 640, "华中师大 媒体伦理案例库 · 2022-08-25", S(f) + w(f, 1) + 0.3, S(f) + w(f, 2), crop_x=380, view_w=960, crop_y=230, view_h=230)
k.scene("s7", f, 0, k.D(f), f"""
  <div id="s7-a" class="card" style="left:140px;top:220px;width:780px;height:330px;padding:40px"><div class="mono">2020 · 脱口秀 · 用来说男生</div><div class="h" style="position:static;font-size:96px;margin-top:30px">普信男</div></div>
  <div id="s7-b" class="card" style="left:1000px;top:220px;width:780px;height:330px;padding:40px"><div class="mono">用来说女生之间的互相比较</div><div class="h" style="position:static;font-size:96px;margin-top:30px">雌竞</div></div>
  {sh}
  <div id="s7-q" class="h md" style="left:860px;top:640px;font-size:48px;line-height:1.5;white-space:normal;width:920px">{k.chars('用一个词，把一个性别<span class="acc">打包成一种毛病</span>')}</div>
""", trans="blur")
k.tw("right", "#s7-a", S(f) + w(f, 1)); k.tw("right", "#s7-b", S(f) + w(f, 3))
k.tw("chars", "#s7-q", S(f) + w(f, 6), stagger=0.04)

# ── F8 薄肌 + 孙学 ─────────────────────────────────────────────────────────
f = 8
sh = shot_at("s8-shot", "public/shots/qq-sunxue-quote.png", "qq-sunxue", 1060, 230, 720, "PANEWS / 腾讯新闻 · 2026-01-30", S(f) + w(f, 5), S(f) + w(f, 7), crop_y=380, view_h=470, **QQ)
k.scene("s8", f, 0, k.D(f), f"""
  <div id="s8-a" class="card" style="left:140px;top:230px;width:840px;height:300px;padding:40px"><div class="mono">2026-08 · X 博主</div>
    <div class="h" style="position:static;font-size:76px;margin-top:22px">薄肌理论</div>
    <div class="lead" style="position:static;font-size:30px;margin-top:20px">练出低体脂薄肌 → 拿回人生的控制感</div></div>
  <div id="s8-p" class="pill acc" style="left:140px;top:560px;font-size:22px">网友称：“第四大理论”</div>
  {sh}
  <div id="s8-q" class="h" style="left:140px;top:680px;font-size:58px">{k.chars('“孙学的本质是<span class="acc">赢</span>”')}</div>
""", trans="blur")
k.tw("up", "#s8-a", S(f) + w(f, 1)); k.tw("left", "#s8-p", S(f) + w(f, 4)); k.tw("chars", "#s8-q", S(f) + w(f, 7))

# ── F9 pipeline ────────────────────────────────────────────────────────────
f = 9
steps = [("暴论", "一个原因解释一大群人", 1), ("名词", "好记，方便接龙", 3), ("站队", "给人分边", 5), ("推流", "吵得越凶推得越多", 7), ("信徒", "用他的词说话", 9), ("变现", "直播收入 · 一门课", 10)]
nodes = ""
for i, (a, b, _) in enumerate(steps):
    x = 140 + i * 280
    nodes += (f'<div id="s9-n{i}" style="left:{x}px;top:430px;width:240px;text-align:center">'
              f'<div class="card" style="position:relative;padding:28px 10px;border-color:{"rgba(201,164,108,.6)" if i==5 else "rgba(233,230,223,.12)"}"><div class="h" style="position:static;font-size:52px">{a}</div></div>'
              f'<div class="unit" style="margin-top:18px;font-size:24px">{b}</div></div>')
    if i < 5:
        nodes += f'<div id="s9-ar{i}" class="mono acc" style="left:{x+246}px;top:470px;font-size:36px">→</div>'
k.scene("s9", f, 0, k.D(f), f"""
  <div id="s9-h" class="h" style="left:140px;top:220px;font-size:72px">{k.chars("生产过程很像")}</div>
  {nodes}
""", trans="zoom")
k.tw("chars", "#s9-h", S(f) + 0.3)
for i, (*_, wi) in enumerate(steps):
    k.tw("up", f"#s9-n{i}", S(f) + w(f, wi))
    if i:
        k.tw("fade", f"#s9-ar{i-1}", S(f) + w(f, wi) - 0.2)

# ── F10 ban → next ─────────────────────────────────────────────────────────
f = 10
k.scene("s10", f, 0, k.D(f), """
  <div id="s10-h" class="h" style="left:140px;top:220px;font-size:96px">封号</div>
  <div id="s10-d" class="mono" style="left:146px;top:350px">2025-09 前后 · 三大理论里的后两个遭到审查</div>
  <div id="s10-a" class="card" style="left:140px;top:420px;width:820px;height:120px"><span class="h md" style="position:static;font-size:40px">苹果安卓相对论 · <span class="steel">户晨风 全网封禁</span></span></div>
  <div id="s10-b" class="card" style="left:140px;top:560px;width:820px;height:120px"><span class="h md" style="position:static;font-size:40px">力工思维 · <span class="steel">原视频全网删除</span></span></div>
  <div id="s10-n" style="left:1100px;top:400px;width:660px;height:300px;border:2px dashed rgba(201,164,108,.6);border-radius:16px;display:flex;align-items:center;justify-content:center"><span class="h acc" style="position:static;font-size:64px">下一个理论</span></div>
""", trans="dip")
k.tw("pop", "#s10-h", S(f) + w(f, 1)); k.tw("fade", "#s10-d", S(f) + w(f, 3))
k.tw("up", "#s10-a", S(f) + w(f, 4)); k.tw("up", "#s10-b", S(f) + w(f, 5)); k.tw("pop", "#s10-n", S(f) + w(f, 7))

# ── F11 另一条线 ───────────────────────────────────────────────────────────
f = 11
sh1 = shot_at("s11-w", "public/shots/wiki-tangping-quote.png", "wiki-tangping", 140, 260, 860, "维基百科 · 躺平", S(f) + w(f, 3), S(f) + w(f, 3) + 0.6, crop_x=250, view_w=900, crop_y=390, view_h=170)
sixteen = [("耍中找钱", 7), ("找钱来耍", 8), ("找耍结合", 9), ("以耍为主", 10)]
sx = "".join(f'<div id="s11-s{i}" class="h" style="left:1120px;top:{300 + i * 105}px;font-size:66px">{t}</div>' for i, (t, _) in enumerate(sixteen))
k.scene("s11", f, 0, k.D(f), f"""
  {phase("另一条线 · 集体自嘲", "没人从中收钱")}
  {sh1}
  <div id="s11-a" class="h" style="left:140px;top:520px;font-size:80px">躺平</div>
  <div id="s11-b" class="h" style="left:440px;top:520px;font-size:80px">牛马</div>
  <div id="s11-c" class="h acc" style="left:740px;top:520px;font-size:80px">耍起</div>
  <div id="s11-who" class="mono" style="left:1124px;top:240px">李伯清 · 评书 · 几十年前</div>
  {sx}
""", trans="focus", glow=True)
k.tw("up", "#s11-a", S(f) + w(f, 3) + 0.3); k.tw("up", "#s11-b", S(f) + w(f, 4)); k.tw("up", "#s11-c", S(f) + w(f, 5))
k.tw("fade", "#s11-who", S(f) + w(f, 6))
for i, (_, wi) in enumerate(sixteen):
    k.tw("up", f"#s11-s{i}", S(f) + w(f, wi), y=18)

# ── F12 李伯清降温 ─────────────────────────────────────────────────────────
f = 12
sh = shot_at("s12-shot", "public/shots/qq-cooldown-quote.png", "qq-cooldown", 140, 300, 900, "腾讯新闻 / 知著网 · 2026-09-13", S(f) + w(f, 1), S(f) + w(f, 3), crop_y=330, view_h=330, **QQ)
k.scene("s12", f, 0, k.D(f), f"""
  <div id="s12-h" class="h" style="left:140px;top:200px;font-size:64px">{k.chars("没有人靠它收钱")}</div>
  {sh}
  <div id="s12-q" class="h md" style="left:1130px;top:330px;font-size:44px;line-height:1.55;white-space:normal;width:650px">李伯清：这话是讲给<span class="acc">退休的人</span>听的，年轻人还是要以奋斗为主。</div>
""", trans="blur")
k.tw("chars", "#s12-h", S(f) + 0.2); k.tw("up", "#s12-q", S(f) + w(f, 3))

# ── F13 history ────────────────────────────────────────────────────────────
f = 13
hist = [("两千多年前", "雅典 · 智者", "收费教人修辞、怎么成功", 2), ("晚明", "市井讲学", "聚众讲一套成圣的道理", 6), ("一百多年前", "美国 · 巡回演讲", "“先相信，就能得到”", 7),
        ("后来", "成功学讲台", "知识付费 · 跨年演讲", 11), ("现在", "直播间", "一个两个字的名词", 13)]
hh = "".join(f'<div id="s13-m{i}" style="left:{140 + i * 340}px;top:330px;width:310px"><div style="width:16px;height:16px;border-radius:50%;background:{"#C9A46C" if i==4 else "#E9E6DF"}"></div>'
             f'<div class="mono" style="margin-top:22px">{a}</div><div class="h md" style="position:static;font-size:38px;margin-top:10px">{b}</div>'
             f'<div class="unit muted" style="margin-top:10px;font-size:24px">{c}</div></div>' for i, (a, b, c, _) in enumerate(hist))
k.scene("s13", f, 0, k.D(f), f"""
  <div id="s13-h" class="h" style="left:140px;top:200px;font-size:64px">{k.chars("布道这门生意，一直都有")}</div>
  <div id="s13-line" class="rule" style="left:140px;top:337px;width:1640px"></div>
  {hh}
  <div id="s13-b1" style="left:140px;top:640px"><div class="mono">一场演讲</div><div id="s13-bar" style="margin-top:12px;height:26px;width:1300px;background:#5A5F6A;border-radius:4px"></div><div class="unit" style="margin-top:10px">3 小时</div></div>
  <div id="s13-b2" class="h acc" style="left:140px;top:790px;font-size:52px">→ 两个字</div>
""", trans="focus")
k.tw("chars", "#s13-h", S(f) + 0.3); k.tw("wipe", "#s13-line", S(f) + w(f, 2) - 0.3, duration=1.2)
for i, (*_, wi) in enumerate(hist):
    k.tw("up", f"#s13-m{i}", S(f) + w(f, wi))
k.tw("fade", "#s13-b1", S(f) + w(f, 16))
k.raw(f'tl.to("#s13-bar",{{width:60,backgroundColor:"#C9A46C",duration:1.4,ease:"power3.inOut"}},{round(S(f)+w(f,16)+0.6,3)});')
k.tw("left", "#s13-b2", S(f) + w(f, 17))

# ── F14 control paradox + Fromm ────────────────────────────────────────────
f = 14
k.scene("s14", f, 0, k.D(f), """
  <div id="s14-k" class="kicker" style="left:140px;top:180px">反思 · 一</div>
  <div id="s14-h" class="h" style="left:140px;top:220px;font-size:96px">控制感</div>
  <div id="s14-you" class="h md" style="left:140px;top:430px;font-size:48px">你</div>
  <svg id="s14-svg" style="left:240px;top:420px" width="900" height="80" viewBox="0 0 900 80"><path id="s14-path" d="M10 40 L 880 40" stroke="#C9A46C" stroke-width="3" stroke-dasharray="10 10" fill="none"/></svg>
  <div id="s14-pen" class="h acc" style="left:250px;top:420px;font-size:52px">✎</div>
  <div id="s14-room" class="card" style="left:1150px;top:400px;width:600px;height:120px"><span class="h md" style="position:static;font-size:40px">别人的理论</span></div>
  <div id="s14-cap" class="lead" style="left:140px;top:540px">解释自己的那支笔，交到了别人手里</div>
  <div id="s14-f" class="card" style="left:140px;top:640px;width:1640px;height:150px;padding:30px 40px"><div class="mono">弗洛姆《逃避自由》 · 1941</div><div class="h md" style="position:static;font-size:40px;margin-top:14px">人在不确定的年代，会主动逃离自由，躲进<span class="acc">权威</span>里</div></div>
  <div id="s14-n" class="pill acc" style="left:140px;top:830px;font-size:22px">今天的权威：一个直播间 · 一个两个字的名词</div>
""", trans="dip", glow=True)
k.tw("fade", "#s14-k", S(f) + 0.3); k.tw("pop", "#s14-h", S(f) + w(f, 1))
k.tw("fade", "#s14-you", S(f) + w(f, 2)); k.tw("fade", "#s14-room", S(f) + w(f, 2) + 0.2); k.tw("fade", "#s14-svg", S(f) + w(f, 2) + 0.2)
k.tw("fade", "#s14-pen", S(f) + w(f, 3))
k.raw(f'tl.to("#s14-pen",{{x:880,duration:1.6,ease:"power2.inOut"}},{round(S(f)+w(f,3)+0.3,3)});')
k.tw("up", "#s14-cap", S(f) + w(f, 4)); k.tw("up", "#s14-f", S(f) + w(f, 5)); k.tw("left", "#s14-n", S(f) + w(f, 9))

# ── F15 looping effect ─────────────────────────────────────────────────────
f = 15
labels = [("力工", 7), ("普信", 8), ("龟男", 9), ("回避型", 10)]
boxes = "".join(f'<div id="s15-b{i}" class="card" style="left:{760 + (i % 2) * 520}px;top:{300 + (i // 2) * 230}px;width:480px;height:200px;display:flex;align-items:center;justify-content:center">'
                f'<span class="h" style="position:static;font-size:60px">{t}</span></div>' for i, (t, _) in enumerate(labels))
k.scene("s15", f, 0, k.D(f), f"""
  <div id="s15-k" class="kicker" style="left:140px;top:180px">反思 · 二</div>
  <div id="s15-h" class="h" style="left:140px;top:220px;font-size:72px">回环效应</div>
  <div id="s15-who" class="mono" style="left:146px;top:330px">哲学家 伊恩·哈金 · LOOPING EFFECTS</div>
  <div id="s15-t" class="lead" style="left:140px;top:400px;width:560px;line-height:1.7">给人分类，会反过来<br/>改造被分类的人。</div>
  <div id="s15-e" class="h md" style="left:140px;top:560px;font-size:38px;line-height:1.6;width:560px;white-space:normal">被叫久了“讨好型人格”，就越来越像<span class="acc">讨好型人格</span></div>
  <div id="s15-frame" style="left:740px;top:280px;width:1040px;height:480px;border:2px solid rgba(201,164,108,.0);border-radius:18px"></div>
  {boxes}
""", trans="blur")
k.tw("fade", "#s15-k", S(f) + 0.3); k.tw("pop", "#s15-h", S(f) + w(f, 1))
k.tw("fade", "#s15-who", S(f) + w(f, 1) + 0.4); k.tw("up", "#s15-t", S(f) + w(f, 2)); k.tw("up", "#s15-e", S(f) + w(f, 4))
for i, (_, wi) in enumerate(labels):
    k.tw("pop", f"#s15-b{i}", S(f) + w(f, wi))
k.raw(f'tl.to("#s15-frame",{{borderColor:"rgba(201,164,108,.8)",duration:0.5}},{round(S(f)+w(f,11),3)});')
k.raw(f'tl.to("#s15-frame",{{scale:0.86,duration:1.6,ease:"power2.inOut"}},{round(S(f)+w(f,11)+0.3,3)});')
k.raw(f'tl.to("[id^=s15-b]",{{scale:0.86,duration:1.6,ease:"power2.inOut",transformOrigin:"50% 50%"}},{round(S(f)+w(f,11)+0.3,3)});')

# ── F16 market ─────────────────────────────────────────────────────────────
f = 16
k.scene("s16", f, 0, k.D(f), """
  <div id="s16-k" class="kicker" style="left:140px;top:180px">反思 · 三</div>
  <div id="s16-h" class="h" style="left:140px;top:220px;font-size:64px">一个奖励简单答案的市场</div>
  <div id="s16-r1" style="left:140px;top:400px;width:1640px"><div class="unit">“一个原因解释一切”</div><div id="s16-b1" style="margin-top:12px;height:30px;width:1500px;background:#C9A46C;border-radius:4px"></div></div>
  <div id="s16-r2" style="left:140px;top:520px;width:1640px"><div class="unit muted">“要看条件、有例外”</div><div id="s16-b2" style="margin-top:12px;height:30px;width:420px;background:#5A5F6A;border-radius:4px"></div></div>
  <div id="s16-q" class="h md" style="left:140px;top:680px;font-size:48px">它奖励什么，取决于我们为什么<span class="acc">停下来</span>，为什么<span class="acc">转发</span></div>
""", trans="blur")
k.tw("fade", "#s16-k", S(f) + 0.3); k.tw("up", "#s16-h", S(f) + w(f, 1))
k.tw("fade", "#s16-r1", S(f) + w(f, 2)); k.tw("wipe", "#s16-b1", S(f) + w(f, 2), duration=1.0)
k.tw("fade", "#s16-r2", S(f) + w(f, 2) + 0.3); k.tw("wipe", "#s16-b2", S(f) + w(f, 2) + 0.3, duration=2.2)
k.tw("up", "#s16-q", S(f) + w(f, 4))

# ── F17 naming power + Socrates + questions ────────────────────────────────
f = 17
t_b = w(f, 10)
k.scene("s17a", f, 0, t_b, """
  <div id="s17-k" class="kicker" style="left:140px;top:180px">反思 · 四</div>
  <div id="s17-c1" class="card" style="left:140px;top:250px;width:780px;height:420px;padding:44px">
    <div class="mono acc">一起起名字</div><div class="lead" style="position:static;margin-top:24px">晚学 · 耍起 · 牛马</div>
    <div id="s17-r1" class="h" style="position:static;font-size:58px;margin-top:60px">→ 互相<span class="acc">看见</span></div></div>
  <div id="s17-c2" class="card" style="left:1000px;top:250px;width:780px;height:420px;padding:44px">
    <div class="mono steel">从别人那里买一个名字</div><div class="lead" style="position:static;margin-top:24px">一个理论 · 一个主播 · 一门课</div>
    <div id="s17-r2" class="h" style="position:static;font-size:58px;margin-top:60px">→ 被分进<span class="steel">格子</span></div></div>
""", trans="dip", glow=True)
k.tw("fade", "#s17-k", S(f) + 0.3); k.tw("up", "#s17-c1", S(f) + w(f, 1)); k.tw("up", "#s17-c2", S(f) + w(f, 8))
k.tw("fade", "#s17-r1", S(f) + w(f, 7)); k.tw("fade", "#s17-r2", S(f) + w(f, 9))
t_c = round(k.vo[f]["duration_s"] + 0.6, 3)
qs = [("它能不能被反驳？", 16), ("说它的人在卖什么？", 17), ("把名字拿掉，还剩下什么？", 18)]
qh = "".join(f'<div id="s17-q{i}" class="h" style="left:140px;top:{470 + i * 120}px;font-size:66px">{q}</div>' for i, (q, _) in enumerate(qs))
k.scene("s17b", f, t_b, t_c, f"""
  <div id="s17b-a" class="h md" style="left:140px;top:220px;font-size:46px">苏格拉底没提出过任何理论，</div>
  <div id="s17b-b" class="h md acc" style="left:140px;top:300px;font-size:46px">他只是一直在问。</div>
  {qh}
""", trans="focus")
k.tw("chars", "#s17b-a", S(f) + w(f, 11)); k.tw("chars", "#s17b-b", S(f) + w(f, 12))
for i, (_, wi) in enumerate(qs):
    k.tw("up", f"#s17-q{i}", S(f) + w(f, wi))
srcs = ["每日人物 / 腾讯新闻：冰学 晚学（2023-11-26）· 晚学（2024-10-24）· 雷学（2024-04-20）",
        "搜狐 2024-12（新浪舆情通：叶珂模仿大赛 14.3 亿次播放）",
        "网络公开报道（2025-09）：“三大理论”及后续审查、封禁",
        "华中师范大学 媒体伦理案例库（2022-08-25）：普信男",
        "X @AlanShao111（2026-08）：薄肌理论 · PANews / 腾讯新闻（2026-01-30）：孙学",
        "维基百科：躺平 · 腾讯新闻 / 知著网（2026-09-13）：耍起、李伯清回应",
        "弗洛姆《逃避自由》（1941）· Ian Hacking, The Looping Effects of Human Kinds（1995）",
        "完整清单（约 200 条）见仓库 research/中文互联网XX理论全清单.md"]
s_html = "".join(f'<div class="mono srcl" style="position:static;color:#C9C6BF;line-height:2.2;border-bottom:1px solid rgba(233,230,223,.08);text-transform:none">{E(s)}</div>' for s in srcs)
k.scene("s17c", f, t_c, k.D(f), f"""
  <div id="s17c-k" class="kicker" style="left:140px;top:160px">来源</div>
  <div id="s17c-l" style="left:140px;top:210px;width:1640px">{s_html}</div>
""", trans="dip", chrome=False)
k.raw(f'tl.fromTo("#s17c-l .srcl",{{opacity:0,y:12}},{{opacity:1,y:0,duration:0.4,ease:"power3.out",stagger:0.07}},{round(S(f)+t_c+0.4,3)});')
k.tw("fade", "#s17c-k", S(f) + t_c + 0.3)

k.write(bgm="assets/audio/bgm-reflect.mp3", bgm_vol=0.12)
