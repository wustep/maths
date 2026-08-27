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

Failed / not used as record:

- Llibre–Schlomiuk, Canad. J. Math. 56 (2004), and Coppel 1966: no PDF opened this session. Li Chengzhi polynomials and Coppel’s unique-singularity statement are used as quoted in line A, not as a fetched record.
- No OEIS lookup (H(n) is not an OEIS sequence we needed).
- Wikipedia and MathOverflow numbers were not opened as citations.
- Piecewise paper [arXiv:1809.03433](https://arxiv.org/abs/1809.03433) (H_p(2)≥16) is a different function; abs not used as an H(n) bound.
- Entropy 26 (2024) quadratic formula: not fetched; the refutation is 2411.09594.
- Li–Liu–Yang JDE 246 (2009) full text: paywalled. Their 13 is cited from later papers’ introductions, not replayed.
