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
