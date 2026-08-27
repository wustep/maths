# Line I — Liénard H(2n+1, 5) and the odd cubic family

Status: kept as a replay. Planar `H(n)` did not move. This is
their Liénard number, not a dent of planar `H(n)`.

Imagined: an explicit Liénard field with deg f = 2n+1, deg g = 5
having more than B(n) isolated cycles (Chen–Dai–Kaloshin–Li,
arXiv:2608.17773v1 Theorem 3), or every field
ẋ = y − F(x), ẏ = −x with deg F ≤ 3 having at most one cycle.

Dropped: constructing a field that beats B(n). The origin-plus-lips
compatibility is the paper’s obstruction, not a finite identity.
Dropped: the full deg-F≤3 conjecture. A quadratic term in F kills
oddness (certificate block `even_term`).

Replay:

```bash
problems/hilbert16-limit-cycles/compute/q2/i-lienard/run.sh
```

Python expands the arithmetic and the family identities; Rust
expands them again and evaluates the energy difference on the
integer box from −3 to 3 in each of x, y, α, β. A degree-at-most-4
polynomial in four variables that vanishes on that box is zero.
The two dumps are `diff`ed. Exit 0. Certs:
`certs/arithmetic.json`, `certs/family.json`.

## Kept — Theorem 3 arithmetic, n = 2 through 40

Write N = 2n+1. Their formula, for n ≥ 2, is

$$
B(n)=2n+\Bigl\lfloor\frac{n}{3}\Bigr\rfloor+\Bigl\lfloor\frac{n+1}{3}\Bigr\rfloor-2.
$$

Han–Romanovski, Xiong–Han +2, and Xiong’s cubic-g bound, as
they compare them after substituting N = 2n+1, are

$$
\mathrm{HR}(N)=2\Bigl\lfloor\frac{N-1}{3}\Bigr\rfloor+\Bigl\lfloor\frac{N-1}{2}\Bigr\rfloor,
$$

$$
\mathrm{HR}_2(N)=2\Bigl\lfloor\frac{N-1}{3}\Bigr\rfloor+\Bigl\lfloor\frac{N}{2}\Bigr\rfloor+2,
$$

$$
\mathrm{Xiong}(N)=N+\Bigl\lfloor\frac{N}{4}\Bigr\rfloor.
$$

The last is a published lower bound for H(N, 3), hence also for
H(N, 5). The differences they print are

$$
\Delta_1(n)=B(n)-\bigl(2\bigl\lfloor 2n/3\bigr\rfloor+n\bigr),
$$

$$
\Delta_2(n)=B(n)-\bigl(2\bigl\lfloor 2n/3\bigr\rfloor+n+2\bigr).
$$

Enumeration on n = 2, …, 40 (both languages, same dump)
certifies their thresholds exactly:

- Δ₁(n) > 0 if and only if n ≥ 7. Negative at n = 2, 3;
  zero at n = 4, 5, 6.
- Δ₂(n) > 0 if and only if n ≥ 13. Zero at n = 10, 11, 12.
- Their Δ₃ against Xiong is positive at n = 21 and for every
  n ≥ 23 in the range (zero at n = 22).

The substitution identities HR(2n+1) = 2⌊2n/3⌋ + n and
HR₂(2n+1) = 2⌊2n/3⌋ + n + 2 hold on the same range. This is
a replay of their comparison, not a new Liénard lower bound
and not a planar Hilbert number.

## Kept — named family ẋ = y − (αx + β x³), ẏ = −x

Energy, as a polynomial identity in Z[x, y, α, β]
(certificate `certs/family.json`, block `energy`):

$$
\frac{d}{dt}\frac{x^2+y^2}{2}
= x\dot x+y\dot y
= -\alpha x^2-\beta x^4
= -x^2(\alpha+\beta x^2).
$$

If α ≥ 0 and β ≥ 0, not both zero, the derivative is ≤ 0 and
is not the zero polynomial. It vanishes only on x = 0. The
field on x = 0 is (y, 0): the only equilibrium is the origin,
and a horizontal line y = const ≠ 0 is not periodic. There is
no periodic orbit.

If β = 0 and α ≠ 0 the field is linear. The characteristic
polynomial is λ² + α λ + 1, with trace −α ≠ 0 and determinant 1.
A linear plane field with nonzero trace has no periodic orbit.
Energy reduces to −α x².

If β > 0 and α < 0 this is van der Pol type. Set
a = √(−α/β) > 0, so α = −β a² and

$$
F(x)=\alpha x+\beta x^3=\beta x(x-a)(x+a).
$$

F is odd. The unique positive root is a. The sign identity

$$
-F(x)=\beta x(a-x)(a+x)
$$

says F < 0 on (0, a) when β > 0 and a > 0 (three positive
factors). Differentiating, F′ = α + 3β x² and

$$
F'(a)=2\beta a^2,\qquad F'(x)-2\beta a^2=3\beta(x^2-a^2).
$$

So F′ ≥ F′(a) > 0 on [a, ∞). Also F → +∞. These are the
algebraic hypotheses of Liénard uniqueness for
ẋ = y − F(x), ẏ = −x with F odd: exactly one periodic orbit,
asymptotically stable. The geometric comparison that finishes
the theorem is not re-proved here.

The same tail positivity is Zhang’s monotonicity of f/g on
x > 0: f = F′, g = x, and g f′ − f g′ = 3β x² − α, which is
positive throughout the chart α < 0, β > 0.

Integer sample (a, β) = (2, 1), hence α = −4: F(1) = −3,
F(3) = 15, F(2) = 0, F′(2) = 8, F′(0) = −4.

This is the two-parameter cousin of classical van der Pol
F = μ(x³/3 − x), which is the slice α + 3β = 0 with β > 0.
Line B already counted that slice. Not a new H(3).

## Dropped / forked

Beating B(n) is dropped. The paper omitted the origin family
from the unconditional Theorem 3 because the finite-dimensional
compatibility with the lips condition is not a one-night field.

The full list ẋ = y − F(x), ẏ = −x, deg F ≤ 3, is dropped. If
F = αx + γ x² + β x³ then F(x) + F(−x) = 2γ x², so F is not
odd unless γ = 0. Liénard’s odd-F list does not apply. That
is the obstruction, not a proof that two cycles exist.

## What this is not

Not a bound on planar H(n). Not a field with more than B(n)
cycles. Not a proof that every cubic-damping Liénard has at
most one cycle. Not a new H(3). The arithmetic and the energy
identity are reusable: a stranger can replay `run.sh` and read
the table and the two energy terms off the JSON.
