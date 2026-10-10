#!/usr/bin/env python3
"""Create a separate candidate with only requested Documentation sections removed."""
from pathlib import Path
import argparse,sys,json,shutil
from modelica_support import Source,apply
from auxiliary_metadata import clean_documentation_html

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('candidate',type=Path);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
 src=a.source.resolve();dst=a.candidate.resolve()
 if not src.is_dir() or dst.exists() or src in dst.parents or dst in src.parents:p.error('Source must exist; candidate must be new, separate and not nested')
 if any(f.is_symlink() for f in src.rglob('*')):p.error('Symlinks require review; none followed')
 rows=[];edits={}
 try:
  for f in sorted(src.rglob('*.mo')):
   text=f.read_text(encoding='utf-8-sig');s=Source(text)
   if s.unparsed:raise ValueError('Unsupported source: '+str(f))
   patches=[]
   for c in s.all_classes():
    old=s.doc_info(c);new,counts=clean_documentation_html(old)
    if old!=new:patches.append(s.doc_patch(c,new))
    rows.append({'class':c.full,'file':f.relative_to(src).as_posix(),'removed':counts})
   out=apply(text,patches)
   if Source(out).canonical(False)!=s.canonical(False):raise ValueError('Protected tokens changed')
   if out!=text:edits[f.relative_to(src)]=out
  if not rows:raise ValueError('No parsed classes; no candidate created')
  shutil.copytree(src,dst,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  for path,text in edits.items():(dst/path).write_text(text,encoding='utf8')
  a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps({'scope':'Documentation-only lexical check; not compilation','changed_files':len(edits),'classes':rows},ensure_ascii=False,indent=2),encoding='utf8')
  return 0
 except (ValueError,OSError) as e:p.error(str(e))
if __name__=='__main__':sys.exit(main())
