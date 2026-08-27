# Research log — simon-lieb-thirring

Papers, OEIS, failed lookups. Cite every URL you opened, including the
ones that gave nothing. Forum numbers (MSE, Reddit, MathOverflow,
AlphaXiv) are leads, not citations.

## 2026-08-27

Record for the $\gamma=1$ ratio, after fetching and reading the sources
below: still $L_{1,d}/L_{1,d}^{\mathrm{cl}}\le 1.456$, from
Frank–Hundertmark–Jex–Nam, arXiv:1808.09017v1 / JEMS 23 (2021). No
later arXiv paper opened tonight states $L_{1,d}/L_{1,d}^{\mathrm{cl}}<1.456$
or $\mathcal{C}_1<0.373556$.

### The 2018 paper (the record)

- [Frank–Hundertmark–Jex–Nam, *The Lieb-Thirring inequality revisited*, arXiv:1808.09017v1](https://arxiv.org/abs/1808.09017)
  ([HTML](https://arxiv.org/html/1808.09017v1); API `export.arxiv.org`).
  Submission history is **v1 only** (27 Aug 2018; 14 pages). Opened the
  abs page, the HTML, and the API metadata.
  **Theorem 1** states, for all $d\ge 1$,
  $$L_{1,d}/L_{1,d}^{\mathrm{cl}}\le 1.456.$$
  It does **not** claim the Lieb–Thirring conjecture, and it does **not**
  give a closed form for the optimal $\mathcal{C}_1$. The one-bound-state
  comparison written in the introduction is
  $L_{1,1}^{\mathrm{So}}/L_{1,1}^{\mathrm{cl}}=2/\sqrt{3}=1.155\ldots$.
  The previous upper bound they quote is Eden–Foias / Dolbeault–Laptev–Loss
  $L_{1,d}/L_{1,d}^{\mathrm{cl}}\le\pi/\sqrt{3}=1.814\ldots$.
  Duality is (7):
  $K_d(1+2/d)=\bigl[L_{1,d}(1+d/2)\bigr]^{-2/d}$.
  **Proposition 10** defines, as (35),
  $$\mathcal{C}_d:=\inf\Bigl\{\Bigl(\int_0^\infty\varphi^2\Bigr)^{d/2}\frac{d}{2}\int_0^\infty\frac{\bigl(1-\int_0^\infty\varphi(s)f(st)\,ds\bigr)^2}{t^{1+d/2}}\,dt\Bigr\}$$
  over $f,\varphi:\mathbb{R}_+\to\mathbb{R}_+$ with
  $\int_0^\infty f^2=\int_0^\infty\varphi=1$, and proves
  $$K_d/K_d^{\mathrm{cl}}\ge\frac{d\,2^{4/d}}{(d+2)^{1+4/d}\,\mathcal{C}_d^{2/d}}.$$
  For $d=1$ this is $K_1/K_1^{\mathrm{cl}}\ge 16/(243\,\mathcal{C}_1^2)$.
  Combined with (7) one has
  $L_{1,1}/L_{1,1}^{\mathrm{cl}}=1/\sqrt{K_1/K_1^{\mathrm{cl}}}=(9\sqrt{3}/4)\,\mathcal{C}_1$.
  The paper itself writes the $d=1$ numbers, not those two algebraic
  identities: Proposition 10 (statement) has
  $K_1/K_1^{\mathrm{cl}}\ge 0.471851$ and
  $L_{1,1}/L_{1,1}^{\mathrm{cl}}\le 1.455786$; the proof of
  Proposition 10 writes $0.471851\ldots$ and $1.455785\ldots$ from
  $\mathcal{C}_1\le 0.373556$.
  **Lemma 11** states $\tfrac13\le\mathcal{C}_1\le 0.373556$. The
  lower bound is Cauchy–Schwarz, not a trial pair. The two trial pairs
  are:
  1. $f(t)=(1+\mu t^{3/2})^{-1}$,
     $\mu=\bigl[4\pi/(9\sqrt{3})\bigr]^{3/2}$,
     $\varphi(t)=5(1-t^{1/4})\mathbf{1}(t\le 1)$, claimed
     $\mathcal{C}_1\le 0.381378$.
  2. $f(t)=(1+\mu_0 t^{4.5})^{-0.25}$,
     $\varphi(t)=c_0(1-t^{0.36})^{2.1}/(1+t)\,\mathbf{1}(t\le 1)$,
     with $\mu_0$ and $c_0$ fixed by $\int f^2=\int\varphi=1$, claimed
     $\mathcal{C}_1\le 0.373556$.
  The paper does **not** print numerical values of $\mu_0$ or $c_0$.
  Replay of the conversion (not a new bound):
  $(9\sqrt{3}/4)\cdot 0.373556\approx 1.455790$ and
  $16/(243\cdot 0.373556^2)\approx 0.471848$, so the published
  $1.455786$ / $1.455785$ / $1.456$ are rounded from that
  $\mathcal{C}_1$ claim.
  Eden–Foias is cited as *J. Math. Anal. Appl.* 162 (1991), 250–254.

- [JEMS published page](https://ems.press/journals/jems/articles/666342)
  and the journal PDF
  [10.4171-jems-1062.pdf](https://content.ems.press/assets/public/full-texts/serials/jems/23/8/666342/online/10.4171-jems-1062.pdf)
  (downloaded; streams compressed, text not extracted here).
  Landing page: J. Eur. Math. Soc. **23** (2021), no. 8, 2583–2600,
  Subscribe-to-Open. Abstract only on the landing page; no numerical
  constant there.

- [KIT author copy of the JEMS article](https://publikationen.bibliothek.kit.edu/1000135256/149445771).
  Same Theorem 1 ($L_{1,d}/L_{1,d}^{\mathrm{cl}}\le 1.456$), same
  Proposition 10 numbers $0.471851$ and $1.455786$, same Lemma 11
  $\mathcal{C}_1\le 0.373556$, and the same two trial pairs
  ($0.381378$ then $0.373556$). Journal text does **not** change the
  number.

### Surveys that still quote 1.456

- [Frank, *The Lieb-Thirring inequalities: Recent results and open problems*, arXiv:2007.09326v1](https://arxiv.org/abs/2007.09326)
  ([HTML](https://arxiv.org/html/2007.09326v1)). v1 only (18 Jul 2020;
  46 pages). Section 1.5 / Theorem 5: “currently the best one in all
  dimensions”, citing FHJN as [57] (then “JEMS, to appear”),
  $K_d\ge(0.471851)^{1/d}K_d^{\mathrm{cl}}$. Section 3.5 equation (18):
  $L_d\le 1.456\,L_d^{\mathrm{cl}}$ for all $d\ge 1$. Later display:
  $L_{\gamma,d}\le 1.456\,L_{\gamma,d}^{\mathrm{cl}}$ for
  $1\le\gamma<3/2$. Does **not** improve $1.456$ or $\mathcal{C}_1$.

- [Schimmer, *The state of the Lieb--Thirring conjecture*, arXiv:2203.06051v1](https://arxiv.org/abs/2203.06051)
  ([HTML](https://arxiv.org/html/2203.06051v1)). v1 only (11 Mar 2022;
  22 pages; Lieb 90th-birthday volume). States that FHJN [20]
  (JEMS 23, 2583–2600) give $K_1\ge 0.471851\,K_1^{\mathrm{cl}}$,
  “or equivalently $L_{1,1}\le 1.456\,L_{1,1}^{\mathrm{cl}}$”, and
  after lifting
  $L_{\gamma,d}\le 1.456\,L_{\gamma,d}^{\mathrm{cl}}$
  (the HTML writes $L_{\gamma,1}^{\mathrm{cl}}$ in one display)
  for $d\ge 1$ and $1\le\gamma<3/2$, “which currently constitute the
  best bounds in these parameter regions.” Figure caption:
  $R_{\gamma,d}\le 1.456$. Does **not** claim a smaller ratio.

- [Nam, *Direct methods to Lieb-Thirring kinetic inequalities*, arXiv:2012.12045v2](https://arxiv.org/abs/2012.12045)
  ([HTML](https://arxiv.org/html/2012.12045v2); v1 HTML also opened).
  v1 22 Dec 2020, v2 27 Jun 2021 (“minor corrections”). Theorem 2.9:
  $(K_d^{\mathrm{cl}}/K_d)^{d/2}=L_{1,d}/L_{1,d}^{\mathrm{cl}}\le 1.456$,
  “also the best known result for all $1\le\kappa<3/2$.” Restates the
  second Lemma 11 pair as
  $f(t)=(1+\mu_0 t^{4.5})^{-0.25}$,
  $\varphi(t)=(1-t^{0.36})^{2.1}/(1+t)\,\mathbf{1}(t\le 1)$
  (no $c_0$ in the display; $\mu_0$ from $\int f^2=1$), and
  $\mathcal{C}_{1,1}\le 0.373556$, hence
  $L_{1,1}/L_{1,1}^{\mathrm{cl}}\le 1.456$. v1 already contains
  $1.456$ and $0.373556$. Does **not** move either number.

- [Ilyin–Kostianko–Zelik, *Applications of the Lieb--Thirring and other bounds…*, arXiv:2202.01531v1](https://arxiv.org/abs/2202.01531)
  ([HTML](https://arxiv.org/html/2202.01531v1)). Opened as a 2022
  restatement. Writes that Eden–Foias / DLL had
  $R=\pi/\sqrt{3}=1.8138\ldots$ and “the best to date estimate”
  from FHJN is $R=1.456\ldots$. Does **not** prove a new $\gamma=1$
  constant.

### The 2008 predecessor

- [Dolbeault–Laptev–Loss, *Lieb-Thirring inequalities with improved constants*, arXiv:0708.1165v2](https://arxiv.org/abs/0708.1165)
  ([HTML v2](https://arxiv.org/html/0708.1165v2);
  [HTML v1](https://arxiv.org/html/0708.1165v1);
  abs page opened). v1 8 Aug 2007, v2 24 Aug 2007 (Seiringer pointed
  out an omission in Theorem 2). **Theorem 1**:
  $\sum|\lambda_n|\le\frac{2}{3\sqrt{3}}\int\mathrm{Tr}[V^{3/2}]\,dx$
  for 1D matrix potentials. They define
  $R:=\frac{2}{3\sqrt{3}}\bigl(\frac{2}{3\pi}\bigr)^{-1}=1.8138\ldots$.
  That identity is exactly $\pi/\sqrt{3}$ (they do **not** write
  $\pi/\sqrt{3}$). Theorem 2 (v2): for any $\gamma\ge 1$ and $d\ge 1$,
  $L_{d,\gamma}\le R\times L_{d,\gamma}^{\mathrm{cl}}$. Remark 1
  compares $\frac{4}{3\sqrt{3}\,\pi}<\frac{2}{3\sqrt{3}}<2\times\frac{2}{3\pi}$,
  “about $0{,}2450\ldots<0{,}3849\ldots<0{,}4244\ldots$”. v1 already
  has the same $R=1.8138\ldots$; v2 only fills the range of Theorem 2.
  Eden–Foias is cited as *J. Funct. Anal.* 162 (1991), 250–254
  (same volume/pages as the JMAA citation in FHJN; the article text
  was not opened). Does **not** claim anything below $1.8138$.

### Older sharp / lifting papers (opened)

- [Laptev–Weidl, *Sharp Lieb-Thirring Inequalities in High Dimensions*, arXiv:math-ph/9903007v2](https://arxiv.org/abs/math-ph/9903007)
  ([HTML](https://arxiv.org/html/math-ph/9903007v2)).
  v1 3 Mar 1999, v2 16 Jun 1999 (“to appear in Acta Math”).
  Proves $L_{\gamma,d}=L_{\gamma,d}^{\mathrm{cl}}$ for all
  $\gamma\ge 3/2$ and all $d\ge 1$ (operator-valued potentials,
  then lifting). Does **not** treat the $\gamma=1$ gap and does **not**
  state $1.456$.

- [Hundertmark–Laptev–Weidl, *New bounds on the Lieb-Thirring constants*, arXiv:math-ph/9906013v1](https://arxiv.org/abs/math-ph/9906013)
  ([HTML](https://arxiv.org/html/math-ph/9906013v1)). v1 only
  (16 Jun 1999; Invent. Math. 140 (2000), 693–704).
  Theorem 4.1: $L_{\gamma,d}\le 2L_{\gamma,d}^{\mathrm{cl}}$ for
  $1\le\gamma<3/2$ and all $d$; also $\le 2L^{\mathrm{cl}}$ for
  $d=1$, $1/2\le\gamma<3/2$, and $\le 4L^{\mathrm{cl}}$ for
  $d\ge 2$, $1/2\le\gamma<1$. Remark: $L_{1,d}^{\mathrm{cl}}\le L_{1,d}\le 2L_{1,d}^{\mathrm{cl}}$.
  Does **not** improve past the factor $2$, and does **not** mention
  $1.456$.

- [Simon, *Schrödinger Operators in the Twenty-First Century*, mp_arc 00-78](https://web.ma.utexas.edu/mp_arc-bin/mpa?yn=00-78)
  ([TeX source](https://web.ma.utexas.edu/mp_arc-bin/mpp/00-78.tex?hd=tex&yn=00-78&la=1&lz=459)).
  Opened the index page and the `.tex`. Problem 15 asks to prove the
  Lieb–Thirring conjecture on $L_{\gamma,\nu}$ for $\nu=1$ and
  $\tfrac12<\gamma<\tfrac32$. States the max of quasiclassical and
  one-bound-state constants; known at $\gamma\ge 3/2$ (Aizenman–Lieb)
  and $\gamma=1/2$ (Hundertmark–Lieb–Thomas). Does **not** give a
  numerical upper bound such as $1.456$ (the note is from 2000).
  The `00-78.ps.gz` URL 404’d. The Rome mirror
  [kleine.mat.uniroma3.it](http://kleine.mat.uniroma3.it/mp_arc-bin/mpa?yn=00-78)
  index loaded.

- [Lieb–Thirring 1976 reprint landing page](https://link.springer.com/chapter/10.1007/978-3-662-02725-7_13)
  (Selecta *The Stability of Matter: From Atoms to Stars*, 1991).
  Preview shows (1.1)
  $\sum|e_j|^\gamma\le L_{\gamma,n}\int |V|_-^{\gamma+n/2}$
  for $\gamma>\max(0,1-n/2)$. Full text is paywalled (“Unable to
  display preview”).
  [Lieb publications list](https://web.math.princeton.edu/~lieb/publications.html)
  records the original as Studies in Mathematical Physics, Princeton
  1976, pp. 269–303; no PDF link there.
  [Princeton University Press book page](https://press.princeton.edu/books/ebook/9781400868940/studies-in-mathematical-physics-pdf)
  is a catalog entry, not the chapter.
  Guessed PDF `https://web.math.princeton.edu/~lieb/LiebThirring1976.pdf`
  404’d. Guessed Springer chapter
  `https://link.springer.com/chapter/10.1007/978-3-662-05255-6_14`
  404’d. **Full 1976 text not obtained.**

### Failed to open (article text)

- Eden–Foias 1991. DLL cites *J. Funct. Anal.* 162 (1991) 250–254;
  FHJN, Schimmer, and MathSciNet cite *J. Math. Anal. Appl.* 162
  (1991) 250–254. Tried
  `https://www.sciencedirect.com/science/article/pii/0022247X9190020C`
  and a JFA-shaped sibling URL: both HTTP 403. MathSciNet relay
  [MR1135275](https://mathscinet.ams.org/mathscinet/relay-station?mr=https%3A%2F%2Fmathscinet.ams.org%2Fmathscinet-getitem%3Fmr%3D1135275)
  confirms the JMAA bibliographic line only. **Article text not
  obtained.** No independent check of their constant tonight.

- Acta Math. journal page for Laptev–Weidl
  ([projecteuclid.org](https://projecteuclid.org/journals/acta-mathematica/volume-184/issue-1/Sharp-Lieb-Thirring-inequalities-in-high-dimensions/10.1007/BF02392782.full)
  via search): bibliographic confirmation only; the arXiv v2 above is
  the text that was read.

### Later papers checked as candidates (did not move 1.456)

- [Seiringer–Solovej, *A simple approach to Lieb--Thirring type inequalities*, arXiv:2303.04504v2](https://arxiv.org/abs/2303.04504)
  ([HTML](https://arxiv.org/html/2303.04504v2)). v2 18 Sep 2023,
  “published version.” Cites FHJN JEMS 2021 as [3] for “the currently
  best known lower bounds.” Their own kinetic bound with a gradient
  remainder is stated to be **weaker** than [3] (and weaker than
  Rumin’s $d/(d+4)$). Does **not** claim
  $L_{1,d}/L^{\mathrm{cl}}<1.456$ or $\mathcal{C}_1<0.373556$.

### arXiv search log (no hit claiming a smaller ratio)

Queries against `https://export.arxiv.org/api/query` (2018–2026 unless
noted), 3 s between calls:

- `all:"Lieb-Thirring" AND all:1.456` — 0 hits (API does not index
  body numbers).
- `all:"0.373556"`, `all:"0.471851"`, `abs:"1.456" AND all:Lieb` — 0.
- `ti:"Lieb-Thirring" AND submittedDate:[20190101 TO 20261231]` —
  40 titles returned (sample: 2607.15504, 2510.24148, 2403.04347,
  2303.04504, 2206.15368, 2203.06051, 2012.12045, 2007.09326,
  2002.04964). None of the titles/abstracts claim
  $L_{1,d}/L^{\mathrm{cl}}<1.456$.
- `au:Nam AND ti:Lieb-Thirring AND submittedDate:[20180101 TO 20261231]`
  — 7 hits, including 1808.09017 itself and the Nam chapter; no new
  constant paper.
- `all:"Lieb-Thirring" AND all:"best constant" AND submittedDate:[20190101 TO 20261231]`
  — 8 hits (periodic LT, NLS/orthonormal, finite-rank Hardy–LT, …);
  none advertise a smaller $L_{1,d}/L^{\mathrm{cl}}$.
- `all:"Lieb-Thirring" AND all:"improved constants" AND submittedDate:[20180101 TO 20261231]`
  — 2 hits, neither the Euclidean $\gamma=1$ ratio.
- `ti:"Schrödinger Operators: Eigenvalues and Lieb-Thirring"` — 0
  (the Frank–Laptev–Weidl Cambridge book is **not** on arXiv; cited
  by 2303.04504 as CUP 2023, not opened).

Opened as leads, **not citations**:
[Wikipedia, *Lieb–Thirring inequality*](https://en.wikipedia.org/wiki/Lieb%E2%80%93Thirring_inequality)
(fetched; last-modified header 13 Aug 2026) still writes “the best
known value for the physical relevant constant $L_{1,3}$ is
$1.456\,L_{1,3}^{\mathrm{cl}}$” and cites FHJN JEMS / 1808.09017
(it misprints the JEMS issue as 10 (4)).
[MathWorld, *Simon's Problems*](https://mathworld.wolfram.com/SimonsProblems.html)
and [MathWorld, *Schrödinger Operator*](https://mathworld.wolfram.com/SchroedingerOperator.html)
are bibliographic leads to Simon 2000 / mp_arc 00-78; they do **not**
state $1.456$.
A Laptev seminar PDF
[msrn-files.sfedu.ru/…/laptev_pr.pdf](https://msrn-files.sfedu.ru/msrp/seminars_info/laptev_pr.pdf)
(search hit) still writes $R_{1,1}=1.456\ldots$; lead only.

## 2026-08-27 (later; q2)

Correction of the log above: a later paper **does** beat $1.456$. The
q1 title/abstract search listed 2403.04347 and did not open the body.
The number is not in the abstract.

### The later record

- [Carvalho Corso–Ried, *On a variational problem related to the Cwikel–Lieb–Rozenblum and Lieb–Thirring inequalities*, arXiv:2403.04347](https://arxiv.org/abs/2403.04347)
  ([v1 abs](https://arxiv.org/abs/2403.04347v1);
  [v1 HTML](https://arxiv.org/html/2403.04347v1);
  [v2 abs](https://arxiv.org/abs/2403.04347);
  [v2 HTML](https://arxiv.org/html/2403.04347v2);
  API `export.arxiv.org`).
  v1 7 Mar 2024 (38 KB); v2 21 Dec 2024 (“Corrected a few typos”).
  Opened abs v1, abs v2, HTML v1, HTML v2, and the API metadata.
  The **abstract does not contain** $1.44655$ or $0.371185695$.
  **Table 1.1** has $M_3=0.371185695$. **Corollary 1.7 / (1.14)** states
  $L_{1,1,1}/L^{\mathrm{cl}}_{1,1,1}\le 1.44655$.
  Identification **(1.12)**: $\mathcal{C}_{d,\sigma}=(d/\sigma)M_{2+d/\sigma}$,
  so $\mathcal{C}_{1,1}=M_3$. Conversion **(1.13)** at $\gamma=3$ is the
  same $(9\sqrt{3}/4)M_3$ as FHJN Proposition 10.
  **Theorem 1.3** writes the optimiser $h=B_\gamma e^{\theta_\gamma}$.
  **Lemma 4.6** (proof) has
  $\mathrm{Re}\,\theta=-(1/\pi)\int_0^\infty g(k)(\cos(kx)\sinh(ky)-ky)/(k(\cosh(2k)-1))\,dk$.
  They present $M_3$ as the method ceiling for FHJN/HKRV.
  v1 already contains $1.44655$ and $0.371185695$.
  HTML “Date: August 24, 2026” is the rendered date, not a new version.

- [Carvalho Corso, *A generalized three lines lemma in Hardy-like spaces*, arXiv:2407.10117](https://arxiv.org/abs/2407.10117)
  ([HTML](https://arxiv.org/html/2407.10117);
  [HTML v2](https://arxiv.org/html/2407.10117v2);
  TeX via `arxiv.org/e-print/2407.10117`).
  v1 14 Jul 2024; v2 3 Jan 2025 (“Added a weighted version… corrected
  many typos”). Opened abs, HTML v1, HTML v2, and the TeX source
  (`introduction.tex`).
  **(1.11)** is the Clausen formula for $H_{\infty,2}(\alpha)$.
  **Corollary 1.8 / (eq:LTbound)** in the TeX is
  $L_{1,d,s}/L^{\mathrm{cl}}\le \pi(1-\alpha)^{1/\alpha}/(\alpha\sin(\pi\alpha))\,\exp(\mathrm{CI}_2(2\pi(1-\alpha))/(\pi\alpha))$
  with $\alpha=2s/(d+2s)$. At $d=s=1$ this is
  $(\pi/3)\exp(3\,\mathrm{CI}_2(2\pi/3)/(2\pi))$.
  The remark after the corollary writes $L_{1,1,1}/L^{\mathrm{cl}}\le 1.447$
  and cites CCR24. **Does not** beat $1.44655$; it is the same bound,
  rounded.

### Later papers opened (did not move 1.44655)

- [Duong–Le–Nam–Nguyen, *Finite-Rank Optimizers for the mass-supercritical Lieb–Thirring and Hardy–Lieb–Thirring Inequalities*, arXiv:2510.24148v1](https://arxiv.org/abs/2510.24148)
  (opened abs/HTML). Still writes that FHJN “provid[es] the best known
  constant to date.” Does **not** state $1.44655$ and does **not**
  improve the Euclidean $\gamma=1$ ratio.

- [Carvalho Corso–Weidl–Zeng, *Lieb-Thirring inequalities for the shifted Coulomb Hamiltonian*, arXiv:2409.01291v3](https://arxiv.org/abs/2409.01291)
  (opened abs/HTML). Shifted Coulomb, not the Euclidean $\gamma=1$
  ratio. Does **not** claim a smaller $1.44655$.

- [Duong–Nam, *Lieb–Thirring inequalities for large quantum systems with inverse nearest-neighbor interactions*, arXiv:2501.00866v1](https://arxiv.org/abs/2501.00866)
  (opened abs/HTML). Different operator. No $1.44655$.

- [Frank–Kovařík, *Lieb-Thirring inequality for the 2D Pauli operator*, arXiv:2404.09926v1](https://arxiv.org/abs/2404.09926)
  (opened abs/HTML). Pauli, not Euclidean $\gamma=1$.

- [Kähler–Kowacs–Ruzhansky, *Lieb-Thirring inequalities for the Dirac operator on spheres*, arXiv:2602.00725v2](https://arxiv.org/abs/2602.00725)
  (opened abs). Spheres, not $\mathbb{R}^d$.

- [Melik-Adamyan title, arXiv:2607.15504v1](https://arxiv.org/abs/2607.15504)
  (opened abs/HTML). Canonical Hamiltonians, not the Euclidean $\gamma=1$
  ratio.

- [Complex-potential LT, arXiv:2510.02288v1](https://arxiv.org/abs/2510.02288)
  (opened abs/HTML). Complex potentials. No $1.44655$.

### arXiv search log (q2)

Queries against `https://export.arxiv.org/api/query`, 3 s between calls:

- `ti:"Lieb-Thirring" AND submittedDate:[20240101 TO 20261231]` — 14
  titles (2607.15504, 2602.00725, 2510.24148, 2510.02288, 2510.02192,
  2509.17307, 2501.00866, 2409.01291, 2406.15134, 2406.00580,
  2405.00799, 2404.09926, …). None of the titles/abstracts claim
  $L_{1,d}/L^{\mathrm{cl}}<1.44655$.
- `all:"1.44655" AND all:Lieb` — 0 (API does not index body numbers).
- `all:"0.371185695"` — 0.
- `all:"Carvalho Corso" AND all:Thirring` — 3 hits: 2409.01291,
  2407.10117, 2403.04347.
- `au:Frank AND all:"Lieb-Thirring" AND submittedDate:[20240301 TO 20261231]`
  — 2404.09926 only.
- `au:Nam AND all:"Lieb-Thirring" AND submittedDate:[20240301 TO 20261231]`
  — 2510.24148, 2501.00866.

Failed lookups: no arXiv hit for a Euclidean $\gamma=1$ ratio below
$1.44655$. The Frank–Laptev–Weidl CUP 2023 book is still not on arXiv
and was not opened as full text this session.
