#!/usr/bin/env python3
"""Run an explicitly supplied local command with a wall-clock process-tree timeout.
No shell, automatic installation, retries or model alteration. Exit 0 only means
that the command exited 0, not that an engineering/modeling gate passed.
"""
import argparse,json,os,signal,subprocess,sys,time
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cwd',required=True,type=Path);p.add_argument('--timeout',required=True,type=float);p.add_argument('--log',required=True,type=Path);p.add_argument('--metadata',required=True,type=Path);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    cmd=a.command[1:] if a.command and a.command[0]=='--' else a.command
    if not cmd or a.timeout<=0 or not a.cwd.is_dir():p.error('Provide command, existing cwd and positive timeout')
    if a.log.exists() or a.metadata.exists() or a.log.resolve()==a.metadata.resolve():p.error('Use new, distinct log and metadata paths')
    for f in (a.log,a.metadata):f.parent.mkdir(parents=True,exist_ok=True)
    start=time.monotonic();state='ERROR';code=None;error=None
    kw={'start_new_session':True} if os.name!='nt' else {'creationflags':subprocess.CREATE_NEW_PROCESS_GROUP}
    with a.log.open('wb') as log:
        proc=None
        try:
            proc=subprocess.Popen(cmd,cwd=a.cwd,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,**kw)
            code=proc.wait(timeout=a.timeout);state='COMPLETED_PROCESS_ONLY' if code==0 else 'ERROR'
        except (subprocess.TimeoutExpired,KeyboardInterrupt) as exc:
            state='TIMEOUT' if isinstance(exc,subprocess.TimeoutExpired) else 'ABORTED'
            if proc is not None:
                if os.name=='nt':subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],stdout=log,stderr=subprocess.STDOUT,check=False)
                else:
                    try:os.killpg(proc.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                code=proc.wait()
        except Exception as exc:error=str(exc)
    result={'status':state,'command':cmd,'cwd':str(a.cwd.resolve()),'wallSeconds':time.monotonic()-start,'deadlineSeconds':a.timeout,'returnCode':code,'error':error,'engineeringAcceptance':'NOT_EVALUATED'}
    a.metadata.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False))
    return 0 if state=='COMPLETED_PROCESS_ONLY' else 124 if state=='TIMEOUT' else 2
if __name__=='__main__':sys.exit(main())
