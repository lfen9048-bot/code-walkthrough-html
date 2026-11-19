# Walkthrough Spec Reference (`spec.json`)

Write a compact JSON spec describing the execution flow and mapping each step to exact file paths and line ranges. `scripts/build_walkthrough.py` reads the real source files from `--repo`, validates all line bounds, and generates the interactive HTML.

## Schema

```json
{
  "title": "Short project or feature title",
  "subtitle": "Optional entry point or scope note (e.g. CLI -> build_html)",
  "nodes": [
    {
      "id": "parse_args",
      "title": "1. 解析 CLI 参数",
      "type": "entry",
      "col": 0,
      "row": 0,
      "file": "scripts/build_walkthrough.py",
      "lines": [105, 121],
      "summary": "What this step does in plain language.",
      "why": "Optional design rationale or architectural context.",
      "symbols": ["main()", "argparse.ArgumentParser"],
      "verify": "Optional note on what the reader should double-check in source."
    }
  ],
  "edges": [
    {
      "from": "parse_args",
      "to": "load_spec",
      "label": "optional"
    }
  ]
}
```

## Field Rules

- **`nodes[].id`**: Unique string identifier.
- **`nodes[].type`**: One of `entry`, `process`, `decision`, `io`, `exit` (defaults to `process`).
- **`nodes[].col` / `nodes[].row`**: Zero-based integer grid coordinates for clean layout:
  - Main happy path: `col: 0`, incrementing `row: 0, 1, 2, ...`
  - Branches / helpers: `col: 1` (or `col: -1` avoided—keep `col >= 0` starting at 0).
- **`nodes[].file`**: Relative path from `--repo` root.
- **`nodes[].lines`**: `[startLine, endLine]` (1-indexed, inclusive). Must be within the actual file's line count.
- **`edges[]`**: `from` and `to` must reference valid `nodes[].id`. Back-edges (`to.row < from.row`) render as loop arcs on the right.

## Anti-Hallucination Checklist

1. Never guess line numbers—inspect the file first and record exact `[start, end]` bounds.
2. Keep each node focused on **one logical step** (typically 5–40 lines), not an entire 300-line file.
3. Include a `verify` note on tricky branches, error handling, or side effects so learners know what to inspect in the raw code.
