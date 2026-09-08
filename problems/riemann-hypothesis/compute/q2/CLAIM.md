# Certified claim — 2026-09-08

The computer-assisted certificate establishes the unconditional inequality

$$
\Lambda\leq\frac{893927}{5000000}=0.1787854<\frac15.
$$

The prior published upper bound is $\Lambda\leq1/5=0.2$, Platt–Trudgian,
[arXiv:2004.09765v1](https://arxiv.org/abs/2004.09765v1), Corollary 2,
using the Polymath 15 criterion,
[arXiv:1904.12438v2](https://arxiv.org/abs/1904.12438v2), Theorem 1.2.
This is a dent relative to that published upper bound. The candidate value
and construction are credited below; no priority for the number is claimed.

## Exact parameters

$$
X=6000000185827,\qquad t_0=\frac{129}{800},\qquad
y_0=\sqrt{\frac{87677}{2500000}}>0.
$$

The implementation lead is Jude Gomila's candidate repository at commit
`a74738deb6d5e0f76887cb36901da08b68dca705`, already examined in `../q1/`.
Its number was an unpublished candidate, not the published record being
compared. The analytic source review is in `ANALYTIC_REVIEW.md`, and the
mathematical note is `NOTE.md`. No external human peer review is claimed.

## Completed certificate

1. Exact parameter arithmetic and the published zero-height input pass.
   The height surplus is $350479773/2$.
2. The original C producer freshly regenerated all 3,149,013 required
   indices, $690988\leq N\leq3840000$, without gaps or uncertain rows.
3. An independently written Rust interpolation algorithm verified the same
   complete range. Both give floor $791366/10^{12}$ at $N=690988$.
   A direct convolution checks that weakest row separately. The two full
   algorithms share Arb; repeating a precision is not counted as independence.
4. Fresh error and tail checks pass, as do the full height transfer and
   all 883 closed barrier prisms. All 7,688 coefficient components were
   regenerated. The independently recomputed prism margin exceeds $0.5198$.
   The analytic review supplies the closed zero-time limit and the transfer
   to every hypothesis of the published criterion.

The exact finite margin after approximation error is

$$
\frac{791366}{10^{12}}-
\frac{233494905212337849}{10^{24}}
=\frac{557871094787662151}{10^{24}}>0.
$$

The complete evidence is retained in `certificate/`, including both full
finite streams, their execution manifests, fresh analytic logs, coefficient
matrix, and exact summaries. `run_all.sh CHECKOUT` checks this certificate;
`run_all.sh CHECKOUT NEW_OUTPUT_DIRECTORY` regenerates all numerical lanes.

`run_all.sh` exits zero only after the complete certificate establishes this
claim. Certificate replay does not purport to rerun the interval arithmetic.
Successful diagnostics alone do not satisfy its gates.

## Falsifier and certificate rejection

A rigorous example of a nonreal zero of $H_{893927/5000000}$ would falsify
the inequality. A missing interval, invalid error bound,
unproved analytic implication, failed independent check, or substituted
rounded parameter rejects this certificate; it does not by itself disprove
the target inequality.
