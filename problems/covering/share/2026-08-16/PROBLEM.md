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
