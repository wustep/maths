# Research log — continuity of the integrated density of states

Status cutoff: 2026-08-27. The arXiv versions are treated as the
record when they exist. Older foundational papers predate arXiv; the
journal or author archive is linked.

## 2026-08-27 — statement and definitions

- Barry Simon, [*Schrödinger operators in the twenty-first
  century*](http://www.math.caltech.edu/papers/bsimon/r40.pdf),
  *Mathematical Physics 2000*, pp. 283–288. The Caltech reprint was
  downloaded and page 5 was rendered. Problem 14 says to prove that
  $k(E)$ is continuous, then records the one-dimensional and
  discrete cases and the open higher-dimensional continuum case.
- The [ResearchGate landing
  page](https://www.researchgate.net/publication/2335557_Schrodinger_Operators_In_The_Twenty-First_Century)
  was also opened while locating the reprint. Its PDF link returned
  404, so no claim is taken from it.
- Werner Kirsch and Bernd Metzger,
  [arXiv:math-ph/0608066](https://arxiv.org/abs/math-ph/0608066),
  [archived full PDF](https://web.ma.utexas.edu/mp_arc/c/06/06-225.pdf),
  *The Integrated Density of States for Random Schrödinger
  Operators*. This survey gives the local trace definition, the
  thermodynamic-limit framework, the Delyon–Souillard boundary
  argument, and the regularity landscape as of 2006.

## 2026-08-27 — foundational record

- Leonid Pastur, [*Spectral properties of disordered systems in the
  one-body approximation*](https://link.springer.com/article/10.1007/BF01222516),
  *Comm. Math. Phys.* 75 (1980), 179–196. This is a foundational
  ergodic random-operator source. The Springer page was readable;
  its full PDF is subscription-gated.
- M. A. Shubin, [*The spectral theory and the index of elliptic
  operators with almost periodic
  coefficients*](https://www.mathnet.ru/eng/rm4044), *Russian Math.
  Surveys* 34 (1979), 109–157. The Math-Net record links the English
  PDF and Shubin's earlier density-of-states work. The PDF endpoint
  timed out in the browser and returned 403 to the command-line
  fetcher.
- Walter Craig and Barry Simon,
  [*Subharmonicity of the Lyaponov
  index*](https://projecteuclid.org/journals/duke-mathematical-journal/volume-50/issue-2/Subharmonicity-of-the-Lyaponov-index/10.1215/S0012-7094-83-05025-1.full),
  *Duke Math. J.* 50 (1983), 551–560. The paper treats bounded
  one-dimensional ergodic continuum operators and their discrete
  analogues; the Thouless/subharmonicity argument gives log-Hölder
  regularity. The [author-uploaded landing
  page](https://www.researchgate.net/publication/38333264_Subharmonicity_of_the_Lyaponov_index)
  was used to inspect the opening definitions when Project Euclid's
  iframe blocked text extraction.
- Walter Craig and Barry Simon, [*Log Hölder continuity of the
  integrated density of states for stochastic Jacobi
  matrices*](https://projecteuclid.org/journals/communications-in-mathematical-physics/volume-90/issue-2/Log-H%C3%B6lder-continuity-of-the-integrated-density-of-states-for-stochastic/cmp/1103940280.full),
  *Comm. Math. Phys.* 90 (1983), 207–218. This is the all-dimensional
  discrete log-Hölder record cited by Bourgain–Klein. Project
  Euclid's PDF endpoint returned an anti-bot page.
- François Delyon and Bernard Souillard, [*Remark on the continuity
  of the density of states of ergodic finite difference
  operators*](https://projecteuclid.org/journals/communications-in-mathematical-physics/volume-94/issue-2/Remark-on-the-continuity-of-the-density-of-states-of-ergodic/cmp/1103941286.full),
  *Comm. Math. Phys.* 94 (1984), 289–291. The discrete proof bounds
  an eigenspace in a cube by two boundary layers. Project Euclid's
  PDF endpoint returned the same anti-bot page; the theorem and proof
  were independently read in the Kirsch–Metzger survey.

## 2026-08-27 — the general deterministic advance

- Jean Bourgain and Abel Klein, [arXiv:1112.1716v3 abstract](https://arxiv.org/abs/1112.1716)
  and [full HTML](https://arxiv.org/html/1112.1716v3), *Bounds on the
  density of states for Schrödinger operators*, *Invent. Math.* 194
  (2013), 41–72. Theorem 1.1 proves, for every bounded deterministic
  continuum potential in $d=1,2,3$,

  $$
  \eta^*([E,E+\varepsilon])
  \leq C\bigl(\log(1/\varepsilon)\bigr)^{-\kappa_d},
  \qquad
  \kappa_1=1,\quad\kappa_2=\tfrac14,\quad\kappa_3=\tfrac18.
  $$

  The outer measure dominates any DOS measure that exists, so this
  proves IDS continuity for ergodic families in those dimensions.
  Equations (3.95), (3.111), and (3.115)–(3.121) expose the dimension
  balance. The introduction says that a UCP power $\beta$ would
  allow dimensions below $\beta/(\beta-1)$; their $\beta=4/3$
  gives $d<4$.
- Abel Klein and C. S. Sidney Tsang,
  [arXiv:1408.7111](https://arxiv.org/abs/1408.7111), *Local behavior
  of solutions ... with singular potentials and bounds on the density
  of states*. This extends the outer-measure result to stated singular
  potential classes in dimensions one through three. It does not
  cross the dimension-four frontier.

## 2026-08-27 — random classes in every dimension

- Jean-Michel Combes, Peter Hislop, and Frédéric Klopp,
  [arXiv:math-ph/0605029v2](https://arxiv.org/abs/math-ph/0605029),
  *An optimal Wegner estimate and its application to the global
  continuity of the integrated density of states for random
  Schrödinger operators*, *Duke Math. J.* 140 (2007), 469–498.
  For continuum Anderson-type models in every dimension, a compactly
  supported nonnegative single-site potential and an atomless
  conditional law give global continuity. A bounded density gives a
  locally Lipschitz IDS.
- The earlier Combes–Hislop–Klopp article,
  [*Hölder continuity of the integrated density of states for some
  random operators at all
  energies*](https://academic.oup.com/imrn/article-pdf/2003/4/179/1898051/2003-4-179.pdf),
  *IMRN* 2003, 179–209, gives all-energy Hölder regularity under a
  bounded-density Anderson hypothesis.
- François Germinet and Abel Klein,
  [arXiv:1105.0213v3](https://arxiv.org/abs/1105.0213), *A
  comprehensive proof of localization for continuous Anderson models
  with singular random potentials*, *JEMS* 15 (2013), 53–143. It
  allows arbitrary bounded nondegenerate single-site distributions,
  including Bernoulli, and proves log-Hölder IDS continuity at the
  bottom of the spectrum in the localization region.
- Thomas Hupfer, Hajo Leschke, Peter Müller, and Simone Warzel,
  [arXiv:math-ph/0105046v2](https://arxiv.org/abs/math-ph/0105046),
  *The absolute continuity of the integrated density of states for
  magnetic Schrödinger operators with certain unbounded random
  potentials*, *Comm. Math. Phys.* 221 (2001), 229–254. A
  one-parameter decomposition gives local Lipschitz continuity for
  broad alloy and Gaussian examples, including some unbounded
  potentials.
- Norbert Peyerimhoff and Ivan Veselić,
  [arXiv:math-ph/0210047](https://arxiv.org/abs/math-ph/0210047),
  concerns existence of the IDS on amenable covering manifolds. It
  was checked for the definition/existence side and does not supply
  general continuity.
- S. Doi, A. Iwatsuka, and T. Mine,
  [arXiv:math-ph/0010013](https://arxiv.org/abs/math-ph/0010013),
  concerns existence and uniqueness with magnetic fields and
  unbounded random potentials. It is an existence source and leaves
  Simon's continuity question open.

## 2026-08-27 — obstruction and separable handle

- Rupert Frank and Paata Ivanisvili,
  [arXiv:2608.00802v1 abstract](https://arxiv.org/abs/2608.00802) and
  [full HTML](https://arxiv.org/html/2608.00802), *Counterexamples to
  the Landis conjecture in dimensions three and higher*. Theorem 1
  constructs smooth real bounded $V$ and a nonzero smooth real
  solution decaying like $\exp(-c|x|^{4/3})$ in every $d\geq3$.
  This makes the power needed by the Bourgain–Klein extension
  impossible in a uniform estimate of the same form. The paper does
  not discuss an IDS or an ergodic family.
- The two-dimensional contrast is Logunov, Malinnikova,
  Nadirashvili, and Nazarov, [*The Landis conjecture on exponential
  decay*](https://link.springer.com/article/10.1007/s00222-025-01340-1),
  *Invent. Math.* 241 (2025), 465–508. It supports a weaker positive
  Landis statement in the plane and does not alter the $d\geq4$
  IDS question.
- David Damanik and Anton Gorodetski, [*Spectral transitions for the
  square Fibonacci
  Hamiltonian*](https://ems.press/content/serial-article-files/33677?nt=1),
  *J. Spectr. Theory* 8 (2018), 1487–1507. Equations (1)–(2) explicitly
  call the spectrum-sum and DOS-convolution identities standard
  separable-operator theory. This is the precedence check that
  prevents treating the free-direction convolution calculation as a
  new continuity class.

## Fetch notes

- `python3 scripts/arxiv_fetch.py 1112.1716 --research
  problems/simon-ids-continuity/RESEARCH.md` first failed because the
  sandbox could not resolve the host. The approved retry reached the
  arXiv API and returned HTTP 429. The abstract and complete v3 HTML
  were therefore read directly at the links above.
- The same fetcher was tried for `math-ph/0608066`; the approved
  retry also returned HTTP 429. Its arXiv abstract and the archived
  full survey PDF linked above were read instead.
- Direct command-line fetches of the three Project Euclid originals
  returned anti-bot HTML. The Math-Net English-PDF endpoint returned
  HTTP 403. These failures are recorded so that the accessible
  journal pages are not mistaken for locally replayed PDFs.
