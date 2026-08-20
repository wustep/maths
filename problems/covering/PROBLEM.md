# Linear covering codes of radius two

- Slug: `covering`
- Solver: Codex `gpt-5.6-sol` Max (2026-08-16 overnight). Grok watched only.
- Status: finite dent certified; asymptotic problem open
- Area: Coding theory
- Sources: Green 100 #40; Cohen et al., *Covering Codes*; Davydov–Marcugini–Pambianco, arXiv:2511.02542 (Table 5.1); Kaikkonen–Rosendahl
- Started: 2026-08-16
- Tonight: finite-cex — beat a documented small \(\ell_2(r,2)\) length, emit H and an exhaustive radius-2 certificate

## In general

For a binary linear code \(C\le\mathbb F_2^n\) of codimension \(r\), the covering radius is the least \(R\) such that every vector of \(\mathbb F_2^n\) lies at distance at most \(R\) from \(C\). Equivalently, if \(H\) is an \(r\times n\) parity-check matrix, every syndrome in \(\mathbb F_2^r\) is a sum of at most \(R\) columns of \(H\). Write \(\ell_2(r,R)\) for the least length of a binary linear code with redundancy \(r\) and covering radius \(R\).

Green's Problem 40 asks for the asymptotic density
\[
f(2)=\liminf_{r\to\infty}\frac{1+\ell_2(r,2)+\binom{\ell_2(r,2)}{2}}{2^r}.
\]
The known range is \(1\le f(2)\le 1.4238\); it is not even known whether \(f(2)=1\). Tonight is not \(f(2)\). Tonight is a documented finite length.

**Stale as written.** The \(1.4238\) had already been superseded by arXiv:2511.02542 (\(\approx 1.32031\)) before this line was typed, and the \(n=50\) seed brings it to \(2601/2048\approx 1.27002\). See [`result/NOTE.md`](result/NOTE.md) §6.

The November 2025 table of Davydov–Marcugini–Pambianco (arXiv:2511.02542v1, Table 5.1) lists \(\ell_2(10,2)\le 51\) (Kaikkonen–Rosendahl), density \(1327/1024\approx 1.29590\). Secondary holes in the same table: \(\ell_2(8,2)\le 26\) and \(\ell_2(9,2)\le 39\).

## Precise statement

A binary \(r\times n\) matrix \(H\) has covering radius at most 2 if its columns \(S\subset\mathbb F_2^r\) satisfy
\[
\{0\}\cup S\cup(S+S)=\mathbb F_2^r.
\]
**Tonight's finite subquestion.** Find an explicit \(H\) whose length improves a documented table entry, preferably \(\ell_2(10,2)\le 50\), and emit an independently re-runnable exhaustive certificate that every one of the \(2^r\) syndromes is a sum of at most two columns. Do not claim \(f(2)\).

## Certified finite dent (quest q1, recovered)

Quest q1 found a binary \([50,40]\) code of covering radius exactly 2. The explicit parity-check matrix is [`compute/H_r10_n50.txt`](compute/H_r10_n50.txt); the integer-column witness is [`compute/witness_r10_n50.json`](compute/witness_r10_n50.json). Independent exhaustive pair-XOR cover: \(1024/1024\) syndromes. Finite density \(319/256=1.24609375\). This proves
\[
\ell_2(10,2)\le 50
\]
and does **not** determine \(f(2)\). An \(n=49\) anneal left 7 uncovered syndromes — a search residue, not a lower bound.


## Certified finite dents (quest q5, 2026-08-19)

From the same 50-set, constructions $\mathrm{QM}_3^2$ and $\mathrm{QM}_5^2$ of arXiv:2511.02542 were implemented and independently replayed (official C verifier plus a second bitset checker; full $2^r$ sweeps):

- $\ell_2(22,2)\le 3325$ (paper 3389) — [`compute/H_r22_n3325.txt`](compute/H_r22_n3325.txt)
- $\ell_2(24,2)\le 6653$ (paper 6781) — [`compute/H_r24_n6653.txt`](compute/H_r24_n6653.txt)
- $\ell_2(26,2)\le 13309$ (paper 13565) — [`compute/H_r26_n13309.txt`](compute/H_r26_n13309.txt)
- $\ell_2(28,2)\le 26111$ (paper 26623) — [`compute/H_r28_n26111.txt`](compute/H_r28_n26111.txt), $p(H)\le 64$

Theorem-only from the $r=28$ seed: $\ell_2(40,2)\le 1671167$, $\ell_2(42,2)\le 3342335$, $\ell_2(44,2)\le 6684671$ (not enumerated). $n=49$ is still a 7-hole search residue, not a lower bound.

## Certified finite dents (quest q6b, 2026-08-19)

- Exact 3-sum: every vector of $\mathbb F_2^{10}$ is a sum of exactly three distinct columns of the 50-set (1024/1024).
- $\ell_2(26,3)\le 817$ (paper 818) — [`compute/H_R3_r26_n817.txt`](compute/H_R3_r26_n817.txt). Full $2^{26}$ radius-3 sweep.
- $p(H)\le 64$ on the $r=28$ matrix — [`compute/partition_r28_n26111_p64.txt`](compute/partition_r28_n26111_p64.txt). Unlocks theorem-only $\ell_2(40,2)\le 1671167$.

## Certified finite dent (quest q6c, 2026-08-19)

- $\ell_2(31,4)\le 689$ (paper 690) — [`compute/H_R4_r31_n689.txt`](compute/H_R4_r31_n689.txt). QM$_4^4$ from OK2 plus the 50-set. Blockwise certificate for all $2^{31}$ syndromes; radius exactly 4. Independent C replay in `/tmp`, not a flat sweep.

## Certified finite dents (quest q7c, 2026-08-19)

- $p(H_{18})\le 17$ on the certified $r=18$, $n=815$ matrix — [`compute/partition_r18_n815_p17.txt`](compute/partition_r18_n815_p17.txt). Full $2^{18}$ cross-block sweep.
- $p(H_{20})\le 14$ on the certified $r=20$, $n=1631$ matrix — [`compute/partition_r20_n1631_p14.txt`](compute/partition_r20_n1631_p14.txt). Full $2^{20}$ cross-block sweep.
- Theorem-only $\ell_2(38,3)\le 13102$ (paper 13118) and $\ell_2(41,3)\le 26206$ (paper 26238) via QM$_5^3$ / Theorem 7.3. Not enumerated.

## Certified finite dents (quest q8, 2026-08-20)

Leftover unused constructions from [`compute/notes_from_authors_2026-08-19.md`](compute/notes_from_authors_2026-08-19.md):

- $M_{OK}$ last word is independently `1CE` (paper OCR `ICE`). Unique among 512 last words making $P_{OK}$ a $(3,1)$-partition.
- $\ell_2(21,3)\le 303$ (older table 308; matches the paper) — [`compute/H_R3_r21_n303.txt`](compute/H_R3_r21_n303.txt). Full $2^{21}$ radius-3 sweep: $2097152/2097152$.
- $\ell_2(26,2)\le 13070$ (paper 13565; previous certified 13309) — [`compute/H_r26_n13070.txt`](compute/H_r26_n13070.txt). QM$_2^1$ from $p(H_{18})\le 17$. Full $2^{26}$ sweep: $67108864/67108864$.
- $p(H_{26})\le 19$ — [`compute/partition_r26_n13070_p19.txt`](compute/partition_r26_n13070_p19.txt). Unlocks theorem-only $\ell_2(36,2)\le 418271$ (paper 425983). Not enumerated.


## What a solution looks like

- An explicit matrix under `compute/` and a verifier that checks F\(_2\)-rank \(r\) and that every syndrome is a sum of at most 2 columns.
- A documented comparison to the previous table entry.
- Do not claim \(f(2)\). Do not claim optimality of the finite length without a matching lower bound.

## Related

- [Ben Green, *100 Open Problems*, Problem 40](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf)
- [Davydov–Marcugini–Pambianco, *New upper bounds for binary linear covering codes*, arXiv:2511.02542](https://arxiv.org/abs/2511.02542)
- Cohen, Honkala, Litsyn, Lobstein, *Covering Codes*

## Quests so far


## Figures

Regenerated from `compute/search_results.json`: [`figures/q1_density_vs_length.png`](figures/q1_density_vs_length.png).

Interactive explainer (Claude Opus and Fable 5): [`explainer.html`](explainer.html).
PDF explainer (problem, process, result, verification): [`explainer.pdf`](explainer.pdf).
