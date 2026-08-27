# Research log — C7 fifth strong power

URLs actually opened this session.

## Papers

- [Polak–Schrijver, arXiv:1808.07438](https://arxiv.org/abs/1808.07438) and [ar5iv HTML](https://ar5iv.labs.arxiv.org/html/1808.07438) — independent set of size 367 in $C_7^{\boxtimes 5}$. Construction: geometric orbit in $C_{108,382}^{\boxtimes 5}$, shift, fold $\lfloor 2i/109\rfloor$, drop non-isolated image vertices ($|M|=327$), extend residual (71 verts, 85 edges, $\alpha=40$). Appendix lists the 367 words. They already report no 368 from other shifts/divisors, and no 3-out/4-in local move.
- [CWI PDF of the same paper](https://ir.cwi.nl/pub/30364/30364.pdf)
- [Tilburg PDF](https://pure.uvt.nl/ws/portalfiles/portal/82278307/1-s2.0-S0020019018302291-main.pdf)
- [Itty–Rosin–Carstensen–Reichman, arXiv:2607.21517](https://arxiv.org/abs/2607.21517) / [HTML](https://arxiv.org/html/2607.21517v1) — $\alpha(C_7^{\boxtimes 10})\ge 134753$, still uses the same 367-set in dimension 5. Explicit $r_j,q_j$ private pairs.
- [Gao, arXiv:2607.27869](https://arxiv.org/abs/2607.27869) / [HTML](https://arxiv.org/html/2607.27869v1) — recursive gadget product; “367 remains the largest currently known” in the fifth power. Points to `inputs/R367.txt`.
- [Buys–Polak–Zuiddam, arXiv:2607.29681](https://arxiv.org/abs/2607.29681) / [HTML](https://arxiv.org/html/2607.29681) — Lean-verified $\Theta(C_7)\ge 3.258805\ldots$ from a profile $(367,8,367,322)$ on $C_7^{\boxtimes 5}$ iterated to the 200th power. Not a larger 5th-power set.

## Data / code

- [Itty et al. GitHub `c7/R367.txt`](https://raw.githubusercontent.com/nathanielitty/lower-bounds-for-shannon-capacity/main/c7/R367.txt) — 367 lines, five integers 0–6. Copied to `compute/R367.txt`.
- [Itty et al. repo root](https://github.com/nathanielitty/lower-bounds-for-shannon-capacity)
- [Gao verification repo](https://github.com/xyz2606/recursive_construction_of_the_Shannon_capacity_of_C_7)
- [Lean formalisation](https://github.com/spectra-research/shannon-capacity-lean) — `ShannonBounds/BaseC7*.lean` holds the valid-tuple literals, not a new 5th-power record.
- [FunSearch `cyclic_graphs/`](https://github.com/google-deepmind/funsearch/tree/main/cyclic_graphs) — recovered the 367-set historically; the public folder has C11 data, not a C7 file.

## Context

- [Ben Green, 100 Open Problems, P38](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf) — $\Theta(C_7)$ between $367^{1/5}$ and $\vartheta(C_7)$. The July 2026 papers moved the capacity lower bound via higher powers; the fifth-power independence number is the finite leftover.
- Table from Polak–Schrijver: $\alpha(C_7^{\boxtimes 5})$ sits in $367$–$401$ (Lovász $\vartheta^5$).

## What the URLs were used for

- ar5iv 1808.07438 supplied the pipeline (shift, fold 54.5, isolate, residual) and the appendix words.
- Itty `R367.txt` was the working seed; it matches the appendix and verifies.
- 2607.21517 / 2607.27869 / 2607.29681 were checked only to confirm that 367 is still the fifth-power record. Their new numbers live in dimensions 10 and 200.
- FunSearch `cyclic_graphs/` has no public C7 file (C11 754-set only).
- Gao `inputs/R367.txt` is the same seed; not re-downloaded after Itty's copy verified.

## 2026-08-23 (this session)

Opened again, and used:

- [arXiv:1808.07438](https://arxiv.org/abs/1808.07438) / [ar5iv](https://ar5iv.labs.arxiv.org/html/1808.07438) — Table 1: $\alpha(C_7)=3$, $\alpha(C_7^{\boxtimes 2})=10$, $\alpha(C_7^{\boxtimes 3})=33$, $\alpha(C_7^{\boxtimes 4})\in[108,115]$, $\alpha(C_7^{\boxtimes 5})\in[367,401]$. Lemma $\alpha(C_n^d)\le \alpha(C_n^{d-1})n/2$ is the 115. No 368 in their shift/divisor/3-out search.
- [arXiv:2607.21517](https://arxiv.org/abs/2607.21517) / [HTML v1](https://arxiv.org/html/2607.21517v1) — still treats 367 as the fifth-power record. Appendix B: $\alpha(C_7^{\boxtimes 6})\ge 1120$. Eight private pairs $(r_j,q_j)$ on the 367-set. 10th-power size 134753 is a gadget around $B\times B$, not a larger 5-set.
- [Itty repo](https://github.com/nathanielitty/lower-bounds-for-shannon-capacity), [`CC_6_7_1120.txt`](https://raw.githubusercontent.com/nathanielitty/lower-bounds-for-shannon-capacity/main/CC_6_7_1120.txt), [`c7/construct_cc_10_7_134753.py`](https://raw.githubusercontent.com/nathanielitty/lower-bounds-for-shannon-capacity/main/c7/construct_cc_10_7_134753.py). 1120 unique 6-tuples, independent; max 5-fiber 165. Reconstructing the 10th-power gadget from R367, max 5-fiber 367.
- [arXiv:2607.27869](https://arxiv.org/abs/2607.27869) / [HTML](https://arxiv.org/html/2607.27869v1) — “367 remains the largest currently known” in the fifth power. Base gadget parameters $(a,t,s,o,h,v)=(367,8,367,321,26,20)$. Capacity bound lives in dimension 200.
- [arXiv:2607.29681](https://arxiv.org/abs/2607.29681) / [HTML](https://arxiv.org/html/2607.29681v1) — Lean-verified $\Theta(C_7)\ge 3.258805\ldots$ from profile $(367,8,367,322)$ on $C_7^{\boxtimes 5}$. Not a new 5th-power set.

Did not reopen CWI/Tilburg PDFs, FunSearch, or Green P38 this session.

## 2026-08-27 (this session)

Opened again, and used:

- [arXiv:1808.07438](https://arxiv.org/abs/1808.07438) / [ar5iv](https://ar5iv.labs.arxiv.org/html/1808.07438) — Table 1 unchanged: $\alpha(C_7^{\boxtimes 4})\in[108,115]$ by Vesel–Žerovnik / Baumert Lemma 2; $\alpha(C_7^{\boxtimes 5})\in[367,401]$. The $115$ is $\alpha(C_7^{\boxtimes 3})n/2$ with $\alpha(C_7^{\boxtimes 3})=33$. No 368 from their shift/divisor/3-out search.
- [arXiv:2607.21517](https://arxiv.org/abs/2607.21517) / [HTML v1](https://arxiv.org/html/2607.21517v1) — fifth-power record still the size-$367$ set. New numbers live in dimension $10$ ($134753$).
- [arXiv:2607.27869](https://arxiv.org/abs/2607.27869) / [HTML v1](https://arxiv.org/html/2607.27869v1) — “it remains the largest currently known such set” for the fifth power. Base gadget $(367,8,367,321,26,20)$.
- [arXiv:2607.29681](https://arxiv.org/abs/2607.29681) / [HTML v1](https://arxiv.org/html/2607.29681v1) — Lean-verified $\Theta(C_7)\ge 3.258805\ldots$ from profile $(367,8,367,322)$ on $C_7^{\boxtimes 5}$, iterated to the $200$th power. Not a larger $5$-set.

Did not reopen CWI/Tilburg PDFs, FunSearch, Green P38, or the Itty GitHub certificates this session.

## 2026-08-27 (q3 session)

Opened again, and used:

- [arXiv:1808.07438](https://arxiv.org/abs/1808.07438) / [ar5iv](https://ar5iv.labs.arxiv.org/html/1808.07438) / [HTML v2](https://arxiv.org/html/1808.07438v2) — Table 1 unchanged: $\alpha(C_7^{\boxtimes 5})\in[367,401]$. No 368 from their shift/divisor/3-out search.
- [arXiv:2607.21517](https://arxiv.org/abs/2607.21517) / [HTML v2](https://arxiv.org/html/2607.21517v2) — now v2 (2026-07-30); the new text is a $C_{15}$ capacity bound. Fifth-power record still the size-$367$ set. “For the 7-cycle $C_7$, the best current bound comes from the strong 5-product, for which the largest known independent set has size 367.”
- [arXiv:2607.27869](https://arxiv.org/abs/2607.27869) / [HTML v1](https://arxiv.org/html/2607.27869v1) — “it remains the largest currently known such set” for the fifth power.
- [arXiv:2607.29681](https://arxiv.org/abs/2607.29681) / [HTML v1](https://arxiv.org/html/2607.29681v1) — Lean-verified $\Theta(C_7)\ge 3.258805\ldots$ from profile $(367,8,367,322)$. Not a larger $5$-set.

Did not reopen CWI/Tilburg PDFs, FunSearch, Green P38, or the Itty GitHub certificates this session.

## 2026-08-27 (q4 session)

Opened again, and used:

- [arXiv:1808.07438](https://arxiv.org/abs/1808.07438) / [HTML v2](https://arxiv.org/html/1808.07438v2) — Table 1 unchanged: $\alpha(C_7^{\boxtimes 5})\in[367,401]$. Construction is still the folded $C_{108,382}$ orbit. No 368 from their shift/divisor/3-out search.
- [arXiv:2607.21517](https://arxiv.org/abs/2607.21517) / [HTML v2](https://arxiv.org/html/2607.21517v2) — “For the 7-cycle $C_7$, the best current bound comes from the strong 5-product, for which the largest known independent set has size 367.” New numbers live in dimension $10$ and in $C_{15}$.
- [arXiv:2607.27869](https://arxiv.org/abs/2607.27869) / [HTML v1](https://arxiv.org/html/2607.27869v1) — “it remains the largest currently known such set” for the fifth power. Base gadget $(367,8,367,321,26,20)$.
- [arXiv:2607.29681](https://arxiv.org/abs/2607.29681) / [HTML v1](https://arxiv.org/html/2607.29681v1) — Lean-verified $\Theta(C_7)\ge 3.258805\ldots$ from profile $(367,8,367,322)$ on $C_7^{\boxtimes 5}$. Not a larger $5$-set.

Did not reopen CWI/Tilburg PDFs, FunSearch, Green P38, or the Itty GitHub certificates this session.

## W(2,7) steal (no new URL)

Methods came from the sibling agent's finish note, not from a new page: `CardEnc.atmost` instead of a homemade sequential counter; few-flip SAT around a published seed; one-violation min-conflicts as a cage; CEGAR on a cyclic/product template with a leftover plateau stop. PySAT `Cadical195` was used locally. No new $\Theta(C_7)$ paper was opened.
