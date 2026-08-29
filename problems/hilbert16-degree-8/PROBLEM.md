# Hilbert 16(a) for degree 8 — real schemes of plane octics

- Slug: `hilbert16-degree-8`
- List: Hilbert 16 (first part), Smale 13 (1998)
- Solver: Claude Fable, then Claude Opus 5 (Claude Code)
- Status: open. Degree 8 is the first degree where the isotopy
  classification is unfinished. Six M-schemes are algebraically
  undecided; the non-maximal census is a lower bound, and we moved
  that lower bound by one (dent C below). Hilbert 16(a) itself is
  untouched.
- Area: Real algebraic geometry / topology of real plane curves
- Sources: Orevkov GAFA 12 (2002); Itenberg–Viro (1996); Viro
  arXiv:math/0611382; Geiselmann–Joswig–Kastner–Mundinger–Pokutta–
  Spiegel–Wack–Zimmer arXiv:2602.06888 v3 and arXiv:2604.09221;
  Gabard arXiv:1310.1865
- Started: 2026-08-21

## Statement

Classify the real schemes (ambient isotopy types in \(\mathbb{RP}^2\))
of nonsingular real plane projective curves of degree 8. A degree-8
curve has at most 22 ovals (Harnack); curves attaining the bound are
M-curves. The classification is complete through degree 7 (Gudkov for
6, Viro for 7). For degree 8 it is not.

Published record, fetched and replayed 2026-08-21 (see RESEARCH.md):

- **M-schemes (22 ovals).** After Gudkov–Rokhlin, Bezout-with-a-conic,
  and the Fiedler–Viro parity restrictions, 104 candidate M-schemes
  remain. Orevkov (GAFA 2002, Table 1) determined that exactly 89 are
  realizable by real pseudo-holomorphic (flexible) M-curves; 83 of
  those are realized by genuine algebraic curves, and six remain open:
  \(\langle 4\sqcup 1\langle 2\sqcup 1\langle 14\rangle\rangle\rangle\),
  \(\langle 14\sqcup 1\langle 2\sqcup 1\langle 4\rangle\rangle\rangle\)
  (both \((p,n)=(19,3)\)), and
  \(\langle 1\sqcup 1\langle 1\rangle\sqcup 1\langle 18\rangle\rangle\),
  \(\langle 1\sqcup 1\langle 4\rangle\sqcup 1\langle 15\rangle\rangle\),
  \(\langle 1\sqcup 1\langle 7\rangle\sqcup 1\langle 12\rangle\rangle\),
  \(\langle 1\sqcup 1\langle 9\rangle\sqcup 1\langle 10\rangle\rangle\)
  (all \((p,n)=(3,19)\)). All six are pseudo-holomorphically
  realizable (Orevkov Thm 1.2b), so no purely topological obstruction
  can kill them.
- **T-curves (combinatorial patchworking).** Geiselmann et al.,
  arXiv:2602.06888 v3 (July 2026): 2,367 distinct nonempty degree-8
  real schemes realized as T-curves (explicitly a lower bound, search
  not exhaustive); certificates published in
  `dmg-lab/CombinatorialPatchworking`. Of the 89 M-schemes, 38 are
  realized as T-curves, the 12 with \((p,n)=(3,19)\) — including four
  of the six open ones — are *provably not* T-curves (their Theorem
  21), and 39 are undecided as T-curves, among them the two open
  deep-nest schemes.

## What would count as a dent

**(A)** A certified combinatorial patchwork (primitive convex
triangulation of \(T_8\) plus signs, exact convexity certificate,
independently computed isotopy type) realizing one of the two open
M-schemes with \((p,n)=(19,3)\). By Viro's theorem that would settle
their algebraic realizability. The four \((p,n)=(3,19)\) open schemes
are unreachable by this stack (Theorem 21 of arXiv:2602.06888v3).

**(B)** A certified exclusion of one of the six. Needs link-theory /
braid-theoretic obstructions, not this stack; not attempted.

**(C)** A certified T-curve whose scheme is not among the published
2,367 — in particular any of the 39 M-schemes undecided as T-curves.
That is a verified finite improvement of a documented lower bound.

Replaying known constructions is not a dent. Search residue is not an
obstruction. SAT/annealing failure to find a scheme is not a bound.


## Outcome (2026-08-21)

**Replay.** All 2,367 certificates of arXiv:2602.06888 v3 pass an
exact from-scratch verifier (convexity certified in rational
arithmetic, isotopy type recomputed via a double-cover argument), and
the 22-oval subset reproduces exactly the 38 bold rows of their
Table 1.

**Dent (C).** **Seventeen** real schemes are realizable as degree-8
T-curves and are **not** among their 2,367, so their §5.3 lower bound
("the search is not exhaustive") becomes **≥ 2,384**:

⟨13 ⊔ 1⟨3 ⊔ 1⟨2⟩⟩⟩, ⟨3 ⊔ 1⟨4⟩ ⊔ 1⟨11⟩⟩, ⟨4 ⊔ 1⟨2⟩ ⊔ 1⟨13⟩⟩, ⟨4 ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩, ⟨4 ⊔ 1⟨4⟩ ⊔ 1⟨11⟩⟩, ⟨4 ⊔ 1⟨5⟩ ⊔ 1⟨10⟩⟩, ⟨5 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨7⟩⟩, ⟨5 ⊔ 1⟨6 ⊔ 1⟨7⟩⟩⟩, ⟨5 ⊔ 1⟨6 ⊔ 1⟨8⟩⟩⟩, ⟨6 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨7⟩⟩, ⟨6 ⊔ 1⟨4 ⊔ 1⟨8⟩⟩⟩, ⟨6 ⊔ 1⟨5 ⊔ 1⟨8⟩⟩⟩, ⟨6 ⊔ 1⟨6 ⊔ 1⟨6⟩⟩⟩, ⟨6 ⊔ 1⟨6 ⊔ 1⟨7⟩⟩⟩, ⟨6 ⊔ 1⟨8 ⊔ 1⟨4⟩⟩⟩, ⟨6 ⊔ 1⟨9 ⊔ 1⟨4⟩⟩⟩, ⟨7 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨7⟩⟩.

Each witness sits on one of the paper's own triangulations with their
integer `MIN_WEIGHTS`, so nothing about the geometry is ours to get
wrong: the weights are re-certified exactly in rational arithmetic, the
scheme is recomputed from scratch, and absence is checked both against
our replay of the 2,367 and against the `.pcom` file names in their
archive. Certificate `compute/certs/new_schemes.json`, checked by
`compute/verify_new.py` (17/17).

**Haas zone decompositions (new machinery).** `compute/haas.py`
implements Harnack splits, zones, compatibility and surgical twists
for \(T_8\) — 1,254 splits, 381,957 compatible pairs. Because a twist
adds a fixed \(\mathbb{F}_2\) vector, every maximal sign distribution
on a fixed triangulation lies in an affine subspace of dimension
\(\le 26\), which `compute/zone_search.py` sweeps exhaustively. Checks:
each of the 1,254 splits alone gives a 22-oval curve, and all **38**
published 22-oval certificates decompose into explicit split
collections (`compute/certs/mcert_collections.json`, rebuilt by
`compute/prep.py`).

**No M-scheme dent.** All 184 triangulations of the census are now
swept exhaustively (230,501,440 maximal sign distributions, all of them
22-oval M-curves): they realize exactly the paper's 38 M-schemes and
nothing else, so no census triangulation carries either open deep nest.
A further 4,609 certified regular triangulations outside the census,
each also swept exhaustively, add no M-scheme either
(`compute/certs/outside_census_sweeps.json`). Exhaustive per
triangulation, not exhaustive over triangulations — residue, not an
obstruction. Counts and certificates in ATTACK.md.

Replay: `cd problems/hilbert16-degree-8/compute && sh run_all.sh`

## Close (2026-08-23)

The bound is unchanged. `compute/verify_new.py` replays 17/17, so the
census lower bound stays **≥ 2,384**, and `compute/check_rokhlin.py`
replays with it.

Two searches were in flight when the machine restarted and neither
finished. Thickening the whole Haas maximal stratum
(`compute/thickc.c`) completed 4 of the 164 census triangulations in
scope, 12,058,624 sign distributions, and found one scheme outside the
census — ⟨4 ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩, already one of the seventeen. No new
candidate, so nothing to certify: residue
(`compute/certs/thick_summary.json`). The search in Haas collection
space for the two open deep nests (`compute/dn_sweep.py`) lost its run
directory in the restart and left no data at all; none is claimed.

What committed data still yielded: all 38 published 22-oval
certificates re-verify through the collection pipeline rather than the
sign-vector one (`compute/dn_charac.py`), and laminar zone depth turns
out not to bound nesting depth usefully — zone depth 2 reaches a triple
nest, zone depth 8 does not — which is why that searcher had no
traction. For a depth-3 M-scheme ⟨a ⊔ 1⟨b ⊔ 1⟨c⟩⟩⟩ Rokhlin forces
\(b\equiv 2 \pmod 4\); the published 38 realize \(b\in\{2,6,10,14\}\)
and the missing \(b=18\) is exactly the \((p,n)=(3,19)\) class their
Theorem 21 excludes from T-curves. Both open nests have \(b=2\), a row
that already contains two published T-curves, so the target is a move
along an occupied row rather than a new class. Details in ATTACK.md.

Hilbert 16(a) in degree 8 remains open.

## Close (2026-08-27)

The bound is unchanged. Parent `verify_new.py` still replays 17/17, so
the census lower bound stays **≥ 2,384**. q1 produced no candidate
for a new scheme.

The leftover whole-stratum thicken is no longer 4 of 164. Radius 1
around the maximal Haas stratum finished every census triangulation
of twist-rank at most 20 (164/164, 1,438,512,000 sign distributions,
exactly \(46\cdot 2^r\) on each,
`compute/q1/certs/thick_r1_rank_le20.json`). Every scheme outside
the published 2,367 is already one of the seventeen. Neither open
nest appeared. That is a finished sweep of the intended leftover,
not a lower bound. The twenty census triangulations of rank 21–26
were never in that leftover.

Collection space: the one-split neighbourhood of all 38 published
M-collections is exactly those 38 (`compute/q1/certs/dn_nbhd.json`).
The two-split ladder around all twelve depth-3 M-collections is
also finished and adds nothing (`compute/q1/certs/dn_ladder.json`).
Nested odd pairs on the five published (19,3) collections hit
neither open nest; the a=10 nest admits no compatible nested odd
pair. Even-only walks stay on the five known (19,3) M-schemes.
Neither open nest is decided.

Replay: `cd problems/hilbert16-degree-8/compute && sh run_all.sh &&
sh q1/run_all.sh && python3 q1/collect.py`

Hilbert 16(a) in degree 8 remains open.

## Close (2026-08-27, leftover rank 21)

The bound is unchanged. Parent `verify_new.py` still replays 17/17, so
the census lower bound stays **≥ 2,384**. No q2 candidate for a new
scheme.

Radius 1 around the maximal Haas stratum finished every leftover
census triangulation of twist-rank 21 (5/5, 482,344,960 sign
distributions, exactly \(46\cdot 2^{21}\) on each,
`compute/q2/certs/thick_r1_rank_21.json`). Every scheme found is
already in the published 2,367. Neither open nest appeared. That is
a finished sweep of this rank, not a lower bound. Fifteen leftover
triangulations of ranks 22–26 are still open (**residue**).

Collection space: a 400,000-step even-split BFS stays on the five
published (19,3) M-schemes (`compute/q2/certs/even_pinned.json`).
Three-split moves around those five collections produced 30 known
schemes and neither nest; the time cap stopped the last seed
(`compute/q2/certs/ladder3.json`). Odd collections of size 4, as
far as the snapshot ran, stay on the same twelve M-schemes as size
≤ 3 (`compute/q2/certs/odd_skel4.json`). Neither open nest is
decided.

Replay: `cd problems/hilbert16-degree-8/compute && sh run_all.sh &&
sh q2/run_all.sh && python3 q2/collect.py`

Hilbert 16(a) in degree 8 remains open.

## Close (2026-08-29, leftover ranks 22–26)

The bound is unchanged. Parent `verify_new.py` still replays 17/17, so
the census lower bound stays **≥ 2,384**. No q3 candidate for a new
scheme.

Radius 1 around the maximal Haas stratum finished every leftover
census triangulation of twist-rank 22–26 (15/15, 8,682,209,280
sign distributions, exactly \(46\cdot 2^r\) on each,
`compute/q3/certs/thick_r1_rank_22_26.json`). The rank-26
certificate is four shards whose evaluation counts sum to
\(46\cdot 2^{26}\). Every scheme found is already in the published
2,367. Neither open nest appeared. That is a finished sweep of
this leftover, not a lower bound.

Odd collections of size 4 finished and stay on the same twelve
M-schemes as size ≤ 3 (`compute/q3/certs/odd_skel4.json`).
Neither open nest is decided.

Replay: `cd problems/hilbert16-degree-8/compute && sh run_all.sh &&
sh q3/run_all.sh && python3 q3/collect.py`

Hilbert 16(a) in degree 8 remains open.
