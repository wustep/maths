# Attack log — the 1/3–2/3 conjecture for posets

## 2026-08-17 — start

- Folder empty except `PROBLEM.md`. House: write only here; no git; cite what we beat; no invented dent.
- Conjecture (Kislitsyn 1968; Fredman; Linial 1984): every finite non-chain poset $P$ has an incomparable pair $x,y$ with
  $$
  \tfrac13\le p_P(x\prec y)\le\tfrac23,
  $$
  equivalently $\delta(P)\ge 1/3$, where $\delta(P)=\max_{x\parallel y}\min\{p(x\prec y),p(y\prec x)\}$.
- Tonight: a certified new finite order, a new structural class with a replayable proof, or an exact minimal candidate with independently checked linear-extension probabilities.

### Published record (fetched 2026-08-17)

**Still open in general.** Chan–Pak, *Linear extensions of finite posets*, arXiv:2311.02743v2 (Feb 2025 / EMS Surv. Math. Sci. online 2025) still list Conjecture 13.1 as open. Wikipedia oldid 1368808118 (fetched tonight) agrees. Aires–Kahn, arXiv:2509.11549 (Sep 2025) make large-width progress on the Kahn–Saks $\delta\to 1/2$ conjecture but do not prove $1/3$–$2/3$.

**General lower bound.** Brightwell–Felsner–Trotter 1995: $\delta(P)\ge(5-\sqrt5)/10\approx 0.276393$. Previous: Kahn–Saks $3/11$; Kahn–Linial / Khachiyan $1/(2e)$. The BFT constant is sharp for a continuous/infinite analogue.

**Finite census.**

| order | what was verified | source |
| ---: | --- | --- |
| $\le 11$ | Gold Partition Conjecture (hence $1/3$–$2/3$) | Peczarski, *Order* 23 (2006) |
| $\le 13$ | full mutual-rank census; worst balanced posets | De Loof–De Baets–De Meyer, *Comput. Math. Appl.* 59 (2010) |
| $\le 14$ | Gold Partition (hence $1/3$–$2/3$); *not* a full $\delta$-census at 14 | Gupta, arXiv:2607.23926 (27 Jul 2026) |

Order 15 is not a one-night exhaustive target (unlabeled posets at 14 already $1.338\times 10^{12}$).

**Structural classes already proved.** Width 2 (Linial 1984; Sah 2021 improves the width-2 constant); height 2 (Trotter–Gehrlein–Fishburn 1992); series-parallel / $N$-free (Zaguia 2012); semiorders (Brightwell 1989); 5-thin (Brightwell–Wright 1992); 6-thin, including Gold Partition (Peczarski 2008); cover-graph a forest / polytrees (Zaguia 2019); posets with a nontrivial automorphism (Ganter–Hafner–Poguntke 1987); almost-twin pairs (Zaguia 2016); Boolean / partition / subspace lattices and Young diagrams including skew and shifted (Olson–Sagan, *Order* 2018, arXiv:1706.04985).

**Explicitly still open in the 2018 Olson–Sagan paper, and I found no later resolution tonight.**

- Products of $k\ge 3$ chains (their Question 3.9). $C_m\times C_n$ is a rectangle, already covered; $C_2\times C_2\times C_n$ has almost-twins, so is covered by Zaguia. The first open boxes are $C_2\times C_3\times C_n$ and $C_3\times C_3\times C_3$.
- All posets of dimension 2 (their Question 5.2). They get $\delta=1/2$ only for a pattern-avoiding subclass.
- All distributive lattices (their Question 3.6).
- Interval orders that are not semiorders (Wikipedia and Chan–Pak list semiorders, not interval orders).

**Extremal numbers.**

- Equality $\delta=1/3$ is achieved by the 3-element poset $T=C_2+C_1$ and by linear sums of copies of $T$ and singletons (Aigner 1985: these are the only width-2 equality cases).
- Next published values above $1/3$: Olson–Sagan $37/106\approx 0.349057$; Chen, *Electron. J. Combin.* 25 (2018), infinite width-2 family with limit $\kappa=\frac1{32}(93-\sqrt{6697})\approx 0.348900$.
- Width $\ge 3$: smallest published example is Saks’ 7-element $M_7$ with $\delta=14/39\approx 0.358974$. Trotter–Gehrlein–Fishburn / Olson–Sagan: no width-$\ge 3$ poset on $\le 9$ elements beats $14/39$. Peczarski 2019 (*Exp. Math.* 28) conjectures the worst non-$1/3$ examples are “ladders with broken rungs”, with a numerical gap $\approx 0.348843$.

**Aires–Kahn 2025 (status, not a $1/3$ proof).** $\delta(P)\to 1/2$ if width $\Omega(n)$ or $|\min P|\gg\log n$; $\delta(P)\ge 1/e-o(1)$ if width $\omega(\sqrt n)$ or height $o(n)$. Kahn–Saks “$\delta\to 1/2$ as width $\to\infty$” remains open.

### Plan

1. Independently replay $T$, Aigner sums, Saks $M_7=14/39$, Olson $C=37/106$, and Chen’s $E(m,n)$ table, with two LE counters.
2. Attack Olson–Sagan Question 3.9: exact pair probabilities in $C_a\times C_b\times C_c$. If a single pair is $\ge 1/3$ for all non-chain boxes, that is a new class with a replayable (computational + closed-form) proof.
3. If the box class closes, try the next open slice (interval orders, or width-3 at order 10).
4. If nothing moves, leave a residue: verifier + independently checked extremal table. Search residue is not a bound.

## 2026-08-17 — literature click

The finite frontier at 14 is already taken (Gupta). The judge was right that “all posets of order $N$” is not a handle. Olson–Sagan Question 3.9 is a handle: a named open class, exact counts available by order-ideal DP, and the 2-dimensional case already has a hook-length proof we can try to imitate.

A second handle: the width-3 minimum $\delta=14/39$ is published only through 9 elements (Trotter–Gehrlein–Fishburn 1992; Olson–Sagan 2018). Order 10 is the first unpublished width-3 order.

## 2026-08-17 — counters work; published numbers replay

Two independent LE counters (order-ideal DP; remaining-set minima recursion) and two pair counters (De Loof forward–backward; add the relation and recount) agree on every small test.

| object | published | tonight |
| --- | ---: | ---: |
| $T=C_2+C_1$ | $\delta=1/3$, $e=3$ | same |
| Chen $E(5,5)$ | 106 | 106 |
| Chen $P(5,5)$ | Olson–Sagan $C$ has $\delta=37/106$ | $\delta=37/106$ on Chen $P(5,5)$ |
| Chen $E(m,n)$ table for $(m,n)\le(5,5)$ | Appendix A of arXiv:1709.05753 | exact match |
| Saks $M_7$ | $e=39$, $\delta=14/39$ | recovered by exhaustive n=7 search; down-sets `[0,0,1,1,7,7,31]`; pair $25:14$ |
| hook-length $e(C_m\times C_n)$ | $(mn)!/\prod h_{ij}$ | exact match for $(2,3),(2,5),(3,3),(3,4)$ |
| $e(Y(4,4,2))$ | 252 | 252 |

So the numbers people cite are real.

## 2026-08-17 — 3-chain boxes: the atom-pair lemma

Olson–Sagan Question 3.9 is still open. Almost-twins fail already for $C_2\times C_3\times C_3$ (explicit search: zero almost-twin pairs). Aut(P) gives $\delta=1/2$ iff two factors have equal size $\ge 2$. Anti-automorphism of a box has at most one fixed point, so Olson–Sagan Prop. 2.6 does not apply.

The useful pair is not the atoms of an arbitrary face. For $C_2\times C_6$ the Olson atom pair already has $\min=7/22<1/3$; thickening in a short third dimension leaves it below $1/3$ (at $c=3$: $0.332759$). That pair is the wrong pair, not a counterexample: the atoms of the two *largest* dimensions of $C_2\times C_6\times C_3$ have min $0.417759\ge 1/3$, and the full $\delta(C_2\times C_6\times C_3)=273419876590786707/569177957111013830\approx 0.480$.

**Case split for every box $C_a\times C_b\times C_c$, $a\le b\le c$:**

1. $a=1$: a rectangle. Olson–Sagan hook-length / Linial.
2. Two of $\{a,b,c\}$ equal and $\ge 2$: coordinate-swap automorphism, a 2-cycle, $\delta=1/2$.
3. Otherwise $a=2<b<c$ or $3\le a<b<c$. The two largest factors $b,c$ are both $\ge 3$, so the 2-dimensional atom pair of $C_b\times C_c$ already lies in $[1/3,2/3]$ (Olson–Sagan: for $m,n\ge 3$, $\frac{(n-1)(m+1)}{2(mn-1)}\in[1/3,2/3]$). Embed those two atoms in the box and thicken by $a$.

**Observed thickening law** (exact plane-partition DP, all $a\le b$, $abc\le 60$, and $C_2\times C_3\times C_n$ through $n=10$): if $p(1)=P(u\prec v)$ in the 2-face, then $p(c)$ is strictly monotone toward $1/2$. In particular $\min(p(c),1-p(c))$ is increasing, so it stays $\ge 1/3$ whenever the 2-face is already $\ge 1/3$.

This would settle *every* 3-chain product. The monotonicity is not proved; it is a replayable computation on the range above. Full $\delta$ (not just one pair) was computed for the dangerous boxes $C_2\times C_k\times C_3$ ($k=3..7$) and $C_2\times C_6\times C_4$, $C_3\times C_4\times C_3$: all have $\delta\ge 0.467$.

Plane-partition DP independently matches the bitmask counters on every box with $n\le 24$.

## 2026-08-17 — width-3 census through 9, then 10

Naturally labelled generation (add a maximal element whose down-set is an ideal; keep width $\le 3$). Every unlabelled poset appears after relabelling by a linear extension.

C implementation `compute/census.c`, independently replayed through $n=8$ by `width3_census.py`.

| n | naturally labelled | width = 3 | min $\delta$ | $<14/39$ | $<1/3$ |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 5 | 314 | 212 | $4/11$ | 0 | 0 |
| 6 | 3339 | 2842 | $4/11$ | 0 | 0 |
| 7 | 43502 | 40916 | $14/39$ | 0 | 0 |
| 8 | 657363 | 643236 | $14/39$ | 0 | 0 |
| 9 | 11106683 | 11026537 | $14/39$ | 0 | 0 |

n=9 independently replays Olson–Sagan / TGF. The n=7 minimum is Saks $M_7$. n=8,9 minima are linear sums of $M_7$ with a chain (same $\delta$).

## 2026-08-17 — n=10 beats 14/39

`./census 10` (666 s): 204,767,041 naturally labelled posets, 204,298,353 of width 3.

- min $\delta = 66/187 = 6/17 \approx 0.352941 < 14/39 \approx 0.358974$
- 187 naturally labelled posets have $\delta<14/39$
- 0 have $\delta<1/3$
- $e=187$ on the minimiser, and $187=n_{<14/39}$, so there is a unique unlabelled width-3 10-element poset below the published record

Witness $W_{10}$, down-sets `[0,0,1,1,7,11,23,87,95,255]`, covers
`(0,2),(0,3),(1,4),(1,5),(2,4),(3,5),(3,8),(4,6),(5,9),(6,7),(6,8),(7,9)`.
3-antichains $\{1,2,3\}$ and $\{5,7,8\}$. Best pair $(3,4)$ splits $121:66$.

Independently rechecked in `verify_W10.py`: four LE counts all 187; two pair counters agree; width 3; $6/17<14/39$ and $6/17>1/3$.

This beats the published width-3 record (Saks $14/39$, TGF/Olson–Sagan through 9). It does **not** beat the overall (all-width) record: width-2 ladders already reach $37/106\approx 0.349$ and Chen's limit $\approx 0.3489$. Peczarski's n=10,11 work is that global width-2 minimum, not this slice.

## 2026-08-17 — residue, not an overclaim

- $W_{10}$ is a certified new finite-order width-3 example. Replay: `python3 compute/verify_W10.py`.
- Three-chain products: every computed box has $\delta\ge 1/3$; the two-largest-factors pair works whenever both are $\ge 3$. Monotonicity of thickening is observed, not proved. Question 3.9 is not closed.
- The unrestricted conjecture and Gupta's order-14 GPC frontier are untouched.

## 2026-08-27 — Gupta v2 is a δ-census; q1 starts there

The 17 August note cited Gupta arXiv:2607.23926 as Gold Partition through 14, not a δ-census. That is v1 (27 Jul). Version 2 (30 Jul 2026, title *Balance Constants, Majority Cycles, and the Gold Partition Conjecture through Fourteen Elements*) computes exact balance constants for every one of the 1,338,193,159,771 unlabelled 14-element posets. Opened tonight: abs, HTML v2, and `data/census-n14.txt` on github.com/agupta/gold-partition-conjecture.

Published record, after v2:

- least δ above 1/3 at order 14 is 37/106 (Chen / L_{10,1,5}, padded)
- least among posets that are not nontrivial ordinal sums is 254/725 = L_{14,1,9}
- no value in Peczarski's printed gap (1/3, 0.348843)
- 128 equality classes, all Aigner sums of T and singletons
- longest majority cycle has length 8 (30 classes)
- GPC still holds through 14 (unchanged from v1)

The width-3 6/17 row in Gupta's tail is 29 ordinal sums, width 3. That is W_{10} (or a dual) padded by singletons. Every strictly smaller tail value is width 2. So there is no width-3 poset on ≤ 14 elements with δ < 6/17. The first unused width-3 order is 15.

q1 independently replays the named witnesses and the broken-rung table, then searches n≥15 width-3 extensions and the three-rail analogue. Isolated random posets stay residue. The unrestricted conjecture is not claimed.

## 2026-08-27 — certified ladder table through 21; no width-3 dent

Independently constructed every broken-rung ladder from Peczarski's §1 formula (rails $x_i<x_{i+2}$, rungs $x_i<x_{i+3}$) and counted $\delta$ with this notebook's pair counters.

Gupta Table 1, exact match, every non-sum ladder at that order:

| n | min $\delta$ | ladder |
| ---: | ---: | --- |
| 7 | $9/25$ | $L_{7,1,2}$ |
| 8 | $17/46$ | $L_{8,1,2,3}$ |
| 9 | $6/17$ | $L_{9,1,2,3,4}$ |
| 10 | $37/106$ | $L_{10,1,5}$ |
| 11 | $20/57$ | $L_{11,1,6}$ |
| 12 | $97/277$ | $L_{12,1,7}$ |
| 13 | $157/448$ | $L_{13,1,8}$ |
| 14 | $254/725$ | $L_{14,1,9}$ |

Past Gupta's table, still a complete subset search of the class (Python through 18; C through 21, with the winning ladder replayed in Python):

| n | min $\delta$ | ladder | note |
| ---: | ---: | --- | --- |
| 15 | $166/475$ | $L_{15,1,5,6,10}$ | Peczarski named the broken set; fraction not in Gupta |
| 16 | $665/1898$ | $L_{16,1,11}$ | not quoted by Gupta |
| 17 | $1304/3737$ | $L_{17,1,5,8,12}$ | Peczarski named the broken set |
| 18 | $387/1108$ | $L_{18,1,5,6,9,13}$ | first order past Peczarski's quoted names |
| 19 | $458/1311$ | $L_{19,1,5,6,9,10,14}$ | |
| 20 | $6059/17366$ | $L_{20,1,5,8,11,15}$ | |
| 21 | $5402/15485$ | $L_{21,1,5,8,9,12,16}$ | $\approx 0.348854$, just above Peczarski's printed $\beta$ |

All of these have $\delta>1/3$. Width 2. They do not beat the conjecture, and they do not beat Chen's infinite-family limit as a theorem. They do move the finite per-order table of this named class.

n=22 was left running; that row is residue, not a minimum.

Width-3: every one-point width-$\le 3$ extension of $W_{10}$ (101 of them) has $\delta\ge 6/17$. The two ordinal-sum extensions keep $6/17$; the 99 non-sums are at best $94/253\approx 0.372$. Three-rail posets (rails $x_i<x_{i+3}$, optional $+4$ and $+5$ rungs) are exhaustive through $n=12$ with min $\delta=3466/8587$ at $n=12$, none below $6/17$. A greedy $n=15$ three-rail search has $\delta=4855/11607>6/17$ and is residue. Naturally labelled interval orders through $n=8$ all have $\delta\ge 1/3$ (min $1/3$, the Aigner family); that is a finite class census, not a proof of the class.

Replay: `cd compute/q1 && ./run_all.sh`.

No width-3 poset with $\delta<6/17$ was certified. The unrestricted conjecture is still open.
