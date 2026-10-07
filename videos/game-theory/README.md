# 博弈论 · 60s（3D 卡点科普短片）

竖屏 1080×1920 · 30fps · 60s。用 three.js 写成，每一帧都是时间 `t` 的纯函数，
所以同一份代码既能在浏览器里**带 BGM 实时预览**，也能**逐帧精确渲染**成 MP4。
BGM 取自素材前 60 秒（112 BPM），所有切镜、文字砸入和变速都对齐在 `assets/audio/beats.json` 的拍点上。

## 本地运行

需要：Node.js 18+、ffmpeg、Chrome（或由 Playwright 自带的 Chromium）。

```bash
git clone <本仓库> && cd opus-video
git checkout claude/determined-pascal-8o5nyd
cd videos/game-theory
npm install
```

### 1) 实时预览（推荐先看这个）
```bash
npm run preview
# 浏览器打开 http://localhost:8123/?play
# 点击画面开始/暂停 · 空格 暂停 · ←/→ 跳 2 秒 · [ ] 跳一拍
# 从某个时间点开始：http://localhost:8123/?play&t=17
```

### 2) 渲染成 MP4
```bash
npx playwright install chromium        # 只需一次；或用 --chrome 指定本机 Chrome
npm run render                          # → renders/game-theory.mp4（带 BGM）
```
常用参数：
```bash
node scripts/render.mjs --chrome "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
node scripts/render.mjs --workers 3            # 多开页面并行（有独显时更快）
node scripts/render.mjs --from 17 --to 26      # 只渲一段
node scripts/render.mjs --headed               # 有窗口模式，确保走显卡
npm run stills                                  # 只出 20 张关键帧到 renders/stills/
```
渲染开始时会打印 `WebGL renderer:`。如果显示 **SwiftShader**，说明在用 CPU 软渲染（很慢，约 1 秒 1 帧），
换成 `--headed` 或用 `--chrome` 指定本机 Chrome 即可走显卡。

## 结构
- `main.js` — 全部场景（7 段）、文字系统、HUD、后期合成（RGB 分离 / 方向模糊 / 颗粒 / 暗角）
- `scripts/serve.mjs` — 本地静态服务器
- `scripts/render.mjs` — Playwright 逐帧抓取 + ffmpeg 合成
- `assets/audio/bgm60.m4a` — BGM（前 60 秒，结尾 1.6s 淡出）；`beats.json` — 拍点与低频包络

## 改内容
- 文案：搜索 `tx(`，每条是 `tx(开始时间, 结束时间, '文字{高亮}', {样式})`，时间都写成 `B(拍号)`。
- 节奏：`B(n)` 是第 n 拍的时间；`bstep(t, n0, n1)` 产生"每拍一顿"的卡点运动；`kick(t)` 是每拍的冲击包络。
- 分段：S1 开场 0–8.6s · S2 囚徒困境 · S3 纳什均衡（17s drop）· S4 重复博弈 · S5 零和/正和 · S6 生活 · S7 结论。
