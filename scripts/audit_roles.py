#!/usr/bin/env python3
"""Read-only checks of explicitly assigned MOSAIC roles.
Conservative lexical findings; not a Modelica compiler/flattening proof. Static
connection templates, redeclare effects and unsupported MSL bodies remain review
items. Never infer full conformance from the absence of local findings.
"""
from pathlib import Path
import argparse,json,re,sys
from modelica_support import Source
from connection_colors import Index,msl_kind,msl_member
WHITE={'TB','SB','AB'};ROLES=WHITE|{'BU','LU'}
BUILTINS={'Real','Boolean','Integer','String'}

def review(root:Path,role_map:dict)->dict:
 ix=Index(root);rows=[]
 roles=role_map.get('roles',role_map)
 if not isinstance(roles,dict) or not roles:raise ValueError('A nonempty class-to-role map is required')
 for name,role in roles.items():
  if role not in ROLES:raise ValueError('Unknown role '+str(role))
  findings=[];pending=[];instances=[];visited=set()
  if name not in ix.classes:
   rows.append({'class':name,'role':role,'status':'REVIEW_REQUIRED','findings':[],'pending':['CLASS_NOT_FOUND']});continue
  def walk(c):
   if c.full in visited:return
   visited.add(c.full);s=ix.sources[ix.class_files[c.full]]
   if role in WHITE:
    nested=[(cc.a,cc.b) for cc in c.children]
    for t in s.scan(c.a,c.b):
     if t.kind!='string' and not any(a<=t.a<b for a,b in nested) and t.value in ('algorithm','initial'):
      findings.append({'owner':c.full,'check':'WHITEBOX_ALGORITHM_OR_INITIAL_SECTION','token':t.value})
    for phase,a,b in c.statements:
     ts=s.scan(a,b)
     if phase!='equation':continue # section presence was handled above
     if not ts:continue
     v=ts[0].value
     if v=='connect':continue
     if v in ('for','if','end','else','elseif'):
      pending.append('STATIC_CONNECT_TEMPLATE_REQUIRES_EXPANSION: '+c.full);continue
     findings.append({'owner':c.full,'check':'WHITEBOX_BEHAVIOR_EQUATION','source':s.text[a:b][:240]})
   for d in c.decls:
    if any(p in d.prefix for p in ('parameter','constant')):continue
    ty=ix.resolve(d.type,c.full);cc=ix.classes.get(ty)
    connector=bool(msl_kind(ty or '') or cc and cc.kind=='connector')
    runtime=bool(cc and cc.kind in ('model','block') or ty and ty.startswith('Modelica.') and not connector and not ty.startswith(('Modelica.Units.','Modelica.Blocks.Types.','Modelica.Icons.')))
    if 'outer' in d.prefix:continue
    if runtime:instances.append({'owner':c.full,'instance':d.name,'type':ty,'childRole':roles.get(ty,'UNASSIGNED')})
    if role=='BU' and runtime:findings.append({'owner':c.full,'check':'BU_RUNTIME_CHILD','instance':d.name,'type':ty})
    if role in WHITE:
     if not runtime and not connector and (ty in BUILTINS or ty and ty.startswith('Modelica.Units.') or cc and cc.kind=='record'):
      findings.append({'owner':c.full,'check':'WHITEBOX_RUNTIME_DECLARATION','field':d.name})
     if d.binding and not runtime:findings.append({'owner':c.full,'check':'WHITEBOX_RUNTIME_BINDING','field':d.name,'binding':d.binding[:180]})
     if runtime and d.modifier:
      # Check known public signal inputs. Other modifier parameter kinds require
      # the real compiler/library declaration, not guessing from their names.
      for m in re.finditer(r'\b([A-Za-z_]\w*)\s*=(?!=)',d.modifier):
       member=m[1];mt=msl_member(ty,member) if ty.startswith('Modelica.') else None
       md=next((z for z in cc.decls if z.name==member),None) if cc else None
       if (mt and mt.endswith('Input')) or (md and ('input' in md.prefix or md.type.endswith('Input'))):
        findings.append({'owner':c.full,'check':'WHITEBOX_CHILD_INPUT_BINDING','instance':d.name,'input':member})
   for e in c.extends:
    ty=ix.resolve(e,c.full)
    if ty in ix.classes:walk(ix.classes[ty])
    elif ty and ty.startswith('Modelica.Icons.'):pass
    else:pending.append('BASE_NOT_FLATTENED: '+str(ty or e))
   if any(t.value=='redeclare' for t in s.scan(c.a,c.b)):
    pending.append('REDECLARE_REQUIRES_COMPILER_REVIEW: '+c.full)
  walk(ix.classes[name])
  if role=='TB' and role_map.get('entryModel') and name!=role_map['entryModel']:
   pending.append('SECOND_EXPERIMENT_ENTRY_REVIEW')
  if role in WHITE:
   for x in instances:
    cr=x['childRole']
    if cr=='TB':findings.append({'check':'EXPERIMENT_AS_FUNCTIONAL_CHILD','instance':x['instance']})
    if role=='AB' and cr in ('SB','AB'):findings.append({'check':'AB_NOT_TERMINAL_ASSEMBLY','instance':x['instance']})
   if role=='AB' and len(instances)<2:findings.append({'check':'AB_FEWER_THAN_TWO_FUNCTIONAL_CHILDREN'})
  if role=='LU':
   c=ix.classes[name]
   if c.statements:findings.append({'check':'LU_ADDED_BEHAVIOR','owner':name})
   if not any((ix.resolve(e,c.full) or '').startswith('Modelica.') for e in c.extends):pending.append('LU_ORIGIN_REQUIRES_REVIEW')
  rows.append({'class':name,'role':role,'status':'FINDINGS' if findings else 'REVIEW_REQUIRED' if pending else 'NO_LOCAL_FINDING','effectiveProjectClasses':sorted(visited),'instances':instances,'findings':findings,'pending':sorted(set(pending))})
 return {'scope':'Explicit-map lexical review; no full inheritance flattening, equation balance, simulation or full conformance claim','version':'0.8.0','status':'FINDINGS' if any(r['findings'] for r in rows) else 'REVIEW_REQUIRED' if any(r['pending'] for r in rows) else 'NO_LOCAL_FINDING','mappedClassCount':len(rows),'unmappedModelBlocks':sorted(n for n,c in ix.classes.items() if c.kind in ('model','block') and n not in roles),'classes':rows}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('--roles',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 try:r=review(a.root,json.loads(a.roles.read_text(encoding='utf8')))
 except (ValueError,OSError) as e:p.error(str(e))
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');return 2 if r['status']!='NO_LOCAL_FINDING' else 0
if __name__=='__main__':sys.exit(main())
