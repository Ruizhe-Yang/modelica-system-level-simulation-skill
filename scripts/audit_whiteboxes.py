#!/usr/bin/env python3
"""Audit graphical Modelica white boxes.

Policy:
- scan only directories explicitly declared with --dirs
- skip package.mo
- require Icon annotation
- equation section contains connect(...) statements only
- every connect has annotation(Line(...))
- reject algorithm/when/der/loops/if in the white-box equation section
- reject model inheritance unless --allow-extends is passed

Usage:
  python audit_whiteboxes.py /path/to/ModelicaPackage --dirs Systems/Functional Systems/Coupling
  python audit_whiteboxes.py . --dirs Components/Assemblies Systems
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def remove_balanced_annotations(text: str) -> str:
    out: list[str] = []
    pos = 0
    while True:
        match = re.search(r"\bannotation\s*\(", text[pos:])
        if not match:
            out.append(text[pos:])
            break
        start = pos + match.start()
        open_at = pos + match.end() - 1
        out.append(text[pos:start])
        depth = 0
        i = open_at
        in_string = False
        while i < len(text):
            char = text[i]
            if char == '"' and (i == 0 or text[i - 1] != "\\"):
                in_string = not in_string
            elif not in_string:
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                    if depth == 0:
                        i += 1
                        if i < len(text) and text[i] == ";":
                            i += 1
                        break
            i += 1
        pos = i
    return "".join(out)


def find_model_name(text: str) -> str | None:
    match = re.search(r"\bmodel\s+(\w+)", text)
    return match.group(1) if match else None


def candidate_files(root: Path, dirs: list[str]) -> list[Path]:
    files: list[Path] = []
    for name in dirs:
        base = root / name
        if base.is_file() and base.suffix.lower() == ".mo":
            files.append(base)
        elif base.is_dir():
            files.extend(base.rglob("*.mo"))
    return sorted({p.resolve() for p in files if p.name != "package.mo"})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--dirs", nargs="+", required=True, help="Directories/files explicitly designated as strict graphical white boxes")
    parser.add_argument("--allow-extends", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []
    checked = 0

    for path in candidate_files(root, args.dirs):
        text = path.read_text(encoding="utf-8-sig")
        name = find_model_name(text)
        if not name:
            continue
        checked += 1
        rel = path.relative_to(root) if root in path.parents else path

        if "Icon(" not in text:
            errors.append(f"{rel}: missing Icon annotation")
        if re.search(r"\bpartial\s+model\b", text):
            errors.append(f"{rel}: partial model forbidden by strict white-box policy")
        if not args.allow_extends and re.search(r"\bextends\s+[A-Za-z_]", text):
            errors.append(f"{rel}: model inheritance hides graphical topology")

        match = re.search(r"\bequation\b(.*?)\bend\s+" + re.escape(name) + r"\s*;", text, re.S)
        if not match:
            errors.append(f"{rel}: no equation section found")
            continue

        original = match.group(1)
        for statement in re.findall(r"\bconnect\s*\(.*?;", original, re.S):
            if "annotation" not in statement or "Line(" not in statement:
                errors.append(f"{rel}: connect() without visible annotation(Line)")

        clean = remove_balanced_annotations(original)
        clean = re.sub(r"//.*?$|/\*.*?\*/", "", clean, flags=re.M | re.S)
        statements = [s.strip() for s in clean.split(";") if s.strip()]
        for statement in statements:
            if not re.fullmatch(r"connect\s*\(.*\)", statement, re.S):
                errors.append(f"{rel}: non-connect equation: {statement[:120]!r}")
        if re.search(r"\b(algorithm|when|while|for|if|der)\b", clean):
            errors.append(f"{rel}: procedural/physical equation syntax found")

    if errors:
        print(f"WHITEBOX AUDIT FAIL: {len(errors)} issue(s), {checked} model(s) checked")
        for error in errors:
            print("-", error)
        return 1

    print(f"WHITEBOX AUDIT PASS: {checked} graphical model(s); connect-only equations; visible connection lines.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
