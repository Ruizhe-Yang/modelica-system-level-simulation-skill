#!/usr/bin/env python3
"""Create a new candidate with only safe whitespace cleanup.

Not an AST pretty-printer: removes repeated blank lines and trailing whitespace
outside strings/quoted identifiers/comments. Preserves those contents verbatim,
checks all lexical tokens and idempotence, and never rewrites the baseline.
"""
from __future__ import annotations
import argparse
import json
import shutil
import sys
from pathlib import Path
from verify_change_scope import lexical_tokens, scoped_signature


def format_text(text: str) -> str:
    tokens = lexical_tokens(text)
    protected = [(a,b) for t,a,b in tokens if t.startswith(('"', "'", '//', '/*'))]
    out = []; pos = 0; blank_run = 0
    for line in text.splitlines(keepends=True):
        end = pos + len(line)
        # Do not alter any line intersecting a literal or comment token. This
        # intentionally favors preservation over maximum cosmetic cleanup.
        if any(a < end and b > pos for a,b in protected):
            out.append(line); blank_run = 0; pos = end; continue
        if line.endswith('\r\n'): body, nl = line[:-2], '\r\n'
        elif line.endswith(('\n','\r')): body, nl = line[:-1], line[-1:]
        else: body, nl = line, ''
        body = body.rstrip(' \t')
        if not body:
            blank_run += 1
            if blank_run == 1: out.append(nl)
        else:
            blank_run = 0; out.append(body+nl)
        pos = end
    result = ''.join(out)
    if scoped_signature(text, 'format-only') != scoped_signature(result, 'format-only'):
        raise ValueError('Formatting changed a protected lexical token')
    return result


def format_tree(source: Path, candidate: Path) -> dict:
    source, candidate = source.resolve(), candidate.resolve()
    if not source.is_dir(): raise ValueError('Source directory does not exist')
    if candidate.exists(): raise ValueError('Candidate must be a new directory')
    if candidate.is_relative_to(source) or source.is_relative_to(candidate):
        raise ValueError('Baseline and candidate may not be nested')
    files = list(source.rglob('*'))
    if any(f.is_symlink() for f in files): raise ValueError('Symlinks require separate review')
    pending = {}; rows = []
    for f in files:
        if not f.is_file() or f.suffix != '.mo': continue
        raw = f.read_bytes(); bom = raw.startswith(b'\xef\xbb\xbf')
        text = raw.decode('utf-8-sig'); result = format_text(text)
        if format_text(result) != result: raise ValueError('Non-idempotent format: '+str(f))
        data = (b'\xef\xbb\xbf' if bom else b'') + result.encode('utf-8')
        rel = f.relative_to(source)
        pending[rel] = data
        rows.append({'file':rel.as_posix(),'changed':data != raw})
    if not pending: raise ValueError('No Modelica files found')
    candidate.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source,candidate)
    for rel,data in pending.items(): (candidate/rel).write_bytes(data)
    return {'version':'0.9.0','status':'FORMAT_ONLY_LEXICAL_MATCH','files':rows,
            'changedFileCount':sum(r['changed'] for r in rows), 'idempotent':True,
            'scope':'Whitespace outside literals/comments only; no full indentation, syntax, compilation or GUI validation'}


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path);p.add_argument('candidate',type=Path)
    p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    try:r=format_tree(a.source,a.candidate)
    except (ValueError,OSError,UnicodeError) as e:p.error(str(e))
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return 0
if __name__=='__main__':sys.exit(main())
