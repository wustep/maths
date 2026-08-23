# Research log — erdos-szekeres-seven

Papers, code, and failed lookups. Forum numbers are leads, not citations.

## 2026-08-23 — published interval

- The local source of “Green P45” is
  `notes/lists/2026-08-16-proposed-50.md`; it is the notebook's green-list
  label, not a paper citation.
- Erdős and Szekeres's 1960–61 construction:
  https://renyi.hu/~p_erdos/1960-09.pdf
- A modern exact-coordinate presentation of the construction, used by q1:
  https://arxiv.org/abs/1602.03075 and
  https://arxiv.org/pdf/1602.03075
- Mojarrad and Vlachos's upper bound:
  https://arxiv.org/abs/1510.06255 and
  https://arxiv.org/pdf/1510.06255
- At k = 7 the two formulas give 33 <= ES(7) <= 113. A 32-point
  construction is already the published lower witness; a new lower bound
  needs 33 points with no convex seven-set.

## 2026-08-23 — Baek and Balko, journal and conference versions

- Journal DOI and publisher page:
  https://doi.org/10.1016/j.jcta.2026.106195 and
  https://www.sciencedirect.com/science/article/pii/S0097316526000385
- Crossref and Elsevier API records:
  https://api.crossref.org/works/10.1016/j.jcta.2026.106195 and
  https://api.elsevier.com/content/article/PII:S0097316526000385
- Full official SoCG 2025 preliminary version:
  https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.SoCG.2025.13
  and
  https://drops.dagstuhl.de/storage/00lipics/lipics-vol332-socg2025/LIPIcs.SoCG.2025.13/LIPIcs.SoCG.2025.13.pdf
- The journal record is JCTA 222 (August 2026), article 106195, open access
  under CC BY. ScienceDirect and its PDF endpoint returned access blocks in
  this environment. The Elsevier API returned core metadata but not the
  version-of-record body without an API key. No page-level claim here is
  attributed to an unread journal PDF; the mathematical checks use the full
  15-page official conference version, which the publisher identifies as the
  preliminary version.
- The conference Theorem 8 proves the conjectured threshold for decomposable
  sets. At k = 7 it forces a convex seven-set above 32 points, but does not
  cover arbitrary point sets. Theorem 7's weak-polygon coloring is an
  abstract coloring, not a geometric lower-bound construction. The new point
  constructions still have exactly 32 points at k = 7.

## 2026-08-23 — arXiv:2512.24061 and public code

- Paper:
  https://arxiv.org/abs/2512.24061,
  https://arxiv.org/pdf/2512.24061, and
  https://arxiv.org/e-print/2512.24061
- Code repository and pinned state:
  https://github.com/bogdan27182/esc-paper and
  https://github.com/bogdan27182/esc-paper/commit/9520ceac1758120124840e0b66b003c559cec4a7
- Raw released files:
  https://raw.githubusercontent.com/bogdan27182/esc-paper/main/README.md and
  https://raw.githubusercontent.com/bogdan27182/esc-paper/main/es_sat_gen.py
- History and archive checks:
  https://github.com/bogdan27182/esc-paper/commits/main/,
  https://github.com/bogdan27182/esc-paper/commits/main.atom,
  https://github.com/bogdan27182/esc-paper/branches,
  https://github.com/bogdan27182/esc-paper/tags, and
  https://codeload.github.com/bogdan27182/esc-paper/tar.gz/9520ceac1758120124840e0b66b003c559cec4a7
- `python3 scripts/arxiv_fetch.py 2512.24061 --research ...` failed at
  `https://export.arxiv.org/api/query` with HTTP 429. The PDF was then fetched
  directly and read in full.
- The repository has exactly two tracked files and no release or tag. It
  publishes no CNFs, saved configurations, solver version or command, logs,
  hashes, proof traces, or checker. Its generator SHA-256 is
  `c34fab1327d4c7dbb14a92a143cab657504074e632cfb3fc725dc58eeb354e27`.
- The cheapest reported ES(7) slice is layers `(5,5,5,5,5,5)` with offsets
  `(0,4,4,4,4,4)`, reported at 2,500 seconds. The public generator emits
  578,336 variables and 16,671,498 clauses for that input. Because the paper
  supplies neither a checked proof nor exhaustive coverage of all layer and
  offset cases, the table does not change the global upper bound.

## 2026-08-23 — earlier SAT certificate trail

- Balko and Valtr's public supplement for the earlier SAT attack:
  https://kam.mff.cuni.cz/~balko/ES_SAT/
- Solver and proof-checker sources used for the local replay:
  https://github.com/arminbiere/kissat and
  https://github.com/marijnheule/drat-trim
- It provides older generator/material for strong polygons, but not the
  Baek–Balko weak-seven coloring certificate or Dumitru's 2025 anchored proof
  traces. It was useful as a model for what a public replay package should
  contain, not as evidence for ES(7) = 33.
