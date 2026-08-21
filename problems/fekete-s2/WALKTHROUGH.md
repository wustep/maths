# Walkthrough — a Table 3 replay, not a new bound

- Problem: `problems/fekete-s2` (Smale 7)
- Date: 2026-08-19
- Argument status: certified replay of a published log-energy table;
  no configuration whose energy beats that table
- Problem status: open. This folder does not claim Smale 7.

## 0. What was actually missing

Smale 7 is an algorithmic question: a polynomial-time machine that
returns an \(N\)-tuple within \(c\log N\) of \(E_{\min}\). That is not
a one-night object. The finite object that *can* move is a better
\(N\)-point energy than a printed table, with points and a verifier.

The printed record used here is Ridgway–Cheviakov, *Comput. Phys.
Commun.* 233 (2018), Table 3, fetched as the author PDF and checked
with `pdftotext`. Rathbun–Ridgway, arXiv:2008.04880, refine the same
\(N\le 65\) list to 77 digits and do not claim new globals beyond the
2018 \(N=19,46\) improvements over Bergersen–Boal–Palffy-Muhoray 1994.
Amore–Figueroa–Ramos, arXiv:2512.12416 (Dec 2025), map the landscape
to \(N=160\) but do not print an \(E_{\min}(N)\) table.

What was missing was not a new potential. It was an independent
recomputation of those numbers, and a search at the \(N\) where the
2018 paper itself reports slack (\(N=33\) saddle, \(N=19,46\) new
globals, modest \(N\) with nearby locals).

## 1. Named false starts

- **Treat Womersley's ME points as a log-energy record.** The UNSW
  energy page (last updated 16-Jan-2003) minimises Coulomb / Riesz
  \(s=2\). Different functional. Lead, not a citation for \(E_{\log}\).

- **Treat Beltrán–Lizarte's printed \(-16.3649557\) as this folder's
  \(E\).** They sum \(i\neq j\). Twice our \(N=7\) 1:5:1 energy
  \(-8.18247786\). Convention, not a second table, and not a beat.

- **Treat an 8-decimal rounding as a beat.** Several search energies
  sit \(10^{-8}\)–\(10^{-9}\) below the printed Table 3 digit. That is
  the extra digit of the same number Rathbun already printed to 77
  places. House rule: \(\Delta\gtrsim 10^{-7}\) and a different
  configuration, or it is not a new bound.

- **Download Amore's 591 MB local-minima dump and call the lowest
  file a record.** The paper does not print \(E_{\min}(N)\). A Zenodo
  dump without a cited number is not a published record.

- **\(N=33\) from random starts.** The 2018 paper needed \(10^6\)
  iterations after first hitting a saddle. Our 32 rng starts stall
  about \(10^{-6}\) above the published global. Kicks from the
  published point stay there. We did not improve it.

## 2. The useful failure

\(N=46\) is the useful failure. Ridgway–Cheviakov's new global
(\(-249.4558479\)) is findable from a generalized spiral and from
several rng starts. Many other rng starts land on their published
*local* \(-249.454650\). Fibonacci stalls worse, at \(-249.44978\).
The 2018 improvement over Bergersen is real and independently
reproducible, and the old basin is still there. A third, lower
basin did not appear.

That is the degree of freedom the night actually had: the 2018 paper
already isolated the slack (\(N=19,46\) versus 1994; \(N=33\) as a
hard saddle). Replaying those lines, and failing to undercut them, is
the leftover.

## 3. The replay

Energy, after projecting to \(S^2\):

\[
E(X)=\sum_{i<j}\log\frac{1}{|x_i-x_j|}
=-\frac12\sum_{i<j}\log\bigl(2(1-\langle x_i,x_j\rangle)\bigr).
\]

`compute/energy.py` is the independent verifier. Closed forms:

\[
\begin{aligned}
E_2&=-\log 2,\\
E_3&=-\tfrac32\log 3,\\
E_4&=3\log(3/8),\\
E_5&=-4\log 2-\tfrac32\log 3,\\
E_6&=-9\log 2.
\end{aligned}
\]

These match Table 3 to the printed 8 decimals, as do the pentagonal
bipyramid (\(N=7\)) and the regular icosahedron (\(N=12\)).

Rathbun–Ridgway's Zenodo `log.3.N.80` files were parsed (including
the occasional `1/2` in the \(N=44\) algebraic file) and run through
the same verifier. For every \(N=2\)–\(65\), the recomputed \(E\)
equals the file's `ener=` to \(\sim 10^{-13}\) and equals Table 3 to
the printed digit. That is the full replay.

Multi-start Riemannian descent with fixed seeds then recovered the
same globals at \(N=7,8,9,10,14,19,24,32,33,46,48\). For \(N=24,32,48\)
every seed — Fibonacci, spiral, and 32 rng — lands on the published
energy. The table is not an artefact of one coordinate file.

## 4. What would have been a new bound

An explicit point set whose verifier energy is below the first Table 3
entry for that \(N\) by more than rounding, with the points stored.
That did not happen. The 77-digit Rathbun–Ridgway refinement of the
same list is the sharper form of the same record. Smale 7 is the
algorithmic question and is untouched.

## 5. How to replay

```bash
cd problems/fekete-s2/compute
sh run_all.sh
```

Expected: closed-form matches for \(N=2\)–\(6\), `PASS` from
`verify_replay.py`, checkpoint energies agreeing with `energy.py`.
The stored Table 3 extract is `ridgway2018.json`. The stored
coordinate replay is `replay_rathbun.json`.
