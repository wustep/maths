# Attack log — Hilbert 16(a), degree-8 real schemes

## 2026-08-21 — start

- New folder `problems/hilbert16-degree-8`. House rules: fetch and
  replay the record before trusting it; a failed search with a
  verifier is the product; do not invent a dent. Hilbert 16(b) /
  \(H(n)\) explicitly out of scope.
- Intended stack: combinatorial patchworking (Viro T-curves), exact
  certificates, no ODEs.

## 2026-08-21 — the record, fetched

Three literature passes (arXiv HTML/PDF, author PDFs, raw downloads;
every URL in RESEARCH.md). Corrections to the prompt's leftover:

- The prompt: "2359 realized schemes, 53 *non-maximal* schemes with
  no T-curve witness". Reality: arXiv:2604.09221 (Apr 2026) says 2359
  realized and 53 *maximal* schemes with algebraic constructions but
  no T-curve witness; and arXiv:2602.06888 v3 (Jul 2026) supersedes
  both numbers: **2,367** realized, **38** of the 89 M-schemes
  T-realized, **12** provably not T-realizable (their Theorem 21: a
  maximal degree-8 T-curve has
  \((p,n)\in\{(19,3),(15,7),(11,11),(7,15)\}\)), **39** undecided.
- The six algebraically open M-schemes (Orevkov GAFA 2002, Table 1
  asterisks; author PDF read): ⟨4⊔1⟨2⊔1⟨14⟩⟩⟩, ⟨14⊔1⟨2⊔1⟨4⟩⟩⟩ at
  \((p,n)=(19,3)\); ⟨1⊔1⟨1⟩⊔1⟨18⟩⟩, ⟨1⊔1⟨4⟩⊔1⟨15⟩⟩, ⟨1⊔1⟨7⟩⊔1⟨12⟩⟩,
  ⟨1⊔1⟨9⟩⊔1⟨10⟩⟩ at \((p,n)=(3,19)\). Theorem 21 kills the last four
  as T-curves. The honest T-curve targets are therefore the two
  deep-nests (dent A) and anything missing from the 2,367 census
  (dent C).
- The census data itself is published
  (`dmg-lab/CombinatorialPatchworking`, `deg8.pcoms.txz`, 2,367
  `.pcom` certificates with points, integer lifting weights, cells,
  signs, claimed type). This makes a real replay possible.

## 2026-08-21 — independent verifier

`compute/tcurve.py`, from scratch, no third-party libraries:
triangulation validation (primitive, all 45 lattice points, edge
manifold), exact rational convexity certificates, T-curve
construction in the antipodally glued rhombus, components and
regions via union-find, oval/pseudoline and outer-region detection
via the \(S^2\) double cover, nesting forest by BFS on the region
tree, canonical bracket notation, \(\chi(\mathbb{RP}^2)=1\)
assertion. Plus `fastcx.py`, an array-based re-implementation for
search speed (1.4 ms vs 6 ms per evaluation), and `notation.py` for
parsing/canonicalizing scheme strings.

Sanity (`compute/sanity.py`, all pass): standard triangulation
certified convex for \(d\le 8\); Harnack signs give the classical
M-schemes in every degree 1–8, matching Prop 10 of arXiv:2602.06888
v3 — for \(d=8\): 22 ovals, ⟨18⊔1⟨3⟩⟩; all-plus signs give ⟨1⟩ in
degree 2 (see WALKTHROUGH.md for the false start) and the depth-4
nest ⟨1⟨1⟨1⟨1⟩⟩⟩⟩ in degree 8; corrupted height certificates are
rejected. Random certified triangulations with Harnack signs also
give ⟨18⊔1⟨3⟩⟩ every time, replaying the triangulation-independence
of Prop 10.

## 2026-08-21 — census replay: 2,367 / 2,367

`compute/replay_census.py` on `deg8.pcoms.txz`:

- every certificate's triangulation is primitive and uses all 45
  points; every integer `MIN_WEIGHTS` vector passes the exact
  convexity check;
- the independently recomputed scheme equals the claimed `TYPE` and
  the directory's oval/p/n counts in **all 2,367 cases** (36 s);
- all 2,367 schemes are distinct; the 22-oval subset is exactly the
  38 bold rows of their Table 1 (checked against `compute/record.py`,
  which self-checks 89 = 38 + 12 + 39 and Gudkov–Rokhlin on every
  row);
- the fast evaluator agreed with the exact engine on every
  certificate.

The published record stands. This is a replay, not a dent.

## 2026-08-21 — search

Setup: `compute/search_m8.py`, 8 workers × 25 minutes. Each worker
draws random certified convex primitive triangulations of \(T_8\)
(positive-definite quadratic heights + integer noise across seven
noise scales, float lower hull, exact re-certification; ~10% of draws
use the standard triangulation) and runs simulated annealing over the
\(2^{45}\) sign distributions — five workers maximizing component
count, three with an additional nesting-depth bonus aimed at the two
open deep-nest schemes. Every distinct scheme is logged with its
witness and later re-verified exactly (`compute/verify_found.py`);
schemes are then diffed against the replayed census and the Table-1
partition.

Results (2026-08-21 06:14 UTC, `compute/found_schemes.json`, 5,435
JSONL records across the eight worker logs):

| | |
| --- | --- |
| workers finished | 8 / 8 |
| certified triangulations drawn | 595 |
| sign assignments evaluated | 2,112,073 |
| distinct schemes logged | 902 |
| re-verified exactly (exact pipeline) | 902 / 902 |
| witnesses rejected by the exact pipeline | 0 |
| already in the replayed 2,367-census | **902 / 902** |
| **not in the census (dent C)** | **0** |
| 22-oval M-schemes hit | 2, both already T-realized (⟨18⊔1⟨3⟩⟩, ⟨17⊔1⟨1⟩⊔1⟨2⟩⟩) |
| hits among the six algebraically open (dent A) | 0 |
| hits among the 39 T-undecided | 0 |
| hits among the 12 Theorem-21-impossible | 0 (a hit would have been a bug) |
| schemes outside the 89-row Table 1 | 0 (a hit would have been a bug) |

**No dent.** The 902 schemes are a strict subset of the published
2,367 — 38% of the census re-found, nothing outside it.

The two \((p,n)=(19,3)\) deep-nest targets ⟨4⊔1⟨2⊔1⟨14⟩⟩⟩ and
⟨14⊔1⟨2⊔1⟨4⟩⟩⟩ **did not appear**, in any worker, at any temperature.
Neither is in the census either, so this is silence, not a
contradiction — and silence from \(2\times10^6\) samples of a
\(2^{45}\)-per-triangulation space is not an obstruction.

Where the search actually got stuck, by nesting depth:

| depth | found | census |
| --- | --- | --- |
| 1 | 16 | 19 |
| 2 | 505 | 1,247 |
| 3 | 381 | 1,100 |
| 4 | 0 | 1 (⟨1⟨1⟨1⟨1⟩⟩⟩⟩, the all-plus curve) |

Both targets are depth 3 with 22 ovals. The annealer reached 22 ovals
only at depth 2; its best depth-3 scheme was ⟨7⊔1⟨10⊔1⟨1⟩⟩⟩ with 20
ovals, two short, and the census itself contains 22-oval depth-3
schemes (e.g. ⟨9⊔1⟨6⊔1⟨5⟩⟩⟩) the search never reached. The
nesting-bonus objective trades ovals for depth rather than buying
both: the three `nest` workers logged more distinct schemes (728/738/
748 vs 500–626) but no deeper ones. That objective is the thing to
replace, not the compute budget.

Artifacts: `compute/found_schemes.json` (committed).
`compute/runs/*.jsonl` (5,435 records) and `compute/data/` stay local
per the runbook. Re-run: `sh compute/run_all.sh`.
