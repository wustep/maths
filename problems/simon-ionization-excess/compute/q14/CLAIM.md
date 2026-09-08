# q14 claim — raised compact target

Status: dent, certified 2026-09-07 by two independent finite verifiers
and the argument in [PROOF.md](PROOF.md).

For the fermionic Coulomb Hamiltonian and $N_c(Z)$ defined in
PROBLEM.md, the bound is

$$
N_c(Z)<1.1005Z+3.933Z^{1/3}\qquad\text{for every real }Z\ge4.
$$

The prior notebook record is q13's
$N_c(Z)<1.1006Z+3.933Z^{1/3}$ for $Z\ge4$.
The published comparison is Hundertmark–Pattakos–Schulz,
[arXiv:2504.18487v1](https://arxiv.org/abs/2504.18487),
Proposition 2.5: $N_c(Z)<1.1185Z+4Z^{1/3}$ for $Z\ge4$.

The finite handle uses 37 rational bins covering $[1,10]$, with
edges near the geometric grid, and target $\varphi=0.912$.
The precise edges and two matrix witnesses are in `certificate.json`.
The compact bound is at least $9087/10000=0.9087$; the mass-stationary
cut $10/11$ exceeds that number. Consequently $\beta_3\ge9087/10000$.
The HPS Section 7 calculation then gives the displayed inequality.

`verify.py` reconstructs the kernel bounds with exact rational
arithmetic, checks positive pivots of one matrix, and checks its
entrywise nonnegative remainder. `verify.rs` independently checks a
different, explicit Gram witness using outward integer intervals.
Both independently verify the discretization error, split, published
$b(3)$ window, and final HPS constants. The solver's numerical status
is not a premise. No older enumeration or success flag is a premise.

Falsifier: a valid bound-state example violating the displayed
inequality disproves it. A nonnegative vector violating the proposed
matrix inequality, an uncovered radial measure, an invalid
compact-to-global argument, or failed outward bounds on the Section 7
constants invalidates this certificate. Numerical optimization and a
stored success flag alone do not certify anything.

`run_all.sh` reconstructs and independently checks every finite
certificate and its numerical implications. Exit 0 means the full
claim holds. Missing certificates, failed checks, or incomplete
search return nonzero. The bounded-excess ionization conjecture remains
open. This improves the specified HPS-style finite bound; it does not
replace the asymptotic results with leading coefficient one.
