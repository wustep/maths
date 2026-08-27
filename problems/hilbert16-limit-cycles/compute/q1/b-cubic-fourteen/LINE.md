# B — cubic fourteen

Imagined: an explicit real cubic planar field with 14 isolated
periodic orbits, hence H(3) ≥ 14, beating Li–Liu–Yang (JDE 246,
2009). Either their (5:1|1:5)+1 configuration plus one extra nest,
or Giné–Gouveia–Torregrosa local M(3) ≥ 12 plus two large cycles.

Forked. H(n) moved? no.

Exact statement (replay `./run.sh`): for every real μ > 0 the cubic
van der Pol field

    dx/dt = y
    dy/dt = −x − μ(x² − 1)y

satisfies the hypotheses of Liénard's uniqueness theorem — F(x) =
μ(x³/3 − x) is odd, unique positive zero √3, F < 0 on (0, √3),
F′ > 0 on [√3, ∞), F → ∞, g(x) = x — hence has exactly one
periodic orbit, and that orbit is asymptotically stable. The
first-order Abelian integral on the linear-center ovals
H = (x² + y²)/2 is I(h) = πμh(2 − h), with exactly one positive
simple zero, at h = 2.

Why 14 failed: Li–Liu–Yang is paywalled, so their 13 is not
replayed and no extra nest is written. Local M(3) ≥ 12 is not a
global field on the page. A nonsingular real cubic curve has at
most two ovals (Harnack), so fourteen algebraic cycles cannot lie
on one invariant cubic. Numerics without a certificate are
residue, not a lower bound.

This line does not claim H(3) ≥ 14. One cycle on this family is
not a dent of H(3) ≥ 13. The radial cubic of line D is a
different field; the two are checked distinct.
