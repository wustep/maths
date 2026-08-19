# Walkthrough — elliptic Fekete points on \(S^2\)

- Problem: `problems/fekete-s2` (Smale 7)
- Date: 2026-08-19
- Argument status: in progress. Verifier + Table 3 extract first; search next.
- Problem status: open. This folder does not claim Smale 7.

## 0. What was actually missing

Smale 7 is an algorithmic question. The finite object that can move in
one night is a better \(N\)-point energy than a printed table, or an
honest replay of that table.

The printed record used here is Ridgway–Cheviakov, *Comput. Phys.
Commun.* 233 (2018), Table 3 (author PDF fetched tonight). Rathbun–
Ridgway, arXiv:2008.04880, refine the same \(N\le 65\) list to 77
digits and do not claim new globals beyond the 2018 \(N=19,46\)
improvements over Bergersen 1994.

## 1. Named false starts

To be filled after the search. Planned dead ends: treating Womersley's
Coulomb ME points as a log-energy record; treating Beltrán–Lizarte's
\(\sum_{i\neq j}\) as this folder's \(E\); treating an 8-decimal
rounding as a beat.

## 2. Replay

`compute/energy.py` is the independent verifier. Sanity configs live in
`compute/known.py`. Table 3 globals are in `compute/ridgway2018.json`.

```bash
cd problems/fekete-s2/compute
sh run_all.sh
```
