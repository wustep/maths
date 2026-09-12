# q15 claim — reaching the aspect-ten cut

Status: residue at the midnight cutoff on 2026-09-12. No new bound.
The SDP search did not run and no q15 certificate or verifier was
produced. The certified leading coefficient remains 1.1005.

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

The proposed finite handle uses 40 rational bins covering $[1,10]$, with
target $\varphi=2281/2500=0.9124$. A positive-semidefinite plus
entrywise nonnegative decomposition would bound the compact radial
quotient. After its reweighting error, the intended target is at least
$10/11$. The existing mass-stationary argument gives $Q>10/11$
for larger used-support aspect. This would prove $\beta_3\ge10/11$;
the HPS Section 7 calculation must then certify the displayed bound.

Certification would require separate rational matrix and Gram
witnesses checked in Python and Rust. Numerical solver status is
never a premise. The present `run_all.sh` returns 2 with an explicit
missing-certificate message. It cannot report success for this
unfinished claim. The target inequality above is not established.

Falsifier: a valid bound-state example violating the displayed
inequality disproves it. An invalid matrix inequality, uncovered
radial measure, incorrect compact-to-global passage, or failed
outward scalar bound invalidates the certificate. Incomplete search
is residue, not a new bound. Bounded excess remains open.
