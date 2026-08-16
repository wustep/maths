# Research log — C7 fifth strong power

URLs actually opened this session.

## Papers

- [Polak–Schrijver, arXiv:1808.07438](https://arxiv.org/abs/1808.07438) and [ar5iv HTML](https://ar5iv.labs.arxiv.org/html/1808.07438) — independent set of size 367 in \(C_7^{\boxtimes 5}\). Construction: geometric orbit in \(C_{108,382}^{\boxtimes 5}\), shift, fold \(\lfloor 2i/109\rfloor\), drop non-isolated image vertices (\(|M|=327\)), extend residual (71 verts, 85 edges, \(\alpha=40\)). Appendix lists the 367 words. They already report no 368 from other shifts/divisors, and no 3-out/4-in local move.
- [CWI PDF of the same paper](https://ir.cwi.nl/pub/30364/30364.pdf)
- [Tilburg PDF](https://pure.uvt.nl/ws/portalfiles/portal/82278307/1-s2.0-S0020019018302291-main.pdf)
- [Itty–Rosin–Carstensen–Reichman, arXiv:2607.21517](https://arxiv.org/abs/2607.21517) / [HTML](https://arxiv.org/html/2607.21517v1) — \(\alpha(C_7^{\boxtimes 10})\ge 134753\), still uses the same 367-set in dimension 5. Explicit \(r_j,q_j\) private pairs.
- [Gao, arXiv:2607.27869](https://arxiv.org/abs/2607.27869) / [HTML](https://arxiv.org/html/2607.27869v1) — recursive gadget product; “367 remains the largest currently known” in the fifth power. Points to `inputs/R367.txt`.
- [Buys–Polak–Zuiddam, arXiv:2607.29681](https://arxiv.org/abs/2607.29681) / [HTML](https://arxiv.org/html/2607.29681) — Lean-verified \(\Theta(C_7)\ge 3.258805\ldots\) from a profile \((367,8,367,322)\) on \(C_7^{\boxtimes 5}\) iterated to the 200th power. Not a larger 5th-power set.

## Data / code

- [Itty et al. GitHub `c7/R367.txt`](https://raw.githubusercontent.com/nathanielitty/lower-bounds-for-shannon-capacity/main/c7/R367.txt) — 367 lines, five integers 0–6. Copied to `compute/R367.txt`.
- [Itty et al. repo root](https://github.com/nathanielitty/lower-bounds-for-shannon-capacity)
- [Gao verification repo](https://github.com/xyz2606/recursive_construction_of_the_Shannon_capacity_of_C_7)
- [Lean formalisation](https://github.com/spectra-research/shannon-capacity-lean) — `ShannonBounds/BaseC7*.lean` holds the valid-tuple literals, not a new 5th-power record.
- [FunSearch `cyclic_graphs/`](https://github.com/google-deepmind/funsearch/tree/main/cyclic_graphs) — recovered the 367-set historically; the public folder has C11 data, not a C7 file.

## Context

- [Ben Green, 100 Open Problems, P38](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf) — \(\Theta(C_7)\) between \(367^{1/5}\) and \(\vartheta(C_7)\). The July 2026 papers moved the capacity lower bound via higher powers; the fifth-power independence number is the finite leftover.
- Table from Polak–Schrijver: \(\alpha(C_7^{\boxtimes 5})\) sits in \(367\)–\(401\) (Lovász \(\vartheta^5\)).

## What the URLs were used for

- ar5iv 1808.07438 supplied the pipeline (shift, fold 54.5, isolate, residual) and the appendix words.
- Itty `R367.txt` was the working seed; it matches the appendix and verifies.
- 2607.21517 / 2607.27869 / 2607.29681 were checked only to confirm that 367 is still the fifth-power record. Their new numbers live in dimensions 10 and 200.
- FunSearch `cyclic_graphs/` has no public C7 file (C11 754-set only).
- Gao `inputs/R367.txt` is the same seed; not re-downloaded after Itty's copy verified.
