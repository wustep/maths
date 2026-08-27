# Line O — iterated non-separable pullback

Status: super-quadratic claim dropped. Kept: iterated degree-2
maps still give at most a quadratic number of regular sheets;
complex squaring itself is only linear in the final degree.
H(n) did not move.

Replay:

```bash
problems/hilbert16-limit-cycles/compute/q2/o-iterated-squaring/run.sh
```

Python expands the identities over Q; rustc expands them again
with a BTreeMap of monomials and counts preimages by axis /
quadratic case analysis plus polar iteration. The two dumps are
`diff`ed. Exit 0.

Opened this session:
[arXiv:2604.12883v1](https://arxiv.org/abs/2604.12883) and its
[HTML](https://arxiv.org/html/2604.12883v1) (Theorem 2, Remark 4,
§6 cubic).

## Dropped — super-quadratic from iterated squaring

The imagined certificate was that k-fold pullback by

$$\Phi(u,v)=(u^2-v^2,\,2uv)$$

of the radial cubic of q1 line D / 2604.12883 §6 would produce
more than a quadratic number of hyperbolic cycles in the final
degree, beating Theorem 2 and answering Remark 4 in the
affirmative.

That does not happen. As a real plane map, z ↦ z² is 2-to-1
away from the origin, not 4-to-1. The two components of Φ are
tied by the Cauchy–Riemann equations, so the Bézout number
m² = 4 per degree-2 step is not attained. After k steps the
actual regular-sheet count is 2^k, which is linear in the
degree N = (n+1)2^k − 1.

## Kept — quadratic ceiling; this map is linear

A real polynomial map of degree at most m has at most m²
regular real preimages of any point (Bézout plus regularity;
q1 line E). The Remark 4 pullback

$$Y=\operatorname{adj}(D\Phi)\,(X\circ\Phi)$$

is

$$\dot u=q_v\,P(\Phi)-p_v\,Q(\Phi),\qquad
\dot v=-q_u\,P(\Phi)+p_u\,Q(\Phi),$$

so that DΦ · Y = (det DΦ)(X ∘ Φ). Cofactors have degree at
most m−1 and X ∘ Φ has degree at most n m, hence

$$\deg Y\le nm+(m-1)=(n+1)m-1.$$

One degree-2 step therefore has deg Y ≤ (n+1)·2 − 1 and at
most 4 regular sheets. After k such steps, if each bound is
sharp,

$$N=(n+1)2^k-1,\qquad\text{sheets}\le 4^k=\Bigl(\frac{N+1}{n+1}\Bigr)^2,$$

still quadratic in N. One-step Chebyshev of degree m = 2^k
matches that count at the same N (Theorem 1 of the same paper).
Separable T2(u), T2(v) is already 4-to-1 on (−1,1)².

Complex squaring does not attain the per-step ceiling. Here
det DΦ = 4(u²+v²) = |Φ'|², and a generic point in C ≅ R² has
two regular real preimages. The k-fold iterate is z ↦ z^{2^k},
which has 2^k preimages, not 4^k. When N is exact,

$$2^k=\frac{N+1}{n+1},$$

linear in N. Iteration of this non-separable map does not beat
m² and does not even attain m² per step. That is a negative
answer to Remark 4 for this map: an analogue of Theorem 2 still
holds, and the growth is strictly slower than the separable
ceiling.

## Certificates

All four checks are in `certs/` and in the dump that `run.sh`
diffs.

1. adj identity on Φ = (u²−v², 2uv), for the radial cubic
   with ρ² = 1/4 and for the linear centre (P, Q) = (y, −x).
   Residuals are the zero polynomial. det DΦ = 4(u²+v²).
2. One-step degree for n = 3: bound 7, exact degree 7 on the
   radial cubic (leading terms −2u(u²+v²)³ and −2v(u²+v²)³).
   Linear centre has exact degree 3. Two-step radial pullback
   has exact degree 15, so the iteration bound
   N = (n+1)2^k − 1 is sharp at k = 2. Separable T2 pullback
   of the same cubic is also degree 7.
3. Regular real preimages of (1/2, 0) and of (1/4, 1/4): 2,
   not 4. The same target under Φ² has 4 (the 4th roots of
   1/2 in the plane). T2 × T2 of (1/2, 1/2) has 4, attaining
   m². Polar iteration of z ↦ z^{2^k} on (1/2, 0) gives
   exactly 2^k distinct regular preimages for k = 1..6.
4. Arithmetic, n = 3, k = 1..6:

| k | N | Bézout 4^k | complex 2^k | Chebyshev m=2^k sheets | 4^k / N² | 2^k / N² |
|---|---|------------|-------------|------------------------|----------|----------|
| 1 | 7 | 4 | 2 | 4 | 4/49 | 2/49 |
| 2 | 15 | 16 | 4 | 16 | 16/225 | 4/225 |
| 3 | 31 | 64 | 8 | 64 | 64/961 | 8/961 |
| 4 | 63 | 256 | 16 | 256 | 256/3969 | 16/3969 |
| 5 | 127 | 1024 | 32 | 1024 | 1024/16129 | 32/16129 |
| 6 | 255 | 4096 | 64 | 4096 | 4096/65025 | 64/65025 |

## What this is not

Not a bound on H(n). Not a new seed. Even if each regular
sheet lifted one hyperbolic cycle of the radial cubic, the
count would be 2^k, which is linear in N and does not beat a
published row. Do not cite 252, 1080, 1380, or 2012 as found
here. Theorem 2 of 2604.12883 is not improved; this line only
says that this particular non-separable iteration does not
escape its quadratic (in fact, linear) envelope.
