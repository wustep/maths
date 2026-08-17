# Attack log — Tuza's triangle packing-covering conjecture

## 2026-08-17 — start

- Folder empty except `PROBLEM.md`. House: write only here; no git; cite what we beat; no invented dent.
- Conjecture (Tuza 1981/1990): every finite simple graph satisfies \(\tau(G)\le 2\nu(G)\), where \(\nu\) is the maximum number of pairwise edge-disjoint triangles and \(\tau\) is the minimum number of edges meeting every triangle.
- Tonight: a certified extremal split or bounded-treewidth example, a new local exchange rule with an independently checkable certificate, or a documented residue. Isolated ILP tables are residue unless they imply a reusable lemma.

### Published record (fetched tonight)

| claim | source | status |
| --- | --- | --- |
| \(\tau\le 3\nu\) | delete all edges of a maximum packing | theorem; trivial |
| \(\tau\le(66/23)\nu\approx 2.8696\nu\) | Haxell, *Discrete Math.* 195 (1999) | theorem; still the universal bound in every 2026 paper we fetched |
| planar | Tuza, *Graphs Combin.* 6 (1990) | theorem |
| no \(K_{3,3}\)-subdivision | Krivelevich, *Discrete Math.* 142 (1995) | theorem |
| triangle-3-colourable (includes 4-colourable) | Aparna Lakshmanan–Bujtás–Tuza, *Graphs Combin.* 28 (2012) | theorem |
| \(\mathrm{mad}(G)<7\) (hence \(\Delta\le 6\)) | Puleo, *European J. Combin.* 49 (2015), [arXiv:1308.2211](https://arxiv.org/abs/1308.2211) | theorem; introduces reducible sets and weak König–Egerváry (WKE) links |
| treewidth \(\le 6\); hence \(K_8\)-free chordal | Botler–Fernandes–Gutiérrez, *Discrete Math.* 344 (2021), [arXiv:2002.07925](https://arxiv.org/abs/2002.07925) | theorem |
| planar triangulations \(\ne K_4\) have \(\tau\le\tfrac32\nu\) | same | theorem; sharp on an infinite family |
| threshold graphs (split \(\cap\) cographs) | Bonamy–Bożyk–Grzesik–Hatzel–Masařík–Novotná–Okrasa, *DMTCS* 24 (2022), [arXiv:2105.09871](https://arxiv.org/abs/2105.09871) | theorem |
| split with \(\delta\ge 3n/5\); dense tripartite ratio; complete 4-partite \(\tau\le\tfrac32\nu\) | Chahua–Gutiérrez, *Discrete Appl. Math.* 377 (2025) 225–233, [arXiv:2405.11409](https://arxiv.org/abs/2405.11409), doi:10.1016/j.dam.2025.06.049 | theorem. The list file called this “Botler et al. 2025”; the DAM paper is Chahua–Gutiérrez. Botler is the 2021 treewidth paper. |
| \(\Delta\le 7\) | Gupta, [arXiv:2608.06538](https://arxiv.org/abs/2608.06538) (6 Aug 2026) | preprint, 11 days old; Puleo reducible pairs at triangle-codegree 4,5,6; 1,144 machine-checked local certificates |
| random \(G(n,p)\) a.a.s. | Kahn–Park 2022; Bennett–Dudek–English–Martin 2020 | theorem |
| random geometric, large density range | Bennett et al., [arXiv:2606.09736](https://arxiv.org/abs/2606.09736) | preprint |
| directed analogue | McDonald–Puleo–Tennenhouse 2020 | theorem (different problem) |

Tight examples already in Tuza 1990: every block graph whose blocks are \(K_2\), \(K_4\) or \(K_5\) has \(\tau=2\nu\). \(K_4\) has \((\nu,\tau)=(1,2)\); \(K_5\) has \((2,4)\). Cui–Haxell–Ma characterised the planar equality case.

Still open, and named as such tonight:

- the conjecture in general (universal constant still \(66/23\));
- split graphs in full generality (threshold and \(\delta\ge 3n/5\) only);
- treewidth 7 (Botler et al. stop at 6);
- Gupta Question 12.1: does \(\mathrm{mad}<8\) imply Tuza?
- Gupta Question 12.3: does any 7-regular graph have \(\tau=2\nu\)?
- Gupta Question 12.4: \(K_5\)-free graphs.

Local PDFs: `compute/refs/`. Gupta ancillary checkers copied to `compute/gupta_anc/` (replay only; not a dent).

### Plan

1. Independently recompute \(\nu,\tau\) on the named tight graphs, and replay Gupta's 7-vertex connected-non-WKE degree lemma (his Lemma 4.5).
2. New finite lemma: the same census on **eight** vertices (the link of an 8-regular vertex). This is the first step of Gupta's Question 12.1 / \(\Delta\le 8\).
3. Search a new local exchange: in an 8-regular graph, the two ends of a triangle-codegree 7 (or 6) edge. Certificates must be independently checkable.
4. In parallel: small split-graph and 7-regular census for new \(\tau=2\nu\) examples that are not Tuza's \(K_4/K_5\)-block family.
5. If the exchange search or the census does not produce a reusable lemma, leave the residue. Do not claim \(\Delta\le 8\) or a split theorem we did not prove.

## 2026-08-17 — published numbers replayed

`compute/replay_known.py` independently recomputed \((\nu,\tau)\) by complete search:

| graph | \((\nu,\tau)\) |
| --- | ---: |
| \(K_3\) | (1,1) |
| \(K_4\) | (1,2) |
| \(K_5\) | (2,4) |
| \(K_6\) | (4,6) |
| \(K_7\) | (7,9) |
| \(K_8\) | (8,12) |
| \(K_4\) plus a pendant edge | (1,2) |
| \(K_5\) plus a pendant edge | (2,4) |
| path of three \(K_4\)-blocks | (3,6) |
| two \(K_4\)s sharing a vertex | (2,4) |

Agrees with Tuza / Gupta's sharpness script. \(K_8\) is 7-regular with ratio \(3/2\), so Gupta's \(\Delta\le 7\) theorem is not tight on the complete graph.

## 2026-08-17 — WKE census, n=5..8

Unlabelled, via nauty `geng` + two independent WKE checkers (bitset tables and a brute matching/cover scan). They agree on every n=8 graph.

n=7 unlabelled: 117 connected non-WKE graphs, every one has at least three vertices of degree \(\ge 4\). This is Gupta's Lemma 4.5 (unlabelled form). Replay, not a dent. (Labelled 2^{21} counts 167871 / 166793 / 4620 not yet re-run; the unlabelled statement already matches.)

n=8 unlabelled, the first step of Gupta Question 12.1 / \(\Delta\le 8\):

| | count |
| ---: | ---: |
| graphs | 12346 |
| connected | 11117 |
| connected non-WKE | 443 |
| those with \(\Delta\le 4\) | 8 |
| those with \(<3\) vertices of deg \(\ge 4\) | 2 |
| those with no vertex of deg \(\ge 5\) | 8 |

**Lemma (verified tonight).** Every connected non-WKE graph on eight vertices has maximum degree at least 4. The bound is sharp: exactly eight such graphs have \(\Delta=4\). In particular the n=7 statement “at least three vertices of degree \(\ge 4\)” **fails** at n=8 (two counterexamples, graph6 `G?r@e[` and `G?ouUW`).

Consequence for an 8-regular minimal counterexample: every link is one of the 443, so every vertex is incident with an edge of triangle-codegree in \(\{4,5,6,7\}\). We cannot force codegree \(\ge 5\). Gupta's high-codegree shortcut therefore does not survive at degree 8 without a codegree-4 catalogue on a 12-vertex local graph (\(|A|=|B|=3\)).

The eight \(\Delta=4\) graphs are stored in `compute/certs/n8_exceptions.json`. Two of them are 4-regular (`GEnfbW`, 6 triangles; `GEnbvG`, 7 triangles).

## 2026-08-17 — labelled n=7 WKE replay

`census_wke.py 7 --labelled` scanned all \(2^{21}=2{,}097{,}152\) labelled 7-vertex graphs. Exact match with Gupta Lemma 4.5:

| | tonight | Gupta |
| ---: | ---: | ---: |
| non-WKE | 167871 | 167871 |
| connected non-WKE | 166793 | 166793 |
| connected non-WKE with \(<3\) verts of deg \(\ge 4\) | 0 | 0 |
| connected non-WKE with exactly 3 such verts | 4620 | 4620 |
| disconnected non-WKE with \(<3\) such verts | 315 | 315 |

Two independent WKE implementations (bitset tables; brute matching/cover) agree on every n=8 unlabelled graph (0 disagreements among the 443 connected non-WKE).

## 2026-08-17 — 8-regular codegree-7 pairs, complete

Unlabelled cores: all 1044 graphs on 7 vertices. Search (`reduce_codegree.py`): 1002 hub-only templates, 42 CBC certificates that use triangles inside the core, **0 failures**.

Independent rebuild-and-check (`verify_c7.py`): every stored template \(R\) expands to an explicit \((S,X)\) satisfying Puleo's three conditions; every ILP triple does too. `PASS all 1044 cores`.

The complete core \(H=K_7\) (graph6 `F~~~w`) is the affine plane of order 3: \(S\) is an STS(9) on \(\{u,v\}\cup C\), \(X=E(K_7)\cup\{uv\}\), \(|S|=12\), \(|X|=22\le 24\). Every pair of the 9 local vertices lies in exactly one member of \(S\).

**Lemma (tonight).** If \(G\) is 8-regular and \(uv\in E(G)\) has triangle-codegree 7, then \(\{u,v\}\) is Puleo-reducible. Certificates: `compute/certs/c7_8reg_verified.json`.

This is a new local exchange. It does **not** prove \(\Delta\le 8\) or \(\mathrm{mad}<8\): the n=8 census does not force codegree 7, only codegree \(\ge 4\).

## 2026-08-17 — codegree 6 attempted, not closed

Same template with \(t=3\) on the 156 unlabelled 6-vertex cores: 120 template, 24 transferable ILP, **12 failures** including the empty graph and \(K_6\). The empty-core failure is an artefact of forcing \(\{ua,vb\}\) into \(X\); neighbourhood-dependent certificates exist there. A transferable codegree-6 rule is not claimed. Residue: `certs/reduce_c6_8reg.json`.

## 2026-08-17 — split census n≤10

`geng -S`, \((\nu,\tau)\) by CBC, classical = triangle-support induces \(K_3\), \(K_4\) or \(K_5\) (Tuza's one-clique-block family, the only split members of his \(K_2/K_4/K_5\)-block graphs).

| n | graphs | tight \(\tau=2\nu\) | nonclassical | counterex |
| ---: | ---: | ---: | ---: | ---: |
| 4 | 9 | 1 | 0 | 0 |
| 5 | 21 | 3 | 0 | 0 |
| 6 | 56 | 6 | 0 | 0 |
| 7 | 164 | 11 | 0 | 0 |
| 8 | 557 | 19 | 0 | 0 |
| 9 | 2223 | 30 | 0 | 0 |
| 10 | 10766 | 46 | 0 | 0 |
| **≤10** | **13796** | **116** | **0** | **0** |

No new tight split example and no split counterexample through 10 vertices. Isolated table; the implied experimental claim is “through n=10, every tight split graph is Tuza-classical”. Not a general split theorem.

## 2026-08-17 — 7-regular census, Gupta Q12.3

All 7-regular graphs on \(n\le 12\) (1 + 5 + 1547 = 1553 unlabelled graphs). None have \(\tau=2\nu\).

| n | graphs | max \(\tau/\nu\) | maximiser |
| ---: | ---: | ---: | --- |
| 8 | 1 | \(12/8=3/2\) | \(K_8\) |
| 10 | 5 | \(12/10=6/5\) | `IUzrv~}~_` |
| 12 | 1547 | \(16/12=4/3\) | `KQyurj]yrzUy` |

Spot-checked the n=12 maximiser by a second CBC run: \((\nu,\tau)=(12,16)\). Finite answer to the small-order part of Gupta Question 12.3: no 7-regular tight example exists through 12 vertices, and the unique ratio-\(3/2\) graph on these orders is \(K_8\). Not a bound for all 7-regular graphs.

## 2026-08-17 — what is a dent vs residue

- **Dent:** 8-regular codegree-7 Puleo reduction, 1044 independently checked certificates. New local exchange rule.
- **Reusable finite lemma, not a \(\Delta\le 8\) proof:** every connected non-WKE 8-vertex graph has \(\Delta\ge 4\), sharp on eight graphs; the n=7 “three vertices of degree \(\ge 4\)” statement fails at n=8.
- **Residue:** split n≤10 all-classical tight list; 7-regular n≤12 no-tight list; codegree-6 12-core remainder.
- **Not claimed:** \(\Delta\le 8\), \(\mathrm{mad}<8\), a split theorem, an improvement of Haxell's \(66/23\), a 7-regular \(\tau\le 3/2\,\nu\) theorem beyond n=12. Haxell's 1999 PDF stayed behind the Elsevier paywall; the bound is taken from every 2026 paper that quotes it.
