# Exact replay

This directory checks the two pieces of arithmetic quoted by the
problem notes:

1. the dimension threshold in Bourgain–Klein's proof; and
2. the local modulus power created by adding free Euclidean
   directions to a separable operator.

Run both independent implementations with:

```bash
./run_all.sh
```

The driver uses only Python's standard library and `rustc`. It checks
the committed CSV certificates, compares the complete Python and Rust
reports, and exits nonzero on any mismatch.

For dimension $d\geq2$, the checked quantities are

$$
g_d=\frac d{d-1}-\frac43
    =\frac{4-d}{3(d-1)},
\qquad
\kappa_d=\frac{4-d}{8}.
$$

The method has room exactly when $g_d>0$. The certificate includes
dimensions 2 through 8, including the equality at 4 and negative
controls above it.

For $m\geq1$ free directions, the cumulative free DOS kernel has
power $\alpha=m/2$. Its checked local continuity power is

$$
\theta_m=\min\{1,m/2\}.
$$

These are algebraic replays of published or elementary formulas. They
do not constitute a new IDS continuity bound.
