# q15 claim — reaching the aspect-ten cut

Status: attempted; no new bound until both independent verifiers pass.

For the fermionic Coulomb Hamiltonian and critical electron count
defined in PROBLEM.md, the target is

$$
N_c(Z)<1.1Z+3.933Z^{1/3}\qquad\text{for every real }Z\ge4.
$$

The prior certified notebook bound is q14's
$N_c(Z)<1.1005Z+3.933Z^{1/3}$ for $Z\ge4$.
The published comparison is Hundertmark–Pattakos–Schulz,
[arXiv:2504.18487v1](https://arxiv.org/abs/2504.18487),
with leading coefficient 1.1185 and remainder coefficient 4
on the same range.

The finite handle uses 40 rational bins covering $[1,10]$, with
target $\varphi=2281/2500=0.9124$. A positive-semidefinite plus
entrywise nonnegative decomposition would bound the compact radial
quotient. After its reweighting error, the target is at least
$10/11$. The existing mass-stationary argument gives $Q>10/11$
for larger used-support aspect. This would prove $\beta_3\ge10/11$;
the HPS Section 7 calculation must then certify the displayed bound.

The intended replay checks separate rational matrix and Gram
witnesses in Python and Rust. Numerical solver status is never a
premise. `run_all.sh` exits 0 only when every finite check and the
claimed HPS constants pass; missing, invalid, or incomplete
certificates return nonzero.

Falsifier: a valid bound-state example violating the displayed
inequality disproves it. An invalid matrix inequality, uncovered
radial measure, incorrect compact-to-global passage, or failed
outward scalar bound invalidates the certificate. Incomplete search
is residue, not a new bound. Bounded excess remains open.
