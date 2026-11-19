#!/usr/bin/env python3
"""Build a self-contained interactive HTML code walkthrough from a JSON spec."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any


VALID_TYPES = {"entry", "process", "decision", "io", "exit"}


def load_json(path: Path) -> dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"Failed to parse spec JSON '{path}': {exc}") from exc


def resolve_repo_file(repo_root: Path, rel_path: str) -> Path:
    """Resolve a relative file path safely within repo_root."""
    candidate = (repo_root / rel_path).resolve()
    root_resolved = repo_root.resolve()
    if candidate != root_resolved and root_resolved not in candidate.parents:
        raise ValueError(f"Path escapes repo root: '{rel_path}'")
    if not candidate.is_file():
        raise FileNotFoundError(f"Referenced source file not found: '{rel_path}'")
    return candidate


def validate_and_collect_files(spec: dict[str, Any], repo_root: Path) -> dict[str, dict[str, Any]]:
    """Validate nodes/edges and read real source files referenced by the spec."""
    nodes = spec.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("Spec must contain a non-empty 'nodes' list.")

    inline_files: dict[str, str] = spec.get("inlineFiles") or {}
    collected: dict[str, dict[str, Any]] = {}
    node_ids: set[str] = set()

    for idx, node in enumerate(nodes):
        if not isinstance(node, dict):
            raise ValueError(f"Node at index {idx} must be an object.")
        nid = node.get("id")
        if not nid or not isinstance(nid, str):
            raise ValueError(f"Node at index {idx} is missing a string 'id'.")
        if nid in node_ids:
            raise ValueError(f"Duplicate node id: '{nid}'")
        node_ids.add(nid)

        ntype = node.get("type", "process")
        if ntype not in VALID_TYPES:
            raise ValueError(f"Node '{nid}' has invalid type '{ntype}'. Allowed: {sorted(VALID_TYPES)}")

        fpath = node.get("file")
        if not fpath or not isinstance(fpath, str):
            raise ValueError(f"Node '{nid}' is missing 'file'.")

        if fpath not in collected:
            if fpath in inline_files:
                content = str(inline_files[fpath])
            else:
                real_path = resolve_repo_file(repo_root, fpath)
                content = real_path.read_text(encoding="utf-8", errors="replace")
            collected[fpath] = {
                "content": content,
                "startLine": 1,
                "totalLines": len(content.splitlines()) or 1,
            }

        lines = node.get("lines")
        if lines is not None:
            if (
                not isinstance(lines, list)
                or len(lines) != 2
                or not all(isinstance(x, int) for x in lines)
            ):
                raise ValueError(f"Node '{nid}' 'lines' must be [startLine, endLine].")
            start, end = lines
            total = collected[fpath]["totalLines"]
            if start < 1 or end < start or end > total:
                raise ValueError(
                    f"Node '{nid}' lines [{start}, {end}] out of bounds for '{fpath}' (1..{total})."
                )

    edges = spec.get("edges") or []
    if not isinstance(edges, list):
        raise ValueError("'edges' must be a list.")
    for idx, edge in enumerate(edges):
        if not isinstance(edge, dict):
            raise ValueError(f"Edge at index {idx} must be an object.")
        src = edge.get("from")
        dst = edge.get("to")
        if src not in node_ids or dst not in node_ids:
            raise ValueError(f"Edge {idx} references unknown node id: {src!r} -> {dst!r}")

    return collected


def build_html(spec: dict[str, Any], files_map: dict[str, dict[str, Any]], template_path: Path) -> str:
    """Inject validated spec and real source files into template.html."""
    template = template_path.read_text(encoding="utf-8")
    payload = {
        "title": spec.get("title", "Source Code Walkthrough"),
        "subtitle": spec.get("subtitle", ""),
        "nodes": spec["nodes"],
        "edges": spec.get("edges", []),
        "files": {
            k: {"content": v["content"], "startLine": v["startLine"]}
            for k, v in files_map.items()
        },
    }
    safe_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    page_title = html.escape(str(payload["title"]))
    return (
        template.replace("__PAGE_TITLE__", page_title)
        .replace("__WALKTHROUGH_DATA__", safe_json)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an interactive HTML code walkthrough.")
    parser.add_argument("--spec", required=True, help="Path to walkthrough spec JSON.")
    parser.add_argument("--repo", default=".", help="Repository root containing referenced source files.")
    parser.add_argument("--output", required=True, help="Output HTML file path.")
    parser.add_argument(
        "--template",
        default=str(Path(__file__).resolve().parent / "template.html"),
        help="Optional custom HTML template path.",
    )
    args = parser.parse_args()

    spec_path = Path(args.spec).resolve()
    repo_root = Path(args.repo).resolve()
    output_path = Path(args.output).resolve()
    template_path = Path(args.template).resolve()

    spec = load_json(spec_path)
    files_map = validate_and_collect_files(spec, repo_root)
    html_out = build_html(spec, files_map, template_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_out, encoding="utf-8")

    summary = {
        "status": "ok",
        "output": str(output_path),
        "nodes": len(spec["nodes"]),
        "edges": len(spec.get("edges", [])),
        "files": list(files_map.keys()),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
