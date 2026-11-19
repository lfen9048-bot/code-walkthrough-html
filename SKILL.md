---
name: code-walkthrough-html
description: >-
  Generate an interactive, self-contained HTML source code walkthrough with a
  split-pane layout: syntax-highlighted source code on the left and an
  interactive flowchart with step-by-step explanations on the right. Clicking a
  flowchart node highlights and scrolls to the exact code lines, and clicking
  annotated code lines jumps back to the node. Use when the user asks to learn a
  codebase, visualize source code execution flow, or create an interactive HTML
  code walkthrough.
---

# Code Walkthrough HTML

Turn real source code into an interactive split-pane HTML learning experience:
- **Left pane**: Multi-file source viewer with line numbers, syntax highlighting, and active line-range focus.
- **Right pane**: Pan/zoom SVG flowchart + detailed explanation card (summary, design intent, key symbols, and source-verification hints).

## Workflow

1. **Trace the real codebase first**
   - Identify the entry point and 5–12 key execution steps across the relevant files.
   - Read the actual files to record exact `[startLine, endLine]` ranges. Never guess line numbers or paraphrase source code into fake snippets.

2. **Write a compact `walkthrough.spec.json`**
   - Follow [the spec reference](./references/spec.md) for node types (`entry`, `process`, `decision`, `io`, `exit`), grid layout (`col`, `row`), edges, and explanations.
   - Keep each node focused on one cohesive logical step so the left-pane highlight is precise.

3. **Build & validate the standalone HTML**
   - Run [build_walkthrough.py](./scripts/build_walkthrough.py) against the target repository:

   ```bash
   python3 scripts/build_walkthrough.py \
     --spec walkthrough.spec.json \
     --repo /path/to/repo \
     --output walkthrough.html
   ```

   - The script reads the real files from `--repo`, verifies every file path, node ID, edge, and `[startLine, endLine]` bound, and outputs a zero-dependency, offline-ready HTML file.
   - If the command exits non-zero, fix the reported line range or reference error and rerun.

4. **Deliver to the user**
   - Share the generated `.html` file path (and open or embed it if the environment supports it).
   - Remind the user they can click nodes, click highlighted code lines, or use `←` / `→` (`k` / `j`) keys to step through the execution flow.
