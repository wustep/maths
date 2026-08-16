# Attack log — C7 fifth power

## 2026-08-16

- Folder created. Grok 4.6 cloud agent launched.

## 2026-08-16 — q1, reconstruction

- Read Polak–Schrijver IPL 2019 / arXiv:1808.07438. The 367-set is an adapted Reed–Solomon orbit in \(C_{108,382}^{\boxtimes 5}\), not a linear \(\mathbb F_7\)-code (those max out at \(7^3=343\)).
- July 2026 papers (Itty et al. 2607.21517, Gao 2607.27869, Buys–Polak–Zuiddam 2607.29681) improve \(\Theta(C_7)\) in dimensions 10 and 200. All three still treat 367 as the fifth-power record. A 368-set would be a finite dent; \(368^{1/5}\approx 3.2596\) would also beat 3.258805, but that is not the tonight target.
- Copied the published 367 words from [Itty `c7/R367.txt`](https://raw.githubusercontent.com/nathanielitty/lower-bounds-for-shannon-capacity/main/c7/R367.txt) into `compute/R367.txt`. Verifier: `python compute/verify_set.py compute/R367.txt`.
- Reconstruction script `compute/reconstruct_polak.py` replays §3 (shift, fold, isolate, residual MIS).
- Search scripts, not yet a 368-set:
  - `search_orbits.py` — geometric orbits with \(k(n,5,q)\ge 2n/7\) (direct homomorphism into \(C_7\)).
  - `search_fold.py` — nearby \((n,q)\) fold-and-repair, the method that produced 367.
  - `search_linear.py` — all RREF 3-dimensional \(\mathbb F_7\)-codes, greedy residual extension.
  - `search_local.py` — 1-out/2-out exact, sampled 3-out/4-out, annealing from the 367 seed.
- No 368-set claimed. No claim that 367 is maximum (Lovász still allows 401).
