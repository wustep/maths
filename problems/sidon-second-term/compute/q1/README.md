# q1 — re-optimize Hou–Zhao vector smoothing

Same lemma as Hou–Zhao arXiv:2607.01169v2 Lemma 2.1. Their certificate
is eight symmetric kernels at `m=32`, `L=4`. The 2026-08-17 campaign
already certified the same kernels at `L=6`. This folder searches the
handles they left open: more kernels, free histograms instead of
six-mode profiles, a finer grid with a resampled shape, and the
left/right split that drops kernel symmetry.

A floating `γ` is not a bound. A claimed improvement has to pass
`../verify_certificate.py` on a rational JSON.

Replay:

```bash
./run_all.sh
```

Search (needs numpy/scipy):

```bash
python3 search.py --phase replay
python3 search.py --phase all
```

Results go to `search.jsonl`. Best floats go to `candidates/`.
If a candidate beats the L=6 plateau by enough to survive rounding,
`rationalize.py` writes `certs/` and the parent verifier checks it.
