#!/usr/bin/env python3
"""Finite regression checks against a dictionary-built direct convolution.

This checks implementation errors, not the Lambda inequality.
Requires python-flint and the independently compiled interpolation binary.
"""
import re
import subprocess
import sys
from flint import arb, ctx

ctx.prec=192
t=arb(129)/800
y=(arb(87677)/2500000).sqrt()

def direct(n,k):
    ds=[(1,arb(1))]
    for p in (2,3,5,7,11)[:k]:
        bp=(t*arb(p).log()**2/4).exp()
        ds += [(d*p,-lam*bp) for d,lam in ds[:]]
    # Generate pairs (d,m), then collect them by their product. This is
    # independent of the Rust merge and of its incremental update.
    a={}; b={}
    for d,lam in ds:
        for m in range(1,n+1):
            h=(t*arb(m).log()**2/4).exp()
            b[d*m]=b.get(d*m,arb(0))+lam*h
            a[d*m]=a.get(d*m,arb(0))+lam*h*(y*arb(m).log()).exp()
    q=arb(n*n)-t/16
    x=4*arb.pi()*q
    inner=1-3*y+4*y*(1+y)/x**2
    sigma=(1+y)/2+t*q.log()/4-t*inner.max(arb(0))/(2*x*x)
    gamma=(y*(arb(1)/50-q.log()/2)).exp()
    rho=t*y/(2*(x-6))
    mass=sum((abs(b[j])+gamma*abs(a[j]))*(-sigma*arb(j).log()).exp()
             for j in b if j!=1)
    norm=sum(abs(lam)*(-sigma*arb(d).log()).exp() for d,lam in ds)
    correction=gamma*sum((t*arb(m).log()**2/4).exp()
         *(rho*arb(m).log()).expm1()*((y-sigma)*arb(m).log()).exp()
         for m in range(2,n+1))
    return (1-gamma-mass)/norm-correction

for k in (2,3,4,5):
    result=subprocess.run([sys.argv[1],'6','30',str(k),'8','192'],
                           check=True,capture_output=True,text=True)
    rows=[(int(n),int(v)) for n,v in re.findall(r'^N (\d+) LOWER12 (-?\d+)$',result.stdout,re.M)]
    if [n for n,_ in rows]!=list(range(6,31)):
        raise SystemExit('FAIL small-case coverage')
    for n,v in rows:
        expected=direct(n,k)
        lower=arb(v)/10**12
        if not (lower < expected and expected-lower < arb('0.0001')):
            raise SystemExit(f'FAIL direct/interpolation comparison at N={n}, primes={k}: {expected}, {lower}')
    print(f'PASS dictionary direct sums vs interpolation: primes={k}, N=6..30')
print('PASS 100 independent finite regression cases; this is not a Lambda certificate')
