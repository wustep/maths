# Walkthrough — Seymour's second-neighborhood conjecture

## 0. What was actually missing

The 2026 computational paper (Halkiewicz, arXiv:2601.21563v3) enumerates *Pisa graphs* — strongly connected oriented graphs with \(\Delta=\max_v(|N_2^+|-|N_1^+|)=0\) — through 7 vertices and stops. It conjectures that every Pisa graph is a directed cycle or an orientation of \(K_n\) minus a matching. The next finite handle is the \(n=8\) census. A dent is a complete type list at that order, or even one certified Pisa graph whose missing graph is neither a matching nor (as their \(n=7\) table actually found) regular.

The degree-threshold line (Kaneko–Locke \(\delta^+\le 6\), Sadhukhan–Sandeep–Sen \(\delta^+=7\), Brukhman \(n\le 2\delta+2\)) is a different problem. Isolated random-graph statistics are residue.

## 1. Named false starts

**Treat Halkiewicz Conjecture 5.1 as the published record.** Their own Table 2 lists 720 Pisa graphs on 7 vertices whose missing graph is 2-regular. Guo–Kang–Zwaneveld's directed cycle-square \(\overrightarrow{C_7}^2\) is one of them. The matching conjecture is already false at the order they computed. What they actually established is a *regular-missing* census through \(n=7\).

**Treat Eulerian \(n=2\delta+3\) as a bound.** Brukhman's counting becomes equality precisely when the graph is Eulerian of degree \(\delta\) on \(n=2\delta+3\) vertices (missing a 2-factor). CP-SAT says there is no counterexample for \(\delta\le 5\). But Kaneko–Locke already covers every oriented graph with a vertex of outdegree \(\le 6\), so those UNSAT results are a check of the encoding, not a new threshold. The first Eulerian case not implied by Kaneko–Locke is \(\delta=7\), \(n=17\).

**Cadical instant UNSAT.** A first CNF encoding reported UNSAT in a millisecond with an empty DRAT file, through \(\delta=8\). Cardinality auxiliaries were colliding (`CardEnc` reused variable ids). After passing `top_id`, the same instance is SAT for “Eulerian only” and for \(|N_2|\le\delta\) (cycle-powers exist) and UNSAT for \(|N_2|\le\delta-1\). The bogus proofs were discarded.

**CEGAR that blocks whole orientations.** Asking SAT for an irregular-missing Pisa graph and forbidding each non-strong model as a full assignment looped for 200 rounds. Switching to source-SCC cuts (force an incoming arc into the source component) found a witness immediately.

**Labeled n=8 enumeration.** \(3^{28}\approx 2.3\cdot 10^{13}\) is about 130 core-hours at the n=7 rate. Not tonight.

## 2. The useful failure

The Eulerian equality case is still the right picture, even if it is not a dent at small \(\delta\). In a hypothetical Eulerian counterexample on \(n=2\delta+3\),

- every trap has capacity exactly 3,
- \(U(v)\) is forced to be the two missing neighbours of \(v\) plus one in-neighbour \(\sigma(v)\),
- \(\sigma\) is a fixed-point-free permutation with no 2-cycles,
- the two missing neighbours of \(x\) together with \(\sigma^{-1}(x)\) form a directed triangle,
- so the missing 2-factor has girth at least 4.

That skeleton is what the SAT instances are killing. It is also why \(n=8\) should first grow new missing types that are 2-regular or “2-regular plus a chord”.

Replaying n=6 and n=7 with an independent C enumerator (`enum_pisa.c`) matched Halkiewicz's labeled counts exactly, and added one fact he did not state: every Pisa graph on 7 vertices is Seymour-tight (all 4080), while only 270 of 1050 on 6 vertices are.

## 3. The click

Halkiewicz's n=7 rigidity (missing graph regular) is an \(n=7\) accident. Already at n=6 the missing graph can be a matching, which is irregular as a degree sequence. The question at n=8 is whether *non-matching irregular* missing graphs occur.

They do. A CEGAR SAT model with source-component cuts produced a strong oriented graph on 8 vertices with

- missing edges \(\{04,07,14,17,23,25,26,35,36\}\),
- missing-degree sequence \(3^2 2^6\),
- margins \((0,-1,0,0,-1,-1,0,0)\),
- \(\Delta=0\).

The missing graph is a 4-cycle plus a \(K_4-e\), not a matching and not regular. `seymour.py` recomputes first and second neighbourhoods from the arc list and confirms Pisa. The same search produced a non-tight 2-regular-missing example (K_8 minus a 2-factor) and recovered the tight cycle and cycle-square.

So the n=8 census is not “the same two families plus matchings”. New types start immediately.

## 4. The argument, in the order it was found

1. Fetch Espuny Díaz et al., Halkiewicz v3, Sadhukhan–Sandeep–Sen, Brukhman, Guo–Kang–Zwaneveld.
2. Implement bitmask first/second neighbourhoods. Replay \(\overrightarrow{C_n}^k\) and lex products.
3. Exhaust labeled oriented graphs for \(n\le 7\). Match Halkiewicz 1050 and 4080.
4. Notice Conjecture 5.1 is already false at n=7; the live claim is regularity of the missing graph.
5. Attempt Brukhman's next layer by SAT. Learn it is implied by Kaneko–Locke for \(\delta\le 6\).
6. Search n=8 by missing-degree type. Tight cycle and cycle-square appear. Then a non-tight 2-factor. Then two irregular missing graphs.
7. Run `geng -q 8` through every undirected iso type (12346 graphs, 2.50 billion orientations of representatives). Exactly seven missing-degree types occur. SAT then supplied an explicit witness for the one type ( \(3^4 2^4\) ) the CEGAR hunt had not been asked for.

The n=8 irregular witness is checked as follows. Vertices \(\{0,\ldots,7\}\). Arcs:

```
0→5, 0→6,
1→0, 1→5, 1→6,
2→0, 2→1,
3→0, 3→1,
4→2, 4→3, 4→7,
5→4, 5→6, 5→7,
6→4, 6→7,
7→2, 7→3.
```

Missing: the C_4 \(0-4-1-7-0\) and the diamond \(2-5-3-6-2\) with chord \(2-3\). Every vertex has \(|N_2^+|\le|N_1^+|\), the maximum margin is 0, and the digraph is strongly connected. Certificate: `compute/certs/n8_irregular_pisa.json`, ternary code `145923119419`.

## 5. Computer residue

- Labeled census: `certs/pisa_n{4,5,6,7}.json`. n=7 took 217s, \(10^{10}\) graphs.
- Geng types n=6,7: `certs/pisa_geng_n{6,7}.json`, types agree with the labeled census.
- Geng n=8, finished: `certs/pisa_geng_n8.json`, `certs/pisa_n8_types.json`. Seven types, 162 Pisa orientations of representatives.
- SAT witnesses, independently rechecked: `certs/verified_witnesses.json`.
- Eulerian \(n=2\delta+3\) UNSAT (OR-Tools \(\delta\le 5\); Cadical \(\delta\le 4\) after the encoding fix). DIMACS in `certs/eulerian_n*_n2le*.cnf`. This does not beat Kaneko–Locke.
- OR-Tools \(\delta=6\) unknown at 300s.

## 6. What is proved vs still open

**Proved tonight (machine-checked, independently replayable).**

- Halkiewicz's labeled Pisa counts for \(n\le 7\) are correct. Every n=7 Pisa graph is Seymour-tight.
- There exist Pisa graphs on 8 vertices whose missing graph is not a matching and is not regular. Explicit certificates above.
- There exist *non-tight* Pisa graphs on 8 vertices whose missing graph is 2-regular.
- **Census.** Every Pisa orientation of an 8-vertex graph, up to undirected isomorphism of the underlying graph, has missing-degree sequence in
  \(\{5^8, 3^8, 3^6 2^2, 3^4 2^4, 3^2 2^6, 2^8, 1^8\}\).
  No tournaments, no 4-regular missing graphs, no incomplete matchings.

**Still open.**

- Seymour's conjecture.
- The full labeled n=8 count (162 is a representative count, not a labeled one).
- Eulerian \(n=2\delta+3\) for \(\delta\ge 7\).
- Any hereditary class beyond those already in Fidler–Yuster / Ghazal / Dara / Daamouch.
