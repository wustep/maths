# Attack log — Linear covering codes of radius two

## 2026-08-16 — q1 (recovered from Codex session 01a009f7-5a24-71e1-bf4c-9667f4d2cbc4)

- Targets tried: \((r,n)=(8,25)\) (documented 26) — best anneal missed 3 of 256 syndromes; CP-SAT/Z3 no model. \((9,38)\) (documented 39) — CP-SAT UNKNOWN; Gabidulin 39-set deletions missed 8.
- Click: seed from the 51-column Kaikkonen–Rosendahl matrix at \(r=10\). Fixed-cardinality targeted simulated annealing, xorshift64 run 0, hit 0 uncovered at proposal 3,600,281.
- Witness: 50 distinct nonzero 10-bit columns. F\(_2\)-rank 10. Exhaustive pair-XOR: 1024/1024. Density \(319/256=1.24609375\).
- Commit remembered in Math-agent memory as `5b93f34`. Watcher (Grok, 03:32 PT) independently rebuilt columns from `H_r10_n50.txt` (LSB = row 1) and confirmed 1024/1024.
- \(n=49\) stochastic run left 7 uncovered syndromes — not a lower bound.

## 2026-08-16 — q2 (recovered from Codex session 01a00a33-832e-7d13-bf0e-59aeab97ec82)

- Push 50→49 using `H_r10_n50.txt` as seed. Search residue still 7 uncovered. Files: `search_n49.c`, `search_n49_lifted.c`, `build_q2_residue.py`, `verify_q2_residue.py`.
- Do not claim \(f(2)\). Holes \((8,25)\) and \((9,38)\) remain secondary.
