#!/usr/bin/env python3
"""Static inventory and coverage audit for a Modelica project.

This is intentionally parser-light: it provides fast project-level signals, not a
replacement for checkModel/instantiateModel.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

CLASS_PATTERNS = {
    "packages": r"^\s*(?:encapsulated\s+)?package\s+\w+",
    "models": r"^\s*(?:partial\s+)?model\s+\w+",
    "blocks": r"^\s*(?:partial\s+)?block\s+\w+",
    "records": r"^\s*record\s+\w+",
    "connectors": r"^\s*(?:expandable\s+)?connector\s+\w+",
    "functions": r"^\s*(?:impure\s+|pure\s+)?function\s+\w+",
}


def count_classes(text: str) -> Counter:
    c = Counter()
    for key, pattern in CLASS_PATTERNS.items():
        c[key] = len(re.findall(pattern, text, re.M))
    return c


def first_public_class(text: str) -> tuple[str | None, str | None]:
    m = re.search(
        r"^\s*(?:(?:partial|encapsulated|expandable|impure|pure)\s+)?"
        r"(model|block|connector|record|function|package)\s+(\w+)",
        text,
        re.M,
    )
    return (m.group(1), m.group(2)) if m else (None, None)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--details", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    files = sorted(root.rglob("*.mo"))
    stats = Counter(files=len(files))
    by_dir = Counter()
    details = []

    for path in files:
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            text = path.read_text(encoding="latin-1")
        rel = path.relative_to(root)
        by_dir[str(rel.parent)] += 1
        stats.update(count_classes(text))
        stats["connect_calls"] += len(re.findall(r"\bconnect\s*\(", text))
        stats["der_calls"] += len(re.findall(r"\bder\s*\(", text))
        stats["when_occurrences"] += len(re.findall(r"\bwhen\b", text))
        stats["algorithm_sections"] += len(re.findall(r"^\s*algorithm\b", text, re.M))
        stats["initial_equation_sections"] += len(re.findall(r"^\s*initial\s+equation\b", text, re.M))
        stats["initial_algorithm_sections"] += len(re.findall(r"^\s*initial\s+algorithm\b", text, re.M))
        stats["dynamic_select"] += len(re.findall(r"\bDynamicSelect\s*\(", text))
        stats["bitmap_graphics"] += len(re.findall(r"\bBitmap\s*\(", text))
        stats["icons"] += int("Icon(" in text)
        stats["diagrams"] += int("Diagram(" in text)
        stats["documentation"] += int("Documentation(" in text)
        stats["standard_icon_extends"] += int(bool(re.search(r"\bextends\s+Modelica\.Icons\.", text)))

        kind, name = first_public_class(text)
        composite = bool(re.search(r"\bconnect\s*\(", text))
        icon_ok = ("Icon(" in text) or bool(re.search(r"\bextends\s+Modelica\.Icons\.", text))
        diagram_ok = "Diagram(" in text
        details.append({
            "file": str(rel),
            "kind": kind,
            "class": name,
            "has_icon": icon_ok,
            "has_diagram": diagram_ok,
            "has_documentation": "Documentation(" in text,
            "connect_calls": len(re.findall(r"\bconnect\s*\(", text)),
            "der_calls": len(re.findall(r"\bder\s*\(", text)),
            "when_occurrences": len(re.findall(r"\bwhen\b", text)),
            "composite_without_diagram": composite and not diagram_ok,
        })

    public_visual = [d for d in details if d["kind"] in {"model", "block", "connector"}]
    icon_coverage = 0.0 if not public_visual else sum(d["has_icon"] for d in public_visual) / len(public_visual)
    composite = [d for d in details if d["connect_calls"] > 0]
    diagram_coverage = 0.0 if not composite else sum(d["has_diagram"] for d in composite) / len(composite)
    doc_coverage = 0.0 if not files else stats["documentation"] / len(files)

    result = {
        "root": str(root),
        "stats": dict(stats),
        "coverage": {
            "icon_public_class": icon_coverage,
            "diagram_composite_file": diagram_coverage,
            "documentation_file": doc_coverage,
        },
        "top_directories": by_dir.most_common(20),
        "warnings": {
            "public_classes_without_icon": [d["file"] for d in public_visual if not d["has_icon"]],
            "composite_files_without_diagram": [d["file"] for d in composite if not d["has_diagram"]],
            "files_with_bitmap": [d["file"] for d in details if "Bitmap(" in (root/d["file"]).read_text(encoding="utf-8-sig", errors="ignore")],
        },
    }
    if args.details:
        result["details"] = details

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Modelica project inventory")
        for key, value in sorted(result["stats"].items()):
            print(f"- {key}: {value}")
        print(f"- icon_coverage(public model/block/connector): {icon_coverage:.1%}")
        print(f"- diagram_coverage(files with connect): {diagram_coverage:.1%}")
        print(f"- documentation_coverage(files): {doc_coverage:.1%}")
        print("Top directories:")
        for name, count in result["top_directories"]:
            print(f"  {name}: {count}")
        for label, items in result["warnings"].items():
            if items:
                print(f"WARNING {label}: {len(items)}")
                for item in items[:20]:
                    print(f"  - {item}")
                if len(items) > 20:
                    print(f"  ... {len(items)-20} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
