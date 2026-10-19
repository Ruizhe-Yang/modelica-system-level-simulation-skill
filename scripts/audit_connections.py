#!/usr/bin/env python3
"""Read-only source-level connection/visibility preflight for MOSAIC v0.9.

Finds local missing/hidden/zero-length Lines, malformed literals, canvas clipping
candidates and local connector Placement issues. Enumerates source connect calls,
not just existing annotations. It does NOT flatten templates, resolve all instance
transformations, prove causality, or certify a native Modelica GUI.
"""
from __future__ import annotations
import argparse
import ast
import collections
import json
import math
import sys
from pathlib import Path
from modelica_support import Source
from connection_colors import Index, all_connections, msl_kind


def attributes(src: Source, group: int) -> dict[str,str]:
    out={}
    for p in src.ann_args(group):
        if len(p)>=3 and p[1].value=='=':
            if p[0].value in out: raise ValueError('Duplicate graphical property '+p[0].value)
            out[p[0].value]=src.text[p[2].a:p[-1].b]
    return out


def number(raw: str | None) -> float | None:
    if raw is None: return None
    try:
        value=float(raw)
        return value if math.isfinite(value) else None
    except ValueError:return None


def matrix(raw: str | None) -> list | None:
    if raw is None:return None
    try: v=ast.literal_eval(raw.replace('{','[').replace('}',']'))
    except (ValueError,SyntaxError,TypeError):return None
    if not isinstance(v,list):return None
    if not all(isinstance(row,list) and len(row)==2 and all(type(x) in (int,float) and math.isfinite(x) for x in row) for row in v):return None
    return v


def diagram_extent(src: Source,c) -> list | None:
    for an in c.anns:
        for p in src.ann_args(an[2]):
            if p[0].value=='Diagram' and len(p)>1:
                for q in src.ann_args(p[1].a):
                    if q[0].value=='coordinateSystem' and len(q)>1:
                        ex=matrix(attributes(src,q[1].a).get('extent'))
                        if ex and len(ex)==2:return ex
    # Missing/inherited canvas is intentionally not guessed.
    return None


def review(root:Path) -> dict:
    if not root.is_dir():raise ValueError('Project directory does not exist')
    if any(p.is_symlink() for p in root.rglob('*')):raise ValueError('Symbolic links require separate review')
    ix=Index(root);rows=[];ports=[];pending=[]
    if not ix.sources:raise ValueError('No Modelica source files found')
    for f,s in ix.sources.items():
        for x in all_connections(s):
            c=x['class'];line=x['line'];issues=[];local_pending=[]
            rec={'file':f.relative_to(root).as_posix(),'class':c.full,
                 'line':s.text.count('\n',0,x['start'])+1,'endpoints':x['endpoints']}
            if line is None:issues.append('MISSING_LINE')
            else:
                a=attributes(s,line.a)
                visible=a.get('visible','true').strip()
                if visible=='false':issues.append('HIDDEN_CONNECTION')
                elif visible!='true':local_pending.append('DYNAMIC_VISIBILITY')
                width=number(a.get('thickness','0.25'))
                if width is None:local_pending.append('NONLITERAL_THICKNESS')
                elif width<=0:issues.append('NONPOSITIVE_LINE_WIDTH')
                if a.get('pattern','').strip()=='LinePattern.None':issues.append('INVISIBLE_LINE_PATTERN')
                pts=matrix(a.get('points'))
                if pts is None:local_pending.append('MISSING_OR_NONLITERAL_POINTS')
                elif len(pts)<2:issues.append('TOO_FEW_POINTS')
                else:
                    if all(p==pts[0] for p in pts):issues.append('ZERO_LENGTH_CONNECTION')
                    extent=diagram_extent(s,c)
                    if extent:
                        xmin,xmax=sorted((extent[0][0],extent[1][0]));ymin,ymax=sorted((extent[0][1],extent[1][1]))
                        # Coordinates with graphical transforms need composition.
                        if 'origin' in a or 'rotation' in a:
                            local_pending.append('LINE_TRANSFORM_REQUIRES_COMPOSITION')
                        elif all(p[0]<xmin for p in pts) or all(p[0]>xmax for p in pts) or all(p[1]<ymin for p in pts) or all(p[1]>ymax for p in pts):
                            issues.append('WHOLE_LINE_OUTSIDE_DECLARED_CANVAS')
                        elif any(not (xmin<=p[0]<=xmax and ymin<=p[1]<=ymax) for p in pts):
                            local_pending.append('PARTIAL_CANVAS_CLIPPING_REVIEW')
                    else:local_pending.append('CANVAS_EXTENT_NOT_RESOLVED')
            rec['endpointResolution']=[ix.endpoint(c.full,e) for e in x['endpoints']]
            if any(not e.get('resolved') for e in rec['endpointResolution']):local_pending.append('ENDPOINT_TYPE_UNRESOLVED')
            if any('[' in e for e in x['endpoints']):local_pending.append('ARRAY_OR_TEMPLATE_REQUIRES_EXPANSION')
            rec.update(findings=issues,pending=sorted(set(local_pending)),endpointGeometry='NOT_CHECKED',causality='NOT_CHECKED',nativeGUI='NOT_CHECKED')
            rows.append(rec)
        for c in s.all_classes():
            if c.extends:pending.append({'class':c.full,'reason':'INHERITED_VISIBILITY_REQUIRES_EFFECTIVE_VIEW'})
            if any(t.value in ('redeclare','for','if') for t in s.scan(c.a,c.b)):
                pending.append({'class':c.full,'reason':'REDECLARE_OR_STATIC_STRUCTURE_REVIEW'})
            for d in c.decls:
                typ=ix.resolve(d.type,c.full);dc=ix.classes.get(typ)
                connector=(dc is not None and dc.kind=='connector') or bool(typ and msl_kind(typ))
                if not connector:continue
                issues=[];pp=[];placement=None
                ts=s.scan(d.a,d.b)
                for i,t in enumerate(ts[:-1]):
                    if t.value=='annotation' and ts[i+1].value=='(':
                        for a in s.ann_args(ts[i+1].a):
                            if a[0].value=='Placement' and len(a)>1:placement=a[1]
                if placement is None:pp.append('NO_LOCAL_PLACEMENT_OR_INHERITED_VIEW')
                else:
                    a=attributes(s,placement.a)
                    if a.get('visible','true').strip()=='false':issues.append('HIDDEN_LOCAL_CONNECTOR')
                    for t in s.ann_args(placement.a):
                        if t[0].value in ('transformation','iconTransformation') and len(t)>1:
                            ex=matrix(attributes(s,t[1].a).get('extent'))
                            if ex and len(ex)==2:
                                if ex[0][0]==ex[1][0] or ex[0][1]==ex[1][1]:issues.append('ZERO_SIZE_'+t[0].value.upper())
                            else:pp.append('NONLITERAL_OR_MISSING_PLACEMENT_EXTENT')
                ports.append({'class':c.full,'port':d.name,'visibility':d.visibility,'findings':issues,'pending':pp})
    counts=collections.Counter((r['class'],tuple(sorted(''.join(x.split()) for x in r['endpoints']))) for r in rows)
    duplicates=[{'class':c,'endpoints':list(ep),'sourceOccurrences':n,'status':'REVIEW_REQUIRED'} for (c,ep),n in counts.items() if n>1]
    # Duplicate source statements may belong to exclusive static branches.
    findings=sum(len(r['findings']) for r in rows+ports)
    return {'version':'0.9.0','status':'FINDINGS' if findings else 'REVIEW_REQUIRED' if pending or duplicates or any(r['pending'] for r in rows+ports) else 'NO_LOCAL_FINDING',
            'scope':'Source preflight only; NO_LOCAL_FINDING is not conformance PASS. Inheritance/template expansion, complete geometry, causality and native GUI remain unverified.',
            'sourceConnectCount':len(rows),'literalFindingCount':findings,'connections':rows,'localConnectors':ports,
            'duplicateCandidates':duplicates,'pending':pending,'modelicaCompilation':'NOT_RUN','modelicaSimulation':'NOT_RUN','nativeGUI':'NOT_CHECKED'}


def main()->int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    try:r=review(a.root)
    except (ValueError,OSError,KeyError,IndexError) as e:
        r={'version':'0.9.0','status':'REVIEW_REQUIRED','errors':[str(e)],'scope':'Source preflight not completed; no pass claim'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return 0 if r['status']=='NO_LOCAL_FINDING' else 2
if __name__=='__main__':sys.exit(main())
