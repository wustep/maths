# Cursor Grok 2026-08-29 — Ramsey R(5,5) leftover 2/3/5

Cursor Grok 4.6. Folder `problems/ramsey-r55/compute/q4/`.

## Result

Residue. No endpoint moved. The published interval remains
$43\le R(5,5)\le46$.

After q3 closed every order-7 automorphism on 43 vertices, the leftover
SAT was orders 2, 3, and 5. q2's encoder was reused unchanged. Three
stored DRATs, independently replayed by pinned `drat-trim`, exclude
cycle types $5^6 1^{13}$ and $5^7 1^8$. The five maximum-cycle
representatives for 2, 3, and 5 remain `UNKNOWN`. No $(5,5,43)$-graph
was found.

This is a restriction on a hypothetical graph, not a bound on $R(5,5)$.
Do not cite the folder as a bound.

## Replay

```
cd problems/ramsey-r55/compute/q4
./run_all.sh
```

Certificate: `compute/q4/certs/q4_summary.json`.
