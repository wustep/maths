#!/usr/bin/env python3
"""Run the direct anchor and four independent interpolation legs in series."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import time

HERE=Path(__file__).resolve().parent
LEGS=[(690988,728999,5),(729000,818999,4),
      (819000,1027999,3),(1028000,3840000,2)]

def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('build',type=Path); p.add_argument('output',type=Path)
    p.add_argument('--lock',type=Path,required=True)
    args=p.parse_args()
    build=args.build.resolve(); out=args.output.resolve()
    out.mkdir(parents=True,exist_ok=True)
    if (out/'manifest.json').exists():
        raise SystemExit('refusing to overwrite an earlier independent run')
    tasks=[('direct-first',[str(build/'direct'),'690988','5','192'])]
    tasks += [(f'interpolation-{lo}-{hi}',[str(build/'interpolate'),str(lo),str(hi),str(k),'8','192']) for lo,hi,k in LEGS]
    record={'certifies_claim':False,'sources':{n:digest(HERE/n) for n in
            ['direct.rs','interpolate.rs','ball.rs','arb_bridge.c','run_independent.py']},
            'binaries':{n:digest(build/n) for n in ['direct','interpolate']},'runs':[]}
    with args.lock.open('a') as lock:
        print('waiting for the shared heavy-job lock',flush=True)
        fcntl.flock(lock,fcntl.LOCK_EX)
        for name,command in tasks:
            started=time.monotonic()
            print('RUN '+name,flush=True)
            path=out/(name+'.txt'); err=out/(name+'.stderr.txt')
            with path.open('w') as f,err.open('w') as e:
                result=subprocess.run(command,stdout=f,stderr=e,preexec_fn=lambda:os.nice(10))
            entry={'name':name,'command':command,'returncode':result.returncode,
                   'wall_seconds':round(time.monotonic()-started,3),
                   'maxrss_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                   'stdout_sha256':digest(path),'stderr_sha256':digest(err)}
            record['runs'].append(entry)
            (out/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
            print(f"DONE {name}: code={result.returncode} wall={entry['wall_seconds']}s",flush=True)
            if result.returncode:
                raise SystemExit('independent finite verification failed; inspect retained output')
    print('ALL FOUR INDEPENDENT FINITE LEGS COMPLETED; analytic assembly still separate',flush=True)

if __name__=='__main__':
    main()
