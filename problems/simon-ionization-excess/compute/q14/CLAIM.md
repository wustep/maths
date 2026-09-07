# q14 claim — raised compact target

Status: open; this is the attempted inequality, not a certified bound.

For the fermionic Coulomb Hamiltonian and $N_c(Z)$ defined in
PROBLEM.md, the target is

$$
N_c(Z)<1.1005Z+3.933Z^{1/3}\qquad\text{for every real }Z\ge4.
$$

The prior notebook record is q13's
$N_c(Z)<1.1006Z+3.933Z^{1/3}$ for $Z\ge4$.
The published comparison is Hundertmark–Pattakos–Schulz,
[arXiv:2504.18487v1](https://arxiv.org/abs/2504.18487),
Proposition 2.5: $N_c(Z)<1.1185Z+4Z^{1/3}$ for $Z\ge4$.

The chosen finite handle is the compact radial quadratic form at
aspect ten. Start with 37 geometric bins and target $\varphi=0.912$;
seek a positive-semidefinite plus entrywise-nonnegative decomposition
of its copositivity matrix, with exact rational verification. The
compact-to-global mass-stationary argument and the HPS Section 7
constants must also survive independent checking. A changed finite
target or discretization will be recorded here before certification.

Falsifier: a valid bound-state example violating the displayed
inequality disproves it. A nonnegative vector violating the proposed
matrix inequality, an uncovered radial measure, an invalid
compact-to-global argument, or failed outward bounds on the Section 7
constants invalidates this certificate. Numerical optimization and a
stored success flag alone do not certify anything.

`run_all.sh` must reconstruct and independently check every finite
certificate and its numerical implications. Exit 0 means the full
claim holds. Missing certificates, failed checks, or incomplete
search return nonzero. A residue wrap leaves the attempted inequality
explicitly uncertified and preserves the previous notebook record.
