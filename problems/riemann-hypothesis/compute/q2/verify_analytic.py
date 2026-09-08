#!/usr/bin/env python3
"""Independently assemble fresh analytic transcripts with exact rationals.

This checks the interfaces and every closed-prism inequality. The numerical
enclosures themselves are produced by replay_analytic.py from pinned source;
the mathematical implications are proved/reviewed in ANALYTIC_REVIEW.md.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re
import subprocess

PIN='a74738deb6d5e0f76887cb36901da08b68dca705'
T=F(129,800); Y2=F(87677,2500000); X=6000000185827
ERROR=F(233494905212337849,10**24)
ALLOWANCE=F(1,800)
NUMBER=r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'
BALL=re.compile(r'\[(?:('+NUMBER+r') )?\+/- ('+NUMBER+r')\]')
PRISM=re.compile(r'Prism\((\d+)\) t=\[(.*?),(.*?)\] winding=(.*?) '
                 r'min_mesh=(.*?) Dz=(.*?) Dt=(.*?) spatial=(.*?) '
                 r'time=(.*?) eps=(.*?) margin=(.*?) mesh=(\d+) PASS')

def require(ok,label):
    if not ok: raise ValueError(label)

def ball(s):
    s=s.strip(); m=BALL.fullmatch(s)
    if m:
        center=F(m[1] or '0'); radius=F(m[2])
        require(radius>=0,'negative ball radius')
        return center-radius,center+radius
    require(re.fullmatch(NUMBER,s) is not None,'malformed ball: '+s)
    return F(s),F(s)

def digest(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

def clean(path,terminal):
    value=path.read_text()
    require(value.strip() and terminal in value,'missing analytic result: '+str(path))
    require(not re.search(r'\[FAIL\]|FAIL:|RESULT:.*(?:FAILED|FAIL\b)|Traceback|aborted',value),
            'failed analytic output: '+str(path))
    return value

def quantity(text,label):
    rows=[s[len(label)+3:] for s in text.splitlines() if s.startswith(label+' = ')]
    require(len(rows)==1,'missing/duplicate quantity '+label)
    return ball(rows[0])

def check_barrier(path):
    text=clean(path,'RESULT: CLOSED SLAB CERTIFIED')
    lines=[s for s in text.splitlines() if s.strip()]
    require(len(lines)==891,'barrier record count')
    require(lines[0].startswith('Filling stored sums matrix with '),'matrix header')
    require(lines[1].startswith('Processing the barrier for X= '),'barrier parameters header')
    require('N-corners=690988,690988' in lines[2],'barrier index')
    allowance=ball(lines[2].split('H/B approximation allowance=')[1])
    require(allowance[0]<=ALLOWANCE<=allowance[1] and allowance[1]-allowance[0]<F(1,10**25),
            'barrier allowance')
    previous='0'; least=None; max_winding=F(0)
    for number,line in enumerate(lines[3:886],1):
        m=PRISM.fullmatch(line); require(m is not None,'malformed prism')
        i,start,end,wind,minimum,dz,dt,space,motion,eps,margin,mesh=m.groups()
        require(int(i)==number and start==previous,'closed prism sequence/seam')
        a,b,w,v,z,t,s,d,e,r=map(ball,[start,end,wind,minimum,dz,dt,space,motion,eps,margin])
        require(a[1]<b[0] and v[0]>0 and r[0]>0,'prism sign')
        require(z[0]==z[1]>0 and z[0].denominator==1 and
                t[0]==t[1]>0 and t[0].denominator==1,'derivative integer ceilings')
        count=int(mesh); require(count>=4 and count%4==0,'polygon mesh')
        spatial=z[0]/(2*(count//4))
        time_low=t[0]*(b[0]-a[1]); time_high=t[0]*(b[1]-a[0])
        require(s[0]<=spatial<=s[1],'spatial formula')
        require(d[0]<=time_low<=time_high<=d[1],'time formula')
        require(e==allowance,'constant approximation allowance')
        lower=v[0]-spatial-time_high-e[1]
        require(lower>0,'recomputed prism margin')
        require(r[0]<=v[1]-s[0]-d[0]-e[0] and
                v[0]-s[1]-d[1]-e[1]<=r[1],'printed margin consistency')
        require(-F(1,4)<w[0]<=0<=w[1]<F(1,4),'winding integer zero')
        max_winding=max(max_winding,abs(w[0]),abs(w[1]))
        least=lower if least is None else min(least,lower)
        previous=end
    require(ball(previous)[0]<=T<=ball(previous)[1],'closed terminal time')
    require(lines[886].startswith('Overall winding number: '),'overall winding record')
    require(lines[887].startswith('Rigorous winding interval: '),'aggregate winding record')
    w=ball(lines[887].split(': ',1)[1])
    require(-F(1,4)<w[0]<=0<=w[1]<F(1,4),'aggregate winding integer')
    require(lines[888]=='Closed coverage endpoint: '+previous,'aggregate endpoint')
    require(lines[889]=='RESULT: CLOSED SLAB CERTIFIED' and lines[890].startswith('cpu/wall(s): '),
            'barrier completion')
    return {'prisms':883,'recomputed_margin_lower':str(least),'maximum_winding_absolute':str(max_winding)}

def matrix(path):
    lines=path.read_text().splitlines()
    require(lines[0]=='6000000185827.00000000000000000, 62, 62, 20','matrix dimensions')
    rows=[s for s in lines[1:] if not s.startswith('cpu/wall')]
    require(len(rows)==62,'matrix row count')
    values=[]
    for row in rows:
        fields=row.split(','); require(len(fields)==124,'matrix column count')
        values.extend(map(ball,fields))
    return values

def check_matrix(upstream,out):
    archived=matrix(upstream/'barrier/data/storedsum_nolemma_6000000185827_dig_20.txt')
    fresh=matrix(out/'barrier/storedsum_interval_regenerated.txt')
    for (p,q),(a,b) in zip(archived,fresh):
        require(p==q and a<b,'coefficient type/radius')
        radius=max(F(1),abs(p))/10**20
        require(p-radius<=a<=b<=p+radius,'coefficient serialization containment')
    return len(fresh)

def check_dini(path):
    text=clean(path,'RESULT PASS: direct-Triangle mass is nonincreasing on the full y interval')
    lines=text.splitlines()
    require(len(lines)==6 and lines[0].startswith('ROW t=16125/100000 y2=350708/10000000 '),'Dini row')
    yrange=re.search(r'ybox=\[('+NUMBER+'),('+NUMBER+r')\]',lines[0])
    require(yrange is not None,'Dini height box')
    require(0<F(yrange[1])**2<=Y2 and F(yrange[2])**2>=1-2*T,'Dini outward height coverage')
    expected=[('235711',690988,728999,243),('2357',729000,818999,81),
              ('235',819000,1027999,27),('23',1028000,3840000,9)]
    for line,(primes,lo,hi,patterns) in zip(lines[1:5],expected):
        require(line.startswith(f'PASS P={primes} N={lo}..{hi} patterns={patterns} '),'Dini full range')
        ratio=re.search(r'ratio_ub=('+NUMBER+r') ',line)
        require(ratio is not None and 0<=F(ratio[1])<1,'Dini strict gate')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('upstream',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--summary',type=Path)
    args=p.parse_args(); root=args.upstream; out=args.output
    require(subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()==PIN,'upstream pin')
    require(not subprocess.check_output(['git','-C',str(root),'status','--porcelain','--untracked-files=all'],text=True),
            'upstream checkout must remain clean')
    manifest=json.loads((out/'manifest.json').read_text())
    names=['prop410','tail','compile-dini-180','dini-180',
           'compile-dini-256','dini-256','normalizer-correction','window','tail-python','barrier']
    if manifest['runs'] and manifest['runs'][0]['name']=='stored-review':
        names.insert(0,'stored-review')
    require(manifest['upstream_pin']==PIN and [r['name'] for r in manifest['runs']]==names,'analytic manifest')
    for run in manifest['runs']:
        require(run['returncode']==0 and digest(out/(run['name']+'.txt'))==run['stdout_sha256'],'analytic successful run/hash')
    if names[0]=='stored-review':
        clean(out/'stored-review.txt','RESULT: STORED UNCONDITIONAL-PROOF REVIEW PASS')
    clean(out/'prop410.txt','RESULT: AUTHORITATIVE ARB PROP410 REPLAY PASS')
    clean(out/'tail.txt','RESULT: INDEPENDENT ARB TAIL REPLAY PASS')
    clean(out/'barrier.txt','RESULT: FRESH CLOSED-BARRIER REPLAY PASS')
    clean(out/'normalizer-correction.txt','RESULT ALL PASS precision 256')
    clean(out/'window.txt','RESULT: ALL PASS')
    clean(out/'tail-python.txt','RESULT: ALL PASS')
    for bits in (180,256): check_dini(out/f'dini-{bits}.txt')
    for bits in (256,512):
        prop=clean(out/f'prop410/prop410_arb_{bits}.log','RESULT: ALL ARB PROP410 CHECKS PASS')
        require('TOTAL CHECKS: 31; FAILURES: 0' in prop,'error gates')
        require(quantity(prop,'Emax upper point')[1]<ERROR,'exact finite error')
        require(quantity(prop,'Tmin-Emax lower point')[0]>F(557,10**9),'finite error margin')
        tail=clean(out/f'tail/tail_arb_{bits}.log','RESULT: ALL ARB TAIL CHECKS PASS')
        require('TOTAL CHECKS: 36; FAILURES: 0' in tail,'tail gates')
        require(quantity(tail,'D upper point')[1]<1,'tail contraction')
        require(quantity(tail,'flow-error lower point')[0]>F(17352,10**8),'tail positive margin')
    trunc=clean(out/'barrier/storedsum_taylor_tail.log','Taylor truncation upper = ')
    require(quantity(trunc,'Taylor truncation upper')[1]<F(1,10**20),'factorial Taylor remainder')
    uniform=clean(out/'barrier/uniform_error.log','RESULT: UNIFORM NUMERICAL ERROR-FORMULA BOUND CERTIFIED')
    require(quantity(uniform,'uniform conservative error total upper')[1]<ALLOWANCE,'uniform barrier error')
    report=check_barrier(out/'barrier/barrier_target_closed.log')
    report['regenerated_coefficient_components']=check_matrix(root,out)
    require(T+Y2/2==F(893927,5000000)<F(1,5),'exact target improvement')
    require(0<F(1809,10000)**2<Y2<1-2*T and 0<T<F(1,2),'criterion domain')
    height=3000175332800
    require(height-F(X,2)==F(350479773,2)>0,'published height coverage')
    report.update({'target':str(T+Y2/2),'prior_record':'1/5',
                   'published_height':height,'height_surplus':str(height-F(X,2))})
    if args.summary: args.summary.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    print('PASS: analytic transcript interfaces and exact criterion arithmetic')

if __name__=='__main__': main()
