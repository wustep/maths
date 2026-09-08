# Attempted claim — not certified

The target is the unconditional inequality

$$
\Lambda\leq\frac{893927}{5000000}=0.1787854<\frac15.
$$

The prior published upper bound is $\Lambda\leq1/5=0.2$, Platt–Trudgian,
[arXiv:2004.09765v1](https://arxiv.org/abs/2004.09765v1), Corollary 2,
using the Polymath 15 criterion,
[arXiv:1904.12438v2](https://arxiv.org/abs/1904.12438v2), Theorem 1.2.
No improvement is asserted while this file says not certified.

## Exact parameters

$$
X=6000000185827,\qquad t_0=\frac{129}{800},\qquad
y_0=\sqrt{\frac{87677}{2500000}}>0.
$$

The implementation lead is Jude Gomila's candidate repository at commit
`a74738deb6d5e0f76887cb36901da08b68dca705`, already examined in `../q1/`.
Its number is a target, not the published record.

## Required certificate

1. Verify exact parameter arithmetic and the published zero-height input.
2. Regenerate a complete finite enclosure for the asymptotic criterion,
   covering every required point rather than only stored sample values.
3. Check the finite enclosure with an independent implementation and a
   different algorithm. Two precisions of one producer do not supply this.
4. Certify the infinite tail, approximation errors, and the whole closed
   time barrier, with a reviewed analytic transfer to the cited theorem.

`run_all.sh` may exit zero only when these obligations establish the target.
Successful diagnostics alone must leave a nonzero exit status.

## Falsifier and certificate rejection

A rigorous example of nonreal zeros of the deformed function at the target
time would falsify the inequality. A missing interval, invalid error bound,
unproved analytic implication, failed independent check, or substituted
rounded parameter rejects this certificate; it does not by itself disprove
the target inequality.
