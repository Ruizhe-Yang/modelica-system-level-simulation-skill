#!/usr/bin/env python3
"""Validate minimal MOSAIC result contract structure. Not physical verification."""
import argparse,json,math,sys
from pathlib import Path

def validate(c):
    errors=[];signals=c.get('signals',[]);ids=set();paths=set()
    if not c.get('entryModel'):errors.append('entryModel required')
    if not signals:errors.append('signals must be nonempty')
    for i,s in enumerate(signals):
        for k in ['id','path','description','unit','identity','timeSemantics','required']:
            if k not in s or s[k] is None or s[k]=='':errors.append(f'signals[{i}].{k} required')
        if not isinstance(s.get('required'),bool):errors.append(f'signals[{i}].required must be Boolean')
        for k,seen in [('id',ids),('path',paths)]:
            v=s.get(k)
            if v in seen:errors.append(f'duplicate {k}: {v}')
            if v is not None:seen.add(v)
        if s.get('identity') not in ('command','measurement','estimate','state','truth','diagnostic','configuration'):errors.append(f'signals[{i}].identity unknown')
    return {'status':'SCHEMA_OK' if not errors else 'INVALID','scope':'Required metadata and key uniqueness only; actual units, producers, paths and signals need model/result evidence.','errors':errors}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('contract',type=Path);a=p.parse_args()
    try:r=validate(json.loads(a.contract.read_text(encoding='utf8')))
    except Exception as e:p.error(str(e))
    print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if not r['errors'] else 2
if __name__=='__main__':sys.exit(main())
