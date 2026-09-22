# One-flip leftover of the seven q10 followup certificates

The recorded finite handle is every unimodular diagonal flip of the
seven q10 followup certificates, followed by every sign change of
Hamming weight at most three. Those seven schemes were produced by
the q10 followup and were never used as one-flip seeds. The baseline
is the 2,407 nonempty degree-eight T-curve schemes already certified
(2,367 published, seventeen parent additions, the q8 scheme, nine
q9 schemes, and thirteen q10 schemes).

From the repository root, replay a certified construction with:

```sh
sh problems/hilbert16-degree-8/compute/q11/run_all.sh
```

This needs Python 3, a C compiler and `rustc`, with no Python packages
to install. Exit zero means the existence claim in
[CLAIM.md](CLAIM.md) holds. A missing or empty certificate is a
failure, not a residue wrap.

```sh
python3 problems/hilbert16-degree-8/compute/q11/collect.py
python3 problems/hilbert16-degree-8/compute/q11/coverage.py
```

`lift_candidate.py` can repeat a lifting solve with SciPy; those
packages are unnecessary for verification.
