# Riemann hypothesis, first computation

## Outcome

The published explicit de Bruijn–Newman window remains

$$
0\leq\Lambda\leq0.2.
$$

This folder has three replayable pieces:

1. Exact arithmetic for the Polymath 15 / Platt–Trudgian parameters. The
   printed decimals in Polymath Table 1 give $0.19999966445$, but the table is
   rounded and Platt–Trudgian prove the stated bound $0.2$. The extra digits
   are therefore diagnostic only.
2. A resource-light audit of the off-arXiv $0.1787854$ candidate at commit
   `a74738deb6d5e0f76887cb36901da08b68dca705`. The upstream stored assembly
   parsed all 3,149,013 finite rows. Fresh Arb runs at 256 and 512 bits checked
   the Proposition 4.10 error bound and the infinite tail; a fresh barrier run
   checked 883 consecutive prisms and all 7,688 stored-sum components. A fresh
   producer run matched the sealed first finite row at $N=690988$. The full
   finite range was not freshly regenerated, and the analytic bridge was not
   independently reviewed, so this is residue and not a new upper bound.
3. The printed Saouter–Gourdon–Demichel Lehmer-pair arithmetic, including
   $G<379.1995$ and the historical $\Lambda>-1.14541\cdot10^{-11}$. That lower
   bound is now dominated by Rodgers–Tao's $\Lambda\geq0$.

## Replay

From any directory:

```bash
problems/riemann-hypothesis/compute/q1/run_all.sh
```

The local replay needs Python 3 and a C compiler, uses no network, and finishes
in well under a second. It checks the fresh-log hashes, exact rational
identities, all decisive log markers, the 883-prism sequence, and the Lehmer
formula through independent Python `Decimal` and C `long double` paths.

## What the retained logs mean

The files under `fresh/` were regenerated sequentially from the candidate
repository with GCC 14 and FLINT/Arb 3.1.3. The two precision lanes agree, and
the finite producer's first canonical row agrees exactly with the sealed row.
`barrier_target_closed.log` took about 55 minutes wall time while another
campaign was already using the machine; the remaining fresh numerical lanes
were short. The candidate source and its archived certificates are not copied
here. Its repository is
[judegomila/dbn-lambda-01787854-candidate-audit](https://github.com/judegomila/dbn-lambda-01787854-candidate-audit).

The scope note in `uniform_error.log` is important: analytic justification at
$t=0$ remains external. Hashing a successful log authenticates this replay;
it does not supply a missing theorem.
