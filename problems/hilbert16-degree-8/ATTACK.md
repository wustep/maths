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

## 2026-08-21 (second session) — finishing the ball phase

Fable's ball/beam/window tasks (`compute/nest_search.py`,
`compute/make_tasks.py`) were left half-run. Resumed rather than
redone: 24 task files, each an exhaustive Hamming-ball enumeration
(radius 4 around eleven key deep-nest certificates, radius 3 around
every other seed) on the census's *own* certified triangulations, with
every distinct scheme diffed against the replayed 2,367.

That is where the dent came from.

## 2026-08-21 — dent (C): eight T-curves outside the published 2,367

**Eight real schemes are realizable as T-curves and are not among the
2,367 of arXiv:2602.06888 v3.**

| scheme | ovals | flips from | seed scheme |
| --- | --- | --- | --- |
| ⟨4 ⊔ 1⟨5⟩ ⊔ 1⟨10⟩⟩ | 21 | 1 | ⟨5 ⊔ 1⟨5⟩ ⊔ 1⟨10⟩⟩ |
| ⟨5 ⊔ 1⟨6 ⊔ 1⟨7⟩⟩⟩ | 20 | 1 | ⟨6 ⊔ 1⟨6 ⊔ 1⟨8⟩⟩⟩ |
| ⟨5 ⊔ 1⟨6 ⊔ 1⟨8⟩⟩⟩ | 21 | 1 | ⟨6 ⊔ 1⟨6 ⊔ 1⟨8⟩⟩⟩ |
| ⟨6 ⊔ 1⟨5 ⊔ 1⟨8⟩⟩⟩ | 21 | 1 | ⟨6 ⊔ 1⟨6 ⊔ 1⟨8⟩⟩⟩ |
| ⟨6 ⊔ 1⟨6 ⊔ 1⟨6⟩⟩⟩ | 20 | 1 | ⟨6 ⊔ 1⟨6 ⊔ 1⟨8⟩⟩⟩ |
| ⟨6 ⊔ 1⟨6 ⊔ 1⟨7⟩⟩⟩ | 21 | 1 | ⟨6 ⊔ 1⟨6 ⊔ 1⟨8⟩⟩⟩ |
| ⟨6 ⊔ 1⟨8 ⊔ 1⟨4⟩⟩⟩ | 20 | 3 | ⟨6 ⊔ 1⟨6 ⊔ 1⟨8⟩⟩⟩ |
| ⟨6 ⊔ 1⟨9 ⊔ 1⟨4⟩⟩⟩ | 21 | 2 | ⟨6 ⊔ 1⟨6 ⊔ 1⟨8⟩⟩⟩ |

Each witness is a handful of sign flips away from one of the paper's
own 22-oval certificates — `deg8/o22-p07-n15/(5v1(5)v1(10)).pcom` and
`deg8/o22-p15-n07/(6v1(6v1(8))).pcom` — so each inherits *their*
triangulation and *their* integer `MIN_WEIGHTS`. Nothing about the
geometry is ours to get wrong. For all eight:

| check | result |
| --- | --- |
| triangulation primitive, all 45 points, edge-manifold | pass |
| convexity of their `MIN_WEIGHTS`, exact `Fraction` arithmetic | pass |
| real scheme recomputed from scratch (`tcurve.TCurve`) | matches the claim |
| in `census_schemes.txt` (our replay of their 2,367) | **no**, all eight |
| a matching `.pcom` file name in their `deg8.pcoms.txz` | **no**, all eight |

Their §5.3 says 2,367 "as the search is not exhaustive, this is a
lower bound". The bound is now **≥ 2,375**.

Seven of the eight are depth-3 nests ⟨a ⊔ 1⟨b ⊔ 1⟨c⟩⟩⟩ neighbouring
their (15,7) M-curve ⟨6⊔1⟨6⊔1⟨8⟩⟩⟩ — i.e. the census is thin exactly
around the deep-nest M-certificates, which is where the two open
schemes live. The eighth fills \(a=4\) in ⟨a ⊔ 1⟨5⟩ ⊔ 1⟨10⟩⟩, a
family their census has at \(a=1,2,5\) and not at \(a=3,4\).

Certificates: `compute/certs/new_schemes.json`.
Re-verify: `cd compute && python3 verify_new.py` (self-contained; the
cross-check also runs against `data/deg8.pcoms.txz` when present).

This is a dent in the census count only. It says nothing about the six
algebraically open M-schemes.

## 2026-08-21 — the real change: Haas zone decompositions

Re-reading arXiv:2602.06888 v3 properly — Section 3, not just the
Theorem 21 headline — changed the attack completely. Their Theorem 13
(Haas): a T-curve is **maximal** iff some collection 𝔖 of compatible
Harnack splits is valid for it; and §3.5: the real scheme
\(\mathcal{C}(\mathfrak{S})\) depends only on 𝔖, not on which
unimodular triangulation refines it.

Two consequences the previous session did not have:

1. Maximal degree-8 T-curves are a *finite combinatorial* object —
   collections of Harnack splits — not a needle in \(2^{45}\) signs.
2. A surgical twist adds the affine \(\mathbb{F}_2\) function
   \(\epsilon+ix+jy\) on \(Z^+\) (Lemma 14 rewritten via
   \(\sigma(s_{ab}(x,y))=\sigma(x,y)+ax+by\)). Twists therefore
   **commute and add**, so on a fixed triangulation \(\mathcal{T}\)
   every maximal sign distribution lies in the affine subspace
   \[\eta \;+\; \operatorname{span}_{\mathbb{F}_2}\{\delta_S : S \text{ a Harnack split with edges in } \mathcal{T}\}.\]

`compute/haas.py` implements splits, zones, compatibility, twists and
refinement from scratch; `compute/zone_search.py` sweeps the subspace.

**Validation, before any search.** Three independent checks, all pass:

| check | result |
| --- | --- |
| Harnack signs \(\eta(x,y)=(x+1)(y+1)\) on a refinement | ⟨18 ⊔ 1⟨3⟩⟩ (Prop 10) |
| all **1,254** Harnack splits of \(T_8\), one at a time | **1,254 / 1,254 give 22 ovals** |
| the 38 published 22-oval certificates, solved for 𝔖 | **38 / 38 decompose** |

The third is the one that matters: for every M-curve certificate the
paper publishes, solving the \(\mathbb{F}_2\) system
\(\eta+\sum_{S\in\mathfrak{S}}\delta_S=\sigma\) over the splits carried
by that certificate's triangulation recovers an explicit collection
(sizes 3–15). Their data and this implementation of Haas' theorem agree
on all 38.

Counts for \(T_8\): 1,254 Harnack splits (117 simple, 1,137 double;
189 odd, 1,065 even), 381,957 compatible pairs, greedy maximal
compatible collections of size 15–24. The 184 distinct triangulations
of the census carry 6–40 splits each, of twist-rank 6–26.

**Why this is a better search.** The previous session's annealer drew
\(2.1\times10^6\) sign vectors and reached 22 ovals twice. In the
first pilot sweep here, **20,480 of 20,480 evaluations were 22-oval
M-curves** — a 100% maximal hit rate, because the subspace *is* the
maximal stratum. Every evaluation lands somewhere in Orevkov's 89-row
Table 1.

## 2026-08-21 — sweeps and residue

**Exhaustive maximal-stratum sweeps.** `compute/zone_search.py` mode
`spanall` walked the census triangulations in order of twist-rank and
swept the *entire* affine subspace \(\eta+\operatorname{span}\{\delta_S\}\)
of each. A finished triangulation is an exhaustive classification of
the M-curves it supports — the first time that question has been
answered for degree 8 rather than sampled.

| | |
| --- | --- |
| certified regular triangulations swept exhaustively | 66 of 184 (twist-rank 6–15) |
| sign distributions evaluated in those sweeps | 666,688 |
| fraction of evaluations that were 22-oval M-curves | 100% |
| distinct M-schemes realized | 30 |
| of the paper's 38 T-realized M-schemes | **30 / 38** |
| M-schemes outside the paper's 38 | **0** |
| hits among the six algebraically open | **0** |
| schemes missing from the 2,367 | 0 |

Plus a dedicated exhaustive sweep of the deep-nest triangulation
carrying `(10v1(2v1(8)))` and `(17v1(2v1(1)))` (twist-rank 19): **15**
distinct M-schemes, including both deep nests, all already in the 38.

The sweeps stopped at rank 15 of the 6–26 range on the clock; the
remaining 118 triangulations, and every triangulation outside the
census, are untouched. **This is not an obstruction.** It is an
exhaustive answer for 66 specific triangulations — and those 66 are
precisely the ones the paper's own search already mined, so re-finding
their M-schemes and nothing else is the expected outcome.

**Ball phase (Fable's design, resumed).** Exhaustive Hamming balls
(radius 4 around eleven key deep-nest certificates, radius 3 around
every other seed) on the census's certified triangulations:
11 of 24 task files finished, **3,558,520** sign evaluations, and the
eight new schemes above. Every logged witness was re-verified on the
exact `Fraction` pipeline; no witness was rejected, so the fast
evaluator and the exact engine still agree everywhere.

Where the deep-nest family stands. Writing the family as
⟨a ⊔ 1⟨2 ⊔ 1⟨c⟩⟩⟩, the balls reached
\((a,c) \in \{(1,15),(8,8),(9,7),(9,8),(10,6),(10,7),(10,8),(11,5),(12,4),(14,2),(15,1),(15,2),(16,0),(16,1),(17,0),(17,1),(18,0)\}\).
The two open M-schemes are \((4,14)\) and \((14,4)\) with \(a+c=18\);
the only \(a+c=18\) points reached are \((10,8)\) — the census's own —
and none other. Silence, not a bound.

**What is and is not claimed.**

- Claimed, and certified: eight real schemes realizable as degree-8
  T-curves that are absent from the published 2,367; a correct,
  tested implementation of Haas' criterion that decomposes all 38
  published M-certificates; exhaustive M-curve classification for 67
  specific certified triangulations.
- Not claimed: anything about the six algebraically open M-schemes;
  any obstruction; any statement about triangulations not swept.
  Hilbert 16(a) in degree 8 is exactly as open as it was.

**Local artifacts.** `compute/runs2/` (ball phase),
`compute/runs3/` (zone sweeps) and `compute/data/` stay local per the
runbook; `compute/nest_tri.json` and `compute/nest_tri_certs.json` are
Fable's scratch from the deep-nest-triangulation selection step and are
not read by any script here. Rebuild the derived inputs with
`python3 prep.py`; re-run everything with `sh run_all.sh`.

## 2026-08-21 — the census triangulations, finished

The zone sweeps above stopped at twist-rank 15 because Python could not
reach the rest: the 118 remaining census triangulations carry
\(2^{16}\)–\(2^{26}\) maximal sign distributions each, 229.5 million in
total. `compute/zonec.c` moves the evaluator into C — the same rhombus
complex, the same union–find, the same nesting logic as
`fastcx.Complex.eval`, with the bracket rendering replaced by a 128-bit
canonical hash so a sweep can deduplicate schemes without building
strings. It runs at ~45,000 sign distributions per second per core,
about 45× the Python path.

**Cross-check before use.** `compute/validate_zonec.py` enumerates the
whole subspace of one triangulation in Python and in C and compares.
On the rank 6, 10, 12 and 13 census triangulations the two agree on
every count that matters — valid schemes, 22-oval count, and the exact
*set* of scheme strings. The C fingerprint is therefore exactly as fine
as the real scheme, so the C sweep loses nothing. The scheme of record
is still recomputed in Python from the emitted witness, and anything
outside the census still goes to the exact `Fraction` verifier.

**All 184 census triangulations are now swept exhaustively.**

| | |
| --- | --- |
| census triangulations classified exhaustively | **184 of 184** (twist-rank 6–26) |
| maximal sign distributions evaluated | **230,501,440** |
| of those that were 22-oval M-curves | **230,501,440 — every one** |
| distinct M-schemes realized | **38** |
| the paper's 38 T-realized M-schemes | **all 38, exactly** |
| M-schemes outside the paper's 38 | **0** |
| hits among the six algebraically open | **0** |
| most M-schemes on a single triangulation | 24 |

Certificate: `compute/certs/census_span_classification.json` (per
triangulation: rank, split count, evaluation count, scheme list).
Reproduce with `cd compute && python3 zonec_drive.py <w> 3 6 runs4`.

What this is. Because every maximal sign distribution on a fixed
triangulation \(\mathcal{T}\) lies in \(\eta+\operatorname{span}\{\delta_S\}\)
(Haas, paper Thm 13), a finished triangulation is an *exhaustive*
classification of the M-curves it supports. So this is a complete
answer to a question that was previously only sampled:

> The 184 triangulations underlying the published degree-8 census
> support exactly the paper's 38 M-schemes and no others. In
> particular **no census triangulation supports any of the six
> algebraically open M-schemes**, including
> ⟨4 ⊔ 1⟨2 ⊔ 1⟨14⟩⟩⟩ and ⟨14 ⊔ 1⟨2 ⊔ 1⟨4⟩⟩⟩.

What this is not. It is not an obstruction and not a bound. Degree-8
has vastly more primitive regular triangulations than these 184; the
statement is about a specific finite family. It does say the previous
session's "30 of 38, 0 new" was the head of exactly this pattern, and
that no amount of further work *on census triangulations* will move the
M-scheme question. The 100% maximal rate is also the largest test Haas'
criterion has been put to here: 230.5 million predicted M-curves,
230.5 million confirmed.
