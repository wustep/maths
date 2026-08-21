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

## 2026-08-16 afternoon — q3 (Claude, `covering-result` branch)

- Built [`result/`](result/) as a self-contained, independently reproducible artifact for the whole result. Run it with `cd problems/covering/result && ./run_all.sh` — 74 checks, exit 0, byte-identical output across runs.
- Two verifiers from scratch, two languages, opposite algorithms: `result/verify/verify.py` is pair-driven, `result/verify/verify.rs` is syndrome-driven. `run_all.sh` diffs their fact dumps. Both re-derive everything from the matrix text; neither reads a stored certificate. A third, quarantined oracle was run only afterwards and agreed on every value; it is not in the tree.
- The missing piece the overnight run never computed: a valid \((2,0)\)-partition of \(H\) into **10** blocks, against the paper's computer-searched \(p(H_{KR})=11\) (arXiv:2511.02542 Thm 5.2). All 973 syndromes that need a pair have a cross-block one; 821 of them have a unique pair, so the partition is tightly forced.
- Minimality: deleting any single column leaves \(\ge 9\) uncovered syndromes (best deletions 381, 479, 927 leave exactly 9). So the 50-set is a minimal 1-saturating set in \(PG(9,2)\) — an LO code. Not padded.
- \(d=3\), exactly 10 dependent triples; exactly one, \((491,734,821)\), spans three distinct blocks (6/4/9). Analogue of Thm 5.2(ii), which is what QM\(_5^2\) needs at \(r=28\).
- Propagation: Construction QM\(_2^2\) (Thm 4.1, eq. (4.2), (4.4)) implemented from the paper. \(n_0\ge 2^m\ge p(H_0)\) permits exactly \(m=4,5\), asserted not assumed. Results exhaustively verified: \(r=18\), \(n=815\), 262144/262144; \(r=20\), \(n=1631\), 1048576/1048576. Published values 831 and 1663.
- These matrices differ from the alternate allocations in [`result/data/alt/`](result/data/alt/) (the indicator allocation is a free choice) and both verify — two distinct witnesses at each \(r\), not one.
- Family: \(n=51\cdot 2^{r/2-5}-1\), \(\bar\mu(2)\le 2601/2048\approx 1.27002\), against the paper's \(2704/2048\approx 1.32031\) and the pre-2025 \(729/512\approx 1.42383\). Even \(r\le 64\) reachable by QM\(_2^2\) from this seed: 10, 18, 20, 30–40, 46–64. Not reachable: 12, 14, 16, 22, 24, 26, 28, 42, 44 — the QM\(_3^2\)/QM\(_5^2\) analogues are not implemented and nothing is claimed there.
- Soft spot, stated in the note: only \(m=4,5\) are exhaustively verified. The rest of the family inherits the paper's \(p(H_C)\le 2^{m+1}+1\) instead of computing partitions. That is the first thing a referee will push on.
- One number in the brief lost to the code: \(2601/2048\) is \(1.27002\), not \(1.26999\). Fraction right, decimal wrong; no bound changes.
- Priority unresolved — Table 5.1 is "best as far as the authors know". Checklist and a drafted email to Davydov/Marcugini/Pambianco in [`result/PRIORITY.md`](result/PRIORITY.md). Nothing goes out before a human works that list.
