#!/usr/bin/env python3
"""Fail-closed lexical scope comparison, not a Modelica compiler.

Unlike the legacy documentation helper, each mode has its own exact exemptions.
FORMAT_ONLY preserves string and comment tokens verbatim. Type/causality changes,
parameter values, connect endpoints, result settings and solver annotations never
become visual edits. Unsupported syntax is a review item, not a pass.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path
from modelica_support import Source, LEX, apply
from connection_colors import all_connections

MODES = {'format-only', 'documentation-only', 'connection-color-only',
         'visual-only', 'auxiliary-only'}


def lexical_tokens(text: str) -> list[tuple[str, int, int]]:
    """Tokenize all text, preserving comments, quoted identifiers and strings."""
    result = []
    i = 0
    while i < len(text):
        m = LEX.match(text, i)
        if m is None:
            raise ValueError(f'Unsupported lexical input at {i}')
        token = m[0]
        if token in ('"', "'"):
            raise ValueError(f'Unterminated quoted token at {i}')
        if text.startswith('/*', i) and not (token.startswith('/*') and token.endswith('*/')):
            raise ValueError(f'Unterminated block comment at {i}')
        if not token.isspace():
            result.append((token, i, m.end()))
        i = m.end()
    return result


def hash_tokens(tokens: list[str]) -> str:
    h = hashlib.sha256()
    for token in tokens:
        h.update(token.encode('utf-8'))
        h.update(b'\0')
    return h.hexdigest()


def scoped_signature(text: str, mode: str, root_version: bool = False) -> str:
    if mode not in MODES:
        raise ValueError('Unknown change mode: ' + mode)
    original = lexical_tokens(text)
    if mode == 'format-only':
        if root_version:
            raise ValueError('FORMAT_ONLY never exempts release versions')
        return hash_tokens([t for t, _, _ in original])
    s = Source(text)
    if s.unparsed:
        raise ValueError('Unsupported Modelica source syntax: ' + repr(s.unparsed[:2]))
    if not s.classes:
        raise ValueError('No class definition found')
    doc = mode in {'documentation-only', 'auxiliary-only'}
    visual = mode == 'visual-only'
    color = mode in {'connection-color-only', 'auxiliary-only'}
    patches: list[tuple[int, int, str]] = []
    exempt: list[tuple[int, int]] = []
    class_annotations = {}
    decl_annotation_starts = set()
    # Recognize only actual declaration/class annotation ownership.
    for c in s.all_classes():
        if doc and c.desc_span:
            patches.append((*c.desc_span, ''))
            exempt.append(c.desc_span)
        for d in c.decls:
            if doc and d.desc_span:
                patches.append((*d.desc_span, ''))
                exempt.append(d.desc_span)
            for t in s.scan(d.a, d.b):
                if t.value == 'annotation':
                    decl_annotation_starts.add(t.a)
        for an in c.anns:
            class_annotations[an[0]] = (c, an)
    # Only top-level metadata nodes are exempt; experiment/Evaluate/etc remain.
    for i, (token, a, b) in enumerate(original):
        if token != 'annotation' or i + 1 >= len(original) or original[i+1][0] != '(':
            continue
        g = original[i+1][1]
        args = s.ann_args(g)
        owner = class_annotations.get(a)
        drop = set()
        if owner:
            if doc:
                drop.add('Documentation')
            if visual:
                drop.update(('Icon', 'Diagram'))
            c, an = owner
            if root_version and not s.within and c in s.classes and c.kind == 'package':
                drop.add('version')
        if visual and a in decl_annotation_starts:
            drop.add('Placement')
        removed = [p for p in args if p and p[0].value in drop]
        if not removed:
            continue
        kept = [s.text[p[0].a:p[-1].b] for p in args if p and p[0].value not in drop]
        for p in removed:
            exempt.append((p[0].a, p[-1].b))
        end = s.pairs[g]
        replacement = 'annotation(' + ','.join(kept) + ')' if kept else ''
        # Class annotations are standalone elements, but declaration annotations
        # must keep the declaration's semicolon.
        if not kept and owner and not owner[0].short:
            end = owner[1][3]
        patches.append((a, end, replacement))
    # Connection Line is exempt only where it annotates a true connect.
    for x in all_connections(s):
        line = x['line']
        if line is None:
            continue
        if color:
            parts = s.ann_args(line.a)
            kept = []
            for p in parts:
                if p[0].value == 'color':
                    exempt.append((p[0].a, p[-1].b))
                else:
                    kept.append(s.text[p[0].a:p[-1].b])
            patches.append((line.a, line.b, '(' + ','.join(kept) + ')'))
        elif visual:
            # Allow adding/removing Line graphics, but preserve any other
            # annotation on the same connect (e.g. tool-specific semantics).
            following = s.scan(x['end'])
            if not following or following[0].value != 'annotation':
                raise ValueError('Cannot resolve connection annotation owner')
            ann_start, group = following[0].a, following[1]
            parts = s.ann_args(group.a)
            kept = [s.text[p[0].a:p[-1].b] for p in parts if p[0].value != 'Line']
            for p in parts:
                if p[0].value == 'Line':
                    exempt.append((p[0].a, p[-1].b))
            patches.append((ann_start, group.b, 'annotation('+','.join(kept)+')' if kept else ''))
    normalized = apply(text, patches)
    # Reconstructed punctuation does not hide changes to comments outside the
    # explicitly exempt nodes. Ordinary comment content remains protected.
    protected_comments = [t for t, a, b in original
                          if t.startswith(('//', '/*'))
                          and not any(x <= a and b <= y for x, y in exempt)]
    code = [t for t, _, _ in lexical_tokens(normalized) if not t.startswith(('//', '/*'))]
    return hash_tokens(code + ['<PROTECTED_COMMENTS>'] + protected_comments)


def compare_trees(before: Path, after: Path, mode: str, allow: list[str] | None = None,
                  root_version: bool = False) -> dict:
    allow = [] if allow is None else allow
    if not isinstance(allow, list) or any(not isinstance(x, str) for x in allow):
        raise ValueError('Allowlist must be a JSON array of exact relative paths')
    if mode not in MODES:
        raise ValueError('Unknown mode')
    if root_version and mode == 'format-only':
        raise ValueError('FORMAT_ONLY cannot change versions')
    for name in allow:
        p = Path(name)
        if p.is_absolute() or '..' in p.parts or name.endswith('.mo') or any(c in name for c in '*?['):
            raise ValueError('Unsafe/non-exact auxiliary path: ' + name)
    if not before.is_dir() or not after.is_dir():
        raise ValueError('Both source roots must exist')
    if before.resolve() == after.resolve():
        raise ValueError('Baseline and candidate must be different directories')
    def collect(root):
        out = {}
        for p in root.rglob('*'):
            if p.is_symlink():
                raise ValueError('Symbolic links require separate review: ' + str(p))
            if p.is_file():
                out[p.relative_to(root).as_posix()] = p
        return out
    a, b = collect(before), collect(after)
    rows, errors = [], []
    for name in sorted(a.keys() | b.keys()):
        if name not in a or name not in b:
            rows.append({'file': name, 'status': 'AUX_FILE_REVIEW' if name in allow else 'PROTECTED_FILE_SET_CHANGE'})
            continue
        aa, bb = a[name].read_bytes(), b[name].read_bytes()
        if aa == bb:
            rows.append({'file': name, 'status': 'BYTE_IDENTICAL'})
            continue
        if not name.endswith('.mo'):
            rows.append({'file': name, 'status': 'AUX_FILE_REVIEW' if name in allow else 'PROTECTED_NONMODELICA_CHANGE'})
            continue
        try:
            ha = scoped_signature(aa.decode('utf-8-sig'), mode, root_version)
            hb = scoped_signature(bb.decode('utf-8-sig'), mode, root_version)
            rows.append({'file': name, 'status': 'WITHIN_SCOPE' if ha == hb else 'PROTECTED_TOKEN_CHANGE',
                         'protectedBefore': ha, 'protectedAfter': hb})
        except (ValueError, KeyError, IndexError, UnicodeError) as exc:
            errors.append({'file': name, 'status': 'UNSUPPORTED_REVIEW', 'reason': str(exc)})
    has_modelica = any(n.endswith('.mo') for n in a)
    bad = any(r['status'].startswith('PROTECTED_') for r in rows)
    status = 'STATIC_SCOPE_MATCH' if has_modelica and not bad and not errors else 'REVIEW_REQUIRED'
    return {'tool': 'MOSAIC scoped source protection', 'version': '0.9.0', 'mode': mode,
            'status': status, 'rootVersionExempt': root_version, 'allowlist': allow,
            'scope': 'Changed-file lexical comparison only; unchanged files are not reparsed. No compiler, simulation or GUI proof.',
            'auxiliaryFilesNeedReview': any(r['status'] == 'AUX_FILE_REVIEW' for r in rows),
            'files': rows, 'errors': errors}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('before', type=Path); p.add_argument('after', type=Path)
    p.add_argument('--mode', choices=sorted(MODES), required=True)
    p.add_argument('--allow-root-version', action='store_true')
    p.add_argument('--allowlist', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    try:
        allow = json.loads(a.allowlist.read_text(encoding='utf-8')) if a.allowlist else []
        result = compare_trees(a.before, a.after, a.mode, allow, a.allow_root_version)
    except (ValueError, OSError) as exc:
        p.error(str(exc))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return 0 if result['status'] == 'STATIC_SCOPE_MATCH' else 2

if __name__ == '__main__':
    sys.exit(main())
