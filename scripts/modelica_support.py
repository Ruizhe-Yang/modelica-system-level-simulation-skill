"""Conservative source-range utilities for Modelica documentation work.
This is a lexical/static helper, not a Modelica compiler or semantic validator.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import re, json, hashlib
from pathlib import Path

STR=r'"(?:\\[\s\S]|[^"\\])*"'
QID=r"'(?:\\[\s\S]|[^'\\])*'"
COMMENT=r'//[^\n\r]*|/\*[\s\S]*?\*/'
SPECIAL=re.compile(STR+'|'+QID+'|'+COMMENT+r'|[(){}\[\]]')
LEX=re.compile(r'\s+|'+COMMENT+'|'+STR+'|'+QID+r'|[A-Za-z_]\w*|(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?|:=|<=|>=|<>|\.\*|\./|\.\^|\S')
IDENT=re.compile(r"^(?:[A-Za-z_]\w*|'(?:\\.|[^'\\])*')$")
KINDS={'model','block','package','record','connector','function','type','class','operator'}
PREFIX={'encapsulated','partial','expandable','pure','impure','final','replaceable','redeclare','operator'}
DPREFIX={'parameter','constant','input','output','flow','stream','discrete','final','inner','outer','replaceable','redeclare'}

@dataclass
class Token:
    value:str; a:int; b:int; kind:str='token'
@dataclass
class Decl:
    name:str; type:str; prefix:list[str]; a:int; b:int; name_end:int; insert:int
    description:str=''; desc_span:tuple[int,int]|None=None
    visibility:str='public'; dims:str=''; modifier:str=''; binding:str=''
@dataclass
class Class:
    name:str; full:str; kind:str; a:int; b:int=0; end_start:int=0; name_end:int=0
    short:bool=False; description:str=''; desc_span:tuple[int,int]|None=None
    decls:list[Decl]=field(default_factory=list); anns:list[tuple[int,int,int,int]]=field(default_factory=list)
    extends:list[str]=field(default_factory=list); imports:list[str]=field(default_factory=list)
    statements:list[tuple[str,int,int]]=field(default_factory=list); children:list['Class']=field(default_factory=list)

def decode_string(s:str)->str:
    if not s.startswith('"'):return s
    s=s[1:-1]
    trans={'n':'\n','r':'\r','t':'\t','"':'"',"'":"'",'\\':'\\','a':'\a','b':'\b','f':'\f','v':'\v','?':'?'}
    return re.sub(r'\\(.)',lambda m:trans.get(m[1],m[1]),s,flags=re.S)
def quote(s:str)->str:
    return '"'+s.replace('\\','\\\\').replace('"','\\"').replace('\r','\\r').replace('\n','\\n').replace('\t','\\t')+'"'
def apply(s:str, patches:list[tuple[int,int,str]])->str:
    patches=sorted(patches,key=lambda x:(x[0],x[1]))
    end=-1
    for a,b,text in patches:
        if a<end:raise ValueError(f'Overlapping edits {a} < {end}')
        end=b
    for a,b,text in reversed(patches):s=s[:a]+text+s[b:]
    return s

class Source:
    def __init__(self,text:str):
        self.text=text; self.pairs={}; stack=[]
        for m in SPECIAL.finditer(text):
            v=m[0]
            if len(v)!=1:continue
            if v in '([{':stack.append((v,m.start()))
            elif v in ')]}':
                if not stack or '([{'.index(stack[-1][0])!=')]}'.index(v):raise ValueError(f'Unbalanced delimiter at {m.start()}')
                _,a=stack.pop();self.pairs[a]=m.end()
        if stack:raise ValueError(f'Unclosed delimiter {stack[-1]}')
        self.tokens=self.scan();self.classes=[];self.unparsed=[];self.within=''
        i=0
        if self.tokens and self.tokens[0].value=='within':
            j=next(j for j,t in enumerate(self.tokens) if t.value==';')
            self.within=''.join(t.value for t in self.tokens[1:j]);i=j+1
        while i<len(self.tokens):
            if self.tokens[i].value==';':i+=1;continue
            c,j=self.parse_class(i,self.within)
            if c is None:
                self.unparsed.append(('root',self.tokens[i].value,self.tokens[i].a));i+=1
            else:self.classes.append(c);i=j
    def scan(self,a=0,b=None):
        b=len(self.text) if b is None else b;out=[];i=a
        while i<b:
            m=LEX.match(self.text,i)
            if not m:raise ValueError(f'Unknown lexical input at {i}')
            v=m[0];j=m.end()
            if v.isspace() or v.startswith('//') or v.startswith('/*'):i=j;continue
            if v in '([{':
                j=self.pairs[i];out.append(Token(v,i,j,'group'))
            else:out.append(Token(v,i,j,'string' if v.startswith('"') else 'token'))
            i=j
        return out
    def string_comment(self,ts,i):
        if i>=len(ts) or ts[i].kind!='string':return '',None,i
        a=ts[i].a;b=ts[i].b;parts=[decode_string(ts[i].value)];i+=1
        while i+1<len(ts) and ts[i].value=='+' and ts[i+1].kind=='string':
            parts.append(decode_string(ts[i+1].value));b=ts[i+1].b;i+=2
        return ''.join(parts),(a,b),i
    def parse_class(self,i,parent):
        ts=self.tokens;start=i;j=i
        while j<len(ts) and ts[j].value in PREFIX and ts[j].value!='operator':j+=1
        if j>=len(ts) or ts[j].value not in KINDS:return None,i
        kind=ts[j].value
        if kind=='operator' and j+1<len(ts) and ts[j+1].value in KINDS:j+=1;kind=ts[j].value
        if j+1>=len(ts) or not IDENT.match(ts[j+1].value):return None,i
        long_extends=(ts[j+1].value=='extends')
        if long_extends:
            name=ts[j+2].value;j+=3
        else:
            name=ts[j+1].value;j+=2
        c=Class(name,(parent+'.' if parent else '')+name,kind,ts[start].a,name_end=ts[j-1].b)
        if long_extends:
            c.extends.append('extends '+name)
            if j<len(ts) and ts[j].value=='(':
                c.extends[-1]+=self.text[ts[j].a:ts[j].b];j+=1
        if j<len(ts) and ts[j].value=='=':
            c.short=True;k=j
            while k<len(ts) and ts[k].value!=';':k+=1
            if k==len(ts):raise ValueError('Unclosed short class '+name)
            sub=ts[j:k];an=next((x for x,t in enumerate(sub) if t.value=='annotation'),None)
            tail=sub if an is None else sub[:an]
            self.set_tail_desc(c,tail)
            if an is not None:
                at=sub[an];g=sub[an+1];c.anns.append((at.a,g.b,g.a,ts[k].b))
            c.end_start=ts[k].a;c.b=ts[k].b
            # base type/expression kept verbatim for documentation
            c.extends=[self.text[ts[j+1].a:(c.desc_span[0] if c.desc_span else (sub[an].a if an is not None else ts[k].a))].strip()]
            return c,k+1
        c.description,c.desc_span,j=self.string_comment(ts,j)
        phase='declaration';vis='public'
        while j<len(ts):
            if ts[j].value=='end' and j+2<len(ts) and ts[j+1].value==name and ts[j+2].value==';':
                c.end_start=ts[j].a;c.b=ts[j+2].b;return c,j+3
            if ts[j].value in ['public','protected']:
                vis=ts[j].value;phase='declaration';j+=1;continue
            if ts[j].value=='initial' and j+1<len(ts) and ts[j+1].value in ['equation','algorithm']:
                phase='initial '+ts[j+1].value;j+=2;continue
            if ts[j].value in ['equation','algorithm']:
                phase=ts[j].value;j+=1;continue
            if phase=='declaration':
                ch,k=self.parse_class(j,c.full)
                if ch is not None:c.children.append(ch);j=k;continue
            k=j
            while k<len(ts) and ts[k].value!=';':
                if ts[k].value=='end' and k+1<len(ts) and ts[k+1].value==name:raise ValueError('Missing semicolon before '+name)
                k+=1
            if k==len(ts):raise ValueError('Unclosed class '+name)
            sub=ts[j:k]
            if sub and sub[0].value=='annotation' and len(sub)>1:
                g=sub[1];c.anns.append((sub[0].a,g.b,g.a,ts[k].b))
            elif sub and sub[0].value=='extends':
                c.extends.append(self.text[sub[1].a:ts[k].a].strip())
            elif sub and sub[0].value=='import':
                c.imports.append(self.text[sub[1].a:ts[k].a].strip())
            elif phase=='declaration' and sub:
                ds=self.parse_decls(sub,ts[k].a,vis)
                if ds:c.decls.extend(ds)
                else:self.unparsed.append((c.full,self.text[sub[0].a:ts[k].b][:180],sub[0].a))
            elif sub:c.statements.append((phase,sub[0].a,ts[k].b))
            j=k+1
        raise ValueError('Missing class end '+name)
    def set_tail_desc(self,obj,ts):
        if not ts or ts[-1].kind!='string':return
        j=len(ts)-1
        while j>=2 and ts[j-1].value=='+' and ts[j-2].kind=='string':j-=2
        if j>0 and ts[j-1].value in ['=',':=','then','else','+','-','*','/']:return
        desc,span,_=self.string_comment(ts,j);obj.description=desc;obj.desc_span=span
    def parse_decls(self,ts,end,vis):
        j=0;pref=[]
        while j<len(ts) and ts[j].value in DPREFIX:pref.append(ts[j].value);j+=1
        if j>=len(ts) or not IDENT.match(ts[j].value) or ts[j].value in ['import','extends','end','external']:return []
        typ=ts[j].value;j+=1
        while j+1<len(ts) and ts[j].value=='.' and IDENT.match(ts[j+1].value):typ+='.'+ts[j+1].value;j+=2
        td=''
        if j<len(ts) and ts[j].value=='[':td=self.text[ts[j].a:ts[j].b];j+=1
        if j>=len(ts) or not IDENT.match(ts[j].value):return []
        start=j;chunks=[]
        for k in range(j,len(ts)):
            if ts[k].value==',':chunks.append((ts[start:k],ts[k].a));start=k+1
        chunks.append((ts[start:],end));res=[]
        for sub,e in chunks:
            if not sub or not IDENT.match(sub[0].value):return []
            name=sub[0];an=next((i for i,t in enumerate(sub) if t.value=='annotation'),len(sub));tail=sub[:an]
            d=Decl(name.value,typ,pref[:],name.a,e,name.b,sub[an].a if an<len(sub) else e,visibility=vis,dims=td)
            self.set_tail_desc(d,tail)
            z=1
            if z<len(tail) and tail[z].value=='[':d.dims+=self.text[tail[z].a:tail[z].b];z+=1
            if z<len(tail) and tail[z].value=='(':
                d.modifier=self.text[tail[z].a:tail[z].b];z+=1
            be=d.desc_span[0] if d.desc_span else d.insert
            if z<len(tail):d.binding=self.text[tail[z].a:be].strip()
            res.append(d)
        return res
    def all_classes(self):
        def walk(c):
            yield c
            for ch in c.children:yield from walk(ch)
        for c in self.classes:yield from walk(c)
    def ann_args(self,group_start):
        ts=self.scan(group_start+1,self.pairs[group_start]-1);parts=[];j=0
        for i,t in enumerate(ts):
            if t.value==',':
                if j<i:parts.append(ts[j:i])
                j=i+1
        if j<len(ts):parts.append(ts[j:])
        return parts
    def documentation(self,c):
        for an in c.anns:
            for part in self.ann_args(an[2]):
                if part and part[0].value=='Documentation' and len(part)>1:
                    return an,part[1]
        return None
    def doc_info(self,c):
        pair=self.documentation(c)
        if not pair:return ''
        for p in self.ann_args(pair[1].a):
            if len(p)>=3 and p[0].value=='info' and p[1].value=='=':
                return ''.join(decode_string(t.value) for t in p[2:] if t.kind=='string')
        return ''
    def doc_patch(self,c,html):
        pair=self.documentation(c);q=quote(html)
        if pair:
            for p in self.ann_args(pair[1].a):
                if len(p)>=3 and p[0].value=='info' and p[1].value=='=':return p[2].a,p[-1].b,q
            pos=pair[1].b-1;sep=', ' if self.ann_args(pair[1].a) else ''
            return pos,pos,sep+'info='+q
        if c.anns:
            an=c.anns[-1];pos=self.pairs[an[2]]-1;sep=', ' if self.ann_args(an[2]) else ''
            return pos,pos,sep+'Documentation(info='+q+')'
        if c.short:return c.end_start,c.end_start,' annotation(Documentation(info='+q+'))'
        return c.end_start,c.end_start,'  annotation(Documentation(info='+q+'));\n'
    def canonical(self,ignore_version=True):
        patches=[]
        for c in self.all_classes():
            if c.desc_span:patches.append((*c.desc_span,''))
            for d in c.decls:
                if d.desc_span:patches.append((*d.desc_span,''))
            for an in c.anns:
                args=self.ann_args(an[2]);kept=[];changed=False
                for p in args:
                    if p[0].value=='Documentation' or (ignore_version and not self.within and c in self.classes and p[0].value=='version'):
                        changed=True;continue
                    kept.append(self.text[p[0].a:p[-1].b])
                if changed:
                    if kept:patches.append((an[0],an[1],'annotation('+','.join(kept)+')'))
                    else:patches.append((an[0],an[3] if not c.short else an[1],''))
        s=apply(self.text,patches)
        h=hashlib.sha256()
        for m in LEX.finditer(s):
            t=m[0]
            if t.isspace() or t.startswith('//') or t.startswith('/*'):continue
            h.update(t.encode('utf8'));h.update(b'\x00')
        return h.hexdigest()

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--output',type=Path)
    a=p.parse_args();rows=[];errors=[]
    for f in sorted(a.root.rglob('*.mo')):
        if f.is_symlink():continue
        try:
            s=Source(f.read_text(encoding='utf-8-sig'))
            for c in s.all_classes():rows.append({'file':str(f.relative_to(a.root)),'class':c.full,'kind':c.kind,'description':c.description,'declared_fields':len(c.decls),'has_documentation':bool(s.doc_info(c))})
            errors.extend([{'file':str(f.relative_to(a.root)),'detail':x} for x in s.unparsed])
        except Exception as e:errors.append({'file':str(f.relative_to(a.root)),'error':str(e)})
    result={'scope':'lexical inventory, not compiler validation','classes':rows,'unparsed':errors}
    data=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output:a.output.write_text(data,encoding='utf8')
    else:print(data)
