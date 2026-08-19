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
  author PDF.
- `compute/run_all.sh` — replay.
