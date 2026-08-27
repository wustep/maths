# Attack log — continuity of the integrated density of states

Chronological attempts, newest last.

## 2026-08-27 — source and record

- Opened Simon's 2000 reprint and checked the printed statement. His
  Problem 14 asks for continuity of $k(E)$, records the
  one-dimensional and discrete cases, and singles out the
  higher-dimensional continuum case.
- Reconstructed $k$ as the cumulative Pastur–Shubin local trace
  measure and separated the discrete, one-dimensional continuum, and
  multidimensional continuum settings.
- The literature reset the starting line. Bourgain–Klein (2013)
  proves continuity for arbitrary bounded deterministic continuum
  potentials in $d=2,3$, whenever the IDS exists. Specialized
  Wegner estimates cover many random models in every dimension. The
  unrestricted bounded continuum leftover begins at $d=4$.

## 2026-08-27 — q1: replay the dimension frontier

- In Bourgain–Klein's proof, the harmonic-jet constraints leave a
  subspace when the vanishing order has scale

  $$
  N\asymp \rho^{1/(d-1)}R^{d/(d-1)},
  $$

  where $\rho$ is the finite-volume density in a short energy
  interval.
- Their quantitative unique-continuation estimate costs
  $R^{4/3}$. The needed comparison $N>MR^{4/3}$ is available only
  when

  $$
  \frac d{d-1}-\frac43>0.
  $$

- Solving that comparison for $\rho$ reproduces
  $\rho\lesssim R^{(d-4)/3}$. Their remaining choice of scale gives
  the logarithmic modulus exponent $(4-d)/8$.
- `compute/q1/verify_frontier.py` and an independent Rust verifier
  check the reduced fractions from certificates. Both identify
  equality and a zero exponent at $d=4$.

## 2026-08-27 — try to improve unique continuation

- Bourgain–Klein explicitly observed that a power $\beta<4/3$ in
  place of $4/3$ would extend their method to dimensions satisfying

  $$
  d<\frac{\beta}{\beta-1}.
  $$

- Frank–Ivanisvili (arXiv:2608.00802) now construct, for every
  $d\geq3$, smooth real $u\ne0$ and smooth bounded real $V$ with

  $$
  -\Delta u+Vu=0,\qquad
  |u(x)|\leq C\exp(-c|x|^{4/3}).
  $$

- This construction rules out the required power improvement for a
  uniform estimate of Bourgain–Klein's form. Fix a ball where $u$
  has positive mass and test a unit ball at distance $Q$. A
  hypothetical $Q^\beta$ estimate with $\beta<4/3$ has a lower
  side of order

  $$
  \exp(-C Q^\beta\log Q),
  $$

  while the constructed solution makes the observation-ball mass at
  most $\exp(-cQ^{4/3})$. The latter is eventually smaller, a
  contradiction.
- The example has no ergodic structure and supplies no IDS
  counterexample. It is a sharp obstruction to lowering the power in
  this deterministic unique-continuation input. Other proof
  architectures remain open.

## 2026-08-27 — imitate the discrete boundary proof

- Delyon–Souillard bound a discrete eigenspace restricted to a cube
  by the number of values in two boundary layers, $O(L^{d-1})$.
  Dividing by the volume rules out a DOS atom.
- Continuum Cauchy data on a hypersurface are infinite-dimensional,
  so the same count has no finite boundary handle. Replacing boundary
  values by harmonic jets returns exactly the $N^{d-1}$ codimension
  count used by Bourgain–Klein, together with its quantitative
  propagation cost. This route therefore meets the same dimension
  frontier.

## 2026-08-27 — add a free direction

- For

  $$
  H=A\otimes I+I\otimes(-\Delta_{\mathbb R^m}),
  $$

  Fourier transform in the free variables gives the exact DOS
  identity

  $$
  \nu_H=\nu_A*\nu_{\mathrm{free},m}.
  $$

- The free DOS has the locally integrable density proportional to
  $t_+^{m/2-1}$. Hence the tensor-sum IDS is locally absolutely
  continuous even when the base measure has atoms. The formulas and
  local Hölder/Lipschitz exponents are proved in `PROBLEM.md` and
  replayed in `compute/q1/`.
- The convolution identity is standard separable-operator theory and
  appears explicitly in later DOS literature. It is a useful exact
  class. The published record therefore receives no dent.

## 2026-08-27 — status

- Residue: no continuity theorem beyond a published class was found.
- Verified handle: the Bourgain–Klein method works precisely for
  $d<4$, is critical at $d=4$, and cannot be extended merely by
  replacing the real-potential Landis exponent with a power below
  $4/3$.
- Leftover: continuity for general bounded ergodic continuum
  Schrödinger operators in every dimension $d\geq4$.
