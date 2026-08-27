# Line P — Gasull–Santana Harnack recurrence

Status: kept as a replay. Hilbert numbers are not moved.

The imagined claim is dropped. Corollary 2 of Gasull–Santana, arXiv:2510.11705v2,

$$H(n+m)\ge H(n)+\mathrm{Har}(m),\qquad \mathrm{Har}(m)=(m-1)(m-2)/2+[1+(-1)^m]/2,$$

does not beat a published table entry for any N = n+m ≤ 50.

Har(1) through Har(6) are 0, 1, 1, 4, 6, 11. In particular Har(1) = 0, so the recurrence is strictly weaker than the increment H(n+1) ≥ H(n)+1 of their earlier note, arXiv:2407.13465v2.

The replay uses the same seeds as the Chebyshev table in q1: small-n 0, 4, 13; Prohens–Torregrosa 2019 Theorem 1 and Corollary 2(a); Han–Li 2012 Theorem 1.2(i) as quoted in arXiv:2604.12883v1 Appendix A and the extra Table 1 rows; and that paper’s Chebyshev column, included here as published lower bounds already on that arXiv. At each degree the quoted table is the pointwise max. That includes

$$H(14)\ge 252,\qquad H(29)\ge 1080,\qquad H(31)\ge 1380,\qquad H(39)\ge 2012.$$

Do not cite those four as found here.

All 1225 pairs with n ≥ 1, m ≥ 1, and N = n+m ≤ 50 were enumerated. No pair with m ≥ 2 exceeds the quoted number at a recorded N. After closing the quoted seeds under the increment H(k+1) ≥ H(k)+1, no pair exceeds a recorded N either.

The only quoted-table exceedance is the m = 1 pair (n, N) = (17, 18): the lift 384 + 0 sits above the Han–Li seed H(18) ≥ 372. That is not a dent. The increment already gives H(18) ≥ 385, and 384 is the published H(17) from Prohens–Torregrosa Corollary 2(a) and the Chebyshev paper. Har(1) = 0 adds nothing.

The toy check in the idea file is confirmed: H(2)+Har(4) = 4+4 = 8, far below Prohens–Torregrosa H(6) ≥ 53. At the four Chebyshev degrees the best Harnack lifts are 212, 1024, 1081, 1540, all below 252, 1080, 1380, 2012.

Corollary 3 of arXiv:2510.11705v2 prints a Kolmogorov number from the unreplayed degree-4 seed:

$$H_K(5)\ge 28=L_{\mathrm{pub}}(4).$$

That 28 is already on that arXiv. It is not the Section 6 nine-oval field. It does not beat planar H(5) ≥ 37 (different function). Do not cite 28 as found here.

Lifts at degrees with no quoted seed (22, 28, 30, 32–34, 36–38, 40–42, 44–50) are Corollary 2 arithmetic, not independent Hilbert numbers.

Replay:

```
sh problems/hilbert16-limit-cycles/compute/q2/p-harnack-recurrence/run.sh
```
