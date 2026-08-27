# q2 — grow free histograms from the q1 mix

Same lemma as Hou–Zhao arXiv:2607.01169v2 Lemma 2.1. q1 leftover refine
and dropped-symmetry never finished; this folder does not continue those
two phases.

`certs/r11_m48_L6.json` is an eleven-kernel rational certificate at
`m=48`, `L=6`. The kernels are free symmetric histograms, grown from
the q1 mix and then reshaped on a 48-bin grid. Exact arithmetic gives

    √(ab) = 0.943006169985179 < 0.94301 < 0.94325 < 0.9435.

So

    F(N) ≤ √N + 0.94301 N^{1/4} + O(1)

for all large N. This beats the folder record 0.94325 and Hou–Zhao’s
published 0.9435. SHA-256 of the JSON is
`341cba5bd8364cd315561d1b89ad3e3ba0c9d5160047781d86c40213b53b02c6`.

Three checks that do not share covering code:

```bash
./run_all.sh
```

that is: leftover check of the q1 log, parent nested-loop and this
folder’s exact matrix-vector verifier on the q1 certificate (do not
regress `C<0.94325`), then the same two Python checks plus the GMP
nested-sum verifier on `certs/r11_m48_L6.json` with `ab < (0.94301)^2`.

A floating γ is not a bound. The search log is `search.jsonl`.
