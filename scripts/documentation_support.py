"""Idempotent Modelica documentation enrichment and opt-in approved Line colors.
The catalog contains reviewed engineering summaries, not replacement equations.
"""
from __future__ import annotations
from pathlib import Path
import json,re,html
try:
    from .modelica_support import Source,apply,quote
except ImportError:
    from modelica_support import Source,apply,quote

SI_UNITS={'Time':'s','Frequency':'Hz','AngularVelocity':'rad/s','AngularAcceleration':'rad/s2','Angle':'rad','Length':'m','Position':'m','Distance':'m','Velocity':'m/s','Acceleration':'m/s2','Mass':'kg','MassFlowRate':'kg/s','Pressure':'Pa','AbsolutePressure':'Pa','PressureDifference':'Pa','Temperature':'K','ThermodynamicTemperature':'K','TemperatureDifference':'K','Power':'W','HeatFlowRate':'W','Energy':'J','Torque':'N.m','MomentOfInertia':'kg.m2','Voltage':'V','Current':'A','ElectricCharge':'C','Resistance':'Ohm','Conductance':'S','Capacitance':'F','HeatCapacity':'J/K','ThermalConductance':'W/K','Density':'kg/m3','SpecificHeatCapacity':'J/(kg.K)','SpecificEnthalpy':'J/kg','SpecificInternalEnergy':'J/kg','Area':'m2','Volume':'m3','Efficiency':'1'}

def unit_of(d):
    m=re.search(r'\bunit\s*=\s*"([^"]*)"',d.modifier)
    if m:return m[1]
    return SI_UNITS.get(d.type.split('.')[-1],'')
def short(s,n=160):
    s=' '.join(s.split())
    return s if len(s)<=n else s[:n]+' …（完整表达式见源码）'
def esc(s):return html.escape(str(s),quote=True)
def table(headers,rows):
    if not rows:return ''
    return '<table border="1" cellspacing="0" cellpadding="5"><tr>'+''.join('<th>'+esc(x)+'</th>' for x in headers)+'</tr>'+''.join('<tr>'+''.join('<td>'+str(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</table>'
def link(name):return '<a href="modelica://'+esc(name)+'">'+esc(name)+'</a>'
def kind_of(d,catalog,c=None):
    if 'parameter' in d.prefix or 'constant' in d.prefix:return '配置'
    t=catalog.get('classes',{}).get(c.full,{}).get('resolved_types',{}).get(d.name,d.type) if c else d.type
    info=catalog.get('classes',{}).get(t)
    if 'input' in d.prefix or t.endswith('Input'):return '输入'
    if 'output' in d.prefix or t.endswith('Output'):return '输出'
    if 'Interfaces' in t or 'Port' in t or 'Pin' in t or 'Flange' in t or (info and info.get('kind')=='connector'):return '接口'
    if t in ['Real','Integer','Boolean','String'] or t.startswith(('SI.','Modelica.Units.')) or 'discrete' in d.prefix or 'flow' in d.prefix or 'stream' in d.prefix:return '内部量' if d.visibility=='protected' else '公开量'
    if t in catalog.get('model_classes',[]) or t.startswith('Modelica.') and not t.startswith('Modelica.Blocks.Types.') or (info and info.get('kind') in ['model','block']):return '组件'
    return '字段'
def field_desc(c,d,catalog):
    meta=catalog['classes'].get(c.full,{})
    desc=meta.get('fields',{}).get(d.name)
    if desc:return desc
    if re.search('[\u4e00-\u9fff]',d.description):return d.description
    role=kind_of(d,catalog,c)
    noun=catalog.get('field_labels',{}).get(d.name,d.name)
    if noun==d.name:
        if role=='配置':noun='配置项 '+d.name
        elif role=='组件':noun='组成单元 '+d.name
        elif role=='接口':noun='交互接口 '+d.name
        elif role=='输入':noun='输入信号 '+d.name
        elif role=='输出':noun='输出信号 '+d.name
        else:noun='计算量 '+d.name
    u=unit_of(d)
    tail='；'+d.description if d.description else ''
    return noun+(' ['+u+']' if u else '')+tail

def render_doc(src,c,cat):
    meta=cat['classes'].get(c.full,{})
    title=meta.get('title',c.name)
    purpose=meta.get('summary') or c.description or ('提供'+title+'的'+{'package':'类组织','record':'配置/数据字段','connector':'公开交互字段','function':'函数计算','type':'类型定义'}.get(c.kind,'局部模型实现')+'。')
    out=['<html><h2>'+esc(title)+'</h2><p><b>类路径：</b><code>'+esc(c.full)+'</code>　<b>类型：</b>'+esc(c.kind)+'</p>','<h3>用途与定位</h3><p>'+esc(purpose)+'</p>']
    if c.full==cat.get('root'):
        out+=['<h3>开始使用</h3><p>'+esc(cat.get('root_usage',''))+'</p><p>完整任务入口：'+link(cat['entry'])+'。建议从任务入口进入总体系统，再逐层查看设备和行为类。</p><p>'+esc(cat.get('release_boundary',''))+'</p>']
    elif c.kind=='package':
        out+=['<h3>阅读与调用</h3><p>本包用于组织类。按下表进入相应模型；包本身不单独启动仿真。</p>']
    elif c.kind in ['record','type']:
        out+=['<h3>配置与调用</h3><p>由使用者声明或传入本类型；记录与常量保存静态配置，不单独代表一套物理状态。修改设计输入后应通过项目既有离线配置入口生成生效快照。</p>']
    elif c.kind=='connector':
        out+=['<h3>连接方法</h3><p>在拥有该边界的模型中实例化，使用真实端口连接。类型、数组维数和成员应与对端一致；字段名相同不自动保证单位、参考系和生产者兼容。input/output、flow/stream及普通字段分别保留原声明语义。</p>']
    elif c.kind=='function':
        out+=['<h3>调用方法</h3><p>通过函数名及声明的输入调用。输入输出与算法以本类及继承合同为准；函数调用不创建独立仿真实验。输入有效域和超界行为见下面的实现摘要与原始算法。</p>']
    else:
        parents=meta.get('parents',[])
        if parents:out+=['<h3>在工程中使用</h3><p>当前直接使用位置：'+ '；'.join(link(p['class'])+' 的 <code>'+esc(p['instance'])+'</code>' for p in parents[:8])+('；另有'+str(len(parents)-8)+'处，见源码引用。' if len(parents)>8 else '。')+'</p>']
        else:out+=['<h3>在工程中使用</h3><p>'+('本类是项目声明的完整任务入口；直接加载根 package.mo 后选择本类。' if c.full==cat.get('entry') else '按本类公开接口在所属父层装配，或由派生类复用。以下清单仅说明当前源码；没有直接使用记录不等于已经证明本类不可达。')+'</p>']
    children=meta.get('package_children',[])
    if c.kind=='package' and children:
        out.append(table(['类','用途'],[[link(x['class']),esc(x['title'])] for x in children]))
    ports=[];params=[];components=[];states=[];variables=[]
    for d in c.decls:
        role=kind_of(d,cat,c);desc=field_desc(c,d,cat);dim=d.dims;unit=unit_of(d)
        row=['<code>'+esc(d.name+dim)+'</code>',esc(d.type),esc(' '.join(d.prefix) or d.visibility),esc(unit or '按声明/类型合同'),esc(desc)]
        if role=='配置':
            bind=d.binding
            if len(bind)>220:bind='数组/矩阵或复杂记录；查看本类参数对话框与源码中的当前声明'
            params.append(['<code>'+esc(d.name+dim)+'</code>',esc(d.type),esc(desc),'<code>'+esc(short(bind or '由调用方、继承或默认声明提供',220))+'</code>'])
        elif role=='组件':components.append(['<code>'+esc(d.name+dim)+'</code>',link(meta.get('resolved_types',{}).get(d.name,d.type)),esc(desc)])
        elif role in ['接口','输入','输出'] or c.kind in ['connector','function','record']:ports.append(row)
        else:variables.append(row)
    if ports:out+=['<h3>接口、输入与输出</h3>',table(['名称/维数','类型','声明角色','单位','含义'],ports)]
    if params:out+=['<h3>配置与参数</h3><p>下面列出当前源码表达式，仅用于阅读；当前参数对话框、生效配置记录与原有配置工具仍是使用依据。本页不新增默认值或换算。</p>',table(['参数','类型','用途','源码表达式'],params)]
    if components:out+=['<h3>内部组成</h3><p>以下为本类直接声明的组成单元，继承类的内部结构另按其文档查看。</p>',table(['实例','类','作用'],components)]
    if c.extends:
        out+=['<h3>继承与复用</h3><p>本类的继承/别名声明如下。继承得到的端口、参数、状态和算法仍由被引用类定义，不重复增加一套行为。</p>']
        for x in c.extends:out.append('<pre>'+esc(short(x,1500))+'</pre>')
    eq=[];conns=[];state_names=[];algo=False
    for ph,a,b in c.statements:
        ts=src.scan(a,b);stop=next((t.a for t in ts if t.value=='annotation'),b)
        st=src.text[a:stop].strip().rstrip(';')+';'
        if st.startswith('connect(') or st.startswith('connect ('):conns.append(st)
        else:
            if len(st)<1600:eq.append((ph,st))
            for m in re.finditer(r'\bder\s*\(\s*([\w.]+(?:\[[^]]*\])?)\s*\)',st):state_names.append(m[1])
        algo|='algorithm' in ph
    if state_names or any('discrete' in d.prefix for d in c.decls):
        names=list(dict.fromkeys(state_names+[d.name for d in c.decls if 'discrete' in d.prefix]))
        out+=['<h3>状态与初始化</h3><p>本类源码中显式出现的导数对象或离散声明：<code>'+esc(', '.join(names))+'</code>。初始化取当前声明的 start/fixed、initial 方程/算法及继承设置。此处是源码级说明，不等同于编译后连续状态统计。</p>']
    if eq:
        out+=['<h3>实现摘要</h3><p>以下表达式直接摘自本类，保留原始符号和单位体系；完整的条件分支、循环与初始化以源码为准。</p>']
        out.append('<pre>'+esc('\n'.join('['+p+'] '+short(t,600) for p,t in eq[:10]))+'</pre>')
        if len(eq)>10:out.append('<p>本类另有'+str(len(eq)-10)+'段语句；阅读完整源码可查看其余边界与逻辑。</p>')
    elif not c.extends and not conns and c.kind in ['model','block']:
        out+=['<h3>当前实现</h3><p>本类没有本层行为语句；其作用由已声明成员、继承关系和现有图形注解共同确定。不能仅凭历史标题推定当前源码存在未声明的显示单元或功能。</p>']
    if variables:
        out+=['<h3>结果与内部计算量</h3>',table(['名称/维数','类型','声明角色','单位','含义'],variables)]
    limit=meta.get('limit','')
    if limit:out+=['<h3>使用边界</h3><p>'+esc(limit)+'</p>']
    if meta.get('license_note'):out+=['<h3>保留的来源与许可说明</h3>',meta['license_note']]
    out+=['</html>']
    return ''.join(out)

_CACHE={}
def enrich_generated(text:str,file_hint:str='',catalog:dict|None=None)->str:
    if catalog is None:
        p=Path(__file__).with_name('catalog.json')
        key=str(p)
        if key not in _CACHE:_CACHE[key]=json.loads(p.read_text(encoding='utf8'))
        catalog=_CACHE[key]
    src=Source(text)
    if src.unparsed:raise ValueError('Documentation parse incomplete: '+repr(src.unparsed[:3]))
    patches=[]
    for c in src.all_classes():
        meta=catalog['classes'].get(c.full,{})
        if not meta:continue
        if catalog.get('rename_descriptions'):
            target=meta.get('declaration_description')
            if target:
                if catalog.get('class_comment_style') == 'chinese-purpose-only':
                    try:
                        from .auxiliary_metadata import concise_class_comment
                    except ImportError:
                        from auxiliary_metadata import concise_class_comment
                    target = concise_class_comment(c.name, target)
                if c.desc_span:patches.append((*c.desc_span,quote(target)))
                elif not c.short:patches.append((c.name_end,c.name_end,' '+quote(target)))
                else:
                    pos=c.anns[0][0] if c.anns else c.end_start
                    patches.append((pos,pos,' '+quote(target)+' '))
        for d in c.decls:
            desc=field_desc(c,d,catalog)
            if d.desc_span:
                if desc!=d.description:patches.append((*d.desc_span,quote(desc)))
            else:patches.append((d.insert,d.insert,' '+quote(desc)+' '))
        patches.append(src.doc_patch(c,render_doc(src,c,catalog)))
    result = apply(text,patches)
    if catalog.get('connection_colors'):
        try:
            from .connection_colors import apply_reviewed_palette
        except ImportError:
            from connection_colors import apply_reviewed_palette
        result = apply_reviewed_palette(result, catalog['connection_colors'])
    return result
