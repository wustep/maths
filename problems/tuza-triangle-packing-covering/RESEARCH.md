# Research log — Tuza's triangle packing-covering conjecture

## 2026-08-17

Fetched and read tonight, in the order used.

### The conjecture

Tuza (Eger 1981, published as a conjecture page in *Finite and Infinite Sets*, Colloq. Math. Soc. János Bolyai 37 (1984), p. 888; article: *Graphs Combin.* 6 (1990) 373–380). For every finite simple graph \(G\),
\[
\tau(G)\le 2\nu(G),
\]
where \(\nu(G)\) is the maximum number of pairwise edge-disjoint triangles and \(\tau(G)\) is the minimum number of edges meeting every triangle. Equivalent form: \(\rho_0(G)\le\alpha_1(G)\).

Trivial sandwich: \(\nu\le\tau\le 3\nu\). The factor 2 is sharp on every block graph whose blocks are \(K_2\), \(K_4\) or \(K_5\) (Tuza 1990). Independently recomputed tonight: \(K_4\) has \((\nu,\tau)=(1,2)\), \(K_5\) has \((2,4)\), a path of three \(K_4\)-blocks has \((3,6)\).

### Universal bound

Haxell, *Discrete Math.* 195 (1999) 251–254, doi:10.1016/S0012-365X(98)00183-6. \(\tau\le(66/23)\nu\approx 2.8696\nu\). Still the best general constant in Wikipedia (oldid 1363377674), Gupta (Aug 2026), Bennett et al. (Jun 2026), and Chahua–Gutiérrez (2025). The PDF was not retrieved (Elsevier 403). The bound is taken from those later sources, not from a local copy of Haxell.

Krivelevich, *Discrete Math.* 142 (1995) 281–286: fractional relaxations; graphs with no \(K_{3,3}\)-subdivision.

Chapuy–DeVos–McDonald–Mohar–Schied, 2010s: \(\tau\le 2\nu^*-(1/\sqrt6)\sqrt{\nu^*}\), tight.

### Sparsity and bounded degree

- Planar: Tuza 1990. Equality characterised by Cui–Haxell–Ma, *Graphs Combin.* 25 (2009).
- \(\mathrm{mad}(G)<7\), hence \(\Delta\le 6\): Puleo, *European J. Combin.* 49 (2015) 134–152, [arXiv:1308.2211](https://arxiv.org/abs/1308.2211). Introduces reducible vertex/edge sets and weak König–Egerváry links. Local PDF: `compute/refs/puleo-1308.2211.pdf`.
- Treewidth \(\le 6\), hence \(K_8\)-free chordal: Botler–Fernandes–Gutiérrez, *Discrete Math.* 344 (2021) 112281, [arXiv:2002.07925](https://arxiv.org/abs/2002.07925). Local: `compute/refs/botler-2002.07925.pdf`. Also \(\tau\le\tfrac32\nu\) for planar triangulations other than \(K_4\), sharp on an infinite family.
- \(\Delta\le 7\): Gupta, [arXiv:2608.06538](https://arxiv.org/abs/2608.06538) (6 Aug 2026). Preprint, independent researcher, computer-assisted. Reducible pairs at triangle-codegree 4, 5, 6 in 7-regular graphs; 1,144 machine-checked local certificates. Ancillary files copied to `compute/gupta_anc/`. Local PDF: `compute/refs/gupta-2608.06538.pdf`. **Not treated as a refereed theorem.** The ancillary labelled 7-vertex WKE counts were independently replayed tonight and match.

Gupta's open questions, used as the live frontier:

- Q12.1. Does \(\mathrm{mad}<8\) imply Tuza?
- Q12.2. Human proof of the codegree-4 catalogue.
- Q12.3. Which \(\Delta\le 7\) graphs have \(\tau=2\nu\)? In particular, does any 7-regular graph?
- Q12.4. \(K_5\)-free graphs.

### Split, threshold, dense

- Threshold graphs (split \(\cap\) cographs): Bonamy–Bożyk–Grzesik–Hatzel–Masařík–Novotná–Okrasa, *DMTCS* 24 (2022), [arXiv:2105.09871](https://arxiv.org/abs/2105.09871). Local: `compute/refs/bonamy-2105.09871.pdf`.
- Split with \(\delta\ge 3n/5\); dense tripartite ratio; complete 4-partite \(\tau\le\tfrac32\nu\), sharp: Chahua–Gutiérrez, *Discrete Appl. Math.* 377 (2025) 225–233, [arXiv:2405.11409](https://arxiv.org/abs/2405.11409), doi:10.1016/j.dam.2025.06.049. Local: `compute/refs/chahua-2405.11409.pdf`. The proposed-50 list called this “Botler et al. 2025”. It is not. Botler is a coauthor of the 2021 treewidth paper only.
- Even co-chain graphs: Chahua–Gutiérrez 2022.
- Tuza: \(K_5\)-free chordal (1990). Strengthened to \(K_8\)-free chordal by treewidth 6.
- Tuza: graphs with at least \(\tfrac7{16}n^2\) edges, and \(\delta\ge 7n/8\).

Split graphs in full generality remain open, as every 2024–2026 paper we fetched states.

### Other classes already settled

- Triangle-3-colourable, including 4-colourable: Aparna Lakshmanan–Bujtás–Tuza, *Graphs Combin.* 28 (2012).
- No \(K_5\)-subdivision: Puleo, from Mader's extremal number and \(\mathrm{mad}<6\).
- Toroidal: Puleo, from Euler.
- Odd-wheel-free (locally no \(C_{\ge 5}\) odd): Puleo, because every link is WKE.
- Random \(G(n,p)\), every \(p=p(n)\): Kahn–Park, *Random Structures Algorithms* 61 (2022).
- Random geometric, large density range: Bennett et al., [arXiv:2606.09736](https://arxiv.org/abs/2606.09736) (8 Jun 2026).
- Directed analogue: McDonald–Puleo–Tennenhouse 2020 (different problem, solved).

### What we compare against

- Gupta's 7-vertex WKE lemma and labelled counts. Tonight independently recomputed; numbers agree. Not a dent.
- Gupta Question 12.1 / the \(\Delta=8\) project. Tonight's n=8 WKE census is the first step and is new. It does **not** force codegree \(\ge 5\). Tonight's codegree-7 reduction is a new local exchange, not a proof of \(\Delta\le 8\).
- Gupta Question 12.3. Tonight: no 7-regular graph on \(n\le 12\) has \(\tau=2\nu\). Finite, checkable, not a general bound. \(K_8\) attains \(3/2\); the n=12 maximum is \(4/3\).
- Tight split examples. Tuza's \(K_4/K_5\)-block family, restricted to split graphs (at most one clique block). Tonight: every tight split graph on \(n\le 10\) is of that form. Not a characterisation theorem.
- Universal constant we did **not** beat: Haxell \(66/23\).

### False or unused full-proof claims

Gupta \(\Delta\le 7\) is an 11-day-old preprint. We used its framework and replayed its finite n=7 lemma; we did not take “\(\Delta\le 7\) is a theorem” as something we needed in any deduction tonight. The 8-regular codegree-7 argument uses only Puleo's definition of reducibility (2015) and a local completeness observation that does not depend on Gupta's theorem.

Chahua–Gutiérrez's n≤8 citation of Puleo as a blanket small-order theorem was not used.

### Local files

PDFs in `compute/refs/`: Puleo, Botler–Fernandes–Gutiérrez, Chahua–Gutiérrez, Bonamy et al., Gupta. Gupta ancillary checkers in `compute/gupta_anc/`. Haxell 1999 is missing.
