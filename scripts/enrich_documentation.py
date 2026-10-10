#!/usr/bin/env python3
"""Write metadata-only candidate files from a reviewed per-class catalog.
Output must be separate from source. Does not overwrite an existing destination.
No project/physics assumptions are invented. Unknown classes remain unchanged.
"""
from pathlib import Path
import argparse,json,shutil,sys
from modelica_support import Source
from documentation_support import enrich_generated

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('candidate',type=Path);p.add_argument('--catalog',required=True,type=Path);a=p.parse_args()
    src=a.source.resolve();out=a.candidate.resolve()
    if not src.is_dir() or out.exists() or src in out.parents:p.error('Use an existing source and a NEW separate candidate outside its tree')
    cat=json.loads(a.catalog.read_text(encoding='utf8'));pending=[]
    for f in src.rglob('*.mo'):
        if f.is_symlink():p.error('Symlink source requires manual review')
        old=f.read_text(encoding='utf-8-sig');new=enrich_generated(old,str(f),cat);sa,sb=Source(old),Source(new)
        if sa.unparsed or sb.unparsed or sa.canonical(False)!=sb.canonical(False):p.error('Protected or unsupported change: '+str(f))
        pending.append((f.relative_to(src),new))
    shutil.copytree(src,out,symlinks=True)
    for rel,new in pending:(out/rel).write_text(new,encoding='utf8')
    print(json.dumps({'status':'CANDIDATE_WRITTEN','files':len(pending),'candidate':str(out),'compiler':'NOT_RUN'},ensure_ascii=False))
if __name__=='__main__':main()
