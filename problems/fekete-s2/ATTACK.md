# Attack log — elliptic Fekete points on \(S^2\)

## 2026-08-19 — start

- New folder `problems/fekete-s2`. House rules: write only here; do not
  touch `problems/covering/` or `problems/landau-n2-plus-1`; do not invent
  a dent; do not claim Smale 7. A configuration is nothing until the
  independent verifier agrees and the beaten number is from a paper.
- Energy used throughout: \(E=\sum_{i<j}\log(1/|x_i-x_j|)\) after
  projecting to \(S^2\).
- Tonight: either (A) a certified energy beat of a published record, or
  (B) an honest replay plus residue.

## Published records fetched tonight

Sources actually opened (arXiv HTML/PDF or author PDF), not forum posts:

- Smale, *Math. Intelligencer* 20 (1998): problem 7 is the
  \(c\log N\) algorithm, not a table.
- Cohn–Kumar, arXiv:math/0508114: \(N=2,3,4,6,12\) on \(S^2\) are
  universally optimal, hence log-optimal. Icosahedron is the \(N=12\)
  case.
- Dragnev–Legg–Townsend, *Pacific J. Math.* 207 (2002): \(N=5\) is the
  triangular bipyramid \(\{1,3,1\}\).
- Beltrán–Lizarte, arXiv:2502.10152v3 / *J. Symbolic Comput.* (2026):
  complete critical-point classification for \(n\le 6\) in every
  dimension; \(N=7\) on \(S^2\) is 1:5:1 among dipole configurations,
  printed \(E_{\log}=\sum_{i\neq j}=-16.3649557\) (twice this folder's
  \(E\)).
- Ridgway–Cheviakov, *Comput. Phys. Commun.* 233 (2018), Table 3:
  putative global log-energies for \(N=4\)–\(65\) to about 8 decimals.
  New globals claimed at \(N=19\) and \(N=46\) versus Bergersen–Boal–
  Palffy-Muhoray 1994. This is the printed table we replay and try to
  beat. Author PDF:
  <https://researchers.usask.ca/alexey-shevyakov/papersetc/2018_wr_ac_cpc_iterative_optim.pdf>
- Rathbun–Ridgway, arXiv:2008.04880: 77-digit coordinates for the same
  \(N\le 65\) log-minima (Zenodo 5595366). They match Ridgway–Cheviakov
  to \(4.95\times 10^{-8}\). Algebraic energies for several small \(N\).
- Amore–Figueroa–Ramos, arXiv:2512.12416 (Dec 2025) / *J. Stat. Phys.*
  (2026): landscape to \(N=160\), 14142 local minima at \(N=160\). No
  printed \(E_{\min}(N)\) table. Zenodo 17923310 is a 591 MB dump of
  all local minima, not a record table.
- Brauchart–Hardin–Saff, arXiv:1202.4037: next-order log-energy
  asymptotics. Notes that Rakhmanov–Saff–Zhou 1994 used half this
  folder's \(E\) (i.e. \(\sum_{i<j}\)).
- Hardin–Michaels–Saff, arXiv:1607.04590: comparison of constructions;
  Womersley supplied near-min log points for \(N<500\). Mesh-ratio
  table, not an \(E_{\min}\) table.
- Womersley energy page
  <https://web.maths.unsw.edu.au/~rsw/Sphere/Energy/>: Coulomb / \(s=2\)
  ME points (2003), not a log-energy record table.

No later accepted table with a lower \(E_{\min}\) for any modest \(N\)
was found tonight. The number to beat for \(4\le N\le 65\) is the first
(global) entry of Ridgway–Cheviakov Table 3, refined by Rathbun–Ridgway
to many more digits.

## Plan

1. Independent verifier: project to \(S^2\), print \(E\). Sanity:
   tetrahedron, octahedron, icosahedron.
2. Replay Table 3 for several \(N\) by regenerating known optima and by
   multi-start Riemannian descent with deterministic seeds.
3. Search at \(N\) with slack: 7, 8, 9, 10, 14, 19, 24, 32, 33, 46, 48.
   \(N=33\) is the paper's own hard case (saddle first, then \(10^6\)
   iterations).
4. A printed 8-decimal that we undercut only in the last digit is
   rounding, not a beat. A new configuration whose \(E\) is below the
   printed global by more than \(10^{-7}\) (Rathbun's comparison
   tolerance) would be a candidate.

## Files

- `compute/energy.py` — from-scratch verifier.
- `compute/known.py` — exact \(N=2\)–\(6,12\) and 1:5:1 for \(N=7\).
- `compute/optimize.py` — deterministic multi-start descent.
- `compute/ridgway2018.json` — Table 3 globals extracted from the
  author PDF (checked against `pdftotext` of that PDF).
- `compute/replay_published.py` — parse Rathbun GP-Pari files.
- `compute/replay_rathbun.json` — \(N=2\)–\(65\) recomputed energies.
- `compute/checkpoints/N*.json` — search points + start log.
- `compute/run_all.sh` — replay.

## 2026-08-19 — verifier sanity

`compute/known.py` + `energy.py`:

| \(N\) | config | \(E\) | Table 3 |
| ---: | --- | ---: | ---: |
| 4 | tetrahedron \(3\log(3/8)\) | \(-2.942487759035\) | \(-2.9424878\) |
| 5 | 1:3:1 \(-4\log 2-1.5\log 3\) | \(-4.420507155242\) | \(-4.4205072\) |
| 6 | octahedron \(-9\log 2\) | \(-6.238324625040\) | \(-6.2383246\) |
| 7 | 1:5:1 | \(-8.182477864445\) | \(-8.1824779\) |
| 12 | icosahedron | \(-21.606145230445\) | \(-21.6061452\) |

Beltrán–Lizarte's printed \(E_{\log}=-16.3649557\) for \(N=7\) is
exactly \(2E\) (their \(\sum_{i\neq j}\)). Convention check, not a beat.

## 2026-08-19 — full Table 3 replay from published coordinates

Zenodo 5595366 `log.3.N.80` parsed and run through `energy.py`. Every
\(N=2\)–\(65\) matches the file `ener=` to \(\sim 10^{-13}\) (N=34 has
no `ener=` line; we still recompute \(E=-142.3758522709\) vs Table 3
\(-142.3758523\)). Every Table 3 global matches to the printed 8
decimals (\(|\Delta|<5\times 10^{-8}\), the rounding of the last digit).
Table: `compute/replay_rathbun.json`.

This is a replay of the published record, not a dent.

## 2026-08-19 — search at slack \(N\)

Deterministic seeds (Fibonacci, RSZ spiral, square-antiprism heights
for \(N=8\), 32 RNG seeds with base 4102, plus Rathbun + four kicks).
Riemannian Armijo descent. Independent verifier on stored points.

| \(N\) | our \(E\) | Table 3 | \(\Delta\) | from-scratch? |
| ---: | ---: | ---: | ---: | --- |
| 7 | \(-8.182477864445\) | \(-8.1824779\) | \(+3.6\cdot 10^{-8}\) | yes (1:5:1) |
| 8 | \(-10.428017781460\) | \(-10.4280178\) | \(+1.9\cdot 10^{-8}\) | yes (antiprism) |
| 9 | \(-12.887752725759\) | \(-12.8877527\) | \(-2.6\cdot 10^{-8}\) | rounding only |
| 10 | \(-15.563123389022\) | \(-15.5631234\) | \(+1.1\cdot 10^{-8}\) | yes |
| 14 | \(-28.407813009242\) | \(-28.407813\) | \(-9\cdot 10^{-9}\) | rounding only |
| 19 | \(-49.199891565787\) | \(-49.1998916\) | \(+3.4\cdot 10^{-8}\) | rng within \(10^{-7}\) |
| 24 | \(-75.213984788629\) | \(-75.2139848\) | \(+1.1\cdot 10^{-8}\) | yes (all seeds) |
| 32 | \(-127.378867614780\) | \(-127.3788676\) | \(-1.5\cdot 10^{-8}\) | yes (all seeds) |
| 33 | \(-134.747820824333\) | \(-134.7478208\) | \(-2.4\cdot 10^{-8}\) | no; rng \(\sim 10^{-6}\) high |
| 46 | \(-249.455847900857\) | \(-249.4558479\) | \(-9\cdot 10^{-10}\) | yes (spiral, some rng) |
| 48 | \(-270.117949959283\) | \(-270.11795\) | \(+4.1\cdot 10^{-8}\) | yes (all seeds) |

No \(\Delta < -10^{-7}\). The tiny negatives are extra digits of the
same 8-decimal print. Not a beat.

\(N=46\) independently recovers the 2018 new global from spiral and
several rng starts. Many rng land on the published local
\(-249.454650\), which is Table 3's second line. Fibonacci stalls at
\(-249.44978\), a still-worse basin. That is the residue: the landscape
has the old and new globals close together, and we found both, not a
third.

\(N=33\) is the paper's saddle/global struggle. Kicks from the published
point stay at the global; 32 random starts do not reach it within
\(10^{-6}\). We did not improve it.

## Stop

No certified beat. Outcome (B): replay + residue. Smale 7 not claimed.
