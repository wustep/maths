# Line C — Chebyshev replication

Status: kept as a replay. Hilbert numbers are not moved.

The identity

$$H(nm+m-1)\ge m^2 H(n)\qquad(m\ge 2)$$

replays from the separable pullback in Eshkobilov–Kadyrov–Mamayusupov, arXiv:2604.12883v1. Write Tm for the Chebyshev polynomial of the first kind. On each of the m monotone full branches of Tm on (−1,1) the map Φ(u,v)=(Tm(u),Tm(v)) is a diffeomorphism onto (−1,1)², and the field

$$\dot u=T_m'(v)\,P(T_m(u),T_m(v)),\qquad\dot v=T_m'(u)\,Q(T_m(u),T_m(v))$$

satisfies DΦ·Y = λ X∘Φ with λ = Tm'(u) Tm'(v) nonzero on those rectangles. Degree is exact:

$$\deg Y = nm+(m-1).$$

That is their Theorem 1, checked here by integer Tm, the Pell identity

$$m^2 T_m(t)^2+(1-t^2)\bigl(T_m'(t)\bigr)^2=m^2,$$

Sturm counts of Tm' on (−1,1) for m=2 through 16, symbolic conjugacy, and the degree formula on monomial samples.

The missed-factorization half is dropped. Exhaustive one-step lifts N+1=m(n+1) for N≤50, using only the Appendix A seeds (Prohens–Torregrosa 2019 Theorem 1 and Corollary 2(a); Han–Li 2012 Theorem 1.2(i) as quoted there), match Table 1 and Table 2 exactly. In particular

$$
H(14)\ge 9\cdot 28=252\quad(n,m)=(4,3),\qquad
H(29)\ge 9\cdot 120=1080\quad(9,3),
$$
$$
H(31)\ge 4\cdot 345=1380\quad(15,2),\qquad
H(39)\ge 4\cdot 503=2012\quad(19,2)
$$

are already on that arXiv. No other factorization of those four N, with the same seeds, beats those four numbers. Adding H(2)≥4, H(3)≥13, and the extra Han–Li Table 1 rows still does not beat them. Do not cite 252, 1080, 1380, or 2012 as a bound found here.

The Section 6 half is kept. For ρ²=1/4 the cubic

$$\dot x=y-x(x^2+y^2-1/4),\qquad\dot y=-x-y(x^2+y^2-1/4)$$

has the hyperbolic circle r=1/2, because rdot = r(1/4−r²) and f'(1/2)=−1/2≠0. Its T3-pullback is an explicit degree-11 field. The derivative T3' equals 3(2t−1)(2t+1) and has no zero in I1=(1/2,1), I2=(−1/2,1/2), or I3=(−1,−1/2). Φ is a diffeomorphism on each of the nine open rectangles. The circle sits in [−1/2,1/2]², compactly inside (−1,1)², so each rectangle contains exactly one compact oval of

$$T_3(u)^2+T_3(v)^2=1/4.$$

The degree-6 curve does not split into nine factors over Q. This gives H(11)≥9, which does not beat Han–Li 153. The strongest one-step lift at degree 11 is 4·37=148, as the paper says.

Table 1 is not a complete N≤50 list. The same seeds also give one-step values at N that the paper did not print, for example LCh(9)=112, LCh(32)=1278, LCh(41)=2036, LCh(44)=2400, LCh(47)=3105, LCh(49)=3000. Those are lifts, not independent Hilbert numbers, and they are not a dent of 252/1080/1380/2012.

Replay:

```
sh problems/hilbert16-limit-cycles/compute/q1/c-chebyshev/run.sh
```
