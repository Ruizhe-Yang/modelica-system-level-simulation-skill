#!/usr/bin/env python3
"""Read-only Modelica inventory. Does not certify physical or compiler correctness."""
from pathlib import Path
import argparse,json,sys
from modelica_support import Source

def audit(root:Path)->dict:
    if not root.is_dir():raise ValueError('Project directory does not exist')
    rows=[];errors=[];files=sorted(root.rglob('*.mo'))
    for p in files:
        if p.is_symlink():errors.append({'file':str(p),'error':'SYMLINK_NOT_READ'});continue
        try:
            s=Source(p.read_text(encoding='utf-8-sig'))
            if s.unparsed:errors.append({'file':str(p.relative_to(root)),'error':'UNSUPPORTED_SYNTAX','details':s.unparsed})
            for c in s.all_classes():
                rows.append({'file':str(p.relative_to(root)),'class':c.full,'kind':c.kind,'description':c.description,'documentation':bool(s.doc_info(c)),'directDeclarations':len(c.decls),'missingComments':[d.name for d in c.decls if not d.description],'extends':c.extends,'declaredDerivatives':[s.text[a:b][:200] for ph,a,b in c.statements if 'der(' in s.text[a:b]][:10]})
        except Exception as exc:errors.append({'file':str(p.relative_to(root)),'error':str(exc)})
    names=[r['class'] for r in rows]
    duplicates=sorted({x for x in names if names.count(x)>1})
    return {'tool':'MOSAIC source inventory','version':'0.9.0','scope':'Lexical evidence only. No flattening, inheritance expansion, simulation or physical certification.','status':'PARSED' if not errors and not duplicates and files else 'UNKNOWN','fileCount':len(files),'classCount':len(rows),'modelBlockCount':sum(r['kind'] in ('model','block') for r in rows),'documentationCount':sum(r['documentation'] for r in rows),'missingCommentCount':sum(len(r['missingComments']) for r in rows),'classes':rows,'duplicates':duplicates,'errors':errors}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    try:r=audit(a.root.resolve())
    except Exception as e:p.error(str(e))
    text=json.dumps(r,ensure_ascii=False,indent=2)
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text,encoding='utf8')
    else:print(text)
    return 0 if r['status']=='PARSED' else 2
if __name__=='__main__':sys.exit(main())
