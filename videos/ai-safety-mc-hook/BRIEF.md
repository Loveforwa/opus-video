---
workflow: faceless-explainer
flow: automation
storyboard: yes
message: "AI 的能力已经强到能把 MC 塞进别的游戏里——同样的能力落在坏人手里、或 AI 自己犯错时，后果可能无法挽回；安全是让它走得更远的方向盘。"
destination: bilibili-youtube
aspect: 1920x1080
language: zh-CN
audience: 对 AI 感兴趣的中文互联网用户、开发者和游戏玩家
length: 90s
angle: narrative
narration: yes
voice: minimax-male-explainer
style_preset: broadside
---

## Intent

一支 90 秒的中文 AI 安全思考视频。开头用当下很火的「AI 逆向游戏、把 Minecraft 导入/在别的游戏里玩 MC」做钩子，解释它是怎么做到的，
然后转向：同样的能力被坏人使用会怎样（真实案例），AI 自己犯错造成无法挽回的后果会怎样（真实案例），
穿插 AI 安全关键词，最后让 AI 思考自己的存在。基调：冷静、有分量、不贩卖恐慌。

## Assets

- public/shots/*.png — 真实网页截图（Playwright 抓取），每个案例一张，作为证据镜头使用。

## Customizations

- 配音：MiniMax TTS（speech 系列 HD 模型），男声、适合讲解的声线；API key 只存在仓库之外，绝不提交。
- 真实案例必须配真实网页 / 图片截图，而不是纯 HTML 图形。
- 字幕：中文逐句字幕。

## Notes

- 所有案例必须可查证，屏幕上标注来源与日期。
- 不夸大、不编造；没有核实的说法不进片。
- 网络环境受限：x.com / bilibili / youtube / 多数新闻站当前被出口策略拦截，能直接截图的是 anthropic.com 与 github.com；需要用户放行更多域名后再补截。
