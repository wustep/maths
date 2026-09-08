#!/usr/bin/env python3
"""Verify the retained complete certificate without rerunning its arithmetic.

Hashes establish which evidence is being read, not the mathematical result.
Both entire finite streams and all barrier inequalities are checked below.
Pass a new output directory to run_all.sh for full arithmetic regeneration.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('upstream',type=Path);p.add_argument('certificate',type=Path)
    args=p.parse_args(); cert=args.certificate.resolve(); here=Path(__file__).resolve().parent
    manifest=json.loads((cert/'manifest.json').read_text())
    if manifest.get('claim')!='Lambda <= 893927/5000000 < 1/5':
        raise SystemExit('FAIL: certificate target')
    actual={str(path.relative_to(cert)) for path in cert.rglob('*') if path.is_file() and path!=cert/'manifest.json'}
    if actual!=set(manifest['files']): raise SystemExit('FAIL: certificate file set')
    for name,expected in manifest['files'].items():
        with (cert/name).open('rb') as stream:
            digest=hashlib.file_digest(stream,'sha256').hexdigest()
        if digest!=expected: raise SystemExit('FAIL: certificate hash '+name)
    for name,expected in manifest['sources'].items():
        with (here/name).open('rb') as stream:
            digest=hashlib.file_digest(stream,'sha256').hexdigest()
        if digest!=expected: raise SystemExit('FAIL: numerical source hash '+name)
    subprocess.run([sys.executable,str(here/'verify_finite.py'),str(cert/'finite'),str(cert/'independent')],check=True)
    subprocess.run([sys.executable,str(here/'verify_analytic.py'),str(args.upstream),str(cert/'analytic')],check=True)
    print('PASS: retained complete certificate; arithmetic regeneration is the two-argument mode')

if __name__=='__main__': main()
