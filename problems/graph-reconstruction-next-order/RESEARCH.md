# Research log — Graph reconstruction past 13 vertices

## Statement (as attacked)

The Kelly–Ulam reconstruction conjecture: every simple graph on n≥3
vertices is determined up to isomorphism by the multiset of its
vertex-deleted subgraphs. Harary’s set-reconstruction strengthening uses
the *set* of cards.

Tonight’s allowed dent: a certified reconstruction result at n=14, a
structural reduction with an independently checkable certificate, or a
documented residue. Isolated unlabelled enumerations without a verifier
are not a dent.

## Sources fetched (2026-08-17)

- McKay, *Reconstruction of small graphs and digraphs*, Australas. J.
  Combin. 83 (2022), 448–457; arXiv:2102.01942v4 (2 Jan 2022). PDF at
  `compute/refs/mckay-2102.01942.pdf`. **Published finite record.**
- Status page
  https://mlelarge.github.io/graph-conjectures/op/reconstruction_conjecture/
  (auto-reviewed 2026-05-08): still open; McKay n=13 is the computational
  bound cited.
- Wikipedia “Reconstruction conjecture” (oldid 1364713382): same n=13
  verification; reconstructible families include regular, trees,
  disconnected, separable without endvertices, outerplanar, maximal
  planar; Yang Yongzhi: the conjecture holds iff it holds for 2-connected
  graphs.
- Heinrich–Kiyomi–Otachi–Schweitzer, *Interval graphs are
  reconstructible*, arXiv:2504.02353v2 (12 May 2026). Infinite family,
  not a finite-order advance.
- Hammer–Simeone, *The splittance of a graph*, Combinatorica 1 (1981),
  275–284. Split-ness is a predicate of the degree sequence.
- O’Shea–Wilkins, Information Sciences 2023, plus 2024 corrigendum.
  Unaccepted general proof. Unused.

Computational records we did **not** beat: McKay’s all-graphs n=13
(50,502,031,367,952 unlabelled graphs); his triangle-free n≤16, girth≥5
n≤20, C4-free n≤19, bipartite n≤17, Δ≤3 n≤22, and the six degree-window
triples in Theorem 3.1(h).

## Published theorems used

1. Kelly: number of edges, degree sequence, and subgraph counts for any
   H with |V(H)|<n are reconstructible from the full deck.
2. Manvel / McKay Lemma 2.2: the reduced deck determines min degree, max
   degree, presence of any k-cycle for 3≤k<n, and bipartiteness.
3. Complements: G is reconstructible iff its complement is (the cards of
   the complement are the complements of the cards).
4. Disconnected graphs, trees, regular graphs are reconstructible
   (Kelly / Harary). Separable graphs without endvertices: Bondy;
   Greenwell–Hemminger. Yang: it is enough to treat 2-connected graphs.
5. McKay Theorem 3.1, quoted in ATTACK.md. In particular at n=14:
   Δ≤5; degrees in [5,6]; degrees in [6,7].

## What this folder proves

**Theorem.** Every simple graph on 14 vertices with degree sequence
(4,4,4,4,4,4,4,4,4,4,4,6,6,6) is reconstructible from its full deck.

Proof outline.

(i) *Generation is complete.* Let G have that sequence and let S be the
three degree-6 vertices. Each v∈S has two “extra” incidences beyond
degree 4. Those extra edges cannot meet V\S (that would raise a
degree-4 vertex). The only 2-regular graph on three vertices is K3, so
G[S]≅K3 and H:=G minus those three edges is 4-regular. Conversely every
4-regular H and every triangle of non-edges of H produces such a G.
`geng` 2.9.1 lists 88,193 unlabelled 4-regular 14-vertex graphs;
overlaying complement triangles and reducing by `shortg` produces
8,571,837 unlabelled graphs, all of the stated sequence (`degcheck`).

(ii) *The class is full-deck recognisable.* The degree sequence is
reconstructible (Kelly). A graph hypomorphic to one of these 8,571,837
graphs has the same sequence, hence is on the list.

(iii) *Decks are unique.* `deckrecon` writes the SHA-256 of the sorted
nauty-canonical graph6 cards (full deck) and of the uniqued cards
(reduced deck). All 8,571,837 graphs have distinct full-deck hashes and
distinct reduced-deck hashes (`compute/certs/bireg46_s3all_unique.txt`).

(iv) *Independent check.* `verify_labelg.py` rebuilds cards in Python
and canonicalises them with nauty `labelg`, not the `densenauty` call
inside `deckrecon`. 17,143 samples from the complete list: 0 mismatches.
The connected-parent sublist (8,571,676 graphs) was hashed separately
with 21,429 `labelg` samples, also 0 mismatches. The tester reproduces
McKay on all graphs with n≤10 (OEIS A000088), including the n=2
exception and the n=3 set-reconstruction exception.

This class is not among McKay’s Theorem 3.1 families: it has triangles,
δ=4 and Δ=6.

## What is not claimed

- All of n=14, or the full interval of graphs with degrees in [4,6].
- Set-reconstruction of 4^11 6^3 graphs against a mate that has a
  degree-5 vertex.
- Uniqueness of the 41,538,279 graphs of sequence 4^10 6^4 until
  `certs/bireg46_s4_unique.txt` says so.
- Split-graph reconstruction at n=14 (67,997,750 graphs counted, not
  uniqueness-tested).
- Any improvement of McKay’s all-graphs n=13 record.
