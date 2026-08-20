# Notes from authors — 2026-08-19

**Do not add the source PDF to the git repo.** Citation only; no figures, no long excerpts.

**Same paper as arXiv:2511.02542.** IEEE author’s accepted version of
Davydov–Marcugini–Pambianco, *New upper bounds for binary linear covering codes*,
IEEE Trans. Inform. Theory (accepted 2026), DOI [10.1109/TIT.2026.3716379](https://doi.org/10.1109/TIT.2026.3716379)
= arXiv:2511.02542 (4 Nov 2025). Same title, abstract bounds, Table 5.1
(still \(\ell_2(10,2)\le 51\)), and QM numbering. Not a later paper. Extract
**unused tactics only**. Already used from this paper: QM\(_2^2\) (Thm 4.1 / (4.2)),
QM\(_3^2\) (Thm 5.1), QM\(_5^2\) (Thm 5.4(ii)), 10-block \((2,0)\)-partition of the
50-set, theorem-only QM\(_2^2\) at \(r=42,44\).

## Bibliographic facts (from the PDF)

- Authors: Alexander A. Davydov (IITP RAS); Stefano Marcugini, Fernanda Pambianco (Perugia).
- MSC 94B65, 94B25, 94B60, 94B05.
- Correspondence they use: \(\ell_q(r,R)=s_q(r-1,R-1)\) (1-saturating sets in \(PG(r-1,q)\)).
- Computer-search method is **not specified** (Thms 5.2, 7.1, Lemma 7.5 just say “computer search”). Magma is cited [9]; no anneal/SAT recipe.

## Unused constructions (R = 2)

**QM\(_{2}^{1}\)** (Thm 4.1 / (4.1), (4.3); from [27]). \(B\subseteq\mathbb F_{2^m}\cup\{*\}\),
\(2^m+1\ge p(H_0)\), \(D=D_2(2)\) (two Hamming blocks). Length
\(n=2^m(n_0+2)-2\) is *worse* than QM\(_2^2\), but **\(p(H_C)\le p(H_0)\)** — the
partition size is preserved, not grown to \(2^{m+1}+1\). Use as an intermediate
when a later lift is blocked by a large inherited \(p\).

**Block-splitting to hit exactly \(2^m\)** (Thm 5.4, QM\(_{2}^{4}\), display (5.9)).
They take the computer-searched 11-block 2-partition \(P_{KR}\) of the
Kaikkonen–Rosendahl 51-set (Thm 5.2 / (5.3)) and *split* the first three
blocks so the dependent triple \(\{h_5,h_{27},h_{29}\}\) becomes three
singletons and \(p=16=2^4\). Same indicator per block, \(B=\mathbb F_{2^4}\),
\(D=D_1(2)\). We already isolate \((491,734,821)\) for QM\(_5^2\); the unused
move is **splitting an existing good partition until \(p=2^m\)** (or \(2^m+1\)
for QM\(_{2}^{1}\)) to unlock a smaller \(m\).

**Explicit lift-partition, not the inequality** (proof of Thm 5.4).
Constructive 2-partition of \(H_C\): (i) interim blocks = seed blocks, copied
across each \(A(h_j,\beta_j)\); (ii) split every interim block into
\(\{\xi=0\}\) vs the rest; (iii) \(D\) is its own last block. QM\(_{2}^{2}\)
gives \(p\le 2^{m+1}+1\). QM\(_{2}^{5}\) with a \(*\) block: do **not** split
the \(*\) block, so \(p\le 2^{m+1}+2\). This is how to *compute* \(p(H_C)\)
instead of inheriting the paper bound — the stated soft spot.

**QM\(_{2}^{6}\)** (Thm 5.6) is just iterated QM\(_{2}^{2}\) on \(\Phi\)-length
seeds with the window \(t_0\ge m\ge\lambda_0+1\). Iteration recipe is in the
proof of Thm 5.7; \(p\)-tracking for even \(r\ge 42\) is (5.16).

## Unused constructions (other radii) — plug the 50-set in

**QM\(_{3}^{5}\)** (Thm 7.3, new here). Start from a radius-3 code \(C_0\)
(they use the perfect Golay \([23,12,7]_2 3\), trivial \((3,0)\)-partition,
\(p=23\)) and glue a radius-2 code \(V_{2m}\) as \(D=D_4\).
\(n=2^m(n_0+1)+n_{2m}-1\), \(r=r_0+3m\). They plug KR / \(\Phi\) as \(V_{2m}\).
Our shorter \(V_{2m}\) beat their Table 7.1/7.2 on the spot:

| r | their \(n_{2m}\) | their n | our \(n_{2m}\) | our n |
|---|---|---|---|---|
| 26 | 51 | 818 | 50 | **817** |
| 38 | 831 | 13118 | 815 | **13102** |
| 41 | 1663 | 26238 | 1631 | **26206** |

Need the Lemma 7.5 analogue: every vector of \(\mathbb F_2^{10}\) is a
**3-sum** of the 50-set (they verified this for KR by computer search; it
gives \(\ell_C=2\) at \(r=26\)). Remark 7.4 (proof omitted): if \(\ell_C=2\)
and \(m\ge 3\), they claim \(p(H_C,2)=5p(H_0,0)+n_{2m}+3\).

**QM\(_{3}^{4}\) from the Östergård–Kaikkonen \([18,9]_2 3\) seed** (Thms 6.4,
7.1–7.2). Explicit 11-block \((3,1)\)-partition \(P_{OK}\); \(m=4\) gives
\(\ell_2(21,3)\le 303\). Hex last entry is printed `ICE` — treat as OCR until
checked against [65].

**QM\(_{4}^{4}\)** (Thm 9.1, new here). Odd \(m\), \(D=D_5\) contains a
radius-2 \(H_{2m}\). They use OK2 \([19,8]_2 4\) + KR to get
\(\ell_2(31,4)\le 690\). Our 50-set: \(n=2^5(19+1)+50-1=689\).

Unused \(D\)-blocks vs what we built: \(D_2(2)\) (QM\(_{2}^{1}\)), \(D_3\)
(QM\(_{3}^{3/4}\)), \(D_4\) (QM\(_{3}^{5}\)), \(D_5\) (QM\(_{4}^{4}\)). We
already use \(D_1(2)\) and \(D_6\).

## Table 5.1 still weak (their “best as far as we know”)

- **All odd \(r\)** still the old \(f(r)=5\cdot 2^{(r-3)/2}-1\) family
  (Thm 4.2(ii) / [32]). Densities \(\approx 1.52\)–\(1.56\). Open problem
  §10: new families for \(R=2\), \(r=2t-1\). First holes: \(r=9\) (\(n=39\)),
  \(r=11\) (79), \(r=13\) (159). (\(r=8,9\) already searched; no dent.)
- **Even leftovers not in \(\Phi\)**: \(r=12\) (107), \(14\) (215), \(16\) (431)
  — old \(\varphi\) / [27]. No QM from the 50-set hits these \(r\).
- They never improve \(n<51\) at \(r=10\). Open problem §10: improve
  sporadic codes that are not in an infinite family — that *is* \(n=49\).

## How to get below 49

The paper has **no** shortening construction at \(r=10\). Their computer
search is for partitions of a *fixed* \(H\), not for a shorter \(H\).
\(\ell_2(10,2)=s_2(9,1)\): a 49-column code is a 1-saturating 49-set in
\(PG(9,2)\). Deletion from the 50-set leaves \(\ge 9\) holes — need a
different 49-set, not a subset. Possible starts: KR 51 minus two with a
different repair; geometric 1-saturating-set search; do not expect a QM lift
(lifts increase \(r\)).

## How to tighten \(p(H)\)

1. Implement the Thm 5.4 constructive lift-partition on our \(r=18,20,28\)
   matrices and *count* \(p\), then computer-search a smaller one.
2. Concrete unlock: our \(r=28\), \(n=26111\) has \(p\le 66\), so QM\(_2^2\)
   needs \(2^m\ge 66\) (\(m\ge 7\)). If a search gets \(p\le 64\), \(m=6\)
   gives \(\ell_2(40,2)\le 64\cdot 26111+63=1671167\) (table: 1703935).
   \(p\le 33\) would unlock \(m=5\) and \(r=38\).
3. QM\(_{2}^{1}\) if we would rather keep \(p\) than shorten \(n\).
4. For QM\(_{3}^{5}\): a dependent triple in three distinct blocks makes
   \(p(H_C,1)=p(H_C,0)\) (saves 2).

## Other radii / open list (§10)

They flag: \(R=2\) odd \(r\); \(R=3\) residues \(3t-2\) and \(3t\) (the
\(\varphi,\psi\) families, densities \(\approx 2.25\) and \(1.90\)); \(R=4\)
residues \(4t-1,4t-2,4t-3\); and **no infinite families for \(R\ge 5\)**.
Methods “can be used” for \(R\ge 5\); only sporadic examples exist.

## Check before citing (do not trust the PDF blindly)

- KR hex (4.9) and \(P_{KR}\) (5.3) / \(P_{KR}^*\) (5.9) against [50].
- \(h_5+h_{27}+h_{29}=0\) (Thm 5.2(ii)).
- Lemma 7.5 on KR, and the same 3-sum property on *our* 50-set.
- \(M_{OK}\) last word `ICE` (6.10) — invalid hex; independently recovered as `1CE` (unique among 512 last words). See `compute/recover_mok.py`.
- Table 5.1 commas (`1,56219`) are decimal-comma typos.
- Abstract densities vs (5.15): \(\mu(2)\approx 262/2^9\approx 1.32031\).
- IEEE vs arXiv v1: abstract numbers match; we did not line-diff the body.
