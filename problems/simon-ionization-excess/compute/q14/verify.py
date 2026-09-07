#!/usr/bin/env python3
"""Exact rational verifier. No solver, mpmath, numpy, or shared search code.

Checks P positive definite by rational elimination and M-P entrywise
nonnegative. Proves all scalar bounds using rational power comparisons.
"""
import argparse
import json
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def root_upper(x, degree, digits=12):
    """Ceiling of the positive root onto a rational grid; exact bisection."""
    scale = 10**digits
    lo, hi = 0, scale
    while Q(hi, scale)**degree < x:
        hi *= 2
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if Q(mid, scale)**degree < x:
            lo = mid
        else:
            hi = mid
    return Q(hi, scale)


def verify(path):
    data = json.loads(path.read_text())
    n = data['n']
    require(n == 37 and Q(data['phi']) == Q(114,125), 'wrong claim parameters')
    e = list(map(Q, data['edges']))
    require(len(e) == n+1 and e[0] == 1 and e[-1] == 10, 'wrong radial coverage')
    require(all(a < b for a,b in zip(e,e[1:])), 'unordered edges')
    floor = Q(8941,10000)
    require(Q(data['f_floor']) == floor, 'wrong floor')
    # f(t)>=floor follows from min_{t>=0} (t^3-floor*t^2+1-floor).
    require(1-floor-4*floor**3/27 > 0, 'global kernel floor failed')
    h = lambda x: x**3 + 3*x - 2
    left, right = Q(596,1000), Q(5961,10000)
    require(h(left) < 0 < h(right), 'derivative root not bracketed')
    den = data['P_denominator']
    require(isinstance(den,int) and den > 0, 'bad matrix denominator')
    nums = data['P_numerators']
    require(len(nums)==n and all(len(row)==n for row in nums), 'wrong matrix shape')
    require(all(isinstance(x,int) for row in nums for x in row), 'noninteger matrix')
    P = [[Q(x,den) for x in row] for row in nums]
    require(all(P[i][j]==P[j][i] for i in range(n) for j in range(n)), 'asymmetric P')
    # Schur complements: positive pivots certify positive definiteness.
    S = [row[:] for row in P]
    pivots = []
    for k in range(n):
        pivot = S[k][k]
        require(pivot > 0, f'nonpositive pivot {k}')
        pivots.append(pivot)
        for i in range(k+1,n):
            for j in range(i,n):
                S[i][j] -= S[i][k]*S[j][k]/pivot
                S[j][i] = S[i][j]
    c = [a*b for a,b in zip(e,e[1:])]
    d = [(a+b)/2 for a,b in zip(e,e[1:])]
    slack = []
    for i in range(n):
        for j in range(n):
            # Four corners, with a separate overlap test.
            ratios = [min(r,s)/max(r,s) for r in e[i:i+2] for s in e[j:j+2]]
            lo, hi = min(ratios), max(ratios)
            if max(e[i],e[j]) <= min(e[i+1],e[j+1]):
                hi = Q(1)
            if hi <= left:
                t = hi
                f = (1+t**3)/(1+t**2)
            elif lo >= right:
                t = lo
                f = (1+t**3)/(1+t**2)
            else:
                f = floor
            value = (f-Q(114,125))*(c[i]+c[j])/2/d[i]/d[j]-P[i][j]
            require(value >= 0, f'negative residual ({i},{j})')
            slack.append(value)
    ratio = max(b/a for a,b in zip(e,e[1:]))
    tv = (ratio-1)/(ratio+1)
    gamma = Q(114,125)-tv*(1-floor)
    # Use a deliberately rounded-down beta for both final verifiers.
    beta = Q(9087,10000)
    require(gamma > beta and Q(10,11) > beta, 'compact/global split failed')
    b = 1/beta
    require(b < Q(11005,10000) < Q(11006,10000), 'leading improvement failed')
    # HPS (7.34): pi cancels and c^6=4^6/27 * (2*1.456/9)^2.
    c6 = Q(4**6,27)*(Q(2,9)*Q(1456,1000))**2
    C = root_upper(c6,6)
    A = 3*root_upper(Q(3,10),3)
    # A*x^(1/3)/beta^(2/3)+C/(beta*x^(2/3)) has a unique
    # interior minimum; its maximum is at one of these endpoints.
    a_left = A*b + C*root_upper(b,3)
    a_right = A*root_upper(Q(9,4)*b*b,3) + C*root_upper(Q(16,81)*b**3,3)
    a1 = max(a_left,a_right)
    a2 = b/84
    a3 = C/5*root_upper(Q(25,144)*b,3)
    a4 = C/84*root_upper(b,3)
    remainder = a1+a2*root_upper(Q(1,4),3)+a3*root_upper(Q(1,16),3)+a4/4
    require(remainder < Q(3933,1000), 'remainder failed')
    require(Q(5,12)/4 < Q(1,8), 'HPS smoothing radius failed')
    # Replay the closed-form published leading via the derivative root:
    # b(3)=2/(3*t), where t^3+3*t-2=0.
    tlo, thi = Q(2,3)/Q(11185,10000), Q(2,3)/Q(11184,10000)
    require(h(tlo)<0<h(thi), 'published b(3) window failed')
    return {'status':'dent', 'n':n, 'matrix_entries_checked':n*n,
            'beta_lower':'9087/10000', 'compact_gamma_exact':str(gamma),
            'compact_gamma_approx':float(gamma), 'min_pivot_approx':float(min(pivots)),
            'residual_lower':'1/100000',
            'residual_gt_1e-5':min(slack)>Q(1,100000),
            'leading_upper':'1.1005', 'remainder_upper':'3.933',
            'hps_remainder_rational_upper':str(remainder),
            'hps_remainder_approx':float(remainder),
            'inequality':'N_c(Z) < 1.1005 Z + 3.933 Z^(1/3), Z >= 4'}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('certificate',nargs='?',type=Path,default=HERE/'certificate.json')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=verify(args.certificate)
    require(result['residual_gt_1e-5'], 'residual margin too small')
    text=json.dumps(result,indent=2)+'\n'
    if args.output:
        args.output.write_text(text)
    print(text,end='')


if __name__=='__main__':
    main()
