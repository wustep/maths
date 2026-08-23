# Research log — Brocard–Ramanujan factorial square

Every external lookup made during q2 is recorded here. Search snippets were
used only to locate sources; mathematical claims in the attack rely on the
linked paper itself, the checked computation, or the Lean proof.

## 2026-08-16 — q2

### Sources read

- Abderrahim Makki Naciri, [*On the Brocard–Ramanujan Equation with
  7-Free Integers and Prime Powers*](https://math.colgate.edu/~integers/z71/z71.pdf),
  *INTEGERS* 25 (2025), #A71,
  [DOI/Zenodo record](https://zenodo.org/records/16881781). The paper explicitly
  starts from $n!=(x-1)(x+1)$, and proves finiteness only under restrictions
  such as one neighbor being $k$-free or having few distinct prime divisors.
  It states that the unrestricted problem remains open. This was important
  scope control: q2's factorization is standard, while the full-prime-power
  Lean consequence and exact unitary-divisor experiment are quest artifacts,
  not a claimed literature novelty or an unrestricted solution.
- OEIS [A034444](https://oeis.org/A034444), “number of unitary divisors.” It
  gives the definition $d\mid N$ with $\gcd(d,N/d)=1$, and equivalently says
  that each complete prime-power block of $N$ is either present or absent.
  This justifies the standard term *unitary divisor* and the count
  $2^{\omega(N)}$ before identifying complementary choices.
- Saša Novaković,
  [*The Diophantine equation $P(x)=\prod H_{n_i}$*](https://arxiv.org/abs/2601.16757)
  (2026 preprint). Its introduction records that the integer
  Brocard–Ramanujan problem is open, cites Overholt's conditional result, and
  summarizes Naciri's restricted-neighbor result. It supplied a recent check
  that no unconditional factorization theorem was being overlooked.
- Berndt and Galway,
  [*On the Brocard–Ramanujan Diophantine equation $n!+1=m^2$*](https://doi.org/10.1023/A:1009873805276),
  *Ramanujan Journal* 4 (2000), 41–42. The
  [Illinois bibliographic record](https://experts.illinois.edu/en/publications/on-the-brocard-ramanujan-diophantine-equation-n-1-msup2sup/)
  confirms that the paper reports a computation through $10^9$. q1 had
  already read the two-page paper and rerun only a labeled $10^7$ method
  slice; q2 did not reuse $10^9$ as its own bound.
- [Brocard–Ramanujan problem for polynomials over finite fields](https://doi.org/10.1016/j.ffa.2025.102731),
  *Finite Fields and Their Applications* 110 (2026), 102731. The abstract
  concerns Carlitz factorials over $\mathbb F_q[T]$, not the integer equation;
  it was screened out after confirming that it does not supply the needed
  integer factorization obstruction.

### Negative and failed lookups

- OEIS was searched for the initial q2 minimum-gap terms
  \`1, 1, 11, 1, 97, 181\` and for “unitary divisor factorial square Brocard.”
  No matching sequence was found. [A365401](https://oeis.org/A365401), the
  first search hit, instead counts divisors of the largest *square* unitary
  divisor and is unrelated. Accordingly no OEIS or priority claim is made for
  the q2 gap data.
- Web/arXiv searches for \`Brocard Ramanujan (m-1)(m+1) prime powers\`,
  \`consecutive coprime factors n!/4\`, and the corresponding $p$-adic
  congruence found the sources above but no paper asserting an unrestricted
  conclusion from this exact prime-block split.
- The direct author-PDF URL
  [faculty.math.illinois.edu/~berndt/articles/galway.pdf](https://faculty.math.illinois.edu/~berndt/articles/galway.pdf)
  timed out in the q2 web fetch; the paper had already been read in q1 and its
  metadata was checked through the DOI and Illinois record instead.
- The normal HTML page for [Erdős problem 398](https://www.erdosproblems.com/398)
  returned HTTP 403 to the fetcher. Its
  [text/LaTeX endpoint](https://www.erdosproblems.com/latex/398) appeared in a
  later search and lists the Naciri paper; no theorem from that endpoint is used
  here.
- General searches also surfaced MathWorld/Wikipedia summaries and several
  nonstandard-host “solution” manuscripts. They were not used: their advertised
  conclusions conflict with the peer-reviewed sources' explicit open status,
  and q2 makes no novelty or solution claim.

## 2026-08-23 — q3

### Sources opened

- OEIS [A085692](https://oeis.org/A085692), fetched with
  `scripts/oeis_lookup.py`.  It lists the square values $25,121,5041$ arising
  from the three known positive indices.  This matches the folder statement;
  it does not assert that the list is complete.
- Crossref's record for Berndt–Galway,
  [DOI 10.1023/A:1009873805276](https://api.crossref.org/works/10.1023/A:1009873805276),
  was opened.  It confirms the authors, title, journal, year, volume, and pages
  41–42, but exposes no theorem text or abstract.
- The [Springer article page](https://link.springer.com/article/10.1023/A:1009873805276/fulltext.html)
  and [Springer PDF endpoint](https://link.springer.com/content/pdf/10.1023/A:1009873805276.pdf)
  were opened but returned a browser challenge rather than the paper.

### Failed lookup and scope consequence

- The Berndt [author-PDF URL](https://faculty.math.illinois.edu/~berndt/articles/galway.pdf)
  failed repeatedly with a TLS end-of-file error.  Unpaywall and Semantic
  Scholar both report the article as closed and provide no repository copy.
  Therefore q3 does not treat the often-quoted $10^9$ as a replayed baseline
  or use it in any new claim.  The attack below relies only on Wilson's theorem
  and exact arithmetic that is reproduced locally.
