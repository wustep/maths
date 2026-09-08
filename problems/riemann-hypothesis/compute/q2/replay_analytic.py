#!/usr/bin/env python3
"""Fresh, sequential replay of the pinned height/error/tail/barrier lanes.

Numerical lanes are rerun from source, including the full barrier coefficients.
The historical stored assembly is optional: it buffers about 1 GiB and is
redundant with this campaign's streaming finite and analytic assembly checks.
Requires a Python interpreter with the upstream mpmath/sympy dependencies.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

PIN='a74738deb6d5e0f76887cb36901da08b68dca705'

def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('upstream',type=Path); p.add_argument('output',type=Path)
    p.add_argument('--lock',type=Path,required=True)
    p.add_argument('--flint-prefix',type=Path)
    p.add_argument('--stored-review',action='store_true')
    args=p.parse_args(); root=args.upstream.resolve(); out=args.output.resolve()
    if subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()!=PIN:
        raise SystemExit('FAIL: upstream pin')
    out.mkdir(parents=True,exist_ok=True)
    if (out/'manifest.json').exists():
        raise SystemExit('refusing to overwrite a recorded analytic replay')
    env=os.environ.copy(); env['PATH']=str(Path(sys.executable).parent)+os.pathsep+env['PATH']
    env['PYTHONDONTWRITEBYTECODE']='1'
    includes=[]; links=[]
    if args.flint_prefix:
        prefix=args.flint_prefix.resolve(); lib=prefix/'lib/x86_64-linux-gnu'
        if not lib.exists(): lib=prefix/'lib'
        env['FLINT_INCLUDE_DIR']=str(prefix/'include')
        env['FLINT_LIB_DIR']=str(lib)
        env['CPPFLAGS']='-I'+str(prefix/'include/x86_64-linux-gnu')
        # The upstream independent constant checker invokes gcc directly.
        # GCC's standard search variables also cover that unmodified call.
        env['CPATH']=os.pathsep.join(map(str,[prefix/'include',prefix/'include/x86_64-linux-gnu']))
        env['LIBRARY_PATH']=str(lib)
        env['LD_LIBRARY_PATH']=str(lib)
        includes=['-I'+str(prefix/'include'),'-I'+str(prefix/'include/x86_64-linux-gnu')]
        links=['-L'+str(lib),'-Wl,-rpath,'+str(lib)]
    jobs=[('stored-review',['bash',str(root/'verify.sh')])] if args.stored_review else []
    for stem in ['prop410','tail']:
        jobs.append((stem,['bash',str(root/f'scripts/run_{stem}_arb.sh'),str(out/stem)]))
    for bits in (180,256):
        binary=out/f'dini-{bits}'
        jobs += [(f'compile-dini-{bits}',['cc','-O2',f'-DPREC={bits}',*includes,
                   str(root/'verifiers/verify_triangle_y_dini_arb.c'),*links,'-lflint','-lm','-o',str(binary)]),
                 (f'dini-{bits}',[str(binary)])]
    jobs += [('normalizer-correction',[sys.executable,str(root/'verifiers/verify_triangle_normalizer_corr_iv.py'),'--prec','256']),
             ('window',[sys.executable,str(root/'verifiers/verify_window_freeze.py')]),
             ('tail-python',[sys.executable,str(root/'verifiers/verify_tail_1787854_256.py')]),
             ('barrier',['bash',str(root/'scripts/run_barrier_replay.sh'),str(out/'barrier')])]
    record={'claim_certified':False,'upstream_pin':PIN,'runs':[]}
    with args.lock.open('a') as lock:
        print('waiting for shared heavy-job lock',flush=True)
        fcntl.flock(lock,fcntl.LOCK_EX)
        for name,command in jobs:
            print('RUN '+name,flush=True); start=time.monotonic()
            logfile=out/(name+'.txt')
            with logfile.open('w') as log:
                r=subprocess.run(command,cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT,
                                 preexec_fn=lambda:os.nice(10))
            entry={'name':name,'command':command,'returncode':r.returncode,
                   'wall_seconds':round(time.monotonic()-start,3),'stdout_sha256':sha(logfile),
                   'maxrss_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss}
            record['runs'].append(entry)
            (out/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
            print(f"DONE {name}: code={r.returncode} wall={entry['wall_seconds']}s",flush=True)
            if r.returncode:
                raise SystemExit('FAIL: analytic replay; see retained log')
    print('FRESH ANALYTIC LANES COMPLETED; final assembly still required',flush=True)

if __name__=='__main__':
    main()
