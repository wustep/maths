# One-flip leftover of the four q9 followup certificates

The recorded finite handle is every unimodular diagonal flip of the
four q9 followup certificates, followed by every sign change of
Hamming weight at most three. Those four schemes were produced by
the q9 followup and were never used as one-flip seeds. The baseline
is the 2,394 nonempty degree-eight T-curve schemes already certified
(2,367 published, seventeen parent additions, the q8 scheme, and
nine q9 schemes).

From the repository root, replay a certified construction with:

```sh
sh problems/hilbert16-degree-8/compute/q10/run_all.sh
```

This needs Python 3, a C compiler and `rustc`, with no Python packages
to install. Exit zero means the existence claim in
[CLAIM.md](CLAIM.md) holds. A missing or empty certificate is a
failure, not a residue wrap.

```sh
python3 problems/hilbert16-degree-8/compute/q10/collect.py
python3 problems/hilbert16-degree-8/compute/q10/coverage.py
```

`lift_candidate.py` can repeat a lifting solve with SciPy; those
packages are unnecessary for verification.
