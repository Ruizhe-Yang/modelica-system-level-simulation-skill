"""Read-only connector-type resolution plus narrowly scoped Line.color edits.
Not a compiler: unsupported source/type resolution is reported, never guessed.
"""
from pathlib import Path
import sys,re,json,collections,hashlib
try:
 from .modelica_support import Source,LEX,apply
except ImportError:
 from modelica_support import Source,LEX,apply

MSL_PREFIX='Modelica.'
BI='Modelica.Blocks.Interfaces.'
HEAT='Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a'
PIN='Modelica.Electrical.Analog.Interfaces.Pin'
FRAME='Modelica.Mechanics.MultiBody.Interfaces.Frame_a'
ROT='Modelica.Mechanics.Rotational.Interfaces.Flange_a'
TRANS='Modelica.Mechanics.Translational.Interfaces.Flange_a'
FLUID='Modelica.Fluid.Interfaces.FluidPort_a'
MSL_COLORS={
 'REAL':(0,0,127),'BOOLEAN':(255,0,255),'INTEGER':(255,127,0),
 'ANALOG':(0,0,255),'HEAT':(191,0,0),'ROTATIONAL':(0,0,0),
 'TRANSLATIONAL':(0,127,0),'MULTIBODY':(95,95,95),'FLUID':(0,127,255),
}
MSL_SOURCE_BASE='https://github.com/modelica/ModelicaStandardLibrary/blob/v4.0.0/'
MSL_REFS={
 'REAL':'Modelica/Blocks/Interfaces.mo','BOOLEAN':'Modelica/Blocks/Interfaces.mo','INTEGER':'Modelica/Blocks/Interfaces.mo',
 'ANALOG':'Modelica/Electrical/Analog/Interfaces/PositivePin.mo',
 'HEAT':'Modelica/Thermal/HeatTransfer/Interfaces/HeatPort_a.mo',
 'ROTATIONAL':'Modelica/Mechanics/Rotational/Interfaces/Flange_a.mo',
 'TRANSLATIONAL':'Modelica/Mechanics/Translational/Interfaces/Flange_a.mo',
 'MULTIBODY':'Modelica/Mechanics/MultiBody/Interfaces/Frame_a.mo','FLUID':'Modelica/Fluid/Interfaces.mo'}

def base_name(e):
 e=re.sub(r'^(?:(?:input|output|flow|stream|extends)\s+)+','',e.strip())
 m=re.match(r'[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*',e)
 return m[0] if m else ''

def msl_kind(t):
 if t.startswith(BI):
  short=t[len(BI):]
  if short in ('RealInput','RealOutput','RealVectorInput'):return 'REAL'
  if short in ('BooleanInput','BooleanOutput','BooleanVectorInput'):return 'BOOLEAN'
  if short in ('IntegerInput','IntegerOutput'):return 'INTEGER'
 if t.startswith('Modelica.Electrical.Analog.Interfaces.') and t.rsplit('.',1)[-1] in ('Pin','PositivePin','NegativePin'):return 'ANALOG'
 if t.startswith('Modelica.Thermal.HeatTransfer.Interfaces.') and t.rsplit('.',1)[-1] in ('HeatPort','HeatPort_a','HeatPort_b'):return 'HEAT'
 if t.startswith('Modelica.Mechanics.Rotational.Interfaces.') and t.rsplit('.',1)[-1] in ('Flange','Flange_a','Flange_b','Support'):return 'ROTATIONAL'
 if t.startswith('Modelica.Mechanics.Translational.Interfaces.') and t.rsplit('.',1)[-1] in ('Flange','Flange_a','Flange_b','Support'):return 'TRANSLATIONAL'
 if t.startswith('Modelica.Mechanics.MultiBody.Interfaces.') and t.rsplit('.',1)[-1] in ('Frame','Frame_a','Frame_b','Frame_resolve'):return 'MULTIBODY'
 if t.startswith('Modelica.Fluid.Interfaces.') and t.rsplit('.',1)[-1] in ('FluidPort','FluidPort_a','FluidPort_b','FluidPorts_a','FluidPorts_b'):return 'FLUID'
 return None

# Limited endpoint signature registry, for the actually used MSL 4.0.0 families.
# Unknown members are NOT assigned a color. The opposite endpoint cannot silently
# turn an unresolved endpoint into a resolved one.
REAL_BLOCKS={
 'Continuous.FirstOrder','Continuous.Integrator','Continuous.LimIntegrator','Continuous.LimPID',
 'Discrete.ZeroOrderHold','Math.Abs','Math.Add','Math.Add3','Math.Atan2','Math.Division','Math.Feedback','Math.Gain','Math.Max','Math.Min','Math.Product','Math.Sqrt',
 'Nonlinear.Limiter','Nonlinear.VariableLimiter','Nonlinear.SlewRateLimiter',
 'Sources.Constant','Sources.Ramp','Sources.Step','Sources.Sine','Sources.CombiTimeTable','Tables.CombiTable1Ds','Tables.CombiTable1D','Tables.CombiTable2Ds'}
BOOLEAN_BLOCKS={'Logical.And','Logical.Not','Logical.Or','Logical.Timer','Logical.Hysteresis','Logical.OnOffController','Logical.GreaterEqualThreshold','Logical.GreaterThreshold','Logical.LessEqualThreshold','Logical.Switch','Sources.BooleanConstant'}

def msl_member(t,n):
 if t.startswith('Modelica.Blocks.'):
  q=t[len('Modelica.Blocks.'):]
  if q in REAL_BLOCKS and n in ('u','u1','u2','u3','y','u_s','u_m','limit1','limit2'):return BI+('RealOutput' if n=='y' else 'RealInput')
  if q in BOOLEAN_BLOCKS:
   if n=='y':return BI+('RealOutput' if q in ('Logical.Timer','Logical.Switch') else 'BooleanOutput')
   if n in ('u','u1','u2','u3','reference'):
    real=(q in ('Logical.Hysteresis','Logical.OnOffController','Logical.GreaterEqualThreshold','Logical.GreaterThreshold','Logical.LessEqualThreshold')) or (q=='Logical.Switch' and n in ('u1','u3'))
    return BI+('RealInput' if real else 'BooleanInput')
  if q in ('Math.BooleanToInteger','Math.BooleanToReal','Math.IntegerToReal'):
   a,b={'Math.BooleanToInteger':('Boolean','Integer'),'Math.BooleanToReal':('Boolean','Real'),'Math.IntegerToReal':('Integer','Real')}[q]
   if n=='u':return BI+a+'Input'
   if n=='y':return BI+b+'Output'
  if q=='Sources.IntegerConstant' and n=='y':return BI+'IntegerOutput'
 if t.startswith('Modelica.Electrical.Analog.'):
  if n in ('p','n','p1','p2','n1','n2'):return PIN
  if n=='heatPort':return HEAT
  if t.endswith('.IdealClosingSwitch') and n=='control':return BI+'BooleanInput'
  if n in ('i','v','G') and any(t.endswith('.'+x) for x in ('SignalCurrent','SignalVoltage','VariableConductor')):return BI+'RealInput'
  if n in ('i','v') and '.Sensors.' in t:return BI+'RealOutput'
 if t.startswith('Modelica.Thermal.HeatTransfer.'):
  if n in ('port','port_a','port_b','solid','fluid'):return HEAT
  if n in ('T','Q_flow') and '.Sensors.' in t:return BI+'RealOutput'
  if n in ('T','Q_flow','Gc') and ('.Sources.' in t or t.endswith('.Convection')):return BI+'RealInput'
 if t.startswith('Modelica.Mechanics.Rotational.'):
  if n in ('flange','flange_a','flange_b','support'):return ROT
  if n=='heatPort':return HEAT
  if '.Sources.' in t and n in ('tau','w','phi','a'):return BI+'RealInput'
  if '.Sensors.' in t and n in ('w','phi','a','tau','power'):return BI+'RealOutput'
 if t.startswith('Modelica.Mechanics.Translational.'):
  if n in ('flange','flange_a','flange_b','support'):return TRANS
  if n=='heatPort':return HEAT
  if '.Sources.' in t and n in ('f','v','s','a'):return BI+'RealInput'
  if '.Sensors.' in t and n in ('v','s','a','f','power'):return BI+'RealOutput'
 if t.startswith('Modelica.Mechanics.MultiBody.'):
  if n in ('frame_a','frame_b','frame_resolve'):return FRAME
  if t.endswith('.Mounting1D') and n=='flange_b':return ROT
  if t.endswith('.WorldTorque') and n=='torque':return BI+'RealInput'
  if '.Sensors.' in t and n in ('angles','w','w_abs','a_abs','r','r_abs','v','v_abs','a','angles','z','f','t','a_0'):return BI+'RealOutput'
 if t.startswith('Modelica.Fluid.'):
  if n in ('port','port_a','port_b','ports'):return FLUID
  if '.Sensors.' in t and n in ('m_flow','p','T','h_out','V_flow'):return BI+'RealOutput'
 return None

def all_connections(src):
 toks=[m for m in LEX.finditer(src.text) if not(m[0].isspace() or m[0].startswith('//') or m[0].startswith('/*'))]
 positions={m.start():i for i,m in enumerate(toks)}
 cs=list(src.all_classes())
 for i,m in enumerate(toks):
  if m[0]!='connect' or i+1>=len(toks) or toks[i+1][0]!='(':continue
  a=toks[i+1].start();end=src.pairs[a];args=src.ann_args(a)
  if len(args)!=2:raise ValueError('connect must have two endpoints')
  endpoints=[src.text[p[0].a:p[-1].b] for p in args]
  owner=min((c for c in cs if c.a<=m.start()<c.b),key=lambda c:c.b-c.a)
  j=positions.get(end,None)
  # whitespace/comment may follow close parenthesis.
  if j is None:
   j=i+2
   while j<len(toks) and toks[j].start()<end:j+=1
  line=None;color=None
  if j<len(toks) and toks[j][0]=='annotation' and toks[j+1][0]=='(':
   for arg in src.ann_args(toks[j+1].start()):
    if arg[0].value=='Line':
     if line:raise ValueError('duplicate connection Line')
     line=arg[1]
     for lp in src.ann_args(line.a):
      if lp[0].value=='color':
       color=(lp[2].a,lp[-1].b,src.text[lp[2].a:lp[-1].b])
  yield {'class':owner,'start':m.start(),'end':end,'endpoints':endpoints,'line':line,'color':color}

class Index:
 def __init__(self,root, reviewed_palette=None, require_reviewed_palette=False):
  self.root=Path(root);self.sources={};self.classes={};self.class_files={};self.custom_colors={};self.cat={}
  cp=self.root/'Scripts/DocumentationSupport/catalog.json'
  if cp.exists():self.cat=json.loads(cp.read_text())
  for f in sorted(self.root.rglob('*.mo')):
   s=Source(f.read_text(encoding='utf-8-sig'))
   if s.unparsed:raise ValueError(str(f)+' unsupported '+repr(s.unparsed[:2]))
   self.sources[f]=s
   for c in s.all_classes():
    if c.full in self.classes:raise ValueError('duplicate '+c.full)
    self.classes[c.full]=c;self.class_files[c.full]=f
  for c in self.classes.values():
   if c.kind=='connector':
    s=self.sources[self.class_files[c.full]]
    for a in c.anns:
     for arg in s.ann_args(a[2]):
      if arg[0].value=='Icon':
       raw=s.text[arg[0].a:arg[-1].b]
       colors=collections.Counter(tuple(int(n.strip()) for n in m.split(',')) for m in re.findall(r'\b(?:lineColor|fillColor|color)\s*=\s*\{(\d+\s*,\s*\d+\s*,\s*\d+)\}',raw))
       sat=[(v,k) for k,v in colors.items() if max(k)-min(k)>30 and min(k)<200]
       if sat:self.custom_colors[c.full]=max(sat,key=lambda p:(p[0],max(p[1])-min(p[1])))[1]
       elif colors:self.custom_colors[c.full]=(0,0,0)
  self.inferred_custom_colors=dict(self.custom_colors)
  self.reviewed_custom_colors={}
  if reviewed_palette is not None:
   if not isinstance(reviewed_palette,dict) or reviewed_palette.get('reviewed') is not True:
    raise ValueError('Custom palette must be explicitly reviewed')
   if reviewed_palette.get('mslVersion')!='4.0.0':raise ValueError('Palette registry is fixed to MSL 4.0.0')
   colors=reviewed_palette.get('customColors')
   if not isinstance(colors,dict):raise ValueError('customColors must be a dictionary')
   for name,color in colors.items():
    if name not in self.classes or self.classes[name].kind!='connector':raise ValueError('Unknown custom connector '+name)
    if any(msl_kind(a) for a in self.ancestry(name)):raise ValueError('MSL-derived color cannot be overridden: '+name)
    if not isinstance(color,list) or len(color)!=3 or any(type(v)!=int or not 0<=v<=255 for v in color):raise ValueError('Invalid palette RGB')
    self.reviewed_custom_colors[name]=tuple(color)
  if require_reviewed_palette:self.custom_colors=dict(self.reviewed_custom_colors)
  elif self.reviewed_custom_colors:self.custom_colors.update(self.reviewed_custom_colors)
 def resolve(self,t,context):
  t=base_name(t)
  if t.startswith('Modelica.') or t in ('Real','Integer','Boolean','String','enumeration'):return t
  if t in self.classes:return t
  c=self.classes.get(context)
  # import aliases at each lexical enclosing scope
  scope=context
  while scope:
   cc=self.classes.get(scope)
   if cc:
    for imp in cc.imports:
     p=imp.split('=',1)
     if len(p)==2:
      a,b=(x.strip() for x in p)
      if t==a or t.startswith(a+'.'):return b+t[len(a):]
     elif imp.endswith('.*') and (imp[:-2]+'.'+t) in self.classes:return imp[:-2]+'.'+t
     elif t.split('.')[0]==imp.rsplit('.',1)[-1]:return imp+t[len(t.split('.')[0]):]
   if scope+'.'+t in self.classes:return scope+'.'+t
   scope=scope.rsplit('.',1)[0] if '.' in scope else ''
  return None
 def member(self,context,n,seen=None):
  if context.startswith('Modelica.'):
   t=msl_member(context,n)
   return (t,'MSL_SIGNATURE') if t else (None,'unknown MSL member '+context+'.'+n)
  c=self.classes.get(context)
  if not c:return None,'unknown class '+str(context)
  seen=set() if seen is None else seen
  if context in seen:return None,'inheritance cycle'
  seen.add(context)
  for d in c.decls:
   if d.name==n:
    t=self.resolve(d.type,c.full)
    ct=self.cat.get('classes',{}).get(c.full,{}).get('resolved_types',{}).get(n)
    if not t and ct and (ct in self.classes or ct.startswith('Modelica.') or ct in ('Real','Boolean','Integer','String')):t=ct
    return t, 'DECLARATION'
  for e in c.extends:
   b=self.resolve(e,c.full)
   if b:
    out=self.member(b,n,seen.copy())
    if out[0]:return out
  return None,'missing member '+context+'.'+n
 def ancestry(self,t,seen=None):
  seen=set() if seen is None else seen
  if not t or t in seen:return []
  seen.add(t);a=[t]
  c=self.classes.get(t)
  if c:
   for e in c.extends:
    b=self.resolve(e,c.full)
    if b:a+=self.ancestry(b,seen)
  return a
 def endpoint(self,context,path):
  # Only component references supported; array subscripts do not change class.
  clean=re.sub(r'\[[^\[\]]*\]','',path);parts=[x.strip() for x in clean.split('.')]
  t=context;trace=[];nearest=None
  for n in parts:
   if t in self.classes and self.classes[t].kind=='connector':nearest=t
   nt,source=self.member(t,n)
   trace.append({'owner':t,'member':n,'type':nt,'resolution':source})
   if not nt:return {'resolved':False,'path':path,'trace':trace}
   t=nt
  ancestors=self.ancestry(t)
  for a in ancestors:
   kind=msl_kind(a)
   if kind:return {'resolved':True,'path':path,'type':t,'basis':a,'family':kind,'color':MSL_COLORS[kind],'trace':trace,'standard':True}
  if t in self.custom_colors:return {'resolved':True,'path':path,'type':t,'basis':t,'family':'CUSTOM','color':self.custom_colors[t],'trace':trace,'standard':False}
  if nearest in self.custom_colors and t in ('Real','Integer','Boolean','String'):
   return {'resolved':True,'path':path,'type':t,'basis':nearest,'family':'CUSTOM_MEMBER','color':self.custom_colors[nearest],'trace':trace,'standard':False}
  return {'resolved':False,'path':path,'type':t,'trace':trace,'reason':'not a supported graphical connector'}
 def inspect(self):
  rows=[];edits={}
  for f,s in self.sources.items():
   for x in all_connections(s):
    c=x['class'];eps=[self.endpoint(c.full,e) for e in x['endpoints']]
    rec={'file':f.relative_to(self.root).as_posix(),'class':c.full,'connect':x['endpoints'],'endpoints':eps,'line_number':s.text.count('\n',0,x['start'])+1}
    color=x['color'];old=None
    if color:
     m=re.fullmatch(r'\{\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\}',color[2])
     if m:old=tuple(map(int,m.groups()))
    rec['old_color']=old
    if not all(e['resolved'] for e in eps):rec['status']='UNRESOLVED';rows.append(rec);continue
    std=[e for e in eps if e['standard']]
    if std:
     kinds=set(e['family'] for e in std)
     if len(kinds)>1:rec['status']='MSL_FAMILY_CONFLICT';rows.append(rec);continue
     target=std[0]['color'];rec['basis']='MSL_DEFAULT';rec['family']=std[0]['family'];rec['source']=MSL_SOURCE_BASE+MSL_REFS[std[0]['family']]
    else:
     colors=set(tuple(e['color']) for e in eps)
     if len(colors)>1:rec['status']='CUSTOM_COLOR_CONFLICT';rows.append(rec);continue
     target=eps[0]['color'];rec['basis']='CUSTOM_ICON';rec['family']='CUSTOM'
    rec['target_color']=target
    if x['line'] is None:rec['status']='NO_LINE';rows.append(rec);continue
    if color and old is None:rec['status']='DYNAMIC_OR_UNSUPPORTED_COLOR';rows.append(rec);continue
    if old==tuple(target):rec['status']='ALREADY_MATCHES'
    else:
     rec['status']='COLOR_CHANGED'
     q='{'+','.join(map(str,target))+'}'
     if color:edits.setdefault(f,[]).append((color[0],color[1],q))
     else:
      pos=x['line'].b-1;sep=', ' if s.ann_args(x['line'].a) else ''
      edits.setdefault(f,[]).append((pos,pos,sep+'color='+q))
    rows.append(rec)
  return rows,edits

def canonical_with_connection_colors(text, ignore_root_version=False):
 """Exempt ONLY Line.color on actual connect statements; protect all else."""
 s=Source(text)
 if s.unparsed:raise ValueError('Unsupported source syntax')
 edits=[]
 for x in all_connections(s):
  if x['line'] is None:continue
  if x['color']:
   a,b,_=x['color'];edits.append((a,b,'{0,0,0}'))
  else:
   pos=x['line'].b-1;sep=', ' if s.ann_args(x['line'].a) else ''
   edits.append((pos,pos,sep+'color={0,0,0}'))
 return Source(apply(text,edits)).canonical(ignore_root_version)

def palette_key(endpoints):
 return ' | '.join(re.sub(r'\s+','',x) for x in endpoints)

def apply_reviewed_palette(text, class_palette):
 """Apply a previously reviewed current-topology palette to generated code.
 Unknown topology fails closed for classes with a palette; regenerate/review the
 palette after any authorized structural change. No endpoint/type is rewritten.
 """
 s=Source(text);edits=[]
 if s.unparsed:raise ValueError('Unsupported generated source')
 for x in all_connections(s):
  table=class_palette.get(x['class'].full)
  if table is None:continue
  key=palette_key(x['endpoints'])
  if key not in table:raise ValueError('Connection palette needs review: '+x['class'].full+' '+key)
  color=table[key]
  if len(color)!=3 or any(not isinstance(v,int) or not 0<=v<=255 for v in color):raise ValueError('Invalid RGB palette')
  if x['line'] is None:raise ValueError('Generated connection has no Line')
  q='{'+','.join(map(str,color))+'}'
  if x['color']:
   a,b,v=x['color']
   if v!=q:edits.append((a,b,q))
  else:
   pos=x['line'].b-1;sep=', ' if s.ann_args(x['line'].a) else ''
   edits.append((pos,pos,sep+'color='+q))
 out=apply(text,edits)
 if canonical_with_connection_colors(text)!=canonical_with_connection_colors(out):raise ValueError('Protected generated tokens changed')
 return out

def main():
 import argparse
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('root',type=Path);p.add_argument('--report',type=Path,required=True)
 p.add_argument('--apply',action='store_true',help='Explicitly authorize Line.color changes; default read-only')
 p.add_argument('--palette',type=Path,help='Reviewed custom connector colors; unknown main colors are not guessed')
 p.add_argument('--msl-version',help='Explicitly confirm installed MSL version; writing supports only 4.0.0')
 a=p.parse_args()
 try:
  if a.msl_version and a.msl_version!='4.0.0':raise ValueError('Unsupported MSL version: registry requires actual-source review')
  if a.apply and a.msl_version!='4.0.0':raise ValueError('--apply requires explicit --msl-version 4.0.0 confirmation')
  palette=json.loads(a.palette.read_text(encoding='utf-8')) if a.palette else None
  ix=Index(a.root,reviewed_palette=palette,require_reviewed_palette=True);rows,edits=ix.inspect()
  bad=[r for r in rows if r['status'] not in ('ALREADY_MATCHES','COLOR_CHANGED')]
  if a.apply and bad:raise ValueError('Unresolved/conflicting connections: no files written')
  if a.apply:
   for f,es in edits.items():
    before=ix.sources[f].text;after=apply(before,es)
    if canonical_with_connection_colors(before)!=canonical_with_connection_colors(after):raise ValueError('Protected tokens changed')
    f.write_text(after,encoding='utf-8')
  result={'scope':'MSL 4.0.0 finite static resolver; not compiler/GUI validation',
          'mode':'APPLIED' if a.apply else 'READ_ONLY','status':'PALETTE_RESOLVED' if rows and not bad else 'REVIEW_REQUIRED',
          'version':'0.9.0','registryVersion':'4.0.0','semanticValidation':'NOT_CHECKED',
          'customPaletteReviewed':bool(palette),'connections':rows,'planned_or_applied_changes':sum(len(v) for v in edits.values())}
  a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
  return 0 if rows and not bad else 2
 except (ValueError,OSError,KeyError) as e:p.error(str(e))
if __name__=='__main__':sys.exit(main())
