# Research log — Frankl's union-closed sets conjecture

## 2026-08-17

Fetched and read tonight, in the order used.

### Primary (frequency constant)

- [Gilmer, *A constant lower bound for the union-closed sets conjecture*, arXiv:2211.09055v2](https://arxiv.org/abs/2211.09055) (28 Nov 2022). First constant `0.01`. Entropy of two iid samples. Conjectures the iid limit `φ=(3−√5)/2`. Local PDF: `compute/refs/gilmer-2211.09055.pdf`.
- [Alweiss–Huang–Sellke, *Improved lower bound…*, arXiv:2211.11731](https://arxiv.org/abs/2211.11731); EJC 31(3) P35 (2024). Proves Gilmer's `φ`. One 1-variable inequality checked by computer. Local: `compute/refs/alweiss-2211.11731.pdf`.
- [Chase–Lovett, *Approximate union-closed conjecture*, arXiv:2211.11689](https://arxiv.org/abs/2211.11689). `φ` is sharp for *approximate* union-closed families. Local: `compute/refs/chase-lovett-2211.11689.pdf`.
- [Sawin, *An improved lower bound…*, arXiv:2211.11504v3](https://arxiv.org/abs/2211.11504) (19 Jun 2023). Mix iid with max-entropy coupling; proves some `c>φ` without evaluating it. Local: `compute/refs/sawin-2211.11504.pdf`.
- [Yu, *Dimension-free bounds…*, arXiv:2212.00658v2](https://arxiv.org/abs/2212.00658); *Entropy* 25(5):767 (2023). Makes Sawin computable; `c*≈0.38234`. Cardinality reduction to two 2-point blocks. Local: `compute/refs/yu-2212.00658.pdf`.
- [Cambie, *Better bounds…*, arXiv:2212.12500v2](https://arxiv.org/abs/2212.12500) (16 Feb 2025). Evaluates Sawin exactly: `0.382345533366702 ≤ c* ≤ 0.382345533366703`, `α*≈0.03560698136437784`. Code: https://github.com/StijnCambie/UCconjecture. Calls the computer check “slightly less rigorous”. Local: `compute/refs/cambie-2212.12500.pdf`.
- [Liu, *Improving the lower bound… via conditionally IID coupling*, arXiv:2306.08824](https://arxiv.org/abs/2306.08824) (15 Jun 2023). Theorem 6: some unspecified `c>c*` (Example 4 perturbation). Theorem 13: `c′≈0.382709` under PSD + 9-D global-min hypotheses, Example 5. Local: `compute/refs/liu-2306.08824.pdf`.

### Status quotes (what the literature treats as “the” constant)

- [Lu–Raz, *Note on the union-closed sets conjecture and Reimer's average set size theorem*, arXiv:2405.10639v2](https://arxiv.org/abs/2405.10639) (30 May 2024): “The best constant lower bound currently is approximately 0.38271, proven by Liu.” Local: `compute/refs/lu-raz-2405.10639.pdf`.
- [Wikipedia, *Union-closed sets conjecture*](https://en.wikipedia.org/wiki/Union-closed_sets_conjecture), oldid 1350313043, fetched 2026-08-17: quotes `0.38271` and cites Liu + Lu–Raz.
- [Das–Janzer–Sudakov, *Frequent elements in union-closed set families*, arXiv:2412.03862](https://arxiv.org/abs/2412.03862): treats Liu's number as the standing frequency bound; k-th most frequent element matches the Gilmeresque constant for large families.

### Finite cases (not moved tonight)

- [Bruhn–Schaudt, *The journey of the union-closed sets conjecture*, arXiv:1309.3297](https://arxiv.org/abs/1309.3297); *Graphs Combin.* 31 (2015). Survey through 2013.
- [Roberts–Simpson, *A note on the union-closed sets conjecture*](http://ajc.maths.uq.edu.au/pdf/47/ajc_v47_p265.pdf), *Australas. J. Combin.* 47 (2010) 265–267. Minimal counterexample has `|A|≥4q−1`. Combined with `q≥13` this is `|F|≥51`, hence the `|F|≤50` statement.
- [Vučković–Živković, *The 12-element case of Frankl's conjecture*](https://ipsitransactions.org/journals/papers/tir/2017jan/p9.pdf), *IPSI BGD Trans. Internet Research* 13 (2017). Universe size `≤12`.
- [Sarvate–Renaud, *On the union-closed sets conjecture*, *Ars Combin.* 27 (1989)]. Smallest set of size 1 or 2 forces an abundant element of that set; size 3 does not (Graham-type examples).

### False or unused full-proof claims

- Scandone, arXiv:2302.03484, “A proof of the union-closed sets conjecture”. Later literature still treats the conjecture as open.
- A January 2026 HAL note claiming an “algorithmic proof” was not used.

### What we compare against

- Best *unconditional explicit* published constant with a complete reduction: Yu–Cambie `c* = 0.3823455333667027…` (computer-checked 2-variable inequality). Independently recomputed tonight, residual `<10^{-15}` vs Cambie's quote.
- Best *quoted* published constant: Liu `0.382709087918741`, under two numerical hypotheses. Independently recomputed: `0.382709087918735`. Mesh first-crossing of his Example-5 mix on `{b,1}`: `0.38271065`.
- Tonight's number `0.38285` beats Liu on that same family, with his Example 4 protocol. It does not replace Yu–Cambie as an unconditional theorem, and it is not `1/2`.

## 2026-08-27

Fetched and read tonight, in the order used. No paper after Liu moves the frequency constant.

### Primary (frequency constant, re-opened)

- [Gilmer, *A constant lower bound for the union-closed sets conjecture*, arXiv:2211.09055v2](https://arxiv.org/abs/2211.09055) (28 Nov 2022). Re-fetched. Theorem: some element in a 0.01 fraction. Does not claim `φ` as a theorem; conjectures it as the iid limit. Local PDF: `compute/refs/gilmer-2211.09055.pdf`.
- [Liu, *Improving the lower bound… via conditionally IID coupling*, arXiv:2306.08824v1](https://arxiv.org/abs/2306.08824) (15 Jun 2023). Re-fetched HTML. Example 4 is (22)–(23); Theorem 6 is existential `c > c*`; Theorem 13 is `c′ ≈ 0.382709087918741` under PSD + global-min, Example 5, `β* ≈ 0.10005`. No Example-4 numerical section. Local: `compute/refs/liu-2306.08824.pdf`.
- [Lu–Raz, *Note on the union-closed sets conjecture and Reimer's average set size theorem*, arXiv:2405.10639](https://arxiv.org/abs/2405.10639). Re-opened abs page. Still: “The best constant lower bound currently is approximately 0.38271, proven by Liu.”
- [Wikipedia, *Union-closed sets conjecture*](https://en.wikipedia.org/wiki/Union-closed_sets_conjecture), fetched 2026-08-27. Still quotes 0.38271 and cites Liu + Lu–Raz. Finite cases still 50 sets / 12 elements.
- [Das–Wu, *Frequent elements in union-closed set families*, arXiv:2412.03862v3](https://arxiv.org/abs/2412.03862) (11 Jul 2025). Re-opened abs. k-th frequent element; large-family frequency `φ − o(1)`. Intro treats 0.3823455 as “where things stand today” and cites Liu's CISS writeup separately. Does not claim a number above Liu.

### Later papers that do not move the frequency constant

- [DeFranco, *On Boolean polynomials and the Union-Closed Conjecture*, arXiv:2606.26191](https://arxiv.org/abs/2606.26191) (24 Jun 2026). Encoding: the conjecture for given `(m,n)` iff a Boolean polynomial is identically zero. No numerical constant.
- [Tian, *Frankl's Conjecture at Height Four…*, arXiv:2608.25147](https://arxiv.org/abs/2608.25147) (25 Aug 2026). Proves the empty-set-free form for poset height ≤ 4. Structural constraints at height 5. Not a frequency constant; first-open universe size remains 13 in the papers that state that frontier.
- [Gendler, *Partial results for union-closed conjectures on the weighted cube*, arXiv:2504.13347v3](https://arxiv.org/abs/2504.13347) (4 Nov 2025). Weighted product measure; Karpas-type density and Knill log bound. No 0.38-style constant.
- arXiv API query `all:union-closed AND all:conjecture`, sorted by submitted date, 30 hits (2026-08-27). No hit after Liu claims a frequency constant above 0.38271.

### What we compare against tonight

- Best *quoted* published constant: still Liu 0.382709087918741 (conditional). Independently recomputed: 0.382709087918735.
- Repo ray-record from 2026-08-17: 0.38285 at `β = 1/5`, mesh min ratio 1.000077. Replayed; `compute/run_all.sh` exit 0.
- Tonight: analytic first-crossing of pure Example 4 on `{b,1}` is 0.38305135658682558…; certified 0.38304 with mesh min ratio 1.000021687. Beats both. Same hypothesis class. Not `1/2`.

## 2026-08-27 (q2)

Fetched and read tonight, in the order used. No paper after Liu moves the frequency constant. The 2-sample `{b,1}` class cannot pass 0.383051.

### Primary (re-opened)

- [Gilmer, *A constant lower bound for the union-closed sets conjecture*, arXiv:2211.09055v2](https://arxiv.org/abs/2211.09055) (28 Nov 2022). Re-fetched abs + HTML. Theorem: some element in a 0.01 fraction. §5 Conjecture 1 (`H(A∪B)+D(A∪B||A)>H(A)` whenever every frequency is `<1/2`) would imply Frankl 1/2. v2 note: Sawin and Ellis refute Conjecture 1; without extra assumptions the KL term cannot improve the bound. Local PDF: `compute/refs/gilmer-2211.09055.pdf`.
- [Liu, *Improving the lower bound… via conditionally IID coupling*, arXiv:2306.08824v1](https://arxiv.org/abs/2306.08824) (15 Jun 2023). Re-fetched abs + HTML. Theorem 6: some unspecified `c>c*` via Example 4. Theorem 13: `c′≈0.382709087918741` under PSD + global-min, Example 5, `β*≈0.10005`. Example 4 is (22)–(23). No later version. Local: `compute/refs/liu-2306.08824.pdf`.
- [Ellis, *Note: a counterexample to a conjecture of Gilmer…*, arXiv:2211.12401](https://arxiv.org/abs/2211.12401) (22 Nov 2022). Opened abs + HTML. n=2 law `p(∅)=p({1,2})=0.3`, `p({1})=p({2})=0.2`; functional `< −0.04`; a small perturbation has frequencies `<1/2` and stays negative. Independently replayed: `−0.046797` unperturbed, `−0.043422` at `ε=10^{-3}`.
- [Wikipedia, *Union-closed sets conjecture*](https://en.wikipedia.org/wiki/Union-closed_sets_conjecture), fetched 2026-08-27. Still quotes 0.38271 and cites Liu + Lu–Raz. Finite cases still 50 sets / 12 elements.

### Later papers that do not move the frequency constant

- arXiv API query `all:"union-closed" AND all:conjecture`, submitted-date desc, 25 hits (2026-08-27). Newest frequency-adjacent items are Tian 2608.25147 (height 4), DeFranco 2606.26191 (Boolean encoding), Das–Wu 2412.03862 / 2412.03863 (k-th frequency). No hit after Liu claims a first-frequency constant above 0.38271.
- [Tian, arXiv:2608.25147](https://arxiv.org/abs/2608.25147). Height ≤ 4. Not a frequency constant.
- [“The union-closed set conjecture is true”, arXiv:2405.03731](https://arxiv.org/abs/2405.03731). Title-only full-proof claim; later literature and Wikipedia still treat the conjecture as open. Not used.

### What we compare against tonight

- Best *quoted* published constant: still Liu 0.382709087918741 (conditional). Independently recomputed: 0.382709087918735.
- Repo ray-record from q1: 0.38304, analytic crossing 0.38305135658682558…. Replayed; `compute/q1/run_all.sh` exit 0.
- Tonight: that crossing is a ceiling for every 2-sample bit protocol on `{b,1}`. Mixes and a half-target protocol do not beat it. A constructed 2-mixture has pure-Example-4 CIID ratio 0.909137 at mean 0.38304. Constant unchanged. Not `1/2`.
