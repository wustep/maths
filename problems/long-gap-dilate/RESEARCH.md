# Research log — a long gap in a dilate modulo a prime

## Status (accessed 2026-08-27)

Opened again:

- [Green, *100 Open Problems*, Problem 32](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf)
  (Dec 2025 update, PDF fetched this session). Still open. Shakan
  replaces 100 by 2, “the limit of his method”. Finite-field model
  $\mathbb F_2^n$ is easy by averaging. A positive answer would not
  automatically improve Green #31 (infinitely many primes with a Sidon
  set of size $\sqrt p+O(1)$ are not known).
- Shakan, [arXiv:2004.14828](https://arxiv.org/abs/2004.14828) /
  [ar5iv HTML](https://ar5iv.labs.arxiv.org/html/2004.14828),
  fetched with `python3 scripts/arxiv_fetch.py 2004.14828`. Theorem 1
  is $\sup_d g(dA)\ge 2p/|A|-2$. Proof is Rédei / Alon on
  $P=A\times\{1,\ldots,m\}$; the 2 is $\deg W\le 2k-1$. SIAM page
  [10.1137/20M1335030](https://doi.org/10.1137/20m1335030) still has
  no later improvement of the leading 2 in the text I opened.
- The list id [arXiv:2205.14038](https://arxiv.org/abs/2205.14038) is
  Jiang–Cai–Wu et al., *Quantum Simulation of the Two-Dimensional Weyl
  Equation* (quant-ph). Fetched this session; not Shakan.
- Shakan’s note
  [A large gap in a dilate of a set](https://blog.georgeshakan.com/a-large-gap-in-a-dilate-of-a-set/)
  (1 May 2020): Ruzsa’s Sidon set in $\mathbb Z/(p(p-1)\mathbb Z)$ has
  no gap much longer than $2p$, so the prime-field theorem is false
  for general cyclic groups. Bose–Chowla is the Sidon family he says
  might still improve. Chen–Shparlinski–Winterhof is cited for the
  no-translation variant, not for a larger $C$.
- Di Benedetto–Solymosi–White, [arXiv:2001.06994](https://ar5iv.labs.arxiv.org/html/2001.06994)
  (the [BSW20] Shakan cites): directions of a cartesian product
  $A\times B$, Rédei with Szőnyi’s extension. A direction bound, not a
  blocking-set bound. Tight on long rectangles $A=\{0,1\}$. Does not
  replace Shakan’s 2.
- Korsky, [arXiv:2606.01780](https://arxiv.org/abs/2606.01780), hitting
  $k$-APs in $\{0,\ldots,N-1\}$ at $k\sim\sqrt N$. Linear interval,
  not $\mathbb Z/p\mathbb Z$. Not a citation for Green #32.

Published record I must beat: **Shakan’s universal 2**.
I did not beat it.

## Status (accessed 2026-08-17)

- [Green, *100 Open Problems*, Problem 32](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf)
  (Dec 2025 update): still **OPEN**. If $A\subset\mathbb Z/p\mathbb Z$
  has size $\sqrt p$, is there a dilate with a gap of length
  $100\sqrt p$? Comments record Shakan with 100 replaced by 2, “the
  limit of his method”. Variants: $\omega(p)\sim cp$ is Szemerédi;
  $\omega(p)\le c\log p$ is Dirichlet on Bohr sets. $\mathbb F_2^n$
  is easy by averaging. A positive answer would not automatically
  improve Green #31.
- Shakan, *A large gap in a dilate of a set*,
  [arXiv:2004.14828](https://arxiv.org/abs/2004.14828),
  SIAM J. Discrete Math. 34 (2020), 2553–2555. Theorem 1:
  $$
    \sup_{d\in\mathbb F_p^\times} g(d\cdot A)\;\ge\; 2p/|A|-2
    \qquad(|A|>1).
  $$
  SIAM “Cited By” empty. No later improvement of the leading 2 found.
- The list id `arXiv:2205.14038` is **not** this paper (Jiang–Cai–Wu
  et al., quant-ph). Formal-conjectures #1588 is a Lean ticket only.
- Korsky, arXiv:2606.01780, is hitting $k$-APs in $[N]$ at
  $k=\sqrt N$, a different ambient.

Published record I must beat: **Shakan’s universal 2**.
I did not beat it.

## Published bound

| constant | meaning | reference |
| --- | --- | --- |
| 1 | pigeonhole, $g(A)\ge p/\|A\|-1$ | trivial |
| 2 | some dilate misses $2p/\|A\|-2$ | Shakan 2020 |
| 100 | Green’s asked-for constant at $\|A\|\sim\sqrt p$ | open |

For $|A|=\lfloor\sqrt p\rfloor$, Shakan is a gap of $2\sqrt p-2$.

## Independent checks (this folder)

```bash
python3 compute/verify.py
compute/.venv/bin/python compute/verify_sat_witnesses.py
compute/.venv/bin/python compute/enum_diagonal.py
```

- `verify.py` — PASS. Shakan holds on every nonempty proper subset of
  $\mathbb F_p$ for $p=5,7,11,13$, and on squares / equal / geom /
  subgroup / random constructions for all primes $5\le p\le 80$.
  `max_d g(dA)` agrees with the longest AP in the complement.
- `verify_sat_witnesses.py` — PASS. Every SAT witness in
  `certs/sat_G.jsonl` recomputes to the claimed $G$.
- `enum_diagonal.py` — PASS. Brute-force $G(p,\mathrm{round}\sqrt p)$
  matches SAT for every prime $5\le p\le 41$.

## What we computed (residue, not a bound)

Exact $G(p,n)=\min_{|A|=n}\max_d g(dA)$ for $n=\mathrm{round}\sqrt p$,
primes $p\le 71$, by SAT (hits-every-$T$-AP), Glucose4:

| p | n | G | 2p/n−2 | G/(p/n) | G/√p |
| --- | --- | --- | --- | --- | --- |
| 17 | 4 | 9 | 6.50 | 2.118 | 2.183 |
| 23 | 5 | 11 | 7.20 | 2.391 | 2.294 |
| 31 | 6 | 13 | 8.33 | 2.516 | 2.335 |
| 47 | 7 | 18 | 11.43 | 2.681 | 2.626 |
| 53 | 7 | 22 | 13.14 | 2.906 | 3.022 |
| 71 | 8 | 26 | 15.75 | 2.930 | 3.086 |

On this range $G/\sqrt p$ lives in $[2.18,3.09]$ and extra above
Shakan is order $n$. That is compatible with a hidden leading 3 and
compatible with slack that returns to 2. It is not a universal $C>2$.

Fixed $n$: $G(p,3)/(p/3)=2.76$ at $p=199$ and still rising, as
Dirichlet predicts ($G=p-\Theta(\sqrt p)$, ratio $\to 3$).
$G(p,4)/(p/4)=2.97$ at $p=97$.

Upper bounds: local search gives ratios $3.0$–$3.5$ for
$p\le 113$. Singer matches SAT at $p=13,31$ and then has ratio
$5.28$ at $p=307$. No family with $\max_d g\le(2+\varepsilon)\sqrt p$.

## What the method cannot do

Write $m=\sup g(dA)+1$, $\chi(t)=\prod_{a\in A}(t+a)$,
$k=nm-p+1$. Shakan produces $\chi^m=t^pg+h$ with
$\deg g,\deg h\le k$, then $\chi^{m-1}\mid(h'g-hg')$. The degree
comparison is $nm\ge 2p-O(n)$. For $m=Cp/n$ and $C>2$ the
range of “middle” coefficients of $\chi^m$ is empty, so the slice
imposes no condition. Ordinary vs discrete derivatives, or
$\deg W\le 2k-2$, change only $O(1)$. The interval in the original
product $w(d,t)=d\prod(t+j+da)$ is lost in the top homogeneous part.

## 2026-08-27 compute (still residue)

```bash
sh compute/run_all.sh
cd compute/q1 && ./run_all.sh
```

- Rising $w$ at $p=11,13$ and $m=G+1$: remainder 0, Alon degrees of
  $u,v$ equal $k=nm-p+1$. Cert: `compute/q1/certs/wronskian_slice.json`.
- SAT upper bounds, Glucose4 walk, hard 60–90s kill:
  $G(73,9)\le 24$, $G(79,9)\le 26$, $G(83,9)\le 27$,
  $G(89,9)\le 30$. Cadical: $T=23$ UNSAT at $p=73$ in 54s, so
  $23\le G(73,9)\le 24$; $T=24$ timed out on Glucose4, Glucose42,
  Cadical. Certs: `compute/q1/certs/sat_extend.jsonl`,
  `sat_alt_73.jsonl`. Not an exact census past $p=71$.
- Constructions through $p=199$: best diagonal ratios $3.3$–$5.3$
  past $p=50$. No family at $2+\varepsilon$.
  `compute/q1/certs/constructions_best.json`.

## Did not beat

- Shakan’s universal leading constant 2.
- Green’s asked-for 100, or any fixed $C>2$, for all large $p$ and
  $|A|\sim\sqrt p$.
- A construction showing that 2 is sharp.
- A use of the rising-factorial structure that improves the Wronskian
  degree.
- An exact $G$ row past $p=71$ that lifts to an infinite family.
