# Line KK — Gasull–Santana +1 on the radial cubic

Status: two-cycle dent dropped. Kept: the translated cubic, the
explicit degree-4 product, and the exact miss of the line past
the translated circle. Not a dent of `H(4)`.

Imagined certificate. Apply the Gasull–Santana construction
`H(n+1) ≥ H(n)+1` to the radial cubic of q1 line D
(`ρ² = 1/4`). The result is an explicit degree-4 field with two
hyperbolic isolated periodic orbits: the translated circle, plus
a Hopf cycle from the new monodromic point. A constructive `+1`,
and in particular `H(4) ≥ 2`.

Drop immediately. The second cycle is a Hopf they do not write
term-by-term. This line does not invent a numeric `(ε, δ)`
perturbation and call it two cycles. One explicit hyperbolic
circle in degree 4, or even two, does not beat Prohens–Torregrosa
`H(4) ≥ 28`.

Fork kept. The finite algebra of their Theorem 1, specialised to
this cubic: translate the regular point `(2, 0)` to the origin,
multiply by the line `4x − 15y`, prove that line misses the
translated circle, and read the Jacobian identities off the
product. The `n+2` field `(x²+y²)X` on the untranslated cubic is
degree 5 and has the same unique circle; it is not a `+1`.
Symbolic only. Fractions as strings. No ODE integration. Not a
bound on `H(n)`.

Replay:

```bash
problems/hilbert16-limit-cycles/compute/q3/kk-plus-one/run.sh
```

Python expands the translated field and the degree-4 product over
`Q`. Rust expands the content-cleared integer field with a
`BTreeMap` and evaluates the residuals on the integer box from
`−3` to `3`. The two dumps are `diff`ed. Exit 0. Certs:
`certs/core.json`, `certs/identities.json`.

Opened this session:
[arXiv:2407.13465v2](https://arxiv.org/abs/2407.13465) and its
[HTML](https://arxiv.org/html/2407.13465v2) (Theorem 1 and its
proof; Lemma 1; the `n+2` remark in §4). Same two theorems as
PAMS 153 (2025) 669–677. The introduction still records
`H(4) ≥ 28`.

## Dropped — two hyperbolic cycles, hence H(4) at least 2

The fiction needs an explicit degree-4 field with two hyperbolic
isolated periodic orbits, offered as a constructive `+1` and as
a dent of `H(4) ≥ 28`.

Theorem 1 of Gasull–Santana is an existence argument, not a
term-by-term field. After the product they unfold

$$R_{\varepsilon}=(ax+(b+\varepsilon)y)P,\qquad
S_{\delta}=((a+\delta)x+by)Q,$$

choose small `ε, δ` so the origin is an isolated monodromic
singularity with `L₁ ≠ 0`, and perturb once more to birth a
Hopf cycle. None of those perturbations is written here. A
numeric integrator is not a certificate. Two cycles would not
beat 28 in any case.

The product field below has one proved periodic orbit: the
translated circle. The origin of that product is a non-isolated
equilibrium on a line of singularities, not a focus.

## Kept — translate (2, 0), then multiply

The radial cubic of q1 line D, with `ρ² = 1/4`, is

$$\dot x=y-x\bigl(x^2+y^2-\tfrac14\bigr),\qquad
\dot y=-x-y\bigl(x^2+y^2-\tfrac14\bigr).$$

The unique periodic orbit is the circle of radius `1/2`. Polar
form `ṙ = r(ρ² − r²)`, `θ̇ = −1`. The origin is an equilibrium,
so the Gasull–Santana multipliers `a = −Q(0, 0)`,
`b = P(0, 0)` both vanish. Multiplying the untranslated field
by a line through the origin is not their construction: every
such line meets the circle, because the distance from `(0, 0)`
to the line is `0 < 1/2`.

Take the regular point `p = (2, 0)`, outside any closed ball
that contains the circle in its interior. Then

$$P(2,0)=-2\bigl(4-\tfrac14\bigr)=-\tfrac{15}{2},\qquad
Q(2,0)=-2.$$

Translate `p` to the origin: `P_t(x, y) = P(x+2, y)` and
`Q_t(x, y) = Q(x+2, y)`. Expanding over `Q` with `ρ² = 1/4`
gives

$$\begin{aligned}
P_t&=-x^3-xy^2-6x^2-2y^2+y-\tfrac{47}{4}x-\tfrac{15}{2},\\
Q_t&=-x^2y-y^3-4xy-x-\tfrac{15}{4}y-2.
\end{aligned}$$

In particular `P_t(0, 0) = −15/2` and `Q_t(0, 0) = −2`. The
Gasull–Santana line is `ax + by` with

$$a=-Q_t(0,0)=2,\qquad b=P_t(0,0)=-\tfrac{15}{2},$$

so `2x − (15/2)y`. Clear content by doubling: `L = 4x − 15y`.
The degree-4 field is

$$R=L\,P_t,\qquad S=L\,Q_t.$$

(Equivalently work with `(2R, 2S)`, or with the integer field
`(L · 4P_t, L · 4Q_t)`.) Thirteen plus ten monomials; leading
term of `R` is `−4x⁴`. The whole line `L = 0` is a line of
singularities. The origin is a non-isolated equilibrium.

## Kept — the line misses the translated circle

The translated circle is `(x+2)² + y² = 1/4`: centre `(-2, 0)`,
radius `1/2`. Distance from the centre to `4x − 15y = 0` is

$$\frac{|4(-2)|}{\sqrt{16+225}}=\frac{8}{\sqrt{241}}.$$

The line misses the circle if and only if that distance exceeds
the radius:

$$\frac{8}{\sqrt{241}}>\frac12\iff 16>\sqrt{241}\iff 256>241
\iff 15>0.$$

Cleared comparison, integers only: `4 · 8² − 241 = 15 > 0`.
The same miss as a quadratic: substituting `y = 4x/15` into the
circle and clearing produces

$$964x^2+3600x+3375=0,$$

discriminant `3600² − 4 · 964 · 3375 = −54000 < 0`. No real
intersection.

On the circle, `L ≠ 0`. Sample values: `L(-2, 0) = −8` at the
centre, `L(-3/2, 0) = −6` at the rightmost point. The circle is
connected and does not meet the line, so `L` has constant sign
on it (negative).

## Kept — the translated circle remains a periodic orbit

The original polar identity, after translation, is

$$(x+2)P_t+yQ_t=\bigl((x+2)^2+y^2\bigr)
\bigl(\tfrac14-(x+2)^2-y^2\bigr).$$

The right-hand side vanishes on the translated circle, so that
circle is invariant for `(P_t, Q_t)`. Off the origin of the
original field the angular identity is `θ̇ = −1 ≠ 0`, so the
orbit is periodic. Because `L ≠ 0` on the circle, `(R, S)` is a
nowhere-zero time rescaling of `(P_t, Q_t)` along that orbit.
The translated circle is therefore a periodic orbit of the
degree-4 field. Time is reversed (`L < 0`), so the attracting
circle of the cubic becomes repelling; it stays hyperbolic.
One cycle. Not two.

## Kept — Jacobian identities at the origin

Write `X = (R, S) = (L P_t, L Q_t)`. At the origin `L = 0`, so

$$DX(0,0)=\begin{pmatrix}L_x P_t&L_y P_t\\ L_x Q_t&L_y Q_t\end{pmatrix}
=\begin{pmatrix}-30&225/2\\ -8&30\end{pmatrix}.$$

Determinant `0`, trace `0`. Their display, for the uncleared
line `ax + by`, is

$$DX(0,0)=\begin{pmatrix}ab&b^2\\ -a^2&-ab\end{pmatrix}
=\begin{pmatrix}-15&225/4\\ -4&15\end{pmatrix},$$

again determinant `0` and trace `0`. The doubled line multiplies
that matrix by `2`; the two vanishing identities are unchanged.

## Kept — n+2 on the untranslated cubic

Section 4 of the paper notes that `H(n+2) ≥ H(n)+1` is easier:
`Y = (x² + y²) X` is degree `n+2` and agrees with `X` off the
origin. On the untranslated radial cubic this is degree 5. The
polar identities become

$$r\,\dot r=r^4(\rho^2-r^2),\qquad r^2\dot\theta=-r^4,$$

so `ṙ = r³(ρ² − r²)` and `θ̇ = −r²`. The only positive root of
`ṙ = 0` is still `r = ρ`. Same unique circle. The origin is an
extra degenerate equilibrium. No new cycle is written. This is
not a `+1` in degree 4, and it is not a dent of `H(5) ≥ 37`.

## What this is not

Not a bound on `H(n)`. Not a dent. Not two hyperbolic cycles.
Not an explicit Hopf perturbation. Not `H(4) ≥ 2` as a published
improvement. The reusable lemma is the explicit product and the
miss: a stranger can run `run.sh` and read `4x − 15y` and
`4 · 8² − 241 = 15` off the dump.
