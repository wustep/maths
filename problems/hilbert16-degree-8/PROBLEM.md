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

**Dent (C).** ⟨4 ⊔ 1⟨5⟩ ⊔ 1⟨10⟩⟩ (21 ovals) is realizable as a
T-curve and is **not** among their 2,367. The witness is one sign
flip, at \((6,1)\), from their own certificate
`deg8/o22-p07-n15/(5v1(5)v1(10)).pcom`, so it uses their triangulation
and their integer `MIN_WEIGHTS`; those weights are re-certified
exactly, and the scheme is recomputed from scratch. Their §5.3 states
2,367 as a lower bound ("the search is not exhaustive"); it is now
**≥ 2,368**. Certificate `compute/certs/new_schemes.json`, checked by
`compute/verify_new.py`.

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

**No M-scheme dent.** The sweeps re-find the paper's 38 M-schemes and
nothing outside them; neither open \((19,3)\) deep nest appeared.
Exhaustive per triangulation, not exhaustive over triangulations — so
this is residue, not an obstruction. Counts in ATTACK.md.

Replay: `cd problems/hilbert16-degree-8/compute && sh run_all.sh`
