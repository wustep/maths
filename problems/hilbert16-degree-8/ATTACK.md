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

## 2026-08-21 — outside the census: three families, no ninth scheme

With the census triangulations finished, the three obvious ways out are
(i) regular triangulations that are not in the census, (ii) the
non-maximal sign vectors that carry most of the 2,367, and (iii) going
deeper where the census is already known to be thin. All three were run
in C. Nothing new was found, and two of them stop at a definite wall.

**Deep Hamming balls, radius 7.** Seven of the eight schemes certified
above came from Hamming distance ≤ 3 of a single certificate,
`deg8/o22-p15-n07/(6v1(6v1(8))).pcom`, and the eighth from distance 1 of
`deg8/o22-p07-n15/(5v1(5)v1(10)).pcom`. `compute/ballc.c` walks a whole
Hamming ball on a certificate's own integer-certified triangulation —
54,910,660 sign vectors at radius 7, against 164,220 at radius 4 — and
emits one witness per distinct scheme fingerprint.

| seed | sign vectors | distinct schemes | outside the 2,367 |
| --- | --- | --- | --- |
| `(6v1(6v1(8)))` | 54,910,660 | 1,365 | **7** |
| `(5v1(5)v1(10))` | 54,910,660 | 885 | **1** |

Both balls completed. The eight are exactly the eight already
certified — not one more. So:

> Within Hamming distance 7 of the two certificates that produced
> them, the eight new schemes are **all** the schemes outside the
> published 2,367. There is no ninth in that neighbourhood.

The radius-4 pass over *every* census certificate (2,367 seeds, all 184
triangulations, `compute/ball_drive.py`) is running the same way and has
found nothing outside the census so far.

Certificate: `compute/certs/deep_ball_r7.json`.

**Regular triangulations outside the census.** Two samplers, both
certified exactly before any sign vector is evaluated:

* `gen_fast.py` — the vectorised twin of `gen_triang` (validated against
  it triangulation-for-triangulation on a shared rng stream), random
  positive-definite quadratic form plus noise;
* `walk_drive.py` — scale a census lifting by \(10^6\), add integer
  noise, take the lower hull. Regular by construction, re-certified with
  `Fraction` arithmetic, and skipped when it reproduces a census
  triangulation.

The first sampler lands on near-Delaunay triangulations: short edges,
few Harnack splits, twist-rank 6–16, and it **saturates at two
M-schemes** over 3,750 triangulations. The walk reaches twist-rank 25
and is the useful one.

| | walk | random |
| --- | --- | --- |
| certified regular triangulations, none in the census | **325** | **3,750** |
| swept exhaustively over \(\eta+\operatorname{span}\{\delta_S\}\) | all | all |
| sign distributions | 162,571,648 | 7,728,448 |
| twist-rank range | 6–25 | 6–16 |
| distinct M-schemes | 35 | 2 |
| M-schemes outside the paper's 38 | **0** | **0** |

Certificate: `compute/certs/outside_census_sweeps.json`.

**Where this leaves the two open schemes.** ⟨4 ⊔ 1⟨2 ⊔ 1⟨14⟩⟩⟩ and
⟨14 ⊔ 1⟨2 ⊔ 1⟨4⟩⟩⟩ were not hit by any of it. Adding the exhaustive
census result above, the position is now:

* every triangulation of the census — exhaustive, they are not there;
* 4,074 further certified regular triangulations — exhaustive on each,
  not there either;
* the deep-nest certificates to Hamming radius 7 — not there.

That is a much larger silence than before and it is still silence.
None of it is an obstruction: the paper's own Theorem 21 rules out four
of the six open (3,19) schemes as T-curves, and these two are precisely
the ones it does not rule out. Running total at this point in the
session: **704 million** sign distributions, every witness decoded on
the exact Python complex, every claim re-checkable from the
certificates in `compute/certs/`.

### An independent check that does not look at the geometry

`compute/check_rokhlin.py` takes the bracket strings this search reports
and applies the classical congruences for degree \(2k=8\), \(k^2=16\),
with \(p\) the even-depth ovals and \(n\) the odd-depth ovals:

* Rokhlin, for M-curves: \(p-n \equiv k^2 \pmod 8\);
* Gudkov–Krakhnov–Kharlamov, for (M−1)-curves: \(p-n\equiv k^2\pm1\).

All **38** M-schemes of the exhaustive census classification have 22
ovals and satisfy Rokhlin. Every 22-oval scheme thrown up anywhere in
this session's searches satisfies it too, and the five (M−1)-curves
among the eight certified new schemes satisfy Gudkov–Krakhnov–Kharlamov.
Nothing in that check touches a triangulation or a sign vector, so a
scheme that no real degree-8 curve can carry would show up as a failure.
There are none.

It also explains the one pattern visible in the 38. Writing a depth-3
nest as ⟨a ⊔ 1⟨b ⊔ 1⟨c⟩⟩⟩ with \(a+b+c=20\), we get \(p-n = a+c-b =
20-2b\), so Rokhlin forces \(b\equiv 2 \pmod 4\) — and the twelve
depth-3 nests among the 38 have exactly \(b\in\{2,6,10,14\}\). Both
open schemes have \(b=2\), so the congruence permits them; it is not the
obstruction.

## 2026-08-21 — radius-6 balls on the 38 M-certificates: bound ≥ 2,379

Radius-6 balls around all 38 of the paper's 22-oval M-certificates
(`compute/ball_deep.py`, 9,531,040 sign vectors per seed) turned up a
real scheme on the third seed:

**⟨6 ⊔ 1⟨4 ⊔ 1⟨8⟩⟩⟩**, 20 ovals, from
`deg8/o22-p11-n11/(6v1(10v1(4))).pcom`.

It went through the same exact pipeline as the other eight — the
paper's own triangulation and integer `MIN_WEIGHTS`, convexity certified
in `Fraction` arithmetic, the scheme recomputed from scratch by
`tcurve.TCurve` — and it is absent both from our replay of the 2,367 and
from the `.pcom` file names in `deg8.pcoms.txz`.

`cd compute && python3 verify_new.py` → **9/9**.
The census lower bound is now **≥ 2,376**.

Note where it came from: not the ⟨6⊔1⟨6⊔1⟨8⟩⟩⟩ certificate that gave
seven of the first eight — that neighbourhood is exhausted to radius 7 —
but a *different* M-certificate, ⟨6 ⊔ 1⟨10 ⊔ 1⟨4⟩⟩⟩, at a radius the
previous session never reached. The pattern from the first eight holds:
the census is thin around the 22-oval certificates whose scheme is a
deep nest, and the thinness is in the (M−1)- and (M−2)-curves next to
them, not in the M-curves. The remaining 35 M-certificates are still
running.

**Three more, from a second M-certificate.** The same sweep, on
`deg8/o22-p11-n11/(8v1(1)v1(3)v1(7)).pcom`, produced a whole family:

⟨5 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨7⟩⟩ (19 ovals),
⟨6 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨7⟩⟩ (20 ovals),
⟨7 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨7⟩⟩ (21 ovals).

The census has the M-curve ⟨8 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨7⟩⟩ of this family and
none of the three below it — the same shape of gap as the deep nests:
the paper's search finds the M-curve and misses its immediate
non-maximal neighbours.

`cd compute && python3 verify_new.py` → **12/12**, and
`python3 check_rokhlin.py` puts every (M−1)-curve among them inside the
Gudkov–Krakhnov–Kharlamov congruence.

**The census lower bound is now ≥ 2,379.** 7 of the 38 M-certificate
balls are finished; the other 31 are running.

**And four more, from two further M-certificates.**
⟨13 ⊔ 1⟨3 ⊔ 1⟨2⟩⟩⟩ (20) and ⟨4 ⊔ 1⟨2⟩ ⊔ 1⟨13⟩⟩ (21) from
`(5v1(2)v1(13)).pcom`; ⟨3 ⊔ 1⟨4⟩ ⊔ 1⟨11⟩⟩ (20) and
⟨4 ⊔ 1⟨4⟩ ⊔ 1⟨11⟩⟩ (21) from `(5v1(4)v1(11)).pcom`. Same pipeline,
`verify_new.py` → **16/16**. **Bound ≥ 2,383**, with 12 of the 38
M-certificate balls finished.

The shape of the gap is now unmistakable. Every one of the sixteen sits
within Hamming distance ≤ 6 of one of the paper's own 22-oval
certificates, and every one is an (M−1)- or (M−2)-curve obtained by
shrinking one oval of a *nest* in that M-curve. Their search records the
M-curve and misses the schemes immediately below it.

**All 38 M-certificate balls finished.** 362,179,520 sign vectors, every
ball complete, and one last scheme: ⟨4 ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩ (21 ovals) from
`(5v1(3)v1(12)).pcom`. `verify_new.py` → **17/17**, so the census lower
bound is **≥ 2,384**. Certificate:
`compute/certs/mcert_balls_r6.json` (per seed: ball size, completion
flag, distinct schemes, novelties).

| | |
| --- | --- |
| M-certificates swept, radius 6 | **38 of 38**, all complete |
| sign vectors | 362,179,520 |
| schemes outside the published 2,367 | **17** |
| M-certificates that produced one | 7 |

Seven of the 38 M-certificates have a hole next to them; the other 31
have none within radius 6. That is the exhaustive statement — the balls
are complete, so those 31 M-curves have no missing neighbour at distance
≤ 6, and the 17 are all the holes at distance ≤ 6 from any M-curve of
the census.

### The hole map

`compute/hole_map.py` lays the two-nest family ⟨a ⊔ 1⟨b⟩ ⊔ 1⟨c⟩⟩ out as
a grid — `.` in the published 2,367, `N` certified here, `-` in
neither — and the shape of what this session found becomes visible. The
21-oval row \(a=4\) reads

```
  b =   1  2  3  4  5  6  7
        .  N  N  N  N  -  .
```

— the census had the two ends and none of the middle; four of the five
gaps are now filled. The same happens at 20 ovals, \(a=3\).

Four holes have *both* their neighbours in \(b\) realized, which makes
them the sharpest targets left:

| scheme | ovals | \((p,n)\) |
| --- | --- | --- |
| ⟨5 ⊔ 1⟨6⟩ ⊔ 1⟨9⟩⟩ | 22 | (7,15) |
| ⟨4 ⊔ 1⟨6⟩ ⊔ 1⟨9⟩⟩ | 21 | — |
| ⟨1⟨2⟩ ⊔ 1⟨16⟩⟩ | 20 | — |
| ⟨3 ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩ | 20 | — |

A `-` is a target, not a claim: nothing here says any of them is
unrealizable, and the first is an M-scheme, so whether it is even in
Orevkov's 89 is not something this session checked — Table 1 was not
reachable. What can be said is that ⟨5 ⊔ 1⟨6⟩ ⊔ 1⟨9⟩⟩ is not realized
by any of the 184 census triangulations (exhaustively) nor by any of
the 4,074 others swept here, and that its \((p,n)=(7,15)\) class is the
one where the paper T-realizes 8 M-schemes.

## 2026-08-21 — the radius-7 wall on every productive certificate

Each of the seven M-certificates that has a hole beside it was then
swept to Hamming radius 7 — 54,910,660 sign vectors each, **384,374,620**
in total, every ball complete:

| seed | distinct schemes | outside the 2,367 |
| --- | --- | --- |
| `(6v1(6v1(8)))` | 1,365 | 7 |
| `(6v1(10v1(4)))` | 1,302 | 4 |
| `(8v1(1)v1(3)v1(7))` | 1,217 | 3 |
| `(5v1(2)v1(13))` | 898 | 2 |
| `(5v1(5)v1(10))` | 885 | 1 |
| `(5v1(3)v1(12))` | 833 | 1 |
| `(5v1(4)v1(11))` | 637 | 3 |

Radius 7 adds 45.4 million sign vectors per seed over radius 6 and finds
**nothing new**. So the statement closes:

> The seventeen certified schemes are **exactly** the schemes outside
> the published 2,367 within Hamming distance 7 of any M-certificate
> of the census — the seven that have one, and the thirty-one that
> provably do not.

Certificate: `compute/certs/productive_certs_r7.json`.

**The walk finished too.** 859 certified regular triangulations outside
the census, each swept exhaustively over its whole maximal stratum,
together with 3,750 from the uniform sampler: **4,609 non-census
triangulations**, and they realize **exactly the paper's 38 M-schemes**
— all 38, none beyond. An independent set of triangulations reproduces
their list precisely. Certificate:
`compute/certs/outside_census_sweeps.json`.

## 2026-08-21 — radius 4 around all 2,367, and the session total

The systematic pass finished as well: an exhaustive Hamming ball of
radius 4 (164,221 sign vectors) around **every one of the 2,367
certificates**, each on its own integer-certified triangulation.

| | |
| --- | --- |
| certificates used as ball centres | **2,367 of 2,367** |
| sign vectors | **388,711,107** |
| balls that completed | all 219 chunks |
| distinct schemes found | **2,383** |
| of the published 2,367, re-found | **2,367 — all of them** |
| schemes outside the 2,367 | **16** |

So the census is closed under this move up to distance 4: within Hamming
distance 4 of *any* of their certificates there are exactly 2,383 real
schemes, their 2,367 and sixteen of ours. The seventeenth,
⟨6 ⊔ 1⟨4 ⊔ 1⟨8⟩⟩⟩, lies at distance 5 or 6 from every census
certificate — which is why it took the radius-6 pass to see it, and why
"radius 3 or 4" was the wrong stopping point.

Certificate: `compute/certs/census_balls_r4.json`.

### Session total

`compute/report.py` prints this live. Counting *evaluations performed*
(the balls are nested — a radius-7 ball contains the radius-6 and
radius-4 balls of the same seed — so this is not a count of distinct
sign vectors):

| family | units | sign distributions | outside the 2,367 |
| --- | --- | --- | --- |
| every census triangulation, whole maximal stratum | 184 | 230,501,440 | 0 |
| regular triangulations outside the census, same | 4,871 | 708,918,336 | 0 |
| radius-4 balls, all 2,367 certificates | 2,367 seeds | 388,711,107 | 16 |
| radius-6 balls, all 38 M-certificates | 38 | 362,179,520 | 17 |
| radius-7 balls, the 7 productive certificates | 7 | 384,374,620 | 17 |
| radius-6 balls, (M−1)-certificates (running) | 24 of 78 | 228,744,960 | 0 |
| **total evaluations** | | **> 2.3 billion** | **17 distinct** |

Every one of the seventeen is certified by `verify_new.py` on the exact
`Fraction` pipeline, and every 22-oval scheme anywhere in the above
satisfies Rokhlin's congruence. **The census lower bound is ≥ 2,384.**
Hilbert 16(a) in degree 8 is exactly as open as it was: the two
algebraically open deep nests were not reached, and nothing here is an
obstruction.

## 2026-08-21 — the (M−1)-certificates have no holes

The next ring out: an exhaustive radius-6 ball around **every one of the
78 twenty-one-oval certificates** of the census, 9,531,040 sign vectors
each, **743,421,120** in total, all complete.

**Zero schemes outside the 2,367.**

Set against the M-certificates — where 7 of 38 have a hole beside them —
this says something sharper than any of the individual finds. The
census's thinness is not spread through the neighbourhood of its
certificates; it is concentrated at the *top* of the oval count. Their
search reaches the M-curves and then does not descend from all of them,
but once it is at 21 ovals its neighbourhood is closed under this move
out to distance 6.

Certificate: `compute/certs/m1cert_balls_r6.json`.

## 2026-08-21 — thickening the whole maximal stratum

Every ball so far was centred on the *one* sign vector the paper
published per scheme. But a triangulation of twist rank \(r\) carries
\(2^r\) maximal sign distributions, and the seventeen holes are all
non-maximal curves a short distance from a maximal one. The right object
is therefore the whole maximal stratum thickened, not one point of it
thickened.

`compute/thickc.c` walks the entire span \(\eta+\operatorname{span}\{\delta_S\}\)
and, at every point of it, also evaluates all 45 single-coordinate flips
— so it covers every sign vector within Hamming distance 1 of the
*complete* maximal stratum. On a rank-16 triangulation that is 3,014,656
evaluations and it turns up **111–147 distinct schemes** where the pure
span sweep sees 4.

`compute/thick_drive.py` runs it over the census triangulations, those
carrying a 22-oval certificate first, then by increasing rank (the cost
is \(46\cdot 2^r\)). Running.

## 2026-08-23 — the wrap: what survived the restart

The machine restarted mid-run. `thick_drive.py`, its `thickc` workers
and the `dn_sweep.py` deep-nest searchers all died, and the local run
directories (`thick_out`, `dn_runs`) went with them. Nothing was
restarted. This section says what is left, and what is left is only
what is in git.

### The bound is unchanged

`python3 verify_new.py` replays clean: **17/17** certificates verify as
T-curves outside the published 2,367, each on its own integer-certified
triangulation, convexity re-checked in exact rational arithmetic and the
scheme recomputed from scratch. The census union is 2,367 + 17 = 2,384
with no overlap, checked directly against `census_schemes.txt`.

> The §5.3 lower bound of arXiv:2602.06888 v3 stands at **≥ 2,384**.
> Nothing in this session moved it.

`check_rokhlin.py` also replays: all 38 published M-schemes satisfy
Rokhlin's congruence, and every one of our seventeen is consistent with
the congruences that apply to it.

### The thicken, as far as it got

`certs/thick_summary.json` is the whole harvest — a partial run, and the
only file the sweep left behind.

| | |
| --- | --- |
| census triangulations in scope (rank ≤ 20) | 164 of 184 |
| swept, complete | **4** |
| outstanding | 160 |
| ranks completed | 16 only |
| sign distributions evaluated | 12,058,624 |
| distinct schemes per triangulation | 29–147 |
| schemes outside the census | **1** |
| of those, already certified | **1** — ⟨4 ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩ |
| genuinely new | **0** |

The evaluation count is exactly \(4\cdot 46\cdot 2^{16}\), so the four
triangulations really were swept whole. `NEW_candidates` is empty and
`candidate_cert_file` is null: the sweep produced no candidate for
`verify_new.py` to check, so there is nothing to certify. The one
outsider it found is the seventeenth scheme rediscovered from a new
direction, which is a consistency check and not a bound.

Four of 164 is 2.4% of the intended scope, and the four that finished
are all rank 16 — chosen first because they carry 22-oval certificates,
not because they are representative. **Residue.** It says nothing about
the 160 that did not run.

### The deep-nest search left no data at all

`dn_sweep.py` searched Haas *collection* space rather than sign space,
aiming at the two algebraically open deep nests

\[\langle 4\sqcup 1\langle 2\sqcup 1\langle 14\rangle\rangle\rangle
\quad\text{and}\quad
\langle 14\sqcup 1\langle 2\sqcup 1\langle 4\rangle\rangle\rangle .\]

It wrote its hits to JSONL under `dn_runs`, which is gitignored and is
gone. No certificate, no summary, no log survived. There is no partial
result to report and none is claimed: **no data**.

What is committed is the machinery — `deepnest.py` (collection space,
`fast_refine`, laminar zone forests), `dn_charac.py`, `dn_sweep.py`,
`hole_balls.py`, `thick_collect.py`. It runs, and the next session can
start from it rather than from nothing.

### What committed data still had to give

`dn_charac.py` needs no run directory, so it was re-run today against
`certs/mcert_collections.json`. Two things came out of it.

**The 38 re-verify through the other pipeline.** Every one of the 38
published 22-oval certificates, evaluated *from its recorded split
collection* — refine to a unimodular triangulation, build the complex,
read the scheme — returns 22 components and exactly its claimed scheme.
That is an independent confirmation of `mcert_collections.json`: the
earlier check solved \(\eta+\sum\delta_S=\sigma\) in \(\mathbb{F}_2\),
this one throws the sign vector away and rebuilds the curve from the
collection. Collection sizes run 3–15.

**Laminar zone depth does not control nesting depth.** The design idea
behind `deepnest.py` was that the \(Z^+\) zones of a compatible
collection form a laminar family whose depth bounds the nesting depth,
so growing the forest should grow the nest. Measured on the 38, the
bound is far from tight and not even monotone:

| | zone depth | nest depth |
| --- | --- | --- |
| ⟨6 ⊔ 1⟨10 ⊔ 1⟨4⟩⟩⟩, \(\lvert S\rvert=4\) | 2 | **3** |
| ⟨12 ⊔ 2⟨1⟩ ⊔ 1⟨5⟩⟩, \(\lvert S\rvert=15\) | 8 | **2** |

Zone depth spans 1–9 across the 38; nest depth is 2 or 3 and never
more. A collection with zone depth 2 reaches a triple nest and one with
zone depth 8 does not. So the heuristic the beam and annealing modes
were steering by — push the laminar forest deeper — has no purchase on
the quantity that matters. That is the honest explanation for the
searcher's lack of traction, and it is a reason to redesign the score
rather than to buy more compute.

### Where the two open nests actually sit

For a depth-3 M-scheme ⟨\(a\) ⊔ 1⟨\(b\) ⊔ 1⟨\(c\)⟩⟩⟩ of degree 8 the
oval count forces \(a+b+c=20\), and counting by depth gives
\(p=a+c+1\), \(n=b+1\). Rokhlin's congruence \(p-n\equiv k^2 \equiv 0
\pmod 8\) for \(k=4\) then reads \(20-2b\equiv 0\), i.e.

\[b \equiv 2 \pmod 4, \qquad b\in\{2,6,10,14,18\}.\]

The 12 depth-3 schemes among the published 38 have \(b\in\{2,6,10,14\}\)
and nothing else — so the observed pattern is exactly the congruence,
with no residual structure on top of it. The missing value \(b=18\) is
\((p,n)=(3,19)\), which is precisely the class their Theorem 21 proves
is not T-realizable. The depth-3 row is therefore complete in \(b\):
every value a T-curve can have, a published T-curve has.

Both open nests have \(b=2\), \((p,n)=(19,3)\), and that row *is*
T-realizable — the census contains two of its members:

| \(a\) | \(c\) | scheme | status |
| --- | --- | --- | --- |
| 4 | 14 | ⟨4 ⊔ 1⟨2 ⊔ 1⟨14⟩⟩⟩ | **algebraically open** |
| 10 | 8 | ⟨10 ⊔ 1⟨2 ⊔ 1⟨8⟩⟩⟩ | published T-curve |
| 14 | 4 | ⟨14 ⊔ 1⟨2 ⊔ 1⟨4⟩⟩⟩ | **algebraically open** |
| 17 | 1 | ⟨17 ⊔ 1⟨2 ⊔ 1⟨1⟩⟩⟩ | published T-curve |

So the target is not a new \((p,n)\) class and not a new nesting depth.
It is a move *along* an occupied row: same \(b\), different split of the
remaining 18 ovals between outside and centre. No congruence, no Bezout
count and nothing in this folder's data separates \(a=4\) or \(a=14\)
from \(a=10\) or \(a=17\). That is the sharpest form of the target this
attack reached, and it is a statement about where to look, not a claim
that either is realizable.

### Status

Hilbert 16(a) in degree 8 is exactly as open as it was on 2026-08-21.
The dent is the seventeen schemes and the bound ≥ 2,384; both replay.
The whole-stratum thicken is 4 of 164 and is **residue**; the deep-nest
search is **no data**. Neither is an obstruction and neither is a lower
bound.

Replay: `cd problems/hilbert16-degree-8/compute && python3 verify_new.py`
then `python3 check_rokhlin.py` and `python3 dn_charac.py`.

## 2026-08-27 — q1: leftover thicken prefix and the (19,3) row

Grok 4.6. Record re-fetched first: arXiv:2602.06888 is still **v3,
27 Jul 2026**; §5.3 still 2,367 nonempty T-schemes; Theorem 21
unchanged. Parent `sh run_all.sh` this session: 2,367/2,367 census,
17/17 outside it, Haas 38/38. Bound still ≥ 2,384.

Code in `compute/q1/`. Replay: `sh q1/run_all.sh`.

### The bound did not move

`NEW_candidates` is empty. The only scheme the leftover thicken
found outside the published 2,367 is ⟨4 ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩, already
one of the seventeen. No open nest appeared, even as a PL curve.

### Finished searches

| search | evals | result |
| --- | --- | --- |
| radius-4 balls, all 237 twenty-oval census certs | 38,920,377 | 0 novel |
| odd collections, size ≤ 3 | 368,936 | 12 known M-schemes, 0 hits |
| pinned even-split BFS, 200,000 collections | 200,000 | the five published (19,3) M-schemes only; queue left 196,799 (**residue**) |
| one-split add/drop/swap around all 38 M-collections | 28,861 | exactly those 38, 0 new, 0 hits |
| nested odd pairs on the five (19,3) collections | 122 | 0 hits; the a=10 nest admits **no** compatible nested odd pair |
| radius-1 thicken, every census triangulation of rank ≤ 16 | 130,151,296 | 107/107 complete; novel vs census = the already-certified ⟨4 ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩ |

Certificates: `compute/q1/certs/m2_balls_r4.json`,
`odd_skel.json`, `even_pinned.json`, `dn_nbhd.json`,
`odd_cancel.json`, `thick_r1_rank_le16.json`.

The 4-of-164 leftover from 2026-08-23 is no longer the state of the
cheap ranks. Ranks 6–16 are a **finished prefix**. Ranks 17–20 (57
triangulations of the original 164) were still running at write-up;
until they all have a `complete` record that part is **residue**.

### What the (19,3) row actually does

Even twists of the published (19,3) collections, including the
Prop 31 bow-tie, stay on the five known (19,3) M-schemes
⟨18⊔1⟨3⟩⟩, ⟨17⊔1⟨1⟩⊔1⟨2⟩⟩, ⟨17⊔1⟨2⊔1⟨1⟩⟩⟩, ⟨16⊔3⟨1⟩⟩,
⟨10⊔1⟨2⊔1⟨8⟩⟩⟩. One even drop from the a=10 nest jumps to the
a=17 nested box; there is no intermediate a=11…16. The bow-tie
splits are even (parity includes (0,0)).

The published a=10 nest is already a 12-split collection with
**seven odd** splits. Size ≤ 3 odd enumeration cannot see it, and
adding a nested odd pair to it is impossible (zero compatible
pairs). The open nests ⟨4⊔1⟨2⊔1⟨14⟩⟩⟩ and ⟨14⊔1⟨2⊔1⟨4⟩⟩⟩ are
not one add/drop/swap from any of the 38 published M-collections
and not a canceling-odd-pair from any published (19,3)
collection. That is a distance statement, not an obstruction.

A hit in collection space would still need `haas.regularize` plus
exact `tcurve.check_convexity` (Orevkov arXiv:2607.19457: a
non-regular patchwork can be algebraically unrealisable).

### Status

Hilbert 16(a) in degree 8 remains open. The dent is still the
seventeen schemes and the bound ≥ 2,384; both replay. No new
scheme, no deep-nest decision. The leftover thicken is a finished
prefix through rank 16 and residue past that.

Replay: `cd problems/hilbert16-degree-8/compute && sh run_all.sh &&
sh q1/run_all.sh && python3 q1/collect.py`.
