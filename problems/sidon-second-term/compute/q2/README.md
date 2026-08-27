# q2 — grow free histograms from the q1 mix

Same lemma as Hou–Zhao arXiv:2607.01169v2 Lemma 2.1, and the same
eight-kernel q1 mix as the starting point. q1 leftover refine and
dropped-symmetry never finished; this folder does not continue those
two phases.

Search lives in `search.py`. A floating γ is not a bound.

## Replay

```bash
./run_all.sh
```

that is: leftover check of `../q1/search.jsonl`, then the parent nested
loop and this folder's exact matrix-vector verifier on the q1
certificate (do not regress `C<0.94325`). If `certs/best.json` exists,
the same two Python checks plus the GMP nested-sum verifier run on it.
