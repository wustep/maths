# Research log — a smaller constant in the two-squares gap

## Status (accessed 2026-08-17)

- [Green, *100 Open Problems*, Problem 66](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf)
  (Dec 2025): “Is there always a sum of two squares between
  $X-\tfrac1{10}X^{1/4}$ and $X$?” Still open. Comments point to
  Littlewood (Problem 2), Montgomery, and Erdős 1957 Problem 15.
  Green–Lindqvist give two almost-equal squares in the same
  $O(X^{1/4})$ scale. No later coefficient is recorded.
- The proposed-50 pointer “Erdős #143” is a **numbering error**.
  Bloom #143 is primitive-set sparsity. The matching page is
  **[Erdős Problem #222](https://www.erdosproblems.com/222)**
  (accessed 2026-08-17; cites [Er57], [Er61]). **OPEN**, “cannot be
  resolved with a finite computation”. Zero comments, zero claimed
  proofs. Differences listed at OEIS [A256435](https://oeis.org/A256435).
- Erdős, *Some unsolved problems*, Michigan Math. J. 4 (1957), Problem 15:
  Bambah–Chowla give $a_{k+1}-a_k=O(a_k^{1/4})$; “it has not yet been
  shown that the $O$ can be replaced by $o$”.

Do not claim the Landau–Ramanujan density.

## Published explicit upper bounds on $G(n)$

Write $G(n)=\min\{s-n:s\ge n,\ s=a^2+b^2\}$ (non-negative squares,
$0$ allowed). Consecutive differences of two-squares are the same
sequence, so Green’s backward interval is the same constant.

| bound | range | source |
| --- | --- | --- |
| $G(n)<\alpha n^{1/4}$ for every $\alpha>2\sqrt{2}$ | all large $n$ | Bambah–Chowla 1947 |
| $G(n)<2\sqrt{2}\,n^{1/4}+1$ | all $n\ge 1$ | arithmetic form, Shiu 2013/2019 |
| $G(n)<2\sqrt{2}\,n^{1/4}-1$ | all large $n$ | Uchiyama 1964 |
| $G(n)<2\sqrt{2}\,n^{1/4}-2$ | all $n\ge 1$ | Jameson, Math. Gaz. 103 (2019) |
| $G(n)<2\sqrt{2}\,n^{1/4}-3$ | **open** | Shiu, Integers 19 (2019) |
| any $\alpha<2\sqrt{2}$ | **open** | Shiu: “insurmountable” for 70+ years |
| $C=1/10$ for all large $X$ | **open** | Green #66 / Littlewood |

Log-scale lower bounds (Richards $1/4$; Dietmann–Elsholtz–Kalmynin–
Konyagin–Maynard $0.868\cdots$) do not move the $X^{1/4}$
coefficient.

## What we certified

**Theorem.** $G(n)<2\sqrt{2}\,n^{1/4}-3$ for every integer
$n$ with $2\le n\le 1.024\cdot 10^{15}$, except
$n\in\{3,6,21,91\}$.

- $n=1$ makes the right-hand side negative ($2\sqrt{2}-3<0$);
  excluded.
- The four exceptions are exact, with
  $G(3)=1,\;G(6)=2,\;G(21)=4,\;G(91)=6$. Each satisfies Jameson’s
  $a=2$ and fails $a=3$ by the integer test
  $(G+3)^4\ge 64n>(G+2)^4$.
- Independently, an exhaustive two-square table shows that these
  (plus $n=1$) are the **only** $a=3$ failures on $[1,5\cdot 10^6]$,
  and that Jameson’s $a=2$ has **no** failure on that range.

This is a computer-assisted improvement of the published additive
constant $-2$ (Jameson) to $-3$ (Shiu’s next open increment),
on an explicit range. It is **not** a proof for all large $n$, and
it is **not** Green’s $1/10$.

Independently verified stored witnesses: every danger-zone top with
$m\le 2000$ (so all $n\le 4\cdot 10^{12}$ in the classification),
file `compute/a3_cert_m2000.json.gz`. The same searcher reports
zero unsaved tops for $m\le 8000$, which is the $1.024\cdot 10^{15}$
range.

## Classification (integer)

Let $u=\lfloor\sqrt n\rfloor$, $\mathrm{rem}=n-u^2$, write
$\mathrm{rem}=m^2+\ell$ with $0\le\ell\le 2m$. The Bambah–Chowla
point is $(u,v)$ with $v=\lceil\sqrt{\mathrm{rem}}\rceil$.
Set $h=u^2+v^2-n$ and $h_2=(u+1)^2-n$. Then
$G(n)\le\min(h,h_2)$, and two-point $a=3$ fails if and only if
$(\min(h,h_2)+3)^4\ge 64n$ (equivalently $\min(h,h_2)\ge\Phi-3$
with $\Phi=2\sqrt{2}\,n^{1/4}$).

Shiu’s ladder lemma: after the two zeros at the start of $I_u$,
the values of $h$ form descending unit steps of length $2m$.
The **top** of the $m$-th ladder is $n_0=u^2+m^2+1$ ($\ell=1$),
with $h=2m$ and $h_2=k:=2u-m^2$. Rung $t\ge 1$ has
$n=n_0+t$, leftovers $2m-t$ and $k-t$.

Integer bounds, for $n\ge 2$:

1. If $\ell=0$, then $n$ itself is a two-square and $G(n)=0$.
   For $n\ge 2$ one has $\Phi-3>0$, so $a=3$ holds.
2. If $k\le 2m-3$, then $\min\le 2m-3$ and
   $(\min+3)^4\le(2m)^4=16m^4<64n$, so two-point $a=3$ holds.
3. If $k\ge 3m+3$, then $\min=2m$ and
   $64n\ge 16(m^2+3m+3)^2+64m^2+64>(2m+3)^4$, so two-point $a=3$ holds.
4. If $t\ge 1$ and $k\in[2m-2,3m+2]$, write $\mu=\min(2m,k)$.
   Direct expansion gives $(\mu+2)^4<64(n_0+1)$ in each of the
   three subcases $k=2m-2$, $k=2m-1$, $k\ge 2m$. So no rung
   $t\ge 1$ is a two-point $a=3$ failure.

Thus every two-point $a=3$ failure with $n\ge 2$ is a ladder top
$n=u^2+m^2+1$ with $2u=m^2+k$ and $2m-2\le k\le 3m+2$.
On that set, $a=3$ is exactly the existence of some lattice point
with leftover in $\{0,1,\dots,W\}$, $W=\max\{w:(w+3)^4<64n\}$.

Also $m\le\lfloor\sqrt{2u}\rfloor\le\lfloor\sqrt{2}\,n^{1/4}\rfloor$.
So $m\le 8000$ covers every integer $n\le(8000/\sqrt{2})^4=1.024\cdot 10^{15}$.

## The four exceptions

| $n$ | previous | next | $G(n)$ | $(G+3)^4$ | $64n$ | $(G+2)^4$ |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 2 | 4 | 1 | 256 | 192 | 81 |
| 6 | 5 | 8 | 2 | 625 | 384 | 256 |
| 21 | 20 | 25 | 4 | 2401 | 1344 | 1296 |
| 91 | 90 | 97 | 6 | 6561 | 5824 | 4096 |

Each row has $(G+3)^4\ge 64n>(G+2)^4$.

## Green’s $1/10$

Not proved, and not disproved for all sufficiently large $X$.

A gap census through $N=2\cdot 10^7$ (generate every two-square,
no density claim):

- running-max of $(s_{k+1}-s_k)/s_{k+1}^{1/4}$ is $15/1508^{1/4}\approx 2.407$,
  attained at the empty ladder $38^2+7^2=1493$ to $38^2+8^2=1508$;
- that is $0.851$ of the Bambah–Chowla coefficient $2\sqrt{2}$;
- $1.526\cdot 10^6$ consecutive pairs still exceed $1/10$, including
  at $X=2\cdot 10^7$ itself (gap $7>0.1\cdot(2\cdot 10^7)^{1/4}\approx 6.69$).

Richards-type gaps of size $\asymp\log X$ live at $X=\exp(\Theta(k))$
and are far below $X^{1/4}$ at that scale; they do not produce
infinite-family counterexamples to $1/10$. Isolated gap tables are
not a bound. We do not claim that the running-max ratio tends to $0$.

## Replay

See `compute/README.md`. The integer test $(G+3)^4<64n$ never uses
floating $\Phi$ in the certificate checker.

## Sources fetched

- Green, *100 Open Problems*, Problem 66, Dec 2025 PDF.
- Erdős, Michigan Math. J. 4 (1957), Problem 15 (scan).
- Bloom, Erdős Problem #222, 2026-08-17.
- Bambah–Chowla, Proc. Nat. Inst. Sci. India 13 (1947), via Shiu’s
  arithmetic transcription.
- Shiu, Math. Gazette 97 (2013); Integers 19 (2019) #A48.
- Jameson, Math. Gazette 103 (2019), as cited by Shiu.
- Uchiyama, J. Fac. Sci. Hokkaido Univ. 18 (1964/5).
- Richards, Adv. Math. 1982; Dietmann–Elsholtz arXiv:1810.03203v2
  and the IMRN 2023 constant quoted on Bloom #222.
- Guo–Ilyin, J. Number Theory 2024; Iyer, arXiv:2503.15789 (2025).
