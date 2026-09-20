# q16 claim — reaching the aspect-ten cut

Status: attempted, not yet certified. Continues the unfinished q15
40-bin handle. The certified notebook bound remains q14's
$N_c(Z)<1.1005Z+3.933Z^{1/3}$ for every real $Z\ge4$.

For the fermionic Hamiltonian and critical electron count defined
in PROBLEM.md, the target is

$$
N_c(Z)<1.1Z+3.933Z^{1/3}\qquad\text{for every real }Z\ge4.
$$

The published comparison is Hundertmark–Pattakos–Schulz,
[arXiv:2504.18487v1](https://arxiv.org/abs/2504.18487):
leading coefficient 1.1185 and remainder coefficient 4 on this range.

The finite handle uses 40 rational bins covering $[1,10]$ and target
$\varphi=2281/2500=0.9124$. A positive-semidefinite plus entrywise
nonnegative decomposition must establish a compact quotient bound
at least $10/11$ after the reweighting error. The mass-stationary
argument gives $Q>10/11$ for larger used-support aspect. Separate
rational matrix and Gram witnesses, checked in Python and Rust,
must prove $\beta_3\ge10/11$ and verify the HPS scalar constants.
Solver status is never a premise.

Falsifier: a valid bound-state example violating the displayed
inequality disproves it. An invalid matrix inequality, uncovered
radial measure, incorrect compact-to-global passage, or failed
outward scalar bound invalidates the certificate. Missing witnesses
or incomplete search return nonzero from `run_all.sh`; exit 0 must
mean this full claim holds. Bounded excess remains open.
