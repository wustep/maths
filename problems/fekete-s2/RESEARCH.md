# Research log — elliptic Fekete points on \(S^2\)

Citations only. No paper PDFs in the repo. Forum numbers are leads.

## Problem

- S. Smale, Mathematical problems for the next century, *Mathematical
  Intelligencer* 20 (1998), 7–15. Problem 7: find \(x_1,\dots,x_N\in S^2\)
  with \(E(X)-E_{\min}\le c\log N\) in time polynomial in \(N\).

## Exact optima

- H. Cohn, A. Kumar, Universally optimal distribution of points on
  spheres, *J. Amer. Math. Soc.* 20 (2007), 99–148,
  [arXiv:math/0508114](https://arxiv.org/abs/math/0508114).
  \(N=2,3,4,6,12\) on \(S^2\) are universally optimal.
- P. D. Dragnev, D. A. Legg, D. W. Townsend, Discrete logarithmic energy
  on the sphere, *Pacific J. Math.* 207 (2002), 345–358. \(N=5\) is the
  triangular bipyramid.
- C. Beltrán, F. Lizarte, Characterization of logarithmic Fekete critical
  configurations of at most six points in all dimensions,
  [arXiv:2502.10152v3](https://arxiv.org/abs/2502.10152), *J. Symbolic
  Comput.* (2026), doi:10.1016/j.jsc.2026.102570. Critical-point
  classification for \(n\le 6\); \(N=7\) dipole case is 1:5:1.

## Computational tables (the numbers we replay)

- W. J. M. Ridgway, A. F. Cheviakov, An iterative procedure for finding
  locally and globally optimal arrangements of particles on the unit
  sphere, *Comput. Phys. Commun.* 233 (2018), 84–109,
  doi:10.1016/j.cpc.2018.03.029. Author PDF fetched 2026-08-19:
  <https://researchers.usask.ca/alexey-shevyakov/papersetc/2018_wr_ac_cpc_iterative_optim.pdf>
  Table 3: log-energy locals and globals for \(N=4\)–\(65\). New globals
  at \(N=19,46\) versus Bergersen–Boal–Palffy-Muhoray 1994.
- R. L. Rathbun, W. J. M. Ridgway, Some spherical codes in \(S^2\) and
  their algebraic numbers, [arXiv:2008.04880](https://arxiv.org/abs/2008.04880).
  77-digit log-minima for \(N\le 65\). Coordinates: Zenodo
  [10.5281/zenodo.5595366](https://doi.org/10.5281/zenodo.5595366).
  Match Ridgway–Cheviakov to \(4.95\times 10^{-8}\).
- B. Bergersen, D. Boal, P. Palffy-Muhoray, Equilibrium configurations of
  particles on a sphere: the case of logarithmic interactions, *J. Phys. A*
  27 (1994), 2579. Earlier \(N\le 65\) table that Ridgway beat at 19 and 46.

## 2025–2026 landscape (fetched; not a record table)

- P. Amore, V. Figueroa, R. Ramos, Exploring the energy landscape of the
  logarithmic potential: local minima and stationary states,
  [arXiv:2512.12416v1](https://arxiv.org/abs/2512.12416), *J. Stat. Phys.*
  (2026), doi:10.1007/s10955-026-03629-8. \(N\le 160\) local minima;
  \(N\le 24\) stationary states. Zenodo
  [10.5281/zenodo.17923310](https://doi.org/10.5281/zenodo.17923310)
  (591 MB of spherical-coordinate dumps). No printed \(E_{\min}(N)\).

## Asymptotics and constructions (not records)

- E. A. Rakhmanov, E. B. Saff, Y. M. Zhou, Minimal discrete energy on the
  sphere, *Math. Res. Lett.* 1 (1994), 647–662. \(N\le 200\) experiments;
  \(E=\sum_{i<j}\log(1/r)\). Fitted formula, not a per-\(N\) table we
  could beat line-by-line.
- J. S. Brauchart, D. P. Hardin, E. B. Saff, The next-order term for
  optimal Riesz and logarithmic energy asymptotics on the sphere,
  [arXiv:1202.4037](https://arxiv.org/abs/1202.4037).
- D. P. Hardin, T. Michaels, E. B. Saff, A comparison of popular point
  configurations on \(S^2\), [arXiv:1607.04590](https://arxiv.org/abs/1607.04590),
  *Dolomites Res. Notes Approx.* 9 (2016). Womersley near-min log points
  for \(N<500\); mesh ratios, not \(E_{\min}\).
- D. Armentano, C. Beltrán, M. Shub, Minimizing the discrete logarithmic
  energy on the sphere: the role of random polynomials, *Trans. Amer.
  Math. Soc.* 363 (2011), 2955–2965.
- C. Beltrán, U. Etayo, The Diamond ensemble: a constructive set of
  spherical points with small logarithmic energy, *J. Complexity* 59
  (2020).
- C. Beltrán, The state of the art in Smale's 7th problem, in *Foundations
  of Computational Mathematics, Budapest 2011*, Cambridge Univ. Press,
  2013. Survey; exponential-time algorithm, no table.
- R. S. Womersley, Minimum energy points on the sphere,
  <https://web.maths.unsw.edu.au/~rsw/Sphere/Energy/> (last updated
  16-Jan-2003). Coulomb / Riesz \(s=2\), not log.

## Energy convention

This folder and Ridgway–Cheviakov Table 3:

\[
E=\sum_{i<j}\log(1/|x_i-x_j|).
\]

Beltrán–Lizarte print \(\sum_{i\neq j}=2E\). For the \(N=7\) pentagonal
bipyramid they give \(-16.3649557\), which is \(2\times(-8.18247785)\),
matching Table 3's \(-8.1824779\).

## What would count as a beat

A configuration whose independently recomputed \(E\) is strictly below
the first (global) Table 3 entry for that \(N\), by more than rounding
(\(\gtrsim 10^{-7}\)), with the points stored and the verifier agreeing.
Rathbun–Ridgway's 77-digit refinement of the same table is the sharper
form of the same record for \(N\le 65\).

## Independent checks (this folder)

- `compute/known.py` — PASS. Closed forms for \(N=2,3,4,5,6\) match
  `energy.py` to \(10^{-15}\). \(N=7\) 1:5:1 and \(N=12\) icosahedron
  match Table 3 to the printed 8 decimals.
- `compute/replay_published.py` — PASS on Zenodo 5595366 `log.3.N.80`
  for \(N=2\)–\(65\). Recomputed \(E\) equals the file `ener=` to
  \(\sim 10^{-13}\) (N=34 has no `ener=` line). Table 3 globals match
  to \(|\Delta|<5\times 10^{-8}\).
- `compute/optimize.py` — recovered the same globals at
  \(N=7,8,9,10,14,19,24,32,33,46,48\). Fibonacci / spiral / rng recover
  several of them without published seeds. No energy below the record
  by more than rounding.
- Beltrán–Lizarte \(N=7\) printed \(-16.3649557\) is \(2E\). Convention,
  not a second table.

## What we did not beat

- Any Table 3 global, or the Rathbun–Ridgway 77-digit refinement.
- Smale 7 (polynomial-time \(c\log N\) approximation).
- A published \(E_{\min}\) for \(N>65\): Amore–Figueroa–Ramos 2025
  explores the landscape to \(N=160\) but does not print a record
  table, and their 591 MB Zenodo dump was not treated as a citation
  number.

## How to replay

```bash
cd problems/fekete-s2/compute
sh run_all.sh
```

Expected: `PASS` from `verify_replay.py`, closed-form matches for
\(N=2\)–\(6\), and checkpoint energies agreeing with `energy.py`.
If `/tmp/fekete-data/rathbun` is present, the full \(N=2\)–\(65\)
coordinate replay is re-run; otherwise use the stored
`replay_rathbun.json`.
