# One-flip leftover of the three q11 followup certificates

The recorded finite handle is every unimodular diagonal flip of the
three q11 followup certificates, followed by every sign change of
Hamming weight at most three. Those three schemes were produced by
the q11 followup and were never used as one-flip seeds. The baseline
is the 2,415 nonempty degree-eight T-curve schemes already certified
(2,367 published, seventeen parent additions, the q8 scheme, nine
q9 schemes, thirteen q10 schemes, and eight q11 schemes).

All 93 leftover balls finished (1,416,018 evaluations). No scheme
outside that 2,415 appeared. That finished neighbourhood is not a
new lower bound. Neither of the two open maximal deep nests is
decided.

The [claim](CLAIM.md) is an existence predicate that this leftover
did not establish. From the repository root, replay the controls and
the leftover coverage with:

```sh
python3 problems/hilbert16-degree-8/compute/q12/controls.py
python3 problems/hilbert16-degree-8/compute/q12/coverage.py
```

```sh
python3 problems/hilbert16-degree-8/compute/q12/collect.py
```

This needs Python 3, a C compiler and `rustc`, with no Python packages
to install. `run_all.sh` exits zero only if a certificate outside the
2,415 exists; a missing certificate is a failure.

`lift_candidate.py` can repeat a lifting solve with SciPy; those
packages are unnecessary here.
