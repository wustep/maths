# Research log — smale-tau

Papers, OEIS, contest pages, and failed lookups. Every URL below was opened
in this session unless marked otherwise. Forum posts and search-engine
snippets are leads, not citations.

## 2026-09-02 — statement and record

- Smale, [*Mathematical problems for the next century*](http://smaleinstitute.com/Mathematical_problems_for_the_next_century.pdf)
  (Math. Intelligencer 20, 1998). Problem 4 defines \(\tau(f)\) for
  \(f\in\mathbb Z[t]\) from the program \((1,t,u_1,\dots,u_k)\) and asks
  whether \(Z(f)\le a\tau(f)^c\). It records: \(c\ge 2\) is forced by
  Strassen's results (communicated via Schönhage, Shub and Bürgisser);
  \(Z(f)\le 2^{\tau}\) trivially; Chebyshev polynomials have exponentially
  many real zeros; and the related integer problem "is
  \(\tau(k!)\le(\log k)^c\)?" with the remark that one expects the answer
  no. Both statements are in the same section of the essay.
- Shub and Smale, [*On the intractability of Hilbert's Nullstellensatz and an algebraic version of "NP≠P?"*](http://web.archive.org/web/20220307211001/http://www.cityu.edu.hk/ma/doc/people/smales/pap97.pdf),
  Duke Math. J. 81 (1995), 47–54 (archived copy of the author's PDF;
  located through [Smale's paper list](https://home.ttic.edu/~smale/papers.html)).
  Defines a computation of an integer, states \(\tau(m)\le 2\log m\),
  the Problem "\(\tau(k!)\le(\log k)^c\)?", the notions easy / hard /
  ultimately easy, and the Main Theorem: \(k!\) ultimately hard implies
  the Nullstellensatz is intractable and \(\mathrm{NP}\ne\mathrm P\) over
  \(\mathbb C\). The polynomial \(\tau\)-conjecture is not stated in this
  paper; Bürgisser attributes it to Shub–Smale and to BCSS. The Project
  Euclid download link returned an HTML page, not the PDF; the CiteSeerX
  link on OEIS returned an archive wrapper.
- Bürgisser, [*On defining integers in the counting hierarchy and proving lower bounds in algebraic complexity*](https://eccc.weizmann.ac.il/report/2006/113/),
  ECCC TR06-113 (2006); journal version *On defining integers and proving
  arithmetic circuit lower bounds*, Comput. Complexity 18 (2009), 81–103
  (Springer page redirected to a login and was not read). States the
  \(\tau\)-conjecture as \(z(f)\le(1+\tau(f))^c\), notes that Shub–Smale's
  proof only needs hardness of every sequence \((m_n n!)\), and proves
  (Theorem 1.1) that the \(\tau\)-conjecture, or hardness of \((n!)\),
  implies that the permanent has no polynomial-size constant-free,
  division-free circuits.
- Koiran, [*Valiant's model and the cost of computing integers*](https://perso.ens-lyon.fr/pascal.koiran/Publis/tau.springer.pdf),
  Comput. Complexity 13 (2004), 131–146. Records the standard bounds
  \(\log\log n\le\tau(n)\le 2\log n\), that BCSS start from 1 only while
  de Melo–Svaiter also allow 2 (the measures differ by at most 1), that
  no nontrivial lower bound on \(\tau(n!)\) is known, and that with
  division \(n!\) becomes easy (Shamir 1979).
- de Melo and Svaiter, [*The cost of computing integers*](https://www.ams.org/journals/proc/1996-124-05/S0002-9939-96-03173-5/S0002-9939-96-03173-5.pdf),
  Proc. AMS 124 (1996). Proposition 1: \(\log\log n\le\tau(n)\le 2\log n\)
  with equality \(\tau(2^{2^k})=k\) in their convention (1 and 2 free).
- Moreira, [*On asymptotic estimates for arithmetic cost functions*](https://www.ams.org/journals/proc/1997-125-02/S0002-9939-97-03583-1/S0002-9939-97-03583-1.pdf),
  Proc. AMS 125 (1997). \(\tau(n)\ge\log n/\log\log n\) for almost all
  \(n\), and \(\tau(n)\le(1+\varepsilon)\log n/\log\log n\) for large
  \(n\).
- Rojas, [*A direct ultrametric approach to additive complexity and the Shub–Smale tau conjecture*](https://arxiv.org/abs/math/0304100),
  arXiv:math/0304100v2 (2003). Abstract: a polynomial of additive
  complexity \(s\) has at most \(15+s^3(s+1)(7.5)^s s!\) roots in
  \(\mathbb Q_2\), hence at most that many rational roots; two weak
  versions of the \(\tau\)-conjecture. Only the abstract page was read.
- Markström, [*The straight line complexity of small factorials and primorials*](https://arxiv.org/abs/1306.3091),
  arXiv:1306.3091v4 (2014), INTEGERS 14 (2014). Full text read. Figure 1:
  the number of positive integers reachable in at most \(k\) steps is
  2, 4, 9, 26, 102, 562, 4363, 46154, 652227 for \(k=1,\dots,9\).
  Figure 3: \(\tau(n!)\) exact for \(n\le 19\) with programs, and
  \(\tau(20!)\le 14\) with lower bound 13. Figure 2: the ultimate cost
  \(\tau'(n!)\) (best over nonzero multiples) exact for \(n\le 28\).
  Figures 4–5: primorials, \(\tau(29\#)\le 13\) and \(\tau(31\#)\le 15\)
  with lower bound 12. Appendix A: normalisation to distinct positive
  values, range-isomorphism classes to length 9, then a targeted DFS with
  the bound \(x^{2^{K-k}}<N\). The abstract's "\(n\le 22\)" refers to the
  ultimate cost table, not to \(\tau(n!)\) itself.
- [OEIS A173419](https://oeis.org/A173419) (\(\tau(n)\)): b-file
  [n ≤ 1800](https://oeis.org/A173419/b173419.txt) by Heinz;
  [Mathar's chain list](https://oeis.org/A173419/a173419.txt); comment by
  R. Patanè (28 Aug 2026): the four primes below 5000 with
  \(\tau(p)<\tau(p-1)\) are 3359, 3623, 4909, 4943, found by exhaustive
  enumeration to length 8, extended to length 9 for nine pairs.
- [OEIS A217032](https://oeis.org/A217032) (\(\tau(n!)\)):
  0, 1, 3, 4, 6, 6, 7, 8, 8, 9, 9, 10, 11, 11, 12, 12, 12, 13, 13 for
  \(n=1..19\). Comments: Guilford proved 10 minimal for 12!; Mertensotto
  enumerated all 12-step programs (a(13)–a(17) optimal); 13-step programs
  for 18! and 19! from the contest. The linked
  [digest of the contest mailing list](https://oeis.org/A217032/a217032.txt)
  gives the search details: 19–23 trillion nodes, 55 h on 12 threads,
  arithmetic mod \(2^{64}\) with overflow tracking in Rokicki's run, and
  Dogon's partial 13-step search (values below \(2^{64}\) only, last
  operation assumed to be a multiplication) suggesting 20!, 21!, 22!
  need 14 steps. That partial search is a lead, not a record.
- [OEIS A217031](https://oeis.org/A217031) (ultimate cost of \(n!\)),
  [A216999](https://oeis.org/A216999) (integers reachable in \(n\) steps,
  negatives included), [A141414](https://oeis.org/A141414) (least \(n\)
  with \(\tau(n)=k\): 1, 3, 5, 7, 13, 41, 113, 311, 1821, 10267, …),
  [A003065](https://oeis.org/A003065): names and first terms only. The
  A141414 terms 1821 and 10267 agree with the table in `compute/q1`.
- [Al Zimmermann's Programming Contests, Factorials](http://www.azspcs.com/Contest/Factorials)
  (Jan–Apr 2013; description page live, final report and standings via
  the Wayback Machine). Task: shortest SLP for \(n!\), \(13\le n\le 37\),
  subtraction in either direction, negatives allowed. Best scores:
  13!, 14!: 11; 15!–17!: 12; 18!, 19!: 13; 20!–22!: 14; 23!, 24!, 26!:
  15; 25!, 27!, 28!: 16; 29!, 30!, 34!: 17; 31!–33!, 36!: 18; 35!: 19;
  37!: 20. 7239 entries.

## 2026-09-02 — leads not opened

- Cheng, *On the ultimate complexity of factorials*, STACS 2003 / TCS 326
  (2004): the author's PDF at cs.ou.edu did not download; cited through
  Koiran and Markström (a conditional upper bound on multiples of
  \(n!\)).
- Borwein–Hobart, *The extraordinary power of division in straight line
  programs*, Amer. Math. Monthly 119 (2012): JSTOR only; not read.
- arXiv title search for "tau-conjecture" listed 1308.2286 (Koiran,
  Portier, Tavenas, Thomassé, *A τ-conjecture for Newton polygons*),
  1004.4960 (Koiran, *Shallow circuits with high-powered inputs*, the
  real τ-conjecture), 1011.4128 and 1309.0486 (Rojas et al., adelic and
  p-adic variants). Titles only; none opened.
- Web search snippets mentioned a STOC 2020 paper of Alekseev, Grigoriev,
  Hirsch and Tzameret on the τ-conjecture in proof complexity and a June
  2026 arXiv preprint (2606.25121) on Nullstellensatz intractability and
  the permanent. Not opened.
- Blum–Cucker–Shub–Smale, *Complexity and Real Computation* (1998): not
  available here; cited through Smale's essay and Bürgisser.
