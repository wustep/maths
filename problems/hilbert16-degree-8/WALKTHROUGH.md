# Walkthrough — degree-8 T-curves

## 0. What was actually missing

Not a cleverer search — an independent verifier and the actual
current record. The prompt's leftover was stale twice over: it said
"2359 realized, 53 non-maximal schemes with no T-curve witness",
but the April ICMS paper's 53 are *maximal* schemes, and the July v3
of the companion (arXiv:2602.06888) had already moved the counts to
2,367 realized, 38 of 89 M-schemes T-realized, and — the fact that
reshapes the whole attack — Theorem 21: a maximal degree-8 T-curve
has \((p,n)\in\{(19,3),(15,7),(11,11),(7,15)\}\). Four of the six
algebraically open M-schemes have \((p,n)=(3,19)\). So combinatorial
patchworking, the intended stack, is *provably useless* for four of
the six targets, and the entire T-curve attack surface is: the two
deep-nest schemes ⟨4⊔1⟨2⊔1⟨14⟩⟩⟩, ⟨14⊔1⟨2⊔1⟨4⟩⟩⟩, plus the 39
M-schemes and unknown non-maximal schemes missing from their census.
Nobody knew this in the room until the papers were actually fetched.

## 1. Named false starts

- **The unit-coefficient conic.** Sanity test asserted that all-plus
  signs in degree 2 give an empty curve, because
  \(1+x+y+x^2+xy+y^2\) has negative discriminant. The engine said
  ⟨1⟩. The engine was right: Viro's polynomial is
  \(1+t(x+y)+t^3(x^2+xy+y^2)\) with the lifting in the exponents, and
  on \(y=0\) its discriminant \(t^2(1-4t)\) is positive for small
  \(t\) — the conic is nonempty.
- **Rooting the nesting tree at "the outside".** The planar instinct
  — root the oval-containment forest at the unbounded region — has no
  meaning in \(\mathbb{RP}^2\); there is no unbounded region and no a
  priori marked point. First plan (root at a corner of the rhombus)
  is simply wrong: that region can sit inside ovals.
- **Which Harnack sign rule?** Itenberg–Viro print "− iff both
  coordinates even", other sources "− iff both odd". Ten minutes lost
  to the worry; the two differ by \((x,y)\mapsto(-x,-y)\) composed
  with a global sign flip, so they give the same curve up to isotopy.
  The engine reproduces ⟨18⊔1⟨3⟩⟩ from either.

## 2. The useful failure

The conic false start is the one that taught something: a T-curve is
the curve of the *deformed* polynomial at small \(t\), and no
intuition about unit-coefficient polynomials transfers. After that,
every sanity expectation was taken from published statements
(Prop 10 of arXiv:2602.06888 v3, Harnack component counts) instead of
mental algebra.

## 3. The click

The double cover decides everything that has no planar analogue. Work
on the sphere \(S^2\) = two copies of the glued rhombus, with the
antipodal boundary gluing crossing sheets. Then:

- a curve component is an **oval** iff its preimage has two
  components (a pseudoline lifts connectedly);
- a complement region is the **outermost** one iff its preimage is
  connected (= it contains a noncontractible loop; for even degree
  exactly one region is non-orientable);
- the region-adjacency graph (regions as nodes, ovals as edges) of
  disjoint ovals in \(\mathbb{RP}^2\) is a **tree**, and rooting it at
  the non-orientable region turns BFS into the nesting forest.

Everything is then two union-finds (triangles for the curve, corners
for the regions) run once on the quotient and once on the double
cover, plus an Euler-characteristic assertion \(\chi=1\) that catches
gluing bugs.

## 4. The argument, in the order it was found

1. Reflect the triangulation of \(T_8\) into the rhombus
   \(|x|+|y|\le 8\), signs replicated by
   \(\varepsilon(\pm i,\pm j)=\varepsilon(i,j)(\pm1)^i(\pm1)^j\).
2. In each triangle with both signs, one midpoint segment; segments
   join across an edge iff the edge's endpoint signs differ.
3. Components: union-find over cut triangles. Regions: union-find
   over (triangle, vertex) corners — within a triangle the two
   same-sign corners merge; across every edge, corners at the same
   vertex merge; boundary edges merge antipodally.
4. Double cover: the same relations on two sheets, boundary gluing
   crossing sheets; lift counts classify ovals/pseudolines and find
   the root region.
5. Scheme: BFS the region tree, encode each oval as the sorted tuple
   of its children, print canonically (⟨18 u 1⟨3⟩⟩ style).
6. Convexity: a triangulation is certified convex by exhibiting
   heights whose triangle planes lie strictly below every other
   lifted lattice point — checked in exact `Fraction` arithmetic.
   Their published integer `MIN_WEIGHTS` pass this check verbatim,
   which is what makes the census replay a *certificate* replay, not
   a trust-me replay.
7. Search: random positive-definite quadratic + integer noise
   heights, float lower hull, exact re-certification, then simulated
   annealing on signs with a fast array-based evaluator
   (cross-checked against the exact engine on all 2,367 census
   certificates and 40 random cases; 1.4 ms/eval vs 6 ms).

## 5. Computer residue

- `compute/sanity.py`: Harnack schemes degrees 1–8 exact
  (⟨J⟩, ⟨1⟩, ⟨J⊔1⟩, ⟨4⟩, ⟨J⊔6⟩, ⟨9⊔1⟨1⟩⟩, ⟨J⊔15⟩, ⟨18⊔1⟨3⟩⟩),
  component counts \(g+1\), all-plus degree-8 gives the depth-4 nest
  ⟨1⟨1⟨1⟨1⟩⟩⟩⟩, broken certificates rejected.
- `compute/replay_census.py`: 2,367/2,367 PASS in 36 s; 22-oval
  subset = exactly the 38 bold Table-1 schemes; fast evaluator agreed
  on every certificate.
- `compute/record.py`: the 89-row Orevkov/Geiselmann Table 1 as data;
  self-checks 89 = 38+12+39, Gudkov–Rokhlin on every row, per-(p,n)
  bold counts 5/11/14/8/0.
- Search residue (8 workers × 25 min, finished 06:14 UTC; full
  counts in ATTACK.md and `compute/found_schemes.json`): 595
  certified triangulations, 2,112,073 sign evaluations, 902 distinct
  schemes. All 902 survived exact re-verification — zero witnesses
  where the fast evaluator and the `Fraction` engine disagreed, which
  is the one thing this run does establish about the search code.
  All 902 are already in the census. Nothing new, no bugs.
- The shape of the failure is the interesting part. The annealer
  saturates oval count at depth 2 (it found the two 22-oval
  M-schemes ⟨18⊔1⟨3⟩⟩ and ⟨17⊔1⟨1⟩⊔1⟨2⟩⟩, both depth 2 and both
  already known T-realizable) and saturates depth at 3, but never
  both at once: best depth-3 scheme was ⟨7⊔1⟨10⊔1⟨1⟩⟩⟩ at 20 ovals.
  The census has 22-oval depth-3 schemes, so this is the objective's fault, not the geometry's.
  Adding a nesting bonus (workers 6–8) widened the logged set
  (728/738/748 distinct vs 500–626) without reaching depth 4 — it
  buys diversity, not depth. A next attempt should anneal on a
  target-scheme edit distance, or construct the nest directly from
  the tropical side, rather than hoping a component-count objective
  wanders into ⟨4⊔1⟨2⊔1⟨14⟩⟩⟩.
- Neither open deep-nest target appeared in any worker. Nor is either
  in the census. That is silence from ~2×10⁶ samples of a space of
  size \(2^{45}\) per triangulation. It is residue, not a bound.

## 6. What is proved vs still open

Proved (replayed, certificates in-repo or re-derivable): the census
counts of arXiv:2602.06888 v3 are real; every published degree-8
patchwork certificate is convex, primitive, and produces the claimed
scheme under an independent implementation.

Still open, untouched by tonight: algebraic realizability of the six
Orevkov M-schemes; T-curve realizability of the 39; the true count of
degree-8 real schemes. The search re-found 902 of the 2,367 and
added none; the sign space alone is \(2^{45}\) per triangulation and
the triangulation space is astronomically larger, so absence of a hit
is not evidence of absence. Outcome: residue.

---

# Walkthrough, second session — the maximal stratum

## 7. What was missing the first time

The first session read arXiv:2602.06888 v3 for its *numbers* — 2,367,
38, 12, 39, and Theorem 21 — and then went searching in
\(\{\pm1\}^{45}\). Section 3 of the same paper says that search is the
wrong space.

Their Theorem 13 is Haas' theorem: a T-curve is **maximal** if and only
if some collection 𝔖 of compatible Harnack splits is *valid* for it,
meaning the triangulation refines the zone decomposition and the signs
are Harnack on each zone with neighbouring zones differing. And §3.5:
\(\mathcal{C}(\mathfrak{S})\) does not depend on which unimodular
triangulation refines 𝔖.

So the M-curves are indexed by a finite combinatorial gadget. All the
annealer was ever doing was blindly hunting for members of a stratum
that has an exact description.

## 8. The click: twists commute, so the stratum is a linear subspace

Their surgical twist (Lemma 14) is stated as
\(\sigma \mapsto \epsilon + \sigma\circ s_{ij}\) on \(Z^+\), which reads
like an involution you have to apply in some order. But the extension
rule (4) gives \(\sigma(s_{ab}(x,y)) = \sigma(x,y) + ax + by\), so the
twist of a split \(S\) is nothing but

\[\sigma \;\longmapsto\; \sigma + \mathbb{1}_{Z^+_S}\cdot(\epsilon_S + i_Sx + j_Sy) \pmod 2 .\]

Adding a *fixed vector* \(\delta_S \in \mathbb{F}_2^{45}\). Twists
therefore commute, order is irrelevant, and a whole collection acts by
\(\sum_{S\in\mathfrak{S}}\delta_S\). Combined with Haas' theorem: on a
fixed triangulation \(\mathcal{T}\), **every** maximal sign
distribution lies in

\[\eta \;+\; \operatorname{span}_{\mathbb{F}_2}\{\delta_S : S\text{ a Harnack split all of whose edges are edges of }\mathcal{T}\}.\]

Ranks for the 184 census triangulations are 6–26. A rank-18 subspace
is 262,144 sign vectors — a few minutes. Sweeping it is an
**exhaustive classification of the M-curves that triangulation
supports**, which no amount of annealing can deliver.

The measured payoff is blunt. Annealing: \(2.1\times10^6\) sign
vectors, 22 ovals reached twice. Subspace sweep, first pilot: 20,480
evaluations, **20,480 of them 22-oval M-curves**.

## 9. Three checks before believing any of it

1. \(\eta(x,y)=(x+1)(y+1)\) on a random unimodular refinement gives
   ⟨18 ⊔ 1⟨3⟩⟩ — Proposition 10, and it does.
2. Each of the **1,254** Harnack splits of \(T_8\), applied alone,
   must give an M-curve. All 1,254 give 22 ovals; the six schemes
   produced are ⟨18⊔1⟨3⟩⟩, ⟨17⊔1⟨1⟩⊔1⟨2⟩⟩, ⟨13⊔1⟨1⟩⊔1⟨6⟩⟩,
   ⟨14⊔1⟨7⟩⟩, ⟨17⊔1⟨2⊔1⟨1⟩⟩⟩, ⟨10⊔1⟨11⟩⟩ — all bold in their Table 1.
3. The real test: take the 38 published 22-oval `.pcom` certificates
   and *solve* \(\eta+\sum\delta_S=\sigma\) over \(\mathbb{F}_2\) (up
   to the eight equivalent sign functions). **All 38 decompose**, with
   collections of size 3–15. Their data and this implementation of
   Haas' theorem agree everywhere they can.

## 10. Named false starts, second session

- **Refine first, ask about regularity later.** The first refinement
  routine took a maximal crossing-free set of primitive segments
  containing the split edges — a perfectly good *unimodular*
  triangulation, and Haas' theorem needs nothing more. Then twelve
  attempts to find a lifting for one, via Agmon–Motzkin–Schoenberg
  relaxation on the local-convexity system, returned nothing. The
  relaxation was fine: run on the standard triangulation it recovers
  \(h=i^2+ij+j^2\) with slack exactly 1. Random unimodular
  triangulations of \(T_8\) are simply almost never regular, and only
  regular ones are algebraic curves. Fix: stop refining and start from
  triangulations that are *already* certified — the census's own 184,
  and `gen_triang`'s certified random ones — and read the splits off
  them. Every witness in `runs3/` is then regular by construction.
- **Enumerating collections directly.** 1,254 splits, 381,957
  compatible pairs, maximal compatible collections of size 15–24: the
  clique space is hopeless and sampling it (mode `haas`) was the worst
  performer in the session, ~6 distinct schemes per hour. The subspace
  sweep on a fixed certified triangulation dominates it, because the
  triangulation does the compatibility bookkeeping for free — two
  edges of a triangulation never cross.

## 11. Second-session residue

- **A dent.** ⟨4 ⊔ 1⟨5⟩ ⊔ 1⟨10⟩⟩, 21 ovals, one sign flip at
  \((6,1)\) from their own `(5v1(5)v1(10)).pcom` — certified convex on
  their integer `MIN_WEIGHTS`, scheme recomputed from scratch, and
  absent both from our replayed census and from their archive's file
  names. Their §5.3 lower bound 2,367 becomes ≥ 2,368.
  (`compute/certs/new_schemes.json`, `compute/verify_new.py`.)
- **No M-scheme dent.** Nothing outside their 38 has appeared, and
  neither open \((19,3)\) deep nest. Not an obstruction: the sweeps
  cover a prefix of the 184 census triangulations, and the census
  triangulations are exactly the ones their own search already
  favoured, so re-finding their 38 is the expected outcome. What is
  new is that the answer per triangulation is now *exhaustive* rather
  than sampled, and the tool to ask the question of any triangulation
  now exists.

## 12. Named false start, third session: laminar depth is not nesting depth

The deep-nest search changed the search space, and that part was right.
Every earlier pass swept sign vectors on a *fixed* triangulation; Haas'
theorem (their §3.5) says the scheme of a maximal T-curve depends only
on the compatible collection \(\mathfrak{S}\) of Harnack splits, not on
which unimodular refinement you pick. So the triangulation stops being
an input and becomes a by-product, and the search runs over collections
— which is the level at which nesting is supposed to be visible.

The structural hook: pairwise non-crossing chords have nested-or-disjoint
zones, so the \(Z^+\) zones of a compatible collection form a laminar
family. Its depth bounds the nesting depth of \(C(\mathfrak{S})\). The
plan followed immediately — to build a triple nest, drive the laminar
forest deeper — and both `beam` and `anneal` in `dn_sweep.py` scored on
exactly that.

Then the bound was actually measured, on the 38 published 22-oval
certificates whose collections are already recorded:

| zone depth | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nest depth 2 | 6 | 5 | 3 | 7 | 3 | 1 | — | 1 | — |
| nest depth 3 | — | 1 | 3 | 2 | 3 | — | 1 | 1 | 1 |

Zone depth runs 1 to 9. Nesting depth is 2 or 3 and never more. The two
rows overlap almost everywhere: ⟨6 ⊔ 1⟨10 ⊔ 1⟨4⟩⟩⟩ gets a triple nest
out of four splits at zone depth 2, while ⟨12 ⊔ 2⟨1⟩ ⊔ 1⟨5⟩⟩ spends
fifteen splits reaching zone depth 8 and stays at depth 2. The bound is
true and it is useless — it is not monotone in any direction the search
can push, so a score built on it is close to a random walk. That is the
whole explanation for the searcher's lack of traction; more compute
would not have fixed it.

What the same afternoon's arithmetic gave instead was a much sharper
picture of the target. Write a depth-3 M-scheme as ⟨\(a\) ⊔ 1⟨\(b\) ⊔
1⟨\(c\)⟩⟩⟩. Then \(a+b+c=20\), and counting ovals by depth gives
\(p=a+c+1\), \(n=b+1\), so Rokhlin's \(p-n\equiv k^2\equiv 0 \pmod 8\)
at \(k=4\) collapses to \(20-2b\equiv 0\), that is \(b\equiv 2 \pmod 4\).
The published 38 realize \(b=2,6,10,14\) — every admissible value except
\(b=18\), and \(b=18\) is \((p,n)=(3,19)\), the class their Theorem 21
proves is not T-realizable at all. So the depth-3 family is *saturated*:
the census already has every \(b\) a T-curve can have.

Which means the two open nests, both at \(b=2\), are not asking for a
new congruence class or a deeper nest. They are asking to move \(a\)
from 10 or 17 (published) to 4 or 14 (open) inside a row that is already
occupied. Nothing here decides that — but it is a far better-posed
question than "find a deeper nest", and it is the one the next attempt
should score against.

## 13. Named false start, q1: even twists cannot leave the five

The 23 August note said to score a walk by \(\lvert a-4\rvert\) or
\(\lvert a-14\rvert\) with \(b\) pinned at 2, using only even Harnack
splits (paper Theorem 17: even splits keep \((p,n)\)). That walk was
run. It is the wrong handle.

Start from any of the five published (19,3) collections, including the
Prop 31 bow-tie that produces ⟨17⊔1⟨2⊔1⟨1⟩⟩⟩. Add, drop, or swap even
splits only, and never drop an odd split. Two hundred thousand
collections later the schemes are exactly those five:

⟨18⊔1⟨3⟩⟩, ⟨17⊔1⟨1⟩⊔1⟨2⟩⟩, ⟨17⊔1⟨2⊔1⟨1⟩⟩⟩, ⟨16⊔3⟨1⟩⟩,
⟨10⊔1⟨2⊔1⟨8⟩⟩⟩.

No \(a=11,\dots,16\). One even *drop* from the \(a=10\) nest jumps
straight to the \(a=17\) nested box. The bow-tie path itself is even
— every split's vertex parities include \((0,0)\) — so it was already
inside the even-walk graph. The open nests are not one even move from
any published (19,3) collection.

The first BFS that *did* drop odd splits left the (19,3) row
immediately. That is Theorem 17 in the other direction, and it is why
the pin matters.

## 14. The useful failure: the \(a=10\) nest already has seven odds

Odd collections of size at most 3 were enumerated exhaustively
(189 odd splits, 368,936 compatible collections). They produce twelve
known M-schemes and neither open nest. That looked like a wall until
the published \(a=10\) collection was opened: it is twelve splits, of
which **seven are odd**. Size 3 cannot see the one published depth-3
(19,3) T-curve, so silence there is not evidence about \(a=4\) or
\(a=14\).

Remark 20 says nested odd zones cancel, so a nested odd *pair* can
stay on (19,3) while changing the odd skeleton. Adding every such
pair to each of the five published (19,3) collections is a 122-curve
check. The \(a=10\) nest admits **zero** compatible nested odd pairs.
The other four seeds produce only known M-schemes. So the open nests
are not a canceling pair away from a published (19,3) collection
either.

A stronger negative, still not an obstruction: the one-split
add/drop/swap neighbourhood of *all 38* published M-collections is
exactly those 38 schemes (28,861 evaluations). Collection-distance
from the published M-set to either open nest is at least 2.

## 15. What the leftover thicken actually said through rank 20

The 23 August leftover was four rank-16 triangulations. Cheap first,
then the rest of the intended leftover: every census triangulation
of twist-rank at most 20, radius 1 around the whole Haas maximal
stratum. That is 164 of 164, 1,438,512,000 sign distributions,
exactly \(46\cdot 2^r\) on each. Every scheme outside the published
2,367 is already among the seventeen. Rank 20 is fifteen
triangulations, including the two published (19,3) liftings
`(17v1(1)v1(2)).pcom` and `(17v1(2v1(1))).pcom`. Both of those
finished; neither open nest is on that neighbourhood of either
lifting. One other rank-20 certificate,
`(6v1(6v1(8))).pcom`, rediscovered seven of the seventeen and
nothing new.

That is a neighbourhood statement, not an obstruction. The open
nests may sit at Hamming distance greater than 1 from the maximal
Haas stratum, or on a triangulation that is not among the 184
census ones. Ranks 21–26 (twenty triangulations) were never in
the leftover.

## 16. Rank 21 of that leftover, then the next collection moves

The five leftover triangulations of twist-rank 21 are now finished
the same way: radius 1 around the whole Haas maximal stratum,
\(46\cdot 2^{21}\) sign distributions on each, 482,344,960 in all.
Novel versus the published census is empty. None of the seventeen
reappears either — those five certificates simply do not see the
schemes that sit off the census. The two published (19,3) liftings
were already rank 20. The only (19,3) certificate in ranks 21–26
is the Harnack triangulation at rank 23.

So the leftover thicken is no longer "ranks 21–26 were never
tried." It is "ranks 21–23 are finished neighbourhoods and added
nothing; ranks 24–26 are still open." That is still not an
obstruction. Hamming distance greater than 1, or a triangulation
outside the 184, remains possible.

The Harnack triangulation itself, radius 1 around the whole Haas
maximal stratum, produced 26 schemes already in the published
census. The other five rank-23 leftover certificates did the same.

Collection space was pushed one step past q1 and stayed quiet.
Four hundred thousand even twists still produce exactly the five
published (19,3) M-schemes. Dropping at most one split and adding
three, from those same five collections, produces thirty known
M-schemes and neither open nest — and the last seed was cut by a
time cap, so even that is only a prefix. Odd collections of size 4
finished and stayed on the same twelve M-schemes as size ≤ 3. The
published \(a=10\) nest still has seven odd splits; size 4 can see
a larger odd part than size 3, but it did not see a new M-scheme,
and silence there is still not evidence about \(a=4\) or \(a=14\).
