# code-walkthrough-html

> 把枯燥晦涩的源码变成「左代码 + 右流程图与详解」的交互式 HTML 学习页面。  
> Turn source code into an interactive split-pane HTML walkthrough: **source code on the left, flowchart & step-by-step explanations on the right**.

## 为什么做这个 Skill？

阅读陌生开源项目时，最大的痛点是**缺少全局视角**，只能一行行啃代码；而单纯让 AI 总结，又容易脱离真实源码、甚至出现幻觉。

**code-walkthrough-html** 采用「**Spec 驱动 + 真实源码注入**」的设计：
1. AI 只负责梳理执行主线，编写轻量的 `walkthrough.spec.json`（记录每个步骤对应的文件路径、起止行号与解释）。
2. 构建脚本 [`scripts/build_walkthrough.py`](./scripts/build_walkthrough.py) 从真实代码库读取源码、校验所有行号与引用合法性，然后注入自包含模板 [`scripts/template.html`](./scripts/template.html)。
3. 最终生成一个**零外部依赖、可离线打开**的单个 `.html` 文件：
   - **左侧源码区**：多文件 Tab 切换、行号、语法高亮、高亮区间自动滚动定位。
   - **右侧流程图与详解**：可缩放拖拽的 SVG 流程图 + 分步解析（核心逻辑、设计意图、关键符号、**源码验证提示**）。
   - **双向联动**：点击流程图节点 → 左侧高亮并滚动到对应代码行；点击带标注的代码行 → 右侧反向定位到对应流程节点；支持 `←` / `→`（或 `k` / `j`）键盘单步走读，以及深浅色主题切换。

---

## 目录结构

```text
code-walkthrough-html/
├── SKILL.md                   # Agent Skill 主指令（兼容 Antigravity / Claude Code / Codex 等）
├── references/
│   └── spec.md                # walkthrough.spec.json 字段规范与防幻觉约束
├── scripts/
│   ├── build_walkthrough.py   # 校验 spec、读取真实源码并生成独立 HTML（仅用 Python 标准库）
│   └── template.html          # 零依赖交互式双栏 HTML 模板
└── examples/
    ├── demo.spec.json         # 示例 spec（导读 build_walkthrough.py 自身）
    └── demo.html              # 预构建的示例交互页面（可直接用浏览器打开体验）
```

---

## 快速体验

直接用浏览器打开 [`examples/demo.html`](./examples/demo.html)，或者自己重新构建一次示例：

```bash
python3 scripts/build_walkthrough.py \
  --spec examples/demo.spec.json \
  --repo . \
  --output examples/demo.html
```

---

## 安装为 Agent Skill

### Antigravity / 通用 `.agents` 工作区

将本仓库克隆到项目的 `.agents/skills/` 或全局配置目录：

```bash
# 项目级（推荐分享给团队）
git clone https://github.com/lfen9048-bot/code-walkthrough-html.git .agents/skills/code-walkthrough-html

# 或全局级（Antigravity）
git clone https://github.com/lfen9048-bot/code-walkthrough-html.git ~/.gemini/config/skills/code-walkthrough-html
```

### Claude Code / Codex

```bash
# Claude Code
git clone https://github.com/lfen9048-bot/code-walkthrough-html.git ~/.claude/skills/code-walkthrough-html

# Codex
git clone https://github.com/lfen9048-bot/code-walkthrough-html.git ~/.codex/skills/code-walkthrough-html
```

安装后，直接对你的 AI 助手说：
> “用 `code-walkthrough-html` 带我走读一下 `src/xxx` 的执行流程，生成交互式 HTML。”

---

## License

[MIT](./LICENSE)
