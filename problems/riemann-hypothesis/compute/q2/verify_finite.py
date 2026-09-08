#!/usr/bin/env python3
"""Stream-check complete outputs of both finite implementations.

This is a transcript check. run_all.sh first regenerates both streams.
Reading successful old logs alone is not a fresh numerical verification.
"""
import argparse
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import re
from regenerate import SEGMENTS, SOURCE_SHA
from run_independent import LEGS

ERROR=Fraction(233494905212337849,10**24)

def require(ok,message):
    if not ok: raise ValueError(message)

def digest(path):
    with (gzip.open(path.with_suffix(path.suffix+'.gz'),'rb')
          if not path.exists() else path.open('rb')) as f:
        return hashlib.file_digest(f,'sha256').hexdigest()

def transcript(path):
    return path.open() if path.exists() else gzip.open(path.with_suffix(path.suffix+'.gz'),'rt')

def c_rows(root):
    manifest=json.loads((root/'progress.json').read_text())
    require(manifest['source_sha256']==SOURCE_SHA,'C source pin')
    require(len(manifest['segments'])==len(SEGMENTS),'C segment count')
    for definition,entry in zip(SEGMENTS,manifest['segments']):
        lo,hi,k,bits,order,width=definition
        require((entry['first_N'],entry['last_N'],entry['rows'])==(lo,hi,hi-lo+1),'C manifest coverage')
        require(entry['reused'] is False,'C transcript must come from a fresh run')
        path=root/f'N{lo}-{hi}.txt'
        require(digest(path)==entry['sha256'],'C transcript hash')
        next_n=lo; minimum=10**12; finished=False
        with transcript(path) as f:
            tbox='16125/100000 16125/100000' if k==6 else '161250000/1000000000 161250001/1000000000'
            require(next(f)==f'TBOX {tbox}\n','C time box')
            require(next(f)=='WEIGHT TRIANGLE\n','C weight branch')
            for line in f:
                match=re.fullmatch(r'N (\d+) L12 0\.(\d{12}) GT089 ([01])\n',line)
                if match:
                    n,v=int(match[1]),int(match[2])
                    require(not finished and n==next_n and n<=hi,'C row order')
                    require(Fraction(v,10**12)>ERROR,'C finite positivity')
                    minimum=min(minimum,v); next_n+=1
                    yield n,v
                else:
                    match=re.fullmatch(r'TIMING [0-9.]+ (\d+)\n',line)
                    require(match is not None and not finished,'C unrecognized/extra record')
                    require(int(match[1])==hi-lo+1 and next_n==hi+1,'C completion count')
                    finished=True
        require(finished and minimum==entry['floor_1e12'],'C terminal/minimum')
    require(manifest['rows_regenerated']==3149013,'C total')

def rust_rows(root):
    manifest=json.loads((root/'manifest.json').read_text())
    names=['direct-first']+[f'interpolation-{lo}-{hi}' for lo,hi,_ in LEGS]
    require([r['name'] for r in manifest['runs']]==names,'Rust run list')
    for entry in manifest['runs']:
        require(entry['returncode']==0,'Rust unsuccessful run')
        for suffix,key in [('.txt','stdout_sha256'),('.stderr.txt','stderr_sha256')]:
            require(digest(root/(entry['name']+suffix))==entry[key],'Rust transcript hash')
    for lo,hi,k in LEGS:
        name=f'interpolation-{lo}-{hi}'
        with transcript(root/(name+'.txt')) as f:
            require(next(f)==f'INTERPOLATION first={lo} last={hi} primes={k} nodes=8 bits=192 t=129/800 y2=87677/2500000\n','Rust parameters')
            minimum=10**12; at=lo; next_n=lo; finished=False
            for line in f:
                match=re.fullmatch(r'N (\d+) LOWER12 (-?\d+)\n',line)
                if match:
                    n,v=int(match[1]),int(match[2])
                    require(not finished and n==next_n and n<=hi,'Rust row coverage')
                    require(v>233495 and Fraction(v,10**12)>ERROR,'Rust finite positivity')
                    if v<minimum: minimum,at=v,n
                    next_n+=1
                    yield n,v
                else:
                    match=re.fullmatch(r'COMPLETE rows=(\d+) minimum12=(-?\d+) at=(\d+)\n',line)
                    require(match is not None and not finished,'Rust unrecognized/extra record')
                    require(tuple(map(int,match.groups()))==(hi-lo+1,minimum,at),'Rust terminal summary')
                    require(next_n==hi+1,'Rust incomplete range')
                    finished=True
        require(finished,'Rust missing completion')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original',type=Path);p.add_argument('independent',type=Path)
    p.add_argument('--summary',type=Path)
    args=p.parse_args()
    c=iter(c_rows(args.original));r=iter(rust_rows(args.independent))
    cmin=rmin=10**12; rc=rr=0; count=0
    for n in range(690988,3840001):
        cn,cv=next(c);rn,rv=next(r)
        require(cn==rn==n,'implementation coverage agreement')
        if cv<cmin: cmin,rc=cv,n
        if rv<rmin: rmin,rr=rv,n
        count+=1
    require(next(c,None) is None and next(r,None) is None,'extra finite rows')
    require(cmin==791366 and rc==690988,'original global floor')
    report={'rows_per_implementation':count,'first_N':690988,'last_N':3840000,
            'original_minimum12':cmin,'original_at':rc,'independent_minimum12':rmin,
            'independent_at':rr,'uniform_error_upper':str(ERROR),
            'original_margin_lower':str(Fraction(cmin,10**12)-ERROR),
            'independent_margin_lower':str(Fraction(rmin,10**12)-ERROR)}
    if args.summary: args.summary.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    print('PASS: two complete finite implementations; analytic assembly is separate')

if __name__=='__main__': main()
