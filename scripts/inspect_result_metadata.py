#!/usr/bin/env python3
"""Read variable descriptions from OMC init XML or recognized MAT metadata.
XML needs standard Python; MAT needs locally installed scipy/numpy. Never modifies
results. No values are synthesized; unsupported layouts raise a clear error.
"""
import argparse,csv,json,sys,xml.etree.ElementTree as ET
from pathlib import Path

def read_xml(p):
    root=ET.parse(p).getroot();rows=[]
    for v in root.iter():
        if v.tag.split('}')[-1]!='ScalarVariable':continue
        typ=next(iter(v),None);attrs=typ.attrib if typ is not None else {}
        rows.append({'name':v.get('name',''),'description':v.get('description',''),'unit':attrs.get('unit',''),'displayUnit':attrs.get('displayUnit','')})
    if not rows:raise ValueError('No ScalarVariable metadata found')
    return rows

def read_mat(p):
    try:
        import numpy as np
        from scipy.io import loadmat
    except ImportError as e:raise ValueError('MAT inspection requires preinstalled scipy and numpy; use init XML otherwise') from e
    m=loadmat(p,variable_names=['Aclass','name','description','dataInfo'],chars_as_strings=False)
    if not all(k in m for k in ('Aclass','name','description','dataInfo')):raise ValueError('Unsupported MAT metadata layout; expected Aclass/name/description/dataInfo')
    def decode(seq):
        flat=np.asarray(seq).ravel()
        if flat.dtype.kind in 'iu':raw=bytes(int(x) for x in flat if 0<=int(x)<256);return raw.decode('utf8',errors='replace').rstrip('\x00 ')
        vals=[str(x) for x in flat];text=''.join(vals).rstrip('\x00 ')
        if all(ord(ch)<256 for ch in text):
            try:return text.encode('latin1').decode('utf8')
            except UnicodeDecodeError:pass
        return text
    a=m['Aclass'];h=' '.join(decode(row) for row in a)
    # MAT v4 metadata convention: binTrans -> variable strings in columns.
    if 'binTrans' in h:axis=1
    elif 'binNormal' in h:axis=0
    else:raise ValueError('Unrecognized Aclass orientation; cannot safely align descriptions')
    def strings(a):
        if a.ndim!=2:raise ValueError('Expected 2-D character matrix')
        return [decode(a[:,i]) for i in range(a.shape[1])] if axis==1 else [decode(r) for r in a]
    names,desc=strings(m['name']),strings(m['description'])
    if len(names)!=len(desc):raise ValueError('Name/description cardinality mismatch')
    return [{'name':n,'description':d,'unit':'','displayUnit':''} for n,d in zip(names,desc)]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('--csv',type=Path);a=p.parse_args()
    try:rows=read_xml(a.source) if a.source.suffix.lower()=='.xml' else read_mat(a.source)
    except Exception as e:p.error(str(e))
    if a.csv:
        if a.csv.exists():p.error('Refusing to overwrite CSV')
        a.csv.parent.mkdir(parents=True,exist_ok=True)
        with a.csv.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=['name','description','unit','displayUnit']);w.writeheader();w.writerows(rows)
    print(json.dumps({'variables':len(rows),'withDescription':sum(bool(r['description']) for r in rows),'source':str(a.source),'scope':'Metadata inspected; values and UI rendering not tested.','rows':rows if not a.csv else None},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
