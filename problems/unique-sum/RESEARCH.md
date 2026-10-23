# Research log — Sets with no unique sum mod p

## 2026-08-16

- [OEIS A398173](https://oeis.org/A398173) then had 14 terms through p=47: 3,4,5,7,7,8,9,10,11,11,12,13,13,13.
- [Bedert, arXiv:2303.15134](https://arxiv.org/abs/2303.15134); [Cao–Yuan, arXiv:2608.06728](https://arxiv.org/abs/2608.06728).
- The first recovered run used the wrong predicate ($r=1$ rather than $r\notin\{1,2\}$); memory commit `77d43c5`.
- The recoded `green_m_p.csv` matched A398173 through p=47.

## 2026-08-23

- Fetched and read [Bedert, arXiv:2303.15134v2](https://arxiv.org/abs/2303.15134). Definition 1 uses unordered-pair uniqueness; in ordered notation the paper states that a unique sum is exactly $1\le r_A(g)\le2$. Theorems 3 and 5 give $m(p)\ge\omega(p)\log p$, with $\omega(p)\gg\sqrt{\log^{(3)}p}/\log^{(4)}p$, and $m(p)\ll(\log p)^2$.
- Fetched and read [Cao–Yuan, arXiv:2608.06728v1](https://arxiv.org/abs/2608.06728). Theorem 1.1 gives $m(p)\gg\log p\log\log p$. Theorem 1.3 gives the independent upper construction with leading constant $1/(2(\log_2 3)^2)=0.1990361769\ldots$; the paper explicitly says all unsubscripted logarithms are natural.
- Reopened [OEIS A398173](https://oeis.org/A398173). It now has 15 terms through $p=53$, with $m(53)=14$ added by Paweł Kwaczyński on 2026-07-29. Thus $p=59$ is the first prime at which a finite computation here could extend the published table.

## 2026-09-05 — q4 source check

- Fetched [Bedert v2](https://arxiv.org/pdf/2303.15134v2) with
  `scripts/arxiv_fetch.py` and read Definition 1 and the ordered representation
  convention in section 2. Both multiplicities 1 and 2 are forbidden. Opened
  the [abstract](https://arxiv.org/abs/2303.15134) and
  [HTML](https://arxiv.org/html/2303.15134v2) as well.
- Fetched [Cao–Yuan v1](https://arxiv.org/pdf/2608.06728v1) with the same
  script and read the introduction and Theorems 1.1–1.3. The explicit
  asymptotic lower constant does not decide the boundary at 59. Opened the
  [abstract](https://arxiv.org/abs/2608.06728) and
  [HTML](https://arxiv.org/html/2608.06728v1). No asymptotic improvement is
  attempted here.
- [OEIS A398173](https://oeis.org/A398173): the browser fetch timed out;
  `scripts/oeis_lookup.py A398173` succeeded after network authorization,
  showing the sequence definition and its first 12 terms (the helper truncates
  output). The 15-term baseline supplied for this run is also in the notebook;
  all 15 saved witnesses passed the direct arithmetic verifier.
- The full [OEIS JSON entry](https://oeis.org/search?q=id%3AA398173&fmt=json)
  subsequently succeeded via curl. It has **20**, not 15, terms, through 73:
  `3,4,5,7,7,8,9,10,11,11,12,13,13,13,14,15,15,16,16,16`.
  The extension is attributed to Paweł Kwaczyński on 2026-08-08.
  `compute/q4/published_oeis.json` saves the numerical data and attribution.
- Opened [unique-sum-free-cert](https://github.com/pawelkwaczynski/unique-sum-free-cert).
  Its README says two independent searches established the values at
  59, 61, 67, 71, and 73, but retained lower proof objects are not supplied
  there for those rows. The 53 ledger records hashes of proofs deleted after
  checking. This is a published claim, not a lower proof replayed by q4.
  It credits Scheinerman's 2019 thesis for witnesses through 59 and links
  Watson for retained lower proofs.
- Opening the linked [Zenodo DOI](https://doi.org/10.5281/zenodo.22067683)
  failed in the browser; a GitHub API directory request returned HTTP 403.

## 2026-09-09 — resumed q4 record check

- The [full OEIS JSON entry](https://oeis.org/search?q=id%3AA398173&fmt=json)
  again returns 20 terms through 73, unchanged from the saved September 5
  snapshot. The notebook's local replay through 53 is not the current
  publication boundary. In particular, OEIS reports m(59)=15.
- Reopened [Kwaczyński's certificate repository](https://github.com/pawelkwaczynski/unique-sum-free-cert)
  and [Watson's notes](https://github.com/mkwatson/unique-sums-notes).
  Both acknowledge the later finite values. Their verification and retained
  proof claims are source reports, not proof objects replayed in this run.
- Fetched [Bedert v2](https://arxiv.org/pdf/2303.15134v2) with
  `scripts/arxiv_fetch.py 2303.15134v2 --text pdf` and read Definition 1.
  Both ordered multiplicities 1 and 2 are forbidden. No new asymptotic
  statement is used in this continuation. The browser's
  [OEIS page](https://oeis.org/A398173) request timed out; curl of the JSON
  entry succeeded.

- During the same-day continuation, reopened the
  [Bedert abstract](https://arxiv.org/abs/2303.15134) and
  [Cao–Yuan abstract](https://arxiv.org/abs/2608.06728), and reread the
  previously fetched Bedert PDF text. A fresh curl of the
  [OEIS JSON entry](https://oeis.org/search?q=id%3AA398173&fmt=json)
  exactly matches the saved 20-term record. The ordinary OEIS page again
  timed out in the browser. The work below concerns finite replay only.

## 2026-09-09 — q5 record check

- Opened the [Bedert abstract](https://arxiv.org/abs/2303.15134) and the
  [HTML of v2](https://arxiv.org/html/2303.15134v2). Definition 1 is the
  unordered unique-sum predicate; section 2 states that a unique sum is
  exactly $1\le r_A(g)\le 2$. Theorems 3 and 5 are the $\omega(p)\log p$
  lower bound and the $(\log p)^2$ upper bound. No finite table.
- Opened the [Cao–Yuan abstract](https://arxiv.org/abs/2608.06728) and the
  [HTML of v1](https://arxiv.org/html/2608.06728v1). Theorem 1.1 is
  $m(p)\gg\log p\log\log p$. Theorem 1.3 is the ternary symmetric-square
  upper bound with leading constant $1/(2(\log_2 3)^2)$. Unsubscripted
  logs are natural. The paper does not decide $m(59)$.
- `scripts/arxiv_fetch.py` on both ids (metadata only) matched those
  abstracts. `scripts/oeis_lookup.py A398173` returned the sequence name
  and a truncated prefix. A curl of the
  [OEIS JSON entry](https://oeis.org/search?q=id%3AA398173&fmt=json)
  again has 20 terms through 73:
  `3,4,5,7,7,8,9,10,11,11,12,13,13,13,14,15,15,16,16,16`.
  `compute/q5/published_oeis.json` stores that snapshot.
- Opened [unique-sum-free-cert](https://github.com/pawelkwaczynski/unique-sum-free-cert).
  Its README claims $m(59)=15$ with hash-bound CaDiCaL LRAT ledgers for
  $k=2..14$. That is a published-adjacent lead, not a proof object
  replayed in q5. The notebook's lower half is the named-cover search.

## 2026-09-09 — q6 record check

- Reopened the [Bedert abstract](https://arxiv.org/abs/2303.15134) and the
  [Cao–Yuan abstract](https://arxiv.org/abs/2608.06728). No finite table;
  versions unchanged.
- `scripts/arxiv_fetch.py` on both ids and `scripts/oeis_lookup.py A398173`
  again. Curl of the
  [OEIS JSON entry](https://oeis.org/search?q=id%3AA398173&fmt=json)
  still has 20 terms through 73, including $m(61)=15$ with example
  $\{0,1,2,3,4,6,15,21,22,24,42,49,55,56,58\}$ as a(17).
  `compute/q6/published_oeis.json` stores that snapshot. The example is
  a lead until the local ordered-count check; that check passed.

## 2026-09-12 — q7 source review before cutoff

- Opened [OEIS A398173](https://oeis.org/A398173) in the browser. The
  displayed 20 terms still end at 73; 79 is absent. This source check
  did not replay the table's optimality claims.
- Opened the [Bedert abstract](https://arxiv.org/abs/2303.15134) and
  [v2 HTML](https://arxiv.org/html/2303.15134v2). Read Definition 1 and
  the unique-sum convention; no finite improvement was extracted.
- Also requested the [Cao–Yuan abstract](https://arxiv.org/abs/2608.06728),
  [v1 HTML](https://arxiv.org/html/2608.06728v1),
  [Kwaczyński repository](https://github.com/pawelkwaczynski/unique-sum-free-cert),
  and [Watson notes](https://github.com/mkwatson/unique-sums-notes) in the
  same browser batch. No new claim in this campaign relies on them.
- Shell fetches with `arxiv_fetch.py` for both papers and curl of the
  [OEIS JSON entry](https://oeis.org/search?q=id%3AA398173&fmt=json)
  failed on sandbox DNS. The escalation call was interrupted at cutoff;
  no successful shell fetch result was returned. No further fetch ran.
