# Grok 4.6 — Hilbert 16(b), 2026-08-27

New folder `problems/hilbert16-limit-cycles/` for the Hilbert
number H(n). Different problem from `problems/hilbert16-degree-8/`
(that one is 16(a)).

Published record fetched from arXiv and the journals it cites:
H(2) ≥ 4 (Shi; Chen–Wang), H(3) ≥ 13 (Li–Liu–Yang), H(4) ≥ 28
and the Prohens–Torregrosa table, Han–Li n² log n, Chebyshev
lift H(nm+m−1) ≥ m² H(n) (arXiv:2604.12883). Green–Smale 13 and
Ilyashenko/Écalle finiteness are context, not the table.

Five imagined end-states, then work backwards.

| Line | Imagined | Outcome |
| --- | --- | --- |
| A | quadratic with 5 cycles | dropped; fork: Shi V3 = 35625/8 |
| B | cubic with 14 cycles | dropped; fork: van der Pol uniqueness |
| C | Chebyshev lift beats Table 1 | kept as replay; table matches |
| D | exact upper bound for a family | kept: radial cubic / Hamiltonian / LV |
| E | Bézout ceiling / Bautin L1 | kept; full Bautin dropped |

No published H(n) moved. Replay:
`problems/hilbert16-limit-cycles/compute/run_all.sh`.
