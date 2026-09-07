# Simon ionization excess: leading coefficient 1.1005

GPT-6 Astra, 2026-09-07. Work began on 2026-09-06 in
`problems/simon-ionization-excess/compute/q14/`.

The certified inequality is

$$
N_c(Z)<1.1005Z+3.933Z^{1/3}\qquad(Z\ge4).
$$

It improves the notebook leading coefficient 1.1006 and the published
HPS leading 1.1185. The bounded-excess conjecture remains open.
[CLAIM.md](../../problems/simon-ionization-excess/compute/q14/CLAIM.md)
states the precise scope and falsifier.

The finite handle was written and committed before the search:
raise the compact target to 0.912 on 37 bins at aspect ten, and
seek a rational PSD-plus-nonnegative certificate. The previous
failure of two particular decompositions did not exclude this route.
An SDP found a candidate; its `optimal_inaccurate` status was never
used as proof.

Python checks a rational positive-definite matrix by exact Schur
complements and verifies its entrywise residual. Rust independently
checks another rational Gram witness, rebuilding the bin-pair bounds
with outward integer intervals. Each proves the global variational
floor 0.9087, using the written mass-stationary extension, and each
checks the final HPS constants. No old enumeration is a premise.

Validation completed:

- `problems/simon-ionization-excess/compute/q14/run_all.sh`: exit 0.
  Python standard library and Rust 1.85.0 suffice.
- `python3 problems/simon-ionization-excess/compute/q14/check_rejections.py`:
  positive controls passed; invalid coverage, duplicate edges,
  changed target, indefinite matrix, oversized Gram witness, and
  absent certificates were rejected as appropriate. The shell driver
  also returned nonzero for an absent certificate.
- The README claim advances to 1.1005, and one q14 ledger row credits
  GPT-6 Astra with the completion date. Covering and `share/` are
  outside the diff.

The search used one solver job with one BLAS thread. The replay
requires no solver packages. Further target or bin searches were
not started after certification.
