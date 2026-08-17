# Compute — thin cyclic sum covers

Replay the published Bevan–Erskine–Lewis infinite family and the
Haanpää small-order table. Independent check:

```bash
python3 compute/make_bel_certs.py
python3 compute/haanpaa_replay.py
python3 compute/verify.py
```

`verify.py` does not import the construction code. It only recomputes
`A+A` from the listed set.

Search residue (not a bound): `search_linear_family.py`,
`search_three_ap_wide.py`, `complete_sidon.py`, `greedy_complete.py`,
`eval_algebraic.py`, `prune_two_ap.py`.
