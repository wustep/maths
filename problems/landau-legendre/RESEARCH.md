# Research log: Landau 3 / Legendre

Every numerical claim below was taken from a paper, data page, or local replay.
Community gap tables are identified as community evidence, not substituted for
the published Sorenson--Webster computation.

## 2026-08-27: statement and analytic context

- János Pintz, [*Landau's problems on
  primes*](https://eudml.org/doc/10886), *Journal de Théorie des Nombres de
  Bordeaux* 21 (2009), 357--404. This is the survey used to identify the four
  1912 Landau problems and their historical status. The
  [Numdam PDF](https://archive.numdam.org/item/10.5802/jtnb.676.pdf) was also
  opened.
- R. C. Baker, G. Harman, and J. Pintz,
  [*The Difference Between Consecutive Primes,
  II*](https://londmathsoc.onlinelibrary.wiley.com/doi/10.1112/plms/83.3.532),
  *Proceedings of the London Mathematical Society* 83 (2001), 532--562.
  They prove that $[x-x^{0.525},x]$ contains a prime for all sufficiently large
  $x$. Their constant is effective in principle but not made explicit.
- Marc Chamberland and Armin Straub,
  [*Weakening the Legendre Conjecture*](https://arxiv.org/abs/2602.22502),
  arXiv:2602.22502v1 (2026); the [full HTML](https://arxiv.org/html/2602.22502)
  was replayed line by line. Under RH, Theorem 3.1 uses the
  Carneiro--Milinovich--Soundararajan interval
  $[y,y+(22/25)\sqrt y\log y]$. Their sufficient inequality (5) is
  $x^{\delta/2}\geq(22/25)\log x$. Combining it with the finite computation
  below gives the printed threshold $\delta=0.2253$.
- Thomas Campbell, [*On the Existence of Integers with at Most 3 Prime Factors
  Between Every Pair of Consecutive
  Squares*](https://arxiv.org/abs/2603.10356), arXiv:2603.10356v2 (2026); the
  [full HTML](https://arxiv.org/html/2603.10356) was inspected. It proves an
  $\Omega\leq3$ result for every square interval. Its finite bridge uses the
  Sorenson--Webster range and an explicit prime-gap bound. It does not prove a
  prime exists between every pair of squares.
- Chamberland--Straub record the current explicit consecutive-cubes threshold
  $n\geq\exp(\exp(32.537))$, due to Cully-Hugill, and explain the route from
  Ingham's 1937 prime-gap work. The older explicit paper
  [arXiv:0810.2113](https://arxiv.org/abs/0810.2113) was found during the same
  lookup.

The search for a later paper citing or improving the exact decimal $0.2253$
found no successor. That absence is only a search result, not a priority
claim.

## 2026-08-27: computational record

- Jonathan Sorenson and Jonathan Webster,
  [*An algorithm and computation to verify Legendre's conjecture up to
  $7\cdot10^{13}$*](https://link.springer.com/article/10.1007/s40993-024-00589-4),
  *Research in Number Theory* 11, article 4, DOI
  `10.1007/s40993-024-00589-4`. The journal version verifies the stronger
  Oppermann conjecture through $N=7.05\cdot10^{13}$, exceeding $2^{46}$ and
  the prior $2\cdot10^9$ range. Correctness is unconditional; Cramer's model
  is used only in runtime analysis.
- [arXiv:2401.13753](https://arxiv.org/abs/2401.13753) is the earlier preprint,
  whose v1 abstract reports $3.33\cdot10^{13}$. The journal version, not that
  stale abstract, is the record used here.
- The authors' [OLC source and data repository](https://github.com/sorenson64/olc)
  was cloned with full history at commit
  `5cdaa95f0a4b1428a05480cc1c69d556a8f9517a`. Its checked-in logs are audited
  separately. A partial public upload cannot be used to revise the paper's
  stated result.

Exact replay of the headline arithmetic:

$$
70{,}500{,}000{,}000{,}000^2
=4{,}970{,}250{,}000{,}000{,}000{,}000{,}000{,}000{,}000.
$$

## 2026-08-27: prime-gap tables

- Tomás Oliveira e Silva, Siegfried Herzog, and Silvio Pardi,
  [official paper PDF](https://www.ams.org/mcom/2014-83-288/S0025-5718-2013-02787-1/S0025-5718-2013-02787-1.pdf),
  *Mathematics of Computation* 83 (2014), 2033--2060, DOI
  `10.1090/S0025-5718-2013-02787-1`. They computed all gaps below
  $4\cdot10^{18}$. Their largest gap in that range is $1476$, following
  $1425172824437699411$, and they checked $g(p)<\log^2 p$ for
  $11\leq p\leq4\cdot10^{18}$.
- The corresponding author-maintained [gap data
  page](https://sweet.ua.pt/tos/gaps.html) and [Goldbach computation
  page](https://sweet.ua.pt/tos/goldbach.html) were opened. The page states
  the computed and independently double-checked scopes separately.
- Thomas Nicely and Bertil Nyman,
  [*New Prime Gaps Between $10^{15}$ and
  $5\cdot10^{16}$*](https://cs.uwaterloo.ca/journals/JIS/VOL6/Nicely/nicely2.html),
  *Journal of Integer Sequences* 6 (2003), article 03.3.1, was opened as an
  earlier exhaustive computation.
- The [Prime Gap List community coverage
  page](https://primegap-list-project.github.io/fully-analyzed/) reports
  successive exhaustive limits $2^{64}$ in 2018, $2^{65}$ in 2025,
  $2^{66}$ in February 2026, and $10^{20}$ on 8 May 2026. Its
  [data repository](https://github.com/primegap-list-project/prime-gap-list)
  was opened. These later endpoints are community records linked to forum
  announcements, not a replacement for a peer-reviewed computation.

## 2026-08-27: OEIS replay

- [OEIS A014085](https://oeis.org/A014085) is
  $a(n)=\pi((n+1)^2)-\pi(n^2)$. Its
  [b-file](https://oeis.org/A014085/b014085.txt) contains 10,001 terms and
  cites Sorenson--Webster.
- [OEIS A005250](https://oeis.org/A005250) lists record prime-gap sizes.
- [OEIS A002386](https://oeis.org/A002386) lists the lower primes starting
  those record gaps.

The repository helper `scripts/oeis_lookup.py` was run on all three sequence
IDs. It recovered the same definitions and references.

## Failed or incomplete lookups

- `scripts/arxiv_fetch.py` downloaded arXiv PDFs 2401.13753, 2602.22502, and
  2603.10356 to temporary files, but could not extract text because
  `pdftotext` is absent. The arXiv abstracts and full HTML versions were then
  inspected directly.
- The public OLC repository advertises the $7.05\cdot10^{13}$ result, but the
  checked-in detailed logs appear to stop earlier. That observation must be
  reproduced by `compute/q1/audit_olc.py` before any exact counts are recorded.
