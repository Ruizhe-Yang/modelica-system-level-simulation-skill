#!/usr/bin/env python3
"""Heuristic static QA for Modelica Icon/Diagram annotations.

This tool flags likely visual-maintenance issues. It does not render Modelica
annotations and therefore must not replace visual inspection in OMEdit.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def iter_files(root: Path):
    for p in sorted(root.rglob("*.mo")):
        if any(part.startswith(".") for part in p.relative_to(root).parts):
            continue
        yield p


def inspect(path: Path, root: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8-sig", errors="ignore")
    rel = str(path.relative_to(root))
    issues = []
    is_public_visual = bool(re.search(r"^\s*(?:partial\s+)?(?:model|block)\s+\w+", text, re.M)) or bool(
        re.search(r"^\s*(?:expandable\s+)?connector\s+\w+", text, re.M)
    )
    icon = "Icon(" in text or bool(re.search(r"\bextends\s+Modelica\.Icons\.", text))
    connect_count = len(re.findall(r"\bconnect\s*\(", text))

    if is_public_visual and not icon:
        issues.append({"level": "warning", "file": rel, "issue": "public visual class has no Icon/Modelica.Icons base"})
    if connect_count and "Diagram(" not in text:
        issues.append({"level": "warning", "file": rel, "issue": "composite file has connect() calls but no Diagram annotation"})
    if "Bitmap(" in text:
        issues.append({"level": "info", "file": rel, "issue": "Bitmap graphic found; verify portability/editability is intentional"})
    if "Icon(" in text and "coordinateSystem" not in text:
        issues.append({"level": "info", "file": rel, "issue": "Icon exists without explicit coordinateSystem in this file"})
    if "Diagram(" in text and "coordinateSystem" not in text:
        issues.append({"level": "info", "file": rel, "issue": "Diagram exists without explicit coordinateSystem in this file"})

    # Connection visibility heuristic: inspect statement up to semicolon.
    for i, m in enumerate(re.finditer(r"\bconnect\s*\(.*?;", text, re.S), start=1):
        stmt = m.group(0)
        if "annotation" not in stmt or "Line(" not in stmt:
            issues.append({"level": "info", "file": rel, "issue": f"connect statement #{i} has no visible annotation(Line)"})

    # Generic-placeholder heuristic; intentionally conservative.
    if is_public_visual and "Icon(" in text:
        rects = len(re.findall(r"\bRectangle\s*\(", text))
        ellipses = len(re.findall(r"\bEllipse\s*\(", text))
        polygons = len(re.findall(r"\bPolygon\s*\(", text))
        lines = len(re.findall(r"\bLine\s*\(", text))
        if rects == 1 and ellipses == 0 and polygons == 0 and lines == 0 and "%name" in text:
            issues.append({"level": "info", "file": rel, "issue": "Icon may be a generic single-rectangle placeholder; inspect semantics"})
    return issues


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="Return nonzero when warnings are found")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    issues = []
    files = 0
    for p in iter_files(root):
        files += 1
        issues.extend(inspect(p, root))
    summary = {
        "root": str(root),
        "files_checked": files,
        "warnings": sum(i["level"] == "warning" for i in issues),
        "info": sum(i["level"] == "info" for i in issues),
        "issues": issues,
    }
    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(f"Visual audit: {files} file(s), {summary['warnings']} warning(s), {summary['info']} info item(s)")
        for item in issues:
            print(f"- [{item['level'].upper()}] {item['file']}: {item['issue']}")
    return 1 if args.strict and summary["warnings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
