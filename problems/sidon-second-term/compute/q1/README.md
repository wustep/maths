# q1 — re-optimize Hou–Zhao vector smoothing

Same lemma as Hou–Zhao arXiv:2607.01169v2 Lemma 2.1. Their certificate
is eight symmetric kernels at `m=32`, `L=4`. The 2026-08-17 campaign
certified those kernels at `L=6`. This folder searches the leftover
handles: free histograms instead of six-mode profiles, more kernels,
a resampled finer grid, and dropped kernel symmetry.

## Certified

`certs/joint_r8_L6.json` is an eight-kernel rational certificate at
`m=32`, `L=6`. The kernels are free symmetric histograms, not the
published six-mode shapes. Exact arithmetic gives

    √(ab) = 0.9432425309706136 < 0.94325 < 0.9435.

So

    F(N) ≤ √N + 0.94325 N^{1/4} + O(1)

for all large N. This beats Hou–Zhao’s published four-decimal statement
0.9435, not just their exact γ0. SHA-256 of the JSON is
`edcc2c973809c4bb8a3f25233ffc80e6b5ce432a70c4d01697a3ba8ead8beda5`.

Three checks that do not share covering code:

```bash
./run_all.sh
```

that is: parent `verify_certificate.py` (nested (q,i) loop),
`verify_q1.py` (Fraction convolution), and `verify_q1.c` (GMP nested
sum). All three report min slack 0 and `ab < (0.94325)^2`.

A floating γ is not a bound. The search log is `search.jsonl`.
