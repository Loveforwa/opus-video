#!/usr/bin/env python3
"""Video 2 — 《27 届秋招、十个专业和“耍起”》. Builds index.html with the shared hfkit design."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "..", "_shared"))
from hfkit import Kit, E  # noqa: E402

k = Kit(ROOT, "27届秋招、十个专业和耍起", chrome_left="就业 · 专业 · 耍起")
w = k.W
S = k.S

# ── F1 秋招开始 ──────────────────────────────────────────────────────────────
f = 1
k.scene("s1", f, 0, k.D(f), f"""
  <div id="s1-k" class="kicker" style="left:140px;top:200px">2027 届 · 秋招</div>
  <div id="s1-h" class="h" style="left:140px;top:250px;font-size:92px">{k.chars("秋招开始了")}</div>
  <div id="s1-l1" class="h md" style="left:140px;top:420px;font-size:58px">{k.chars("投了四五十份简历，")}</div>
  <div id="s1-l2" class="h md" style="left:140px;top:510px;font-size:58px">{k.chars('只等来<span class="acc">一次</span>大厂面试')}</div>
  <div id="s1-who" class="mono" style="left:144px;top:620px">河南师范大学 · 汉语言文学 · 27 届本科</div>
  {k.shot("s1-shot", "public/shots/huxiu-resume-quote.png", 1010, 250, 780, "huxiu-resume", "虎嗅 / 定焦One · 2026-08-17", crop_x=300, view_w=840, crop_y=300, view_h=400)}
""", trans="cut")
k.tw("fade", "#s1-k", S(f) + 0.1); k.tw("chars", "#s1-h", S(f) + 0.15)
k.tw("card3d", "#s1-shot", S(f) + w(f, 1)); k.tw("fade", "#s1-shot-src", S(f) + w(f, 1) + 0.5)
k.tw("chars", "#s1-l1", S(f) + w(f, 2)); k.hls("s1-shot", "huxiu-resume", S(f) + w(f, 2) + 0.3)
k.tw("chars", "#s1-l2", S(f) + w(f, 3)); k.tw("fade", "#s1-who", S(f) + w(f, 3) + 0.6)

# ── F2 1270 万 / 18.9% ───────────────────────────────────────────────────────
f = 2
k.scene("s2", f, 0, k.D(f), f"""
  <div id="s2-a" style="left:140px;top:220px"><div class="num" style="font-size:150px">1270<span class="unit" style="font-size:54px;margin-left:10px">万</span></div>
    <div class="unit" style="margin-top:14px">2026 届高校毕业生</div></div>
  <div id="s2-a2" class="pill acc" style="left:140px;top:470px">历年最多</div>
  <div id="s2-r" class="rule" style="left:140px;top:560px;width:700px"></div>
  <div id="s2-b" style="left:140px;top:600px"><div class="num acc" style="font-size:150px">18.9<span style="font-size:90px">%</span></div>
    <div class="unit" style="margin-top:14px">8 月 · 16–24 岁青年失业率（不含在校生）</div></div>
  {k.shot("s2-shot", "public/shots/jiemian-189-quote.png", 1000, 300, 800, "jiemian-189", "界面新闻 · 2026-09-17 · 国家统计局数据", crop_x=170, view_w=760, crop_y=250, view_h=320)}
""")
k.tw("up", "#s2-a", S(f) + 0.2); k.tw("pop", "#s2-a2", S(f) + w(f, 1))
k.tw("wipe", "#s2-r", S(f) + w(f, 2)); k.tw("up", "#s2-b", S(f) + w(f, 3))
k.tw("card3d", "#s2-shot", S(f) + w(f, 2)); k.tw("fade", "#s2-shot-src", S(f) + w(f, 2) + 0.5)
k.hls("s2-shot", "jiemian-189", S(f) + w(f, 3) + 0.4)

# ── F3 考公 vs 考研 → 同学的话 ───────────────────────────────────────────────
f = 3
t_split = w(f, 3)
k.scene("s3a", f, 0, t_split, f"""
  <div id="s3-k" class="kicker" style="left:140px;top:200px">考公 · 考研</div>
  <div id="s3-h" class="h" style="left:140px;top:250px;font-size:76px">{k.chars("很多人转去考公")}</div>
  <div id="s3-g" style="left:140px;top:430px;width:820px">
    <div class="unit">2026 年度国考 · 过审人数</div>
    <div style="display:flex;align-items:center;gap:22px;margin-top:12px"><div id="s3-gb" style="height:34px;width:600px;background:#C9A46C;border-radius:4px"></div><div class="num" style="font-size:56px">371.8万</div></div>
  </div>
  <div id="s3-y" style="left:140px;top:600px;width:820px">
    <div class="unit">2026 年考研 · 报名人数</div>
    <div style="display:flex;align-items:center;gap:22px;margin-top:12px"><div id="s3-yb" style="height:34px;width:553px;background:#5A5F6A;border-radius:4px"></div><div class="num muted" style="font-size:56px">343万</div></div>
  </div>
  <div id="s3-first" class="pill acc" style="left:140px;top:760px">国考人数第一次超过考研</div>
  {k.shot("s3-shot", "public/shots/qq-guokao-quote.png", 1060, 260, 720, "qq-guokao", "腾讯新闻 · 2025-12-01", crop_x=180, view_w=720, crop_y=300, view_h=420)}
""")
k.tw("fade", "#s3-k", S(f)); k.tw("chars", "#s3-h", S(f) + 0.1)
k.tw("fade", "#s3-g", S(f) + w(f, 1)); k.tw("wipe", "#s3-gb", S(f) + w(f, 1) + 0.1, duration=1.0)
k.tw("fade", "#s3-y", S(f) + w(f, 2)); k.tw("wipe", "#s3-yb", S(f) + w(f, 2) + 0.1, duration=1.0)
k.tw("pop", "#s3-first", S(f) + w(f, 2) + 1.0)
k.tw("card3d", "#s3-shot", S(f) + w(f, 1) + 0.3); k.tw("fade", "#s3-shot-src", S(f) + w(f, 1) + 0.8)
k.hls("s3-shot", "qq-guokao", S(f) + w(f, 2))
dots = "".join(f'<div id="s3-d{i}" style="width:64px;height:64px;border-radius:50%;border:2px solid #E9E6DF"></div>' for i in range(5))
k.scene("s3b", f, t_split, k.D(f), f"""
  <div id="s3b-k" class="kicker" style="left:140px;top:190px">那位同学说</div>
  <div id="s3b-l1" class="h md" style="left:140px;top:240px;font-size:52px">{k.chars("比她大一届的五个朋友")}</div>
  <div id="s3b-dots" style="left:140px;top:350px;display:flex;gap:26px">{dots}</div>
  <div id="s3b-l2" class="lead" style="left:140px;top:450px">四个毕业后待业，考公考编一个都没考上</div>
  <div id="s3b-q" class="h" style="left:140px;top:560px;font-size:66px;line-height:1.35">{k.chars("“所有人都在挤的路，")}<br/>{k.chars('未必比<span class="acc">市场化就业</span>更稳。”')}</div>
  {k.shot("s3b-shot", "public/shots/huxiu-crowd-quote.png", 1180, 210, 620, "huxiu-crowd", "虎嗅 / 定焦One · 2026-08-17", crop_x=300, view_w=840, crop_y=330, view_h=260)}
""", trans="focus")
k.tw("fade", "#s3b-k", S(f) + t_split + 0.3); k.tw("chars", "#s3b-l1", S(f) + w(f, 4))
k.raw(f'tl.fromTo("#s3b-dots > div",{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:0.4,ease:"power3.out",stagger:0.08}},{S(f)+w(f,4)+0.5});')
for i in range(1, 5):
    k.raw(f'tl.to("#s3-d{i}",{{borderColor:"#5A5F6A",backgroundColor:"rgba(90,95,106,.25)",duration:0.4}},{round(S(f)+w(f,5)+i*0.12,3)});')
k.tw("up", "#s3b-l2", S(f) + w(f, 5) + 0.2)
k.tw("card3d", "#s3b-shot", S(f) + w(f, 7), ry=12, ry2=4); k.tw("fade", "#s3b-shot-src", S(f) + w(f, 7) + 0.5)
k.tw("chars", "#s3b-q", S(f) + w(f, 8), stagger=0.045); k.hls("s3b-shot", "huxiu-crowd", S(f) + w(f, 8))

# ── F4 大厂押注 AI ───────────────────────────────────────────────────────────
f = 4
k.scene("s4", f, 0, k.D(f), f"""
  <div id="s4-k" class="kicker" style="left:140px;top:190px">大厂校招</div>
  <div id="s4-h" class="h" style="left:140px;top:240px;font-size:72px">{k.chars("几乎都在招 AI")}</div>
  {k.shot("s4-shot", "public/shots/ldb-ai-quote.png", 140, 400, 760, "ldb-ai", "劳动报 · 2026-08-16 · 脉脉数据", crop_x=100, view_w=840, crop_y=230, view_h=300)}
  <div id="s4-n" style="left:1060px;top:230px"><div class="num acc" style="font-size:170px">+47<span style="font-size:100px">%</span></div>
    <div class="unit" style="margin-top:16px">2026 年 1–5 月新发校招 AI 岗位 · 同比</div></div>
  <div id="s4-p1" style="left:1060px;top:520px;width:720px">
    <div class="mono">AI 岗位占新发校招岗位</div>
    <div style="display:flex;align-items:center;gap:16px;margin-top:12px"><div id="s4-b1" style="height:20px;width:264px;background:#5A5F6A;border-radius:3px"></div><div class="unit muted">26.41%</div></div>
    <div style="display:flex;align-items:center;gap:16px;margin-top:12px"><div id="s4-b2" style="height:20px;width:376px;background:#C9A46C;border-radius:3px"></div><div class="unit">37.56%</div></div>
  </div>
  <div id="s4-a" class="pill" style="left:1060px;top:740px">阿里 · AI 相关岗位超过六成</div>
  <div id="s4-b" class="pill acc" style="left:1480px;top:740px">部分企业 · 超九成</div>
""")
k.tw("fade", "#s4-k", S(f)); k.tw("chars", "#s4-h", S(f) + w(f, 1))
k.tw("card3d", "#s4-shot", S(f) + w(f, 2), ry=12, ry2=4); k.tw("fade", "#s4-shot-src", S(f) + w(f, 2) + 0.5)
k.hls("s4-shot", "ldb-ai", S(f) + w(f, 4))
k.tw("fade", "#s4-p1", S(f) + w(f, 3)); k.tw("wipe", "#s4-b1", S(f) + w(f, 3) + 0.2); k.tw("wipe", "#s4-b2", S(f) + w(f, 3) + 0.6)
k.tw("pop", "#s4-n", S(f) + w(f, 4)); k.tw("left", "#s4-a", S(f) + w(f, 5)); k.tw("left", "#s4-b", S(f) + w(f, 6))

# ── F5 计算机还行吗 ──────────────────────────────────────────────────────────
f = 5
k.scene("s5", f, 0, k.D(f), f"""
  <div id="s5-h" class="h" style="left:140px;top:200px;font-size:84px">{k.chars('那学<span class="acc">计算机</span>还行吗？')}</div>
  <div id="s5-who" class="mono" style="left:144px;top:340px">某 985 高校 · 软件工程 · 27 届硕士</div>
  <div id="s5-q" class="h md" style="left:140px;top:410px;font-size:54px;line-height:1.45">{k.chars("“纯做软件开发")}<br/>{k.chars("可能没什么前途了，")}<br/>{k.chars("太卷了。”")}</div>
  <div id="s5-up" class="pill" style="left:140px;top:720px">AI 岗占比 ↑</div>
  <div id="s5-dn" class="pill acc" style="left:360px;top:720px">岗位总数 ↓</div>
  {k.shot("s5-shot", "public/shots/huxiu-swe-quote.png", 1000, 330, 800, "huxiu-swe", "虎嗅 / 定焦One · 2026-08-17", crop_x=300, view_w=840, crop_y=300, view_h=330)}
""", trans="zoom")
k.tw("chars", "#s5-h", S(f) + 0.35); k.tw("fade", "#s5-who", S(f) + w(f, 1))
k.tw("card3d", "#s5-shot", S(f) + w(f, 1) + 0.2); k.tw("fade", "#s5-shot-src", S(f) + w(f, 1) + 0.7)
k.tw("chars", "#s5-q", S(f) + w(f, 2), stagger=0.04); k.hls("s5-shot", "huxiu-swe", S(f) + w(f, 2) + 0.3)
k.tw("left", "#s5-up", S(f) + w(f, 5)); k.tw("left", "#s5-dn", S(f) + w(f, 6))

# ── F6 绿牌专业没有计算机 ───────────────────────────────────────────────────
f = 6
greens = [("电气工程及其自动化", 2), ("微电子科学与工程", 3), ("自动化", 4), ("能源与动力工程", 5), ("车辆工程", 6), ("新能源科学与工程", 6)]
tiles = "".join(f'<div id="s6-t{i}" class="card" style="left:{140+(i%3)*560}px;top:{430+(i//3)*170}px;width:520px;height:140px">'
                f'<div class="mono acc">GREEN · 0{i+1}</div><div class="h md" style="position:static;font-size:40px;margin-top:14px">{n}</div></div>'
                for i, (n, _) in enumerate(greens))
k.scene("s6", f, 0, k.D(f), f"""
  <div id="s6-k" class="kicker" style="left:140px;top:190px">麦可思 · 2026 本科绿牌专业</div>
  <div id="s6-h" class="h" style="left:140px;top:240px;font-size:76px">{k.chars('计算机：<span class="acc">0</span> 个')}</div>
  {tiles}
  <div id="s6-src" class="mono" style="left:140px;top:800px">麦可思研究院《2026 年中国本科生就业报告》· 转引自腾讯新闻 2026-07-01</div>
""")
k.tw("fade", "#s6-k", S(f) + 0.2); k.tw("chars", "#s6-h", S(f) + w(f, 1))
for i, (_, wi) in enumerate(greens):
    k.tw("pop", f"#s6-t{i}", S(f) + w(f, wi) + (0.25 if i == 5 else 0))
k.tw("fade", "#s6-src", S(f) + w(f, 2))

# ── F7 再往后五年（推断） ───────────────────────────────────────────────────
f = 7
cards = [("01", "想清楚要解决什么问题", 4), ("02", "判断 AI 写的东西对不对", 5), ("03", "出了事兜得住", 6)]
c_html = "".join(f'<div id="s7-c{i}" class="card" style="left:{140+i*560}px;top:560px;width:520px;height:200px">'
                 f'<div class="num acc" style="font-size:54px">{a}</div><div class="h md" style="position:static;font-size:40px;margin-top:22px">{b}</div></div>'
                 for i, (a, b, _) in enumerate(cards))
k.scene("s7", f, 0, k.D(f), f"""
  <div id="s7-k" class="kicker" style="left:140px;top:190px">再往后五年 · 我的判断</div>
  <div id="s7-h" class="h" style="left:140px;top:240px;font-size:80px">{k.chars("写代码，会像搜索一样普通")}</div>
  <div id="s7-l" class="lead" style="left:140px;top:420px">程序员值钱的地方，会挪到别处：</div>
  {c_html}
""", trans="focus", glow=True)
k.tw("fade", "#s7-k", S(f) + 0.4); k.tw("chars", "#s7-h", S(f) + w(f, 2))
k.tw("up", "#s7-l", S(f) + w(f, 3))
for i, (_, _, wi) in enumerate(cards):
    k.tw("up", f"#s7-c{i}", S(f) + w(f, wi))

# ── F8 十个专业 ─────────────────────────────────────────────────────────────
f = 8
majors = [  # name, light-at clause, verdict, verdict-at clause, tone
    ("电子信息", 3, "最稳", 6, "acc"), ("电气", 4, "最稳", 6, "acc"), ("新能源", 5, "最稳", 6, "acc"),
    ("人工智能", 7, "最热 · 门槛在涨", 8, "acc"), ("临床医学", 9, "慢，但不太怕 AI", 10, "acc"),
    ("计算机", 11, "基础岗被挤压", 14, "steel"), ("金融", 12, "基础岗被挤压", 14, "steel"), ("法学", 13, "基础岗被挤压", 14, "steel"),
    ("土木", 16, "看房地产 · 投资 −19.9%", 17, "steel"), ("师范", 18, "出生人口 792 万", 19, "steel")]
tiles = ""
for i, (n, _, v, _, tone) in enumerate(majors):
    x, y = 140 + (i % 5) * 332, 330 + (i // 5) * 250
    tiles += (f'<div id="s8-t{i}" class="card" style="left:{x}px;top:{y}px;width:304px;height:220px;opacity:.22">'
              f'<div class="h md" style="position:static;font-size:46px">{n}</div>'
              f'<div id="s8-v{i}" class="unit {tone}" style="position:static;font-size:24px;margin-top:22px;opacity:0">{v}</div></div>')
k.scene("s8", f, 0, k.D(f), f"""
  <div id="s8-k" class="kicker" style="left:140px;top:170px">十个热门专业 · 五年推测</div>
  <div id="s8-h" class="h" style="left:140px;top:210px;font-size:60px">{k.chars("五年后，大概会这样")}</div>
  <div id="s8-tag" class="pill" style="left:1300px;top:220px">推测，不是定论</div>
  {tiles}
  <div id="s8-comp" class="pill acc" style="left:140px;top:840px">懂行业又会用 AI 的人更好找工作</div>
  <div id="s8-news" class="card" style="left:1140px;top:830px;width:660px;height:70px;padding:18px 26px"><span class="unit" style="font-size:26px">新闻传播 · <span class="steel">传统岗位还在变少</span></span></div>
""")
k.tw("fade", "#s8-k", S(f)); k.tw("chars", "#s8-h", S(f) + w(f, 1)); k.tw("pop", "#s8-tag", S(f) + w(f, 2))
for i, (_, li, _, vi, tone) in enumerate(majors):
    lit = "rgba(201,164,108,.55)" if tone == "acc" else "rgba(143,163,184,.45)"
    k.raw(f'tl.fromTo("#s8-t{i}",{{opacity:0.22,borderColor:"rgba(233,230,223,.10)"}},{{opacity:1,borderColor:"{lit}",duration:0.5,ease:"power2.out"}},{round(S(f)+w(f,li),3)});')
    k.tw("up", f"#s8-v{i}", S(f) + w(f, vi) + (i % 3) * 0.08, y=12)
k.tw("left", "#s8-comp", S(f) + w(f, 15)); k.tw("up", "#s8-news", S(f) + w(f, 20))

# ── F9 耍起 ─────────────────────────────────────────────────────────────────
f = 9
lines16 = [("耍中找钱", 3), ("找钱来耍", 4), ("找耍结合", 5), ("以耍为主", 6)]
l_html = "".join(f'<div id="s9-l{i}" class="h" style="left:1260px;top:{330+i*120}px;font-size:76px">{t}</div>' for i, (t, _) in enumerate(lines16))
k.scene("s9", f, 0, k.D(f), f"""
  <div id="s9-k" class="kicker" style="left:140px;top:170px">今年网上火了一个词</div>
  {k.shot("s9-shot", "public/shots/qq-shuaqi-quote.png", 140, 220, 820, "qq-shuaqi", "腾讯新闻 / 知著网 · 2026-09-13", crop_x=180, view_w=720, crop_y=50, view_h=470)}
  <div id="s9-big" class="h acc" style="left:1000px;top:190px;font-size:120px">耍起</div>
  {l_html}
  <div id="s9-who" class="mono" style="left:1264px;top:830px">—— 李伯清 · 评书</div>
""", trans="focus", glow=True)
k.tw("fade", "#s9-k", S(f) + 0.4); k.tw("pop", "#s9-big", S(f) + w(f, 1))
k.tw("card3d", "#s9-shot", S(f) + 0.7, ry=12, ry2=4); k.tw("fade", "#s9-shot-src", S(f) + 1.2)
for i, (_, wi) in enumerate(lines16):
    k.tw("up", f"#s9-l{i}", S(f) + w(f, wi), y=20)
k.hls("s9-shot", "qq-shuaqi", S(f) + w(f, 3)); k.tw("fade", "#s9-who", S(f) + w(f, 6) + 0.4)

# ── F10 为什么能火 ──────────────────────────────────────────────────────────
f = 10
k.scene("s10", f, 0, k.D(f), f"""
  <div id="s10-k" class="kicker" style="left:140px;top:190px">为什么能火 · 我的理解</div>
  <div id="s10-h1" class="h md" style="left:140px;top:250px;font-size:64px">{k.chars("拼命往前冲，回报越来越说不准")}</div>
  <div id="s10-h2" class="h" style="left:140px;top:360px;font-size:80px">{k.chars('那就先把<span class="acc">眼前的日子</span>过好')}</div>
  <div id="s10-c1" class="card" style="left:140px;top:560px;width:640px;height:200px"><div class="mono">躺平</div><div class="h md muted" style="position:static;font-size:40px;margin-top:22px;text-decoration:line-through;text-decoration-thickness:2px">不干了</div></div>
  <div id="s10-c2" class="card" style="left:830px;top:560px;width:960px;height:200px;border-color:rgba(201,164,108,.5)"><div class="mono acc">耍起</div><div class="h md" style="position:static;font-size:40px;margin-top:22px"><span id="s10-a">班照上，</span><span id="s10-b">简历照投，</span><span id="s10-c" class="acc">只是不再把自己绷到极限</span></div></div>
""", trans="blur")
k.tw("fade", "#s10-k", S(f) + 0.3); k.tw("chars", "#s10-h1", S(f) + w(f, 2)); k.tw("chars", "#s10-h2", S(f) + w(f, 4))
k.tw("up", "#s10-c1", S(f) + w(f, 5)); k.tw("up", "#s10-c2", S(f) + w(f, 6))
k.tw("fade", "#s10-a", S(f) + w(f, 6) + 0.2); k.tw("fade", "#s10-b", S(f) + w(f, 7)); k.tw("fade", "#s10-c", S(f) + w(f, 8))

# ── F11 九十年代的日本 ──────────────────────────────────────────────────────
f = 11
k.scene("s11", f, 0, k.D(f), f"""
  <div id="s11-k" class="kicker" style="left:140px;top:170px">历史参照 · 1990s 日本</div>
  <div id="s11-h" class="h" style="left:140px;top:215px;font-size:70px">{k.chars("九十年代的日本，有点像")}</div>
  <div id="s11-line" class="rule" style="left:140px;top:420px;width:1640px;background:rgba(233,230,223,.3)"></div>
  <div id="s11-m1" style="left:140px;top:395px"><div style="width:50px;height:50px;border-radius:50%;background:#C9A46C"></div><div class="unit" style="margin-top:16px">泡沫破了</div></div>
  <div id="s11-m2" style="left:700px;top:395px"><div style="width:50px;height:50px;border-radius:50%;background:#E9E6DF"></div><div class="unit" style="margin-top:16px">毕业生扎堆找工作</div></div>
  <div id="s11-m3" style="left:1260px;top:395px"><div style="width:50px;height:50px;border-radius:50%;background:#8FA3B8"></div><div class="unit" style="margin-top:16px">年轻人降低欲望</div></div>
  <svg id="s11-chart" style="left:140px;top:560px" width="1100" height="300" viewBox="0 0 1100 300">
    <line x1="40" y1="40" x2="1060" y2="40" stroke="rgba(233,230,223,.25)" stroke-dasharray="6 8"/>
    <text x="1060" y="28" fill="#8D919B" font-size="18" text-anchor="end" font-family="IBM Plex Mono">正常年份毕业的同龄人</text>
    <path id="s11-us" d="M40 220 C 260 140, 420 60, 1060 44" fill="none" stroke="#8FA3B8" stroke-width="5"/>
    <path id="s11-jp" d="M40 220 C 300 200, 600 170, 1060 140" fill="none" stroke="#C9A46C" stroke-width="5"/>
  </svg>
  <div id="s11-us-l" class="unit steel" style="left:1270px;top:580px">美国：几年后追了上来</div>
  <div id="s11-jp-l" class="unit acc" style="left:1270px;top:680px">日本：影响拖得更久</div>
  <div id="s11-why" class="pill" style="left:1270px;top:770px">企业习惯只招应届生</div>
  <div id="s11-src" class="mono" style="left:140px;top:870px">示意图 · 依据 Genda, Kondo & Ohta (2010), Journal of Human Resources</div>
""", trans="focus")
k.tw("fade", "#s11-k", S(f) + 0.3); k.tw("chars", "#s11-h", S(f) + w(f, 1))
k.tw("wipe", "#s11-line", S(f) + w(f, 2), duration=1.2)
for i, wi in enumerate([2, 3, 4], 1):
    k.tw("up", f"#s11-m{i}", S(f) + w(f, wi))
k.tw("fade", "#s11-chart", S(f) + w(f, 6))
for pid, wi in [("s11-us", 8), ("s11-jp", 9)]:
    k.raw(f'tl.fromTo("#{pid}",{{strokeDasharray:1200,strokeDashoffset:1200}},{{strokeDashoffset:0,duration:1.6,ease:"power2.inOut"}},{round(S(f)+w(f,wi),3)});')
k.tw("left", "#s11-us-l", S(f) + w(f, 8) + 0.6); k.tw("left", "#s11-jp-l", S(f) + w(f, 9) + 0.6)
k.tw("pop", "#s11-why", S(f) + w(f, 10)); k.tw("fade", "#s11-src", S(f) + w(f, 6) + 0.5)

# ── F12 鼓励 + 来源 ─────────────────────────────────────────────────────────
f = 12
t_b = w(f, 10)
k.scene("s12a", f, 0, t_b, f"""
  <div id="s12-k" class="kicker" style="left:140px;top:170px">对我们来说</div>
  <div id="s12-h" class="h" style="left:140px;top:215px;font-size:72px">{k.chars('第一份工作不理想，<span class="acc">别把它当终点</span>')}</div>
  <svg id="s12-chart" style="left:140px;top:420px" width="1100" height="360" viewBox="0 0 1100 360">
    <line x1="60" y1="60" x2="1060" y2="60" stroke="rgba(233,230,223,.3)" stroke-width="2"/>
    <text x="60" y="40" fill="#8D919B" font-size="20" font-family="IBM Plex Mono">正常年份毕业的同龄人</text>
    <path id="s12-p" d="M60 300 C 360 230, 640 110, 1060 64" fill="none" stroke="#C9A46C" stroke-width="6"/>
    <text x="60" y="345" fill="#8D919B" font-size="20" font-family="IBM Plex Mono">毕业</text>
    <text x="1060" y="345" fill="#8D919B" font-size="20" font-family="IBM Plex Mono" text-anchor="end">≈ 10 年</text>
  </svg>
  <div id="s12-n" style="left:1290px;top:430px"><div class="num acc" style="font-size:120px">−9%</div><div class="unit" style="margin-top:10px">衰退时毕业 · 起薪平均</div></div>
  <div id="s12-z" style="left:1290px;top:640px"><div class="h md" style="position:static;font-size:46px">十年后差距基本消失</div><div class="unit muted" style="margin-top:10px">主要靠换工作，换到更好的公司</div></div>
  <div id="s12-src" class="mono" style="left:140px;top:860px">示意图 · 依据 Oreopoulos, von Wachter & Heisz (2012), AEJ: Applied（加拿大数据）</div>
""", trans="blur")
k.tw("fade", "#s12-k", S(f) + 0.3); k.tw("chars", "#s12-h", S(f) + w(f, 1))
k.tw("fade", "#s12-chart", S(f) + w(f, 3)); k.tw("fade", "#s12-src", S(f) + w(f, 3) + 0.4)
k.tw("pop", "#s12-n", S(f) + w(f, 5))
k.raw(f'tl.fromTo("#s12-p",{{strokeDasharray:1300,strokeDashoffset:1300}},{{strokeDashoffset:0,duration:2.4,ease:"power2.inOut"}},{round(S(f)+w(f,6),3)});')
k.tw("up", "#s12-z", S(f) + w(f, 7));
t_c = round(k.vo[f]["duration_s"] + 0.3, 3)
k.scene("s12b", f, t_b, t_c, f"""
  {k.shot("s12b-shot", "public/shots/qq-cooldown-quote.png", 140, 220, 820, "qq-cooldown", "腾讯新闻 / 知著网 · 2026-09-13", crop_x=180, view_w=720, crop_y=330, view_h=330)}
  <div id="s12b-q" class="lead" style="left:140px;top:640px;width:820px">李伯清：那十六个字是说给退休的人听的，<br/>年轻人还是要以奋斗为主。</div>
  <div id="s12b-1" class="h" style="left:1060px;top:260px;font-size:80px">想耍就耍，</div>
  <div id="s12b-2" class="h" style="left:1060px;top:380px;font-size:80px">简历也接着投。</div>
  <div id="s12b-3" class="h md acc" style="left:1060px;top:560px;font-size:56px;line-height:1.5">{k.chars("行情差的时候，")}<br/>{k.chars("往前挪一点也算数。")}</div>
""", trans="focus", glow=True)
k.tw("card3d", "#s12b-shot", S(f) + t_b + 0.2, ry=12, ry2=4); k.tw("fade", "#s12b-shot-src", S(f) + t_b + 0.7)
k.hls("s12b-shot", "qq-cooldown", S(f) + w(f, 11)); k.tw("up", "#s12b-q", S(f) + w(f, 11) + 0.3)
k.tw("up", "#s12b-1", S(f) + w(f, 13)); k.tw("up", "#s12b-2", S(f) + w(f, 14))
k.tw("chars", "#s12b-3", S(f) + w(f, 15), stagger=0.05)
srcs = ["定焦One《大厂校招狂卷AI，应届生懵了》· 虎嗅 2026-08-17", "国家统计局 8 月分年龄组失业率 · 界面新闻 2026-09-17",
        "教育部：2026 届高校毕业生 1270 万 · 新华网 2025-11-20", "国考过审 371.8 万 / 考研报名 343 万 · 腾讯新闻 2025-12-01",
        "脉脉校招 AI 岗位数据 · 劳动报 2026-08-16", "麦可思《2026 年中国本科生就业报告》· 腾讯新闻 2026-07-01",
        "统计局 1–8 月房地产开发投资 −19.9% · 中新网 2026-09-15", "统计局：2025 年出生人口 792 万 · 2026-01-19",
        "《从大压抑到大耍起》· 腾讯新闻 / 知著网 2026-09-13", "Genda, Kondo & Ohta 2010 · Oreopoulos, von Wachter & Heisz 2012"]
s_html = "".join(f'<div class="mono srcl" style="position:static;color:#C9C6BF;line-height:2.1;border-bottom:1px solid rgba(233,230,223,.08)">{E(s)}</div>' for s in srcs)
k.scene("s12c", f, t_c, k.D(f), f"""
  <div id="s12c-k" class="kicker" style="left:140px;top:150px">来源</div>
  <div id="s12c-l" style="left:140px;top:200px;width:1640px">{s_html}</div>
""", trans="dip", chrome=False)
k.raw(f'tl.fromTo("#s12c-l .srcl",{{opacity:0,y:12}},{{opacity:1,y:0,duration:0.4,ease:"power3.out",stagger:0.06}},{round(S(f)+t_c+0.4,3)});')
k.tw("fade", "#s12c-k", S(f) + t_c + 0.3)

k.write(bgm="assets/audio/bgm-pad.mp3", bgm_vol=0.13)
