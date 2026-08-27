# Research log — hilbert16-limit-cycles

Papers, OEIS, failed lookups. Cite every URL you opened, including the
ones that gave nothing. Forum numbers (MSE, Reddit, MathOverflow,
AlphaXiv) are leads, not citations.

## 2026-08-27

Fetched with `python3 scripts/arxiv_fetch.py <id> --text none --research …`
then opened the abs page (and, for 2604.12883 and 2407.13465, the
HTML). Stubs from the fetcher are expanded below.

- [Eshkobilov–Kadyrov–Mamayusupov, *Limit-Cycle Replication via Chebyshev Pullbacks and a Quadratic Ceiling for Separable Schemes*, arXiv:2604.12883v1](https://arxiv.org/abs/2604.12883) (14 Apr 2026). Opened [abs](https://arxiv.org/abs/2604.12883) and the HTML. Theorem 1: H(nm+m−1) ≥ m² H(n) for m≥2, via Φ(u,v)=(T_m(u),T_m(v)) and the pullback field (u̇,v̇)=(T_m'(v) P∘Φ, T_m'(u) Q∘Φ). Theorem 2: pure separable replication is at most quadratic in the final degree. Table 1 / Appendix A lift published seeds to H(14)≥252, H(29)≥1080, H(31)≥1380, H(39)≥2012. Section 6: explicit cubic with one hyperbolic circle, T_3-pullback of degree 11 with nine lifts. Remark 4 leaves non-separable maps open. Does not claim a new H(2) or H(3). Does not replay Prohens–Torregrosa or Han–Li centers.

- [Gasull–Santana, *A note on Hilbert 16th Problem*, arXiv:2407.13465v2](https://arxiv.org/abs/2407.13465) (1 Oct 2024). Opened [abs](https://arxiv.org/abs/2407.13465) and the HTML. If H(n)<∞ then it is realized by a structurally stable field with only hyperbolic cycles, and H is strictly increasing. Small-n table in the introduction: H(2)≥4, H(3)≥13, H(4)≥28. Cites Shi; Li–Liu–Yang JDE 246 (2009); Prohens–Torregrosa; Christopher–Lloyd.

- [Buzzi–Novaes, *A note on a recent attempt to solve the second part of Hilbert's 16th Problem*, arXiv:2411.09594v1](https://arxiv.org/abs/2411.09594) (14 Nov 2024). Opened [abs](https://arxiv.org/abs/2411.09594). The Entropy 26 (2024) formula H(n)=2(n−1)(4(n−1)−2) is quadratic, hence incompatible with Christopher–Lloyd n² log n. Not a record.

- [Gasull–Santana, *On a variant of Hilbert's 16th problem*, arXiv:2405.04281v3](https://arxiv.org/abs/2405.04281) (26 Sep 2024). Opened [abs](https://arxiv.org/abs/2405.04281). Hilbert number as a function of the number of monomials, not of degree. Introduction restates H(2)≥4, H(3)≥13, H(4)≥28.

- [Novaes–Pereira, *A version of Hilbert's 16th Problem for 3D polynomial vector fields: Counting isolated invariant tori*, arXiv:2212.12006v2](https://arxiv.org/abs/2212.12006) (25 Sep 2024). Opened [abs](https://arxiv.org/abs/2212.12006). Quotes the Prohens–Torregrosa table: H(2)≥4, H(3)≥13, H(4)≥28, H(5)≥37, H(6)≥53, H(7)≥74, H(8)≥96, H(9)≥120, H(10)≥142, and the 4-fold lifts H(13)≥212, H(17)≥384, H(21)≥568, H(31)≥1184, H(35)≥1536, H(39)≥1920, H(43)≥2272. 3D tori, not a planar H(n) improvement.

- [Carvalho–Cruz–Gouveia, *New lower bound for the Hilbert number in low degree Kolmogorov systems*, arXiv:2304.05111v1](https://arxiv.org/abs/2304.05111) (11 Apr 2023). Opened [abs](https://arxiv.org/abs/2304.05111). Kolmogorov local cyclicity M_K(3)≥6, M_K(4)≥13, M_K(5)≥22. Restates H(2)≥4, H(3)≥13, H(4)≥28 and M(2)=3, M(3)≥12, M(4)≥21, M(5)≥33. Different function from H(n).

- [Gasull–Santana, *Limit cycles and invariant algebraic curves*, arXiv:2510.11705v2](https://arxiv.org/abs/2510.11705) (22 Dec 2025). Opened [abs](https://arxiv.org/abs/2510.11705). Lower bounds given a prescribed invariant algebraic curve; a recurrence for H(n); Kolmogorov and game-theory families. Does not replace Li–Liu–Yang 13 or Prohens–Torregrosa 28.

- [Yang, *The cyclicity of period annulus of cubic isochronous Hamiltonian systems*, arXiv:2512.19046v1](https://arxiv.org/abs/2512.19046) (22 Dec 2025). Opened [abs](https://arxiv.org/abs/2512.19046). Weak Hilbert 16th for a cubic isochronous Hamiltonian: cyclicity of the period annulus is n−1 and is attained. Restates Li–Liu–Yang 13. Not a new H(3).

Journal / PDF pages opened (not arXiv ids):

- [Prohens–Torregrosa, Nonlinearity 32 (2019), UAB copy](https://ddd.uab.cat/pub/artpub/2019/204392/newlowbou_a2019v32n1p331.pdf). Theorem 1: H(4)≥28, H(5)≥37, H(6)≥53, H(7)≥74, H(8)≥96, H(9)≥120, H(10)≥142 with configurations ⟨8,12,8⟩, …, ⟨45,52,45⟩. Corollary 2: the 4-fold lifts listed above.

- [Shi Songling, Sci. Sinica 23 (1980) landing page](https://doi.org/10.1360/ya1980-23-2-153). Concrete quadratic with four limit cycles; English version pp. 153–158. Coefficients taken from later expositions, not from a scanned PDF of Shi (no open PDF on that DOI page).

- [Yu–Zhang, visualization preprint](https://publish.uwo.ca/~pyu/pub/preprints/YZ_IJBC2020.pdf). Writes Shi as ẋ=λx−y−10x²+(5+δ)xy+y², ẏ=x+x²+(−25+8ε−9δ)xy with Shi's parameters λ=−10^{−250}, ε=−10^{−52}, δ=−10^{−13}. Chen–Wang is a different quadratic with a order-2 fine focus.

- [Galias–Tucker–Wilczak, AMC 2022 preprint](http://www.zet.agh.edu.pl/~galias/ps/amc2022.pdf). Interval-arithmetic proof that this one Songling system has exactly four cycles (parameters δ=−10^{−13}, ε=−10^{−52}, λ=−10^{−200}). Not a bound on H(2).

- [Han–Li, JDE 252 (2012) ScienceDirect landing](https://www.sciencedirect.com/science/article/pii/S0022039611004943). Abstract: H(m) grows at least as (m+2)² log(m+2)/(2 log 2); improves existing lower bounds for all m≥7 from seeds in degrees 3–6. Full table not extracted from the paywall HTML; numbers used later are those quoted by 2604.12883 Appendix A and 2212.12006.

- [Li–Liu–Yang, JDE 246 (2009) ScienceDirect landing](https://www.sciencedirect.com/science/article/pii/S0022039609000643). Abstract: a planar cubic with at least 13 cycles, via zeros of Abelian integrals. No open PDF.

- [Giné–Gouveia–Torregrosa slides](https://frabdyn.fer.hr/images/50046760/torregrosa.pdf). M(2)=3; M(3)≥12; M(4)≥21; M(5)≥33; M(6)≥48. Local, not H(3).

- [PlanetMath, Hilbert 16th for quadratic vector fields](https://planetmath.org/hilberts16thproblemforquadraticvectorfields). Lead only: writes the Shi system and 0<−λ≪−ε≪−δ≪1. Not a citation.

- [Eshkobilov–Kadyrov–Mamayusupov HTML](https://arxiv.org/html/2604.12883v1). Theorem 1, Theorem 2, §6 cubic, Remark 4, Appendix A seed table. Same claims as the abs fetch; this is the page the Chebyshev replay was read from.

- [Llibre–Valls, *Global asymptotic stability in quadratic systems*, EJDE 2025 no. 36 abstract](https://ejde.math.txstate.edu/Volumes/2025/36/abstr.html). Opened as the source line E used for the w1 = Aα − Bβ cross-check of L1. The paper characterises globally asymptotically stable quadratics; it does not move H(n).

Failed / not used as record (q1):

- Llibre–Schlomiuk and Coppel were not opened in q1 (opened in the q2 section below).
- No OEIS lookup (H(n) is not an OEIS sequence we needed).
- Wikipedia and MathOverflow numbers were not opened as citations.
- Piecewise paper [arXiv:1809.03433](https://arxiv.org/abs/1809.03433) (H_p(2)≥16) is a different function; abs not used as an H(n) bound.
- Entropy 26 (2024) quadratic formula: not fetched; the refutation is 2411.09594.
- Li–Liu–Yang JDE 246 (2009) full text: paywalled in q1. Their 13 is cited from later papers’ introductions, not replayed.

## 2026-08-27 (q2)

Papers q1 left closed, plus later 2025–2026 arXiv. Every URL below was opened this session.

### Previously closed, now opened

- [Coppel, *A survey of quadratic systems*, J. Differential Equations 2 (1966) 293–304](https://rainbow.ldeo.columbia.edu/~alexeyk/Papers/Coppel1966.pdf). Opened the PDF (Columbia copy). Lemma: three finite critical points of a quadratic are never collinear; a line meets the field in at most two contacts-or-equilibria. Theorem 1: the interior of a closed path is convex. Theorem 2: a unique critical point in the interior of each closed path. Theorems 3–4: two closed paths are oppositely (resp. similarly) oriented according as their interiors are disjoint (resp. nested). Theorem 5: two foci/centers are oppositely oriented, hence at most two. Theorem 6: the interior point is a focus or a center. Theorem 7: four critical points, convex quadrilateral, opposite saddles. Does not prove H(2) finite. Does not give an explicit 4-cycle field.

- [Llibre–Schlomiuk, *The geometry of quadratic differential systems with a weak focus of third order*, Canad. J. Math. 56 (2004) 310–343](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/FCA46BEF322C4B8A02C2C47270177DF5/S0008414X00031758a.pdf/the-geometry-of-quadratic-differential-systems-with-a-weak-focus-of-third-order.pdf). Opened the Cambridge PDF (34 pages). Class QW3: 18 topological portraits. A neighborhood of those QW3 systems that have graphics but no polycycle and no limit cycle has at most four limit cycles. Quotes: a quadratic cycle surrounds a unique singularity; if two foci carry cycles, one nest has at most one; no cycle surrounds the unperturbed order-3 weak focus. Does not move H(2)≥4. Does not produce a fifth cycle.

- [Prohens–Torregrosa, Nonlinearity 32 (2019), UAB PDF](https://ddd.uab.cat/pub/artpub/2019/204392/newlowbou_a2019v32n1p331.pdf). Re-opened the full preprint. Theorem 1 and Corollary 2 as in q1. Proposition 6: the explicit rational first integral H = (2x⁴ − x² + y² − 2x − 2)⁵ / (8x⁵ − 5x³ + 5xy² − 10x² − 5x − 4)⁴ is a degree-4 Darboux center at (0,0) and (1, ±2); degree-4 perturbations give configurations ⟨6,10,6⟩, ⟨8,11,8⟩, ⟨8,12,8⟩ at Lyapunov orders 1, 3, 5. Cubic examples (14), (17)–(20) with polynomial first integrals; they did not beat H(3)≥13. The 28-cycle claim is a Lyapunov-budget argument, not an explicit perturbed field written term-by-term.

- [Li–Liu–Yang, JDE 246 (2009)](https://www.sciencedirect.com/science/article/pii/S0022039609000643). Re-tried the landing page, Unpaywall (`is_oa` bronze, PDF URL is the Elsevier `/pdf` endpoint), and four Elsevier PDF URLs. All 403. [Unpaywall API](https://api.unpaywall.org/v2/10.1016/j.jde.2009.01.038?email=research@wustep.me) reports no repository copy. Full text still not fetched. Their 13 is still not replayed.

- [Scholarpedia, *Limit cycles of planar polynomial vector fields*](http://www.scholarpedia.org/article/Limit_cycles_of_planar_polynomial_vector_fields) (Han–Li–Li, 2010). Opened the article. Lead, not a citation. Catalogue: Ye class I has at most one cycle; a quadratic with a straight-line solution has at most one; Zhang: (2,2) is impossible; Liénard numbers H(2,1)=H(1,2)=H(2,2)=H(1,3)=1, H(3,1) conjectured 1, H(2,3)≥5; weak Hilbert Z(3,2)=2 generic / 3 degenerate; Z(2,n)=⌊(n−1)/2⌋.

### Later 2025–2026 arXiv (and two older ones q1 skipped)

- [Chen–Dai–Kaloshin–Li, *Cyclicity of lips and center-focus problem near infinity*, arXiv:2608.17773v1](https://arxiv.org/abs/2608.17773). Opened [abs](https://arxiv.org/abs/2608.17773) and [HTML](https://arxiv.org/html/2608.17773v1). Theorem 3: Liénard Hilbert number H(2n+1, 5) ≥ B(n) = 2n + ⌊n/3⌋ + ⌊(n+1)/3⌋ − 2 for n≥2, from infinity cyclicity plus a two-cuspidal lips. Beats Han–Romanovski for n≥7 and a later +2 bound for n≥13; weaker than some fixed-degree tables at small n. C(3)=+∞ for a typical three-parameter lips family (no uniform cyclicity). Necessary and sufficient condition for a polynomial Liénard center at infinity. Different function from H(n). Not a new planar H(n).

- [Lu, *Local Uniform Finite Cyclicity of the H₁₄³ Semihyperbolic Hemicycle*, arXiv:2607.13785v3](https://arxiv.org/abs/2607.13785) (26 Aug 2026). Opened abs. Completes one labelled open case in the quadratic finite-cyclicity program: a uniform bound in a two-sided annular neighborhood of that graphic. Bound existential, not claimed sharp. Not an H(2) number and not an explicit field.

- [Gavrilov–He–Xiao, *On the cyclicity of the period annulus of quasi-homogeneous polynomial vector fields*, arXiv:2606.22137v1](https://arxiv.org/abs/2606.22137). Opened abs and HTML. Upper bound on zeros of the k-th Melnikov function for a one-parameter polynomial perturbation of a quasi-homogeneous center, in terms of k, max(s₁,s₂), and perturbation degree n. Completely solves one named application. Unperturbed quasi-homogeneous centers have a period annulus, hence no isolated cycles. Not a new H(n).

- [Gasull–Santana, *Limit cycles and invariant algebraic curves*, arXiv:2510.11705v2](https://arxiv.org/abs/2510.11705). Re-opened [HTML](https://arxiv.org/html/2510.11705v2). Theorem A: H_C(n+c) ≥ H(n) + O(C) for a prescribed non-degenerate invariant curve C of degree c. Corollary 2: H(n+m) ≥ H(n) + Har(m) with Harnack number Har(m) = (m−1)(m−2)/2 + [1+(−1)^m]/2. Weaker than H(n+1)≥H(n)+1 when m=1 (Har(1)=0). Corollary 3: Kolmogorov H_K(n) ≥ H(n−1), and they print H_K(5)≥28 (uses the unreplayed H(4)≥28 seed; beats Carvalho–Cruz–Gouveia 22 as a Kolmogorov number, not as H(5)). Corollary 4: game-theory square H_□(n) ≥ H(n−2). Does not beat Li–Liu–Yang 13 or Prohens–Torregrosa 28 as planar H(n).

- [Ascoli–Novaes, arXiv:2601.21865v1](https://arxiv.org/abs/2601.21865). Opened abs. Crossing Hilbert number H_c(n) for piecewise polynomial fields; H_c(n) grows at least as n²/4. Different function.

- [Cruz–Oliveira–Torregrosa, arXiv:2509.06198v1](https://arxiv.org/abs/2509.06198). Opened abs. Piecewise quadratic Kolmogorov: at least 6 crossing cycles. Smooth quadratic Kolmogorov have none (they say so). Different function.

- [Marín–Villadelprat, *The cyclicity of hyperbolic hemicycles*, arXiv:2501.16924v1](https://arxiv.org/abs/2501.16924). Opened abs. Cyclicity of an unbounded hemicycle graphic; for quadratic class Q₃^R, cyclicity of two hemicycles and an alien-cycle statement. Not a new H(2).

- [Yeung, arXiv:2402.12506v1](https://arxiv.org/abs/2402.12506). Opened abs. Claims a gap in Ilyashenko 1991 Dulac asymptotics. Context for per-system finiteness, not a table number.

- [Ilyashenko–Llibre, arXiv:0910.3443v1](https://arxiv.org/abs/0910.3443). Opened abs and PDF. Restricted upper bound for quadratic fields σ-distant from centers and κ-distant from singular fields, counting only cycles δ-distant from equilibria and infinity. Bound depends on (σ,κ,δ); not a uniform H(2). Quotes Zhang: only one quadratic nest can have more than one cycle.

- [Binyamini–Novikov–Yakovenko, arXiv:0808.2952v3](https://arxiv.org/abs/0808.2952). Opened abs. Tangential Hilbert 16th: Abelian-integral zeros bounded by a double exponential in the degree. That is Z(m,n), not H(n).

Failed / not used as record (q2):

- Li–Liu–Yang full text: still 403 after Unpaywall and four Elsevier URLs. No author-page PDF found.
- Chen–Wang 1979 Acta Math. Sinica 22: Chinese journal; Chen Lansun’s index lists the title; no open PDF opened.
- Yu–Han “four limit cycles in quadratic near-integrable systems” was cited as arXiv:1002.1005; that id is a 2010 software-engineering paper (Waignier et al.). Wrong id; not a Hilbert paper.
- ddd.uab.cat and Scholarpedia live fetches timed out once each; the Prohens–Torregrosa PDF succeeded on retry, Scholarpedia was already read from the first search-tool fetch.
- Llibre’s `mat.uab.cat/~jllibre/` homepage returned 164 bytes, not a publication list. The 2004 PDF was the Cambridge file above.
- Piecewise 2025–2026 papers are a different Hilbert number; not used as H(n).
- No OEIS lookup.

## 2026-08-27 (q3)

No new published H(n). Li–Liu–Yang full text still 403. Papers
opened or re-opened while scoring the ten ideas:

- [Gavrilov–He–Xiao, arXiv:2606.22137v1](https://arxiv.org/abs/2606.22137). Re-opened [abs](https://arxiv.org/abs/2606.22137) and [HTML](https://arxiv.org/html/2606.22137v1) for line HH. Their §5 application is the period annulus of a constant multiple of H = x⁴ + 4y² (after rescaling y). They bound every Melnikov order for one-parameter polynomial perturbations of a quasi-homogeneous center and get cyclicity 1 for a linear unfolding. Not a new H(3). Not beaten here.

- [Eshkobilov–Kadyrov–Mamayusupov, arXiv:2604.12883v1](https://arxiv.org/abs/2604.12883). Re-opened abs and HTML for line II (Remark 4, T3 degree budget N = 3n+2). Same claims as q1.

- [Scholarpedia, Han–Li–Li 2010](http://www.scholarpedia.org/article/Limit_cycles_of_planar_polynomial_vector_fields). Re-opened for line JJ. Z(2,n) = floor((n−1)/2) because M(h) is a polynomial. Lead for the formula; the attaining family is replayed in `compute/q3/jj-weak-hilbert/`.

- [Villanueva–Tucker, *Center conditions and cyclicity for generic planar polynomial vector fields*, arXiv:2602.22558v1](https://arxiv.org/abs/2602.22558). Opened [abs](https://arxiv.org/abs/2602.22558) and [HTML](https://arxiv.org/html/2602.22558v1). Generic (residual) upper bounds on small-amplitude cyclicity: M_h^*(n) ≤ n+2 for homogeneous nonlinearities, and a quadratic-in-n bound for generic non-homogeneous fields. They note 3 = M(2) < M^*(2) = 4, so the generic bound is not Bautin. Not a uniform H(n). Not a new lower bound.

- [Gasull–Santana, *A note on Hilbert 16th problem*, PAMS 153 (2025) 669–677](https://ddd.uab.cat/pub/artpub/2025/309367/GasSan24-Postprint.pdf). Opened the UAB postprint. Same two theorems as arXiv:2407.13465v2 (already in q1): H(n+1) ≥ H(n)+1, and if H(n) is finite it is attained by a structurally stable field with only hyperbolic cycles. Table still H(2)≥4, H(3)≥13, H(4)≥28.

Failed / not used as record (q3):

- Li–Liu–Yang JDE 246 (2009) full text: still 403. Their 13 is still not replayed.
- Piecewise crossing numbers (arXiv:2601.21865) remain a different function.
- No OEIS lookup.
