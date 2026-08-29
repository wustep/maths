# Research log — Hilbert 16(a), degree 8

All sources below were actually opened on 2026-08-21 (by this session
or its literature subagents, arXiv HTML/PDF or author PDFs; raw
downloads where noted). Forum posts were not used.

## The record

- S. Yu. Orevkov, *Classification of flexible M-curves of degree 8 up
  to isotopy*, GAFA 12 (2002) 723–755. Author PDF (read, pp. 723–728):
  <https://www.math.univ-toulouse.fr/~orevkov/m8.pdf>. Before it: 9
  M-schemes open (list (1), p. 723). Thm 1.1/1.2a: two of them,
  ⟨1⊔1⟨3⟩⊔1⟨16⟩⟩ and ⟨1⊔1⟨6⟩⊔1⟨13⟩⟩, are not realizable even
  pseudo-holomorphically. Thm 1.2b: the other seven are
  pseudo-holomorphically realizable. Table 1 (p. 725–726): the 89
  pseudo-holomorphically realizable M-schemes; asterisks on the six
  algebraically open ones. Caveat (Remark 1, p. 724): the seven are
  not claimed realizable in a single almost complex structure.
- S. Yu. Orevkov, *New M-curve of degree 8*, Funct. Anal. Appl. 36
  (2002) 247–249. Author PDF (read in full):
  <https://www.math.univ-toulouse.fr/~orevkov/m711.pdf>. Realizes
  ⟨7⊔1⟨2⊔1⟨11⟩⟩⟩ algebraically; states "it remains 6 arrangements of
  22 ovals whose realizability by M-curves is still unknown."
- The six (also independently listed in Gabard arXiv:1310.1865
  Thm 2.2, and still current in arXiv:2602.06888 v3, 2026):
  ⟨4⊔1⟨2⊔1⟨14⟩⟩⟩, ⟨14⊔1⟨2⊔1⟨4⟩⟩⟩ with (p,n)=(19,3);
  ⟨1⊔1⟨1⟩⊔1⟨18⟩⟩, ⟨1⊔1⟨4⟩⊔1⟨15⟩⟩, ⟨1⊔1⟨7⟩⊔1⟨12⟩⟩, ⟨1⊔1⟨9⟩⊔1⟨10⟩⟩
  with (p,n)=(3,19).
- Geiselmann, Joswig, Kastner, Mundinger, Pokutta, Spiegel, Wack,
  Zimmer, *Limits of Combinatorial Patchworking*, arXiv:2602.06888
  (v1 6 Feb 2026 as "121 Patchworked Curves of Degree Seven"; v3
  27 Jul 2026, major revision). Abs + full HTML v3 (raw download,
  quotes verbatim): <https://arxiv.org/abs/2602.06888>,
  <https://arxiv.org/html/2602.06888v3>. Current degree-8 record:
  2,367 distinct nonempty schemes as T-curves ("as the search is not
  exhaustive, this is a lower bound"); 38 of the 89 M-schemes
  T-realized (Table 1 bold; 5/11/14/8 per (p,n) =
  (19,3)/(15,7)/(11,11)/(7,15)); Theorem 21: maximal degree-8
  T-curves have (p,n) ∈ {(19,3),(15,7),(11,11),(7,15)}, so the 12
  M-schemes with (p,n)=(3,19) — including four of the six open — are
  not T-curves; 39 M-schemes undecided as T-curves (Question 39),
  including the two open (19,3) deep-nests. Degree ≤ 7: every
  nonempty scheme is a T-curve (Thm 38: four triangulations cover all
  121 of degree 7), answering Itenberg–Viro 1996. Obstruction
  machinery: Haas' zone decompositions (their Section 3), purely
  combinatorial, no Gudkov–Rokhlin. Corrections they make to
  Orevkov's Table 1: Wiman scheme is ⟨16⊔3⟨1⟩⟩ (misprinted ⟨17⊔3⟨1⟩⟩),
  and ⟨17⊔1⟨2⊔1⟨1⟩⟩⟩ is attributed to Hilbert in Viro's 1980 table.
- Same group, *Fast Isotopy Computation for T-Curves*,
  arXiv:2604.09221 (10 Apr 2026, ICMS): abs + HTML opened. Reports
  the earlier sweep state: "exactly 2359 distinct real schemes …
  of which only 30 are maximum", "53 others have no known T-curve
  realization". **Superseded by 2602.06888 v3** (2,367 / 38). The
  near-quadratic isotopy algorithm and GPU implementation live here;
  C++ library <https://github.com/polymake/libisotopy> (exists,
  branch `master`; no scheme data in the repo).

## Data replayed

- <https://github.com/dmg-lab/CombinatorialPatchworking> — the paper's
  data repo (Appendix B). `deg8.pcoms.txz` (125,932 bytes) downloaded
  from
  <https://raw.githubusercontent.com/dmg-lab/CombinatorialPatchworking/main/deg8.pcoms.txz>:
  exactly 2,367 `.pcom` certificates `deg8/oNN-pNN-nNN/(scheme).pcom`,
  each a polymake JSON with POINTS (the 45 lattice points of T_8),
  MIN_WEIGHTS (integer lifting), MAXIMAL_CELLS (64 triangles), SIGNS
  (45 booleans), TYPE (claimed scheme). The 22-oval directories hold
  exactly 38 files. Replay: `compute/replay_census.py` (all 2,367
  PASS, see ATTACK.md).

## Method sources (for the verifier)

- Itenberg–Viro, *Patchworking algebraic curves disproves the
  Ragsdale conjecture*, Math. Intelligencer 18:4 (1996). Full HTML:
  <https://www.math.stonybrook.edu/~oleg/math/papers-html/iten-vi/index.html>.
  Construction, sign-replication rule σ_{i,j}σ_{εi,δj}ε^iδ^j = 1,
  convexity hypothesis, Theorem 1; the 1996 question answered by
  arXiv:2602.06888.
- O. Viro, *Patchworking real algebraic varieties*,
  arXiv:math/0611382 (abs + HTML §1.1 opened): Patchwork Theorem
  1.1.D; convexity required, primitivity not (primitivity is what
  makes the combinatorial T-curve setting).
- I. Itenberg, *Construction of real algebraic varieties* survey PDF
  (read): <https://webusers.imj-prg.fr/~ilia.itenberg/papers/constr.pdf>.
  Lemma 3.3: Harnack signs on any primitive convex triangulation give
  the Harnack M-curve. Santos' non-convex piecewise-linear curves are
  only known pseudo-holomorphic — convexity matters.
- arXiv:2602.06888 v3 §2: modern statement (regular = convex =
  lifting-induced; unimodular = primitive), diamond A⋄, F₂ sign rule;
  §4.2 Prop 10: Harnack signs give ⟨18⊔1⟨3⟩⟩ for d=8 on ANY
  unimodular triangulation (regular or not).
- Joswig–Vater, arXiv:2003.06326 (polymake patchworking, abs).

## Negative / corrected lookups

- The task prompt's citation said "2359 realized and 53 *non-maximal*
  schemes with no T-curve witness". Wrong on both counts against the
  papers: the April paper's 53 are *maximal* (22-oval) schemes with
  algebraic constructions but no T-curve witness, and the July v3
  supersedes 2359→2,367, 30→38, 53→39-undecided+12-impossible.
- Degtyarev–Kharlamov, arXiv:math/0004134 (*du côté de chez Rokhlin*):
  full PDF text searched — contains **no** degree-8 status table.
  Not a citable source for the six.
- Gabard arXiv:1310.1865 says only three of the six are known
  pseudo-holomorphic; Orevkov's published Thm 1.2(b) covers all six.
  Orevkov is authoritative.
- <https://www.math.stonybrook.edu/~oleg/math/papers.html> — 404.
- De Loera–Wicklin, *On the Need of Convexity in Patchworking* (Adv.
  Appl. Math. 20, 1998): ScienceDirect 403, abstract not fetched;
  known via citations in 2602.06888 (individual degree-7/8 T-curves,
  non-convex experiments).
- api.github.com unauthenticated: 403 rate-limit (worked around via
  `gh` and raw.githubusercontent.com).
- Orevkov's degree-8 papers are not on arXiv; author PDFs used.
- Web searches for any 2003–2026 resolution of one of the six:
  nothing found.

## Haas' theorem (second session, 2026-08-21)

The whole of `compute/haas.py` and `compute/zone_search.py` rests on
Section 3 of arXiv:2602.06888 v3, which was re-fetched and read in
full for this session (raw HTML download,
<https://arxiv.org/html/2602.06888v3>; the first session had only used
the abstract-level claims and Theorem 21):

- **Theorem 13 (their statement of Haas)**: a T-curve
  \(\mathcal{C}(\mathcal{T},\sigma)\) is *maximal* if and only if some
  collection \(\mathfrak{S}\) of compatible Harnack splits has a zone
  decomposition valid for \((\mathcal{T},\sigma)\). No regularity of
  \(\mathcal{T}\) is assumed.
- **Section 3.2**: a Harnack split is a path of one or two primitive
  edges joining exactly two boundary points of \(d\cdot\Delta_2\), with
  vertex parities alternating between two distinct classes
  \(\alpha,\beta\in\mathbb{F}_2^2\); simple = one edge, double = two
  edges through an interior *apex*. \(Z^+\) is the zone containing
  fewer corners of \(d\cdot\Delta_2\); \(Z^-\) is the root zone.
  Compatible = no shared edge and simultaneously realizable in one
  triangulation.
- **Section 3.4, Lemma 14**: the *surgical twist* of a split replaces
  \(\sigma\) by \(\epsilon+\sigma\circ s_{ij}\) on \(Z^+\), with
  \(\epsilon=\alpha_1\beta_2+\alpha_2\beta_1\),
  \(i=\alpha_2+\beta_2\), \(j=\alpha_1+\beta_1\). Since
  \(\sigma(s_{ab}(x,y))=\sigma(x,y)+ax+by\), a twist just *adds* the
  affine \(\mathbb{F}_2\) function \(\epsilon+ix+jy\) on \(Z^+\) —
  so twists commute and a collection acts by a **sum of fixed
  vectors**. That is the observation the search is built on.
- **Section 3.5**: "The notation \(\mathcal{C}(\mathfrak{S})\) is
  independent of \(\mathcal{T}\), as every unimodular triangulation
  that refines \(\mathfrak{S}\) will do." So the real scheme of a
  maximal T-curve is a function of the split collection alone.
- **Theorem 17 (Haas)**: even splits do not change \((p,n)\).
  **Lemma 18 / Remarks 19–20 / Theorem 21**: seven odd splits matter in
  degree 8, each of effect 4 except one of effect 8; nested zones
  cancel; hence \((p,n)\in\{(19,3),(15,7),(11,11),(7,15)\}\).
- **Section 4**: families. Prop 25 onion curves (honeycomb + constant
  signs, maximal nesting depth, maximal only for \(d\le3\));
  **Prop 31 nested box curves** — the bow tie triangulation
  \(\mathcal{B}_d\) is induced by the nested double
  \(\{(0,0),(1,1)\}\)-splits with vertices
  \(\{(i+1,d-i-1),(i,i),(d-i+1,i-1)\}\), and for \(d=8\) gives
  \(\langle17\sqcup1\langle2\sqcup1\langle1\rangle\rangle\rangle\),
  i.e. the \(a=17\) member of the deep-nest family; Prop 32 arrowhead
  curves give \(\langle17\sqcup1\langle1\rangle\sqcup1\langle2\rangle\rangle\)
  and the Wiman scheme \(\langle16\sqcup3\langle1\rangle\rangle\).
- **Section 5.3 / Question 39**: the 39 undecided M-schemes are stated
  as open; the authors do **not** run a zone-decomposition enumeration
  in degree 8 — Theorem 21 is used only for the \((p,n)\) obstruction.
  That gap is what this session attacks.

Cited but **not opened** (no copy reachable): B. Haas, *Real algebraic
curves and combinatorial constructions*, 1997 (their [18]) — every use
of "Haas' theorem" here is via the statement in arXiv:2602.06888 v3
Theorem 13, which is what we implement and test. Also not opened:
B. Bertrand, E. Brugallé, A. Renaudineau, *Haas' theorem revisited*,
Épijournal Géom. Algébrique 1 (2017) Art. 922,
DOI 10.46298/epiga.2017.volume1.2030 (their [4], an independent
formulation of the same theorem); I. Itenberg, *Counter-examples to
Ragsdale conjecture and T-curves*, Contemp. Math. 182 (1995) 55–72
(their [25], source of the Harnack sign distribution
\(\eta(x,y)=(x+1)(y+1)\) used here).

## 2026-08-22 — freshness check

Re-checked the record. **Nothing about degree 8 changed.**
arXiv:2602.06888 is still at **v3 (27 Jul 2026)** — `.../abs/2602.06888v4`
returns 404, and the abs page lists exactly v1 (6 Feb 2026), v2 (23 Feb
2026), v3 (27 Jul 2026), still with no journal-ref. arXiv:2604.09221 is
still **v1 only** (10 Apr 2026). The **2,367** degree-8 T-curve count
stands: `dmg-lab/CombinatorialPatchworking` has had no push since
**2026-07-21** (HEAD `e85b809`, merge of PR #1 "data: add degree-eight
patchwork certificates"), one closed PR, zero issues, zero releases, two
branches (`main`, `feat/degree8-data`, same tree), and the README still
says 2,367. Orevkov's page (last update **11 Aug 2026**) lists nothing on
degree 8 since 2002. **All six M-schemes are still open**: no paper,
preprint, or author page found claiming to realize or exclude any of
them. Sweeps run: arXiv API on `T-curve`/`patchworking`/`M-curve`/`real
plane curve`, on `Hilbert's 16th`/`octic`/`22 ovals`, and on
`cat:math.AG AND (T-curves OR patchworking)`; math.AG 2026-08 listing;
Orevkov's page; the dmg-lab org repo list. Three items are new to this
log — none of them touches the degree-8 census.

- S. Yu. Orevkov, *On arrangements of plane real quartics with respect
  to three lines*, arXiv:2607.19457 (v1 21 Jul 2026, **v2 4 Aug 2026**),
  <https://arxiv.org/abs/2607.19457>; author PDF linked from
  <https://www.math.univ-toulouse.fr/~orevkov/>. Degree 4, not 8, so it
  does not move the census — but it is a live caution for dent (A).
  Verbatim from the abstract: "There is one arrangement which is
  realizable pseudoholomorphically but not algebraically. It can be
  constructed in different ways, in particular, by a combinatorial
  patchworking on an irregular triangulation. This is the first example
  of a combinatorial patchworking which produces a PL curve in RP^2
  whose arrangement relative to the coordinate axes is algebraically
  unrealizable." I.e. patchworking on a **non-regular** triangulation
  can output a PL curve with no algebraic model. Our verifier already
  certifies convexity (regularity) in exact rational arithmetic on every
  witness, which is exactly the hypothesis Viro's theorem needs and
  exactly what Orevkov's example lacks. Nothing to fix; the requirement
  is now backed by a published counterexample rather than by
  Itenberg's survey remark alone.
- K. Ferry, M. Joswig, J. Rambau, *Counting symmetric unimodular
  triangulations*, arXiv:2605.14150 (13 May 2026), abs + full HTML
  opened: <https://arxiv.org/abs/2605.14150>,
  <https://arxiv.org/html/2605.14150v1>. Explicitly "motivated by work
  on T-curves (Geiselmann et al., 2026)". Counts unimodular
  triangulations of \(d\cdot\Delta_2\) that are invariant under a fixed
  symmetry axis \(\mathfrak{H}\), up to \(\mathfrak{H}\)-feasible
  symmetries; their Table 1 gives \(\widetilde{F}(8) =
  1{,}211{,}875{,}888\) (and \(\widetilde{F}(9) =
  422{,}664{,}577{,}207\)). Sizes the residue in ATTACK.md: we swept 184
  census triangulations plus 4,074 more, and the **symmetric** unimodular
  triangulations of \(8\cdot\Delta_2\) alone already number 1.2 billion —
  the unrestricted count is not enumerated anywhere. "Exhaustive per
  triangulation, not exhaustive over triangulations" is not close to
  exhaustive. No degree-8 scheme counts in the paper; it does not
  mention 2,367.
- G. Maletto, *Hilbert's 16th problem for arrangements of curves on a
  surface*, arXiv:2606.21449 (19 Jun 2026),
  <https://arxiv.org/abs/2606.21449>. The preprint Orevkov's quartic
  paper completes. Arrangements of three lines with a cubic (complete)
  and with a quartic (partial) on compact real surfaces; Bézout
  obstructions, Viro patchworking, a Julia library `NWT`. Not degree 8.

## 2026-08-27 — freshness check (q1)

Re-fetched the record before any new search. **Nothing about degree 8
moved.** `python3 scripts/arxiv_fetch.py 2602.06888v3` returns
**v3, 27 Jul 2026**, title *Limits of combinatorial patchworking*,
43 pages, "major revision". Abs
<https://arxiv.org/abs/2602.06888> and full HTML
<https://arxiv.org/html/2602.06888v3> re-read: §5.3 still says
**2,367** nonempty degree-8 T-curve schemes, "as the search is not
exhaustive, this is a lower bound"; 38 of 89 M-schemes T-realised;
Theorem 21 still restricts maximal T-curves to
\((p,n)\in\{(19,3),(15,7),(11,11),(7,15)\}\); Question 39 still leaves
39 M-schemes undecided. A request for
<https://arxiv.org/abs/2602.06888v4> does not produce a v4 paper (the
fetcher landed on the old v1 title). arXiv:2604.09221 is still **v1**
(10 Apr 2026),
<https://arxiv.org/abs/2604.09221>. `dmg-lab/CombinatorialPatchworking`
HEAD is still `e85b809` (2026-07-21, merge of PR #1); no later commit.
Parent `sh run_all.sh` this session: **2,367/2,367** certificates
replay, **17/17** outside the census, Haas 38/38, C/Python agreement
on ranks 6, 10, 12, 13, 16.

A DOML 2026 slide deck by Spiegel,
<https://christophspiegel.berlin/assets/slides/DOML_2026.pdf>, prints
"at least 2,368 isotopy types of degree 8" including 38 M-curves.
That is a talk slide, not a paper. The v3 text says 2,367 *nonempty*
schemes; counting the empty scheme would make 2,368. Not treated as a
census update. No new paper found that realises or excludes any of
the six algebraically open M-schemes.

Checked and **not** relevant to degree 8, recorded so the next check can
skip them: E. Pasquereau, *On the topology of T-manifolds of higher
codimension*, arXiv:2602.14988 (16 Feb 2026),
<https://arxiv.org/abs/2602.14988> — new component bounds, but for high
codimension and \(\mathbb{RP}^3\), nothing on ovals in
\(\mathbb{RP}^2\). Also scanned and off-topic: Akyar–Shkolnikov
arXiv:2603.08094 (non-Abelian patchworking), Demory arXiv:2601.07751
(T-polynomials, dilated triangulations), Ichikawa arXiv:2601.18093
(dimers, M-curves of a Riemann surface, not plane schemes),
Janasz–Pokora arXiv:2512.24707 (M-arrangements of conics and lines),
Frühbis-Krüger–Joswig–Kastner arXiv:2603.12985 (drawing real plane
curves in OSCAR). No forum sources were used.

## 2026-08-27 — freshness check (q2)

Re-fetched before the leftover high-rank thicken. **Nothing about
degree 8 moved.** `python3 scripts/arxiv_fetch.py 2602.06888v3`
returns **v3, 27 Jul 2026**. Abs
<https://arxiv.org/abs/2602.06888> and full HTML
<https://arxiv.org/html/2602.06888v3> re-read: §5.3 still **2,367**
nonempty degree-8 T-schemes, "as the search is not exhaustive, this
is a lower bound". <https://arxiv.org/abs/2602.06888v4> is 404.
Parent 17/17 and q1 replay still green. Bound still ≥ 2,384.

## 2026-08-27 — freshness check (q3)

Re-fetched before the leftover ranks 22–26 thicken. **Nothing about
degree 8 moved.** `python3 scripts/arxiv_fetch.py 2602.06888v3`
returns **v3, 27 Jul 2026**. Abs
<https://arxiv.org/abs/2602.06888> and full HTML
<https://arxiv.org/html/2602.06888v3> re-read: §5.3 still **2,367**
nonempty degree-8 T-schemes, "as the search is not exhaustive, this
is a lower bound". <https://arxiv.org/abs/2602.06888v4> is 404.
Parent 17/17 still the folder bound. Rank 21 leftover finished on
main. Bound still ≥ 2,384.

## 2026-08-29 — freshness check (q4)

Re-fetched after the leftover ranks 22–26 thicken merged.
**Nothing about degree 8 moved.** `python3 scripts/arxiv_fetch.py
2602.06888v3` returns **v3, 27 Jul 2026**. Abs
<https://arxiv.org/abs/2602.06888> and full HTML
<https://arxiv.org/html/2602.06888v3> re-read: §5.3 still **2,367**
nonempty degree-8 T-schemes, "as the search is not exhaustive, this
is a lower bound". <https://arxiv.org/abs/2602.06888v4> is 404.
Parent 17/17 still the folder bound. Leftover ranks 22–26 finished
on main. Bound still ≥ 2,384.

## 2026-08-29 — freshness check (q5)

Re-fetched after the leftover (19,3) neighbourhood wrap merged as
`e6fe948` (PR #151). **Nothing about degree 8 moved.**
`python3 scripts/arxiv_fetch.py 2602.06888v3` returns **v3, 27 Jul
2026**. Abs <https://arxiv.org/abs/2602.06888> and full HTML
<https://arxiv.org/html/2602.06888v3> re-read: §5.3 still **2,367**
nonempty degree-8 T-schemes, "as the search is not exhaustive, this
is a lower bound". <https://arxiv.org/abs/2602.06888v4> is 404.
Parent 17/17 still the folder bound. q4 finished the depth-3
three-split 12/12 and left the even-split BFS queue at 1,167,098.
Bound still ≥ 2,384.

## 2026-08-29 — freshness check (q5 resume)

Re-fetched after the leftover walk was interrupted. **Nothing about
degree 8 moved.** `python3 scripts/arxiv_fetch.py 2602.06888v3`
returns **v3, 27 Jul 2026**. Abs
<https://arxiv.org/abs/2602.06888> and full HTML
<https://arxiv.org/html/2602.06888v3> re-read: §5.3 still **2,367**
nonempty degree-8 T-schemes. <https://arxiv.org/abs/2602.06888v4>
is 404. Parent 17/17 still the folder bound. Bound still ≥ 2,384.
