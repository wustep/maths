# Research log — Seymour's second-neighborhood conjecture

## 2026-08-17

Fetched and read tonight, in the order used.

### The conjecture

Every oriented graph (finite directed graph, no loops, no 2-cycles) has a vertex $v$ with $|N_2^+(v)|\ge|N_1^+(v)|$. Published by Dean–Latka (1995) as Seymour's; the tournament case is Dean's conjecture.

### Degree and order bounds

- [Kaneko–Locke, *Congr. Numer.* 148 (2001)](https://www.researchgate.net/publication/240320571_The_minimum_degree_approach_for_Paul_Seymour''s_distance_2_conjecture). Every oriented graph with a vertex of outdegree $\le 6$ has a Seymour vertex. Implies all $n\le 15$ (n=15 only via tournaments).
- [Sadhukhan–Sandeep–Sen, arXiv:2606.30588](https://arxiv.org/abs/2606.30588) (29 Jun 2026). Claims $\delta^+=7$ by local reductions plus OR-Tools CP-SAT. Preprint; not rechecked tonight. Local PDF: `compute/refs/sadhukhan-2606.30588.pdf`.
- [Brukhman, arXiv:2608.11530](https://arxiv.org/abs/2608.11530) (12 Aug 2026). $n\le 2\delta+2$. Combined with Kaneko–Locke: any counterexample has $n\ge 17$. Combined with SSS: $n\ge 19$. Local: `compute/refs/brukhman-2608.11530.pdf`.
- [Espuny Díaz–Girão–Granet–Kronenberg, arXiv:2403.02842](https://arxiv.org/abs/2403.02842). Vertex-minimal counterexamples have $\delta^+>\sqrt n$; if any counterexample exists then arbitrarily large strong ones have bounded $\delta^+$. Every orientation of $G(n,p)$ for fixed $p<1/2$ works a.a.s.; $p>1/2$ is equivalent to the full conjecture. Local: `compute/refs/espuny-diaz-2403.02842.pdf`.

Wikipedia (oldid 1345329964, fetched 2026-08-17) still quotes Kaneko–Locke and $n\le 15$.

### Missing-graph classes (already proved)

- Tournaments: Fisher 1996; Havet–Thomassé 2000 (median orders).
- Missing a matching, a star, or a clique: Fidler–Yuster, *J. Graph Theory* 55 (2007).
- Missing a generalised star: Ghazal, *J. Graph Theory* 71 (2012).
- Missing a matching plus a star: Dara–Francis–Jacob–Narayanan, *Discrete Appl. Math.* 311 (2022), arXiv:1808.02247.
- Missing two stars; missing disjoint paths: Daamouch–Ghazal–Al-Mniny, [arXiv:2406.03635](https://arxiv.org/abs/2406.03635).
- Bipartite; independent set plus 2-degenerate: Dara et al. 2022.

A missing 2-factor (disjoint cycles) is not on that list. Daamouch treats paths, not cycles.

### Extremal / tight graphs

- [Halkiewicz, arXiv:2601.21563v3](https://arxiv.org/abs/2601.21563) (21 May 2026). Pisa graphs ($\Delta=0$, strong). Labeled census $n\le 7$: 1050 and 4080. Conjecture 5.1 (underlying $C_n$ or $K_n$ minus matching) contradicts his own n=7 table (720 graphs with 2-regular missing). Open problem (3): n=8. Local: `compute/refs/halkiewicz-2601.21563.pdf`.
- [Guo–Kang–Zwaneveld, arXiv:2603.29626](https://arxiv.org/abs/2603.29626) (31 Mar 2026). Seymour-tight orientations (every margin exactly 0). Closed under lex and generalised lex products. $\overrightarrow{C_n}^k$ is tight for $2k<n$. Classifies tight graphs with a vertex of outdegree 1 or 2.

### Constants, not used tonight

- Chen–Shen–Yuster $\gamma\approx 0.657$; Huang–Peng 2024 $\gamma\approx 0.715$. Every oriented graph has some vertex with $|N_2|\ge\gamma|N_1|$. Not a finite census.

### What we compare against

- Published small-order Pisa census: Halkiewicz $n\le 7$. Tonight independently recomputed; numbers agree. n=8 is the first open order. Tonight's census: exactly seven missing-degree types of Pisa graphs on 8 vertices (geng representatives), three of them irregular. See `compute/certs/pisa_n8_types.json`.
- Published structural claim at that frontier: Halkiewicz Conjecture 5.1, already false at n=7; the surviving experimental claim is “missing edges regular”. Tonight's n=8 types beat that claim.
- Order bound we did **not** beat: Brukhman $n\ge 17$ (unconditional), or $n\ge 19$ if SSS is accepted.

### False or unused full-proof claims

None used. SSS is a preprint and was not taken as a theorem for the purpose of claiming a new $\delta$ threshold.
