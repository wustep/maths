# Line PP — Christopher–Lloyd four-fold

Status: table beat dropped. Construction kept. Four hyperbolic
cycles in degree 7 give H(7) ≥ 4, which is not a dent of
Prohens–Torregrosa H(7) ≥ 74.

Imagined: the map (x, y) ↦ (u², v²) produces 4 sheets at
N = 2n+1, and applied to a translated radial cubic gives an
explicit degree-7 field with 4 hyperbolic cycles that beats a
published H(7).

Dropped: four cycles do not beat 74. The inequality H(7) ≥ 4
is true for this field and is not a table improvement.

Kept: the 4-fold that Christopher–Lloyd and Gasull–Santana
(arXiv:2407.13465v2, §4) describe. Same degree budget as
Chebyshev T2. An explicit field, written term by term.

Replay:

```bash
problems/hilbert16-limit-cycles/compute/q3/pp-christopher-lloyd/run.sh
```

Python expands the time-rescale field over Q; rustc expands
it again with a BTreeMap of monomials. The two dumps are
`diff`ed. Exit 0.

Opened this session:
[Gasull–Santana, arXiv:2407.13465v2](https://arxiv.org/abs/2407.13465)
and its [HTML](https://arxiv.org/html/2407.13465v2) (§4: translate
into the first quadrant, then (x, y) ↦ (u², v²) with
dt/dτ = 2uv);
[Eshkobilov–Kadyrov–Mamayusupov, arXiv:2604.12883v1](https://arxiv.org/abs/2604.12883)
and its [HTML](https://arxiv.org/html/2604.12883v1) (Theorem 1,
T2 degree N = 2n+1, §6 radial cubic);
[Novaes–Pereira, arXiv:2212.12006v2](https://arxiv.org/abs/2212.12006)
HTML, quoting Prohens–Torregrosa H(7) ≥ 74.

## Dropped — four cycles beat a published H(7)

The fiction needs H(7) ≥ 4 to improve a published row. The
published row is 74 (Prohens–Torregrosa, Nonlinearity 32,
2019, as quoted by 2212.12006). Four is smaller than 74.
This line does not move H(7). It does not claim 252, 1080,
1380, or 2012.

## Kept — translated radial cubic, then (u², v²)

Start from the radial cubic of q1 §6 / 2604.12883 §6, with
ρ² = 1/4:

$$\dot X=Y-X(X^2+Y^2-\rho^2),\qquad
\dot Y=-X-Y(X^2+Y^2-\rho^2).$$

In polar coordinates, ṙ = r(ρ² − r²) and θ̇ = −1. The circle
X² + Y² = ρ² is the unique nontrivial zero of ṙ. It is
hyperbolic: f(r) = r(ρ² − r²) has f'(ρ) = −2ρ² = −1/2 ≠ 0.

That circle is centred at the origin, so it meets both axes.
The map (u, v) ↦ (u², v²) is singular on the axes (Jacobian
4uv). Translate so the circle sits in the open first
quadrant: X = x − 2, Y = y − 2. Then

$$P(x,y)=P_0(x-2,y-2),\qquad Q(x,y)=Q_0(x-2,y-2),$$

and the circle is (x − 2)² + (y − 2)² = 1/4, hence
x, y ∈ [3/2, 5/2] ⊂ (0, ∞). Expanded,

$$\begin{aligned}
P&=-x^3+6x^2-xy^2+4xy-\tfrac{63}{4}x+2y^2-7y+\tfrac{27}{2},\\
Q&=-x^2y+2x^2+4xy-9x-y^3+6y^2-\tfrac{63}{4}y+\tfrac{35}{2}.
\end{aligned}$$

The Christopher–Lloyd field is the time rescale dt/dτ = 2uv
of the composition, not the Remark 4 adjunction:

$$\dot u=v\,P(u^2,v^2),\qquad\dot v=u\,Q(u^2,v^2).$$

Write Φ = (u², v²). Then DΦ · Y = 2uv (X ∘ Φ). The
Remark 4 adjunction is twice this field and is a different
polynomial:

$$Y_{\mathrm{adj}}=\operatorname{adj}(D\Phi)(X\circ\Phi)
=(2v\,P(\Phi),\,2u\,Q(\Phi)),\qquad
D\Phi\cdot Y_{\mathrm{adj}}=4uv\,(X\circ\Phi).$$

Same orbits, same degree. The certificates expand both and
record that they are not equal as polynomials.

If deg(P, Q) = n then deg Y = 2n+1. For this cubic, n = 3
and the degree is exactly 7. Eight monomials in Yu, eight in
Yv:

$$\begin{aligned}
\dot u&=-u^6v-u^2v^5+6u^4v+4u^2v^3+2v^5-\tfrac{63}{4}u^2v-7v^3+\tfrac{27}{2}v,\\
\dot v&=-u^5v^2-uv^6+2u^5+4u^3v^2+6uv^4-9u^3-\tfrac{63}{4}uv^2+\tfrac{35}{2}u.
\end{aligned}$$

Leading parts −u²v(u⁴ + v⁴) and −uv²(u⁴ + v⁴). Multiplying
by 4 clears the denominators and stays in Z[u, v].

## Kept — four ovals, one per open quadrant

The map (u, v) ↦ (u², v²) sends each open quadrant
diffeomorphically onto the open first quadrant. The Jacobian
is 4uv, nonzero off the axes. A first-quadrant point has
exactly four real preimages, one in each open quadrant: the
four sign combinations of (±√a, ±√b). That is m² = 4, the
Bézout ceiling for a degree-2 map. Holomorphic squaring
z ↦ z² is only 2-to-1: Cauchy–Riemann ties the signs.

The translated circle therefore lifts to exactly four ovals

$$(u^2-2)^2+(v^2-2)^2=\tfrac14,\qquad uv\neq 0.$$

On that curve, u², v² ∈ [3/2, 5/2], so |u|, |v| ≥ √(3/2) > 0
and uv ≠ 0 everywhere on the set. The four sign pairs are
four disjoint compact components. Sample points
(±√(5/2), ±√2) (all four sign combinations) lie on the curve,
have Jacobian 4uv ≠ 0, and have Y ≠ 0.

The oval is invariant: if
G = (u² − 2)² + (v² − 2)² − 1/4, then

$$dG/d\tau+4uv\,G\bigl(G+\tfrac14\bigr)=0$$

as a polynomial, so dG/dτ vanishes on G = 0. Hyperbolicity
passes to the lifts because the original characteristic
number f'(ρ) = −1/2 ≠ 0 and the time rescale 2uv is nonzero
and of constant sign on each open quadrant.

So this explicit degree-7 field has four hyperbolic isolated
periodic orbits. Hence H(7) ≥ 4. That is not a dent of 74.

## Kept — same N as T2; four sheets beat linear, match m²

Separable T2(t) = 2t² − 1 of the *untranslated* radial cubic
is the Chebyshev case m = 2 of Theorem 1 in 2604.12883:

$$\dot u=T_2'(v)\,P_0(T_2(u),T_2(v)),\qquad
\dot v=T_2'(u)\,Q_0(T_2(u),T_2(v)).$$

Degree N = n·2 + 2 − 1 = 2n+1, same budget. For n = 3 the
T2 field is also exact degree 7, also eight plus eight
monomials, and also 4 sheets: T2' = 4t vanishes only at 0,
so two full branches on (−1, 0) and (0, 1), and the circle
X² + Y² = 1/4 sits in [−1/2, 1/2]² ⋐ (−1, 1)². T2(t) = 1/2
has two real roots ±√(3/4) with T2' ≠ 0.

(u², v²) also attains 4 at this N. Neither beats m² = 4.
Linear growth would be (N+1)/(n+1) = 2, because
N = 2n+1. This map attains 4 > 2. That is the difference
from holomorphic z ↦ z², which is 2-to-1 and only linear
(q2 line O). The square (u², v²) is separable: each
coordinate is 2-to-1 on R \ {0}, and the four sign
combinations are four preimages of a first-quadrant point.

| n | N | CL sheets | (N+1)/(n+1) | Bézout 4 | T2 sheets |
|---|---|-----------|-------------|----------|-----------|
| 1 | 3 | 4 | 2 | 4 | 4 |
| 2 | 5 | 4 | 2 | 4 | 4 |
| 3 | 7 | 4 | 2 | 4 | 4 |

The n = 1, 2 rows are the same identity on the linear centre
(y, −x) and the sample (x² + y, y² + x): CL degrees 3 and 5,
T2 degrees 3 and 5.

Without the translation the untranslated circle meets the
axes, the preimages sit on uv = 0, and the 4-fold is
singular. The shift by 2 is the Gasull–Santana §4 step, not
decoration.

## Certificates

All checks are in `certs/` and in the dump that `run.sh`
diffs.

1. Time-rescale identity DΦ · Y = 2uv (X ∘ Φ) on the
   translated radial cubic, the linear centre, and the
   sample quadratic. Residuals are the zero polynomial.
   The adjunction is twice this field and is a different
   polynomial; its identity uses 4uv rather than 2uv.
2. Degrees exactly 3, 5, 7 for n = 1, 2, 3. T2 of the same
   three untranslated fields matches those degrees. Translated
   radial Yu, Yv have 8 monomials each; leading parts as
   above. Oval residual is the zero polynomial.
3. Regular real preimages of (5/2, 2) and of (1/2, 1/2)
   under (u², v²): 4, attaining m². Holomorphic square of
   (1/2, 0): 2. T2 × T2 of (1/2, 1/2): 4. Four sample points
   on the oval, one per open quadrant.
4. Arithmetic, n = 1, 2, 3: N = 2n+1, sheets 4 > 2 =
   (N+1)/(n+1), sheets = T2 = Bézout 4. H(7) ≥ 4 does not
   beat 74.

## What this is not

Not a dent of H(7) ≥ 74. Not a new seed for the Chebyshev
table. Not the Remark 4 adjunction (that field is twice
this one). Even four hyperbolic cycles in degree 7 lose to
the published row and do not improve T2 at the same N.
Do not cite 252, 1080, 1380, or 2012 as found here.
