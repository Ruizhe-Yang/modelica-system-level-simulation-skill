"""Narrow, source-preserving Documentation cleanup and display-name helpers.
No behavior, declaration type, unit, modifier, connection or icon edit is made.
HTML cleanup supports heading-delimited Documentation sections; no HTML serializer
is used, so retained prose, tables, links and license notices keep their bytes.
"""
from __future__ import annotations
from html.parser import HTMLParser
import html,re

class _Spans(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=False)
        self.text=text;self.starts=[0]+[m.end() for m in re.finditer('\n',text)]
        self.stack=[];self.nodes=[];self.heading=[]
        self.feed(text);self.close()
    def pos(self):
        line,col=self.getpos();return self.starts[line-1]+col
    def handle_starttag(self,tag,attrs):
        a=self.pos();b=a+len(self.get_starttag_text())
        if tag in {'br','img','hr','meta','link','input','area','base','col','embed','param','source','track','wbr'}:return
        self.stack.append({'tag':tag,'a':a,'inner':b})
    def handle_startendtag(self,tag,attrs):pass
    def handle_endtag(self,tag):
        a=self.pos();end=self.text.find('>',a)+1
        if end<=0:return
        match=next((i for i in range(len(self.stack)-1,-1,-1) if self.stack[i]['tag']==tag),None)
        if match is None:return
        n=self.stack[match];self.stack=self.stack[:match]
        n.update(end=end,inner_end=a)
        n['plain']=html.unescape(re.sub(r'<[^>]*>','',self.text[n['inner']:a])).strip()
        self.nodes.append(n)
        if re.fullmatch('h[1-6]',tag):self.heading.append(n)

def clean_documentation_html(text:str)->tuple[str,dict]:
    """Remove requested headings and auxiliary-update boilerplate, keep limits."""
    s=_Spans(text);cuts=[];counts={'connection_section':0,'result_howto_section':0,'auxiliary_boilerplate':0}
    hs=sorted(s.heading,key=lambda n:n['a'])
    for i,n in enumerate(hs):
        plain=re.sub(r'^\s*(?:[0-9一二三四五六七八九十]+[.、． ]+)','',n['plain'])
        key={'连接与责任':'connection_section','仿真后如何查看':'result_howto_section'}.get(plain)
        if not key:continue
        # A section ends at the next heading of equal/higher level, or at its
        # containing structural element. Leave its closing element untouched.
        ends=[m['a'] for m in hs[i+1:] if int(m['tag'][1])<=int(n['tag'][1])]
        ends += [m['inner_end'] for m in s.nodes if m['tag'] in ('section','div','body','html') and m['a']<n['a']<m['inner_end']]
        end=min(ends,default=len(text));cuts.append((n['a'],end));counts[key]+=1
    for n in s.nodes:
        if n['tag']=='p' and re.match(r'\s*Documentation\s*辅助更新',n['plain']):
            cuts.append((n['a'],n['end']));counts['auxiliary_boilerplate']+=1
    # Fallback for documents where the same footer was put directly in <small>.
    for n in s.nodes:
        if n['tag']=='small' and re.match(r'\s*Documentation\s*辅助更新',n['plain']) and not any(a<=n['a'] and b>=n['end'] for a,b in cuts):
            cuts.append((n['a'],n['end']));counts['auxiliary_boilerplate']+=1
    merged=[]
    for a,b in sorted(cuts):
        if merged and a<=merged[-1][1]:merged[-1]=(merged[-1][0],max(b,merged[-1][1]))
        else:merged.append((a,b))
    for a,b in reversed(merged):text=text[:a]+text[b:]
    return text,counts

def concise_class_comment(class_name:str,description:str,approved_chinese:str|None=None)->str:
    """Return Chinese purpose only; browsers already provide the class name.
    An approved purpose is needed for untranslatable or English-only descriptions.
    This function never alters a Modelica identifier or guesses a translation.
    """
    if approved_chinese is not None:
        if not re.search(r'[\u4e00-\u9fff]',approved_chinese):raise ValueError('Approved purpose must include Chinese')
        return approved_chinese.strip()
    s=description.strip()
    m=re.fullmatch(re.escape(class_name)+r'\s*[（(](.*)[）)]',s,re.S)
    if m:s=m[1].strip()
    if not re.search(r'[\u4e00-\u9fff]',s):raise ValueError('Chinese purpose requires human review: '+class_name)
    return s
