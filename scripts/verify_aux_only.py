#!/usr/bin/env python3
"""Compare two source trees; preserve everything except explicitly scoped metadata.
Class/declaration comments and Documentation are ignored. All other annotations,
ordinary string constants, units, bindings, connectors and equations stay protected.
An explicit flag additionally exempts ONLY connect annotation Line.color.
Icon/Diagram graphics, route points, widths and all other metadata stay protected.
This is a fail-closed lexical comparison, NOT a Modelica compiler proof.
"""
from pathlib import Path
import argparse,hashlib,json,sys
from modelica_support import Source
from connection_colors import canonical_with_connection_colors

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def compare(before:Path,after:Path,allow:list[str],root_version=False, connection_colors=False)->dict:
    if not before.is_dir() or not after.is_dir():raise ValueError('Both source roots must be directories')
    a={p.relative_to(before).as_posix():p for p in before.rglob('*') if p.is_file()};b={p.relative_to(after).as_posix():p for p in after.rglob('*') if p.is_file()}
    rows=[];errors=[]
    for name in sorted(a.keys()|b.keys()):
        if name not in a or name not in b:
            status='ALLOWED_AUXILIARY_FILE' if name in allow and not name.endswith('.mo') else 'CHANGED_FILE_SET'
            rows.append({'file':name,'status':status});continue
        if a[name].is_symlink() or b[name].is_symlink():errors.append({'file':name,'error':'SYMLINK_UNSUPPORTED'});continue
        ha,hb=digest(a[name]),digest(b[name])
        if ha==hb:rows.append({'file':name,'status':'BYTE_IDENTICAL','sha256':ha});continue
        if name.endswith('.mo'):
            try:
                sa=Source(a[name].read_text(encoding='utf-8-sig'));sb=Source(b[name].read_text(encoding='utf-8-sig'))
                if sa.unparsed or sb.unparsed:raise ValueError('UNSUPPORTED_SOURCE_SYNTAX')
                ca=canonical_with_connection_colors(sa.text,root_version) if connection_colors else sa.canonical(root_version)
                cb=canonical_with_connection_colors(sb.text,root_version) if connection_colors else sb.canonical(root_version)
                same=ca==cb
                rows.append({'file':name,'status':'AUXILIARY_ONLY' if same else 'PROTECTED_CHANGE','before':ha,'after':hb,'protectedBefore':ca,'protectedAfter':cb})
            except Exception as e:errors.append({'file':name,'error':str(e)})
        else:rows.append({'file':name,'status':'ALLOWED_AUXILIARY_FILE' if name in allow else 'UNAPPROVED_NONMODELICA_CHANGE','before':ha,'after':hb})
    bad=[r for r in rows if r['status'] in ('CHANGED_FILE_SET','PROTECTED_CHANGE','UNAPPROVED_NONMODELICA_CHANGE')]
    has_mo=any(n.endswith('.mo') for n in a)
    return {'status':'STATIC_AUXILIARY_ONLY' if has_mo and not bad and not errors else 'REVIEW_REQUIRED','scope':'Token-level check with explicit exemptions; no compilation or simulation. Whitelisted support files still require manual diff review.','rootVersionExempt':root_version,'connectionLineColorExempt':connection_colors,'allowlist':allow,'files':rows,'errors':errors}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('before',type=Path);p.add_argument('after',type=Path);p.add_argument('--allow-file',action='append',default=[]);p.add_argument('--allowlist',type=Path,help='JSON array of exact relative non-.mo paths');p.add_argument('--allow-root-version',action='store_true');p.add_argument('--allow-connection-colors',action='store_true',help='Exempt ONLY color on Line annotations of actual connect statements');p.add_argument('--output',type=Path);a=p.parse_args()
    allow=a.allow_file+(json.loads(a.allowlist.read_text()) if a.allowlist else [])
    try:r=compare(a.before.resolve(),a.after.resolve(),allow,a.allow_root_version,a.allow_connection_colors)
    except Exception as e:p.error(str(e))
    text=json.dumps(r,ensure_ascii=False,indent=2)
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text,encoding='utf8')
    else:print(text)
    return 0 if r['status']=='STATIC_AUXILIARY_ONLY' else 2
if __name__=='__main__':sys.exit(main())
