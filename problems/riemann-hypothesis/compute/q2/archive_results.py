#!/usr/bin/env python3
"""Validate completed runs, then retain their complete compressed evidence.

The shared lock keeps compression/assembly behind the numerical computation.
Only a successful complete set of runs can create the certificate directory.
"""
import argparse
import fcntl
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

def sha(path):
    with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('upstream','finite','independent','analytic','output'):
        p.add_argument(name,type=Path)
    p.add_argument('--lock',type=Path,required=True)
    p.add_argument('--small-checks',type=Path,required=True)
    p.add_argument('--rejections',type=Path,required=True)
    args=p.parse_args();here=Path(__file__).resolve().parent
    with args.lock.open('a') as lock:
        print('Waiting for the one-heavy-job lock before archival assembly',flush=True)
        fcntl.flock(lock,fcntl.LOCK_EX)
        subprocess.run([sys.executable,str(here/'verify_finite.py'),str(args.finite),str(args.independent)],check=True)
        subprocess.run([sys.executable,str(here/'verify_analytic.py'),str(args.upstream),str(args.analytic)],check=True)
        args.output.mkdir(parents=True,exist_ok=False)
        for source,name in ((args.finite,'finite'),(args.independent,'independent')):
            out=args.output/name;out.mkdir()
            for path in sorted(source.iterdir()):
                if path.suffix=='.json': shutil.copyfile(path,out/path.name)
                if path.suffix=='.txt':
                    with path.open('rb') as src,(out/(path.name+'.gz')).open('wb') as dst:
                        with gzip.GzipFile(fileobj=dst,mode='wb',filename='',mtime=0,compresslevel=9) as zipped:
                            shutil.copyfileobj(src,zipped,1024*1024)
        for path in sorted(args.analytic.rglob('*')):
            if path.is_file() and path.suffix in ('.txt','.log','.json'):
                dest=args.output/'analytic'/path.relative_to(args.analytic)
                dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest)
        shutil.copyfile(args.small_checks,args.output/'small-checks.txt')
        shutil.copyfile(args.rejections,args.output/'rejections.txt')
        subprocess.run([sys.executable,str(here/'verify_finite.py'),str(args.finite),str(args.independent),
                        '--summary',str(args.output/'finite-summary.json')],check=True)
        subprocess.run([sys.executable,str(here/'verify_analytic.py'),str(args.upstream),str(args.analytic),
                        '--summary',str(args.output/'analytic-summary.json')],check=True)
        source_names=['vendor/finite_original.c','direct.rs','interpolate.rs','ball.rs','arb_bridge.c']
        files={str(p.relative_to(args.output)):sha(p) for p in sorted(args.output.rglob('*')) if p.is_file()}
        record={'schema':'riemann-q2-complete-v1','claim':'Lambda <= 893927/5000000 < 1/5',
                'date':'2026-09-08','model':'GPT-6 Astra',
                'upstream_pin':'a74738deb6d5e0f76887cb36901da08b68dca705',
                'files':files,'sources':{name:sha(here/name) for name in source_names},
                'scope':'Complete fresh outputs of two finite implementations and the analytic numerical lanes. '
                        'The analytic implication is reviewed in ANALYTIC_REVIEW.md; see NOTE.md for independence boundaries.'}
        (args.output/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
        subprocess.run([sys.executable,str(here/'check_certificate.py'),str(args.upstream),str(args.output)],check=True)
        print('COMPLETE CERTIFICATE ARCHIVED AND CHECKED',flush=True)

if __name__=='__main__': main()
