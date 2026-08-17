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
