# Attack log — a smaller constant in the two-squares gap

## 2026-08-17 — literature (do not claim Landau–Ramanujan)

Fetched, in order:

- Green, *100 Open Problems* (Dec 2025 update), Problem 66:
  “Is there always a sum of two squares between $X-\tfrac1{10}X^{1/4}$
  and $X$?” Comments: Littlewood’s list (Problem 2), Montgomery’s
  list, and Erdős, *Some unsolved problems*, Michigan Math. J. 4 (1957),
  Problem 15. Elementary $O(X^{1/4})$ by subtracting two successive
  largest squares. Green–Lindqvist give two *almost equal* squares in
  the same $O(X^{1/4})$ scale. No later update on the constant.
- The proposed-50 pointer “Erdős Problem #143” is a **numbering error**.
  Bloom #143 is the primitive-set sparsity problem. The matching Bloom
  page is **[Erdős Problem #222](https://www.erdosproblems.com/222)**
  (accessed 2026-08-17; cites [Er57] and [Er61]). Status: **OPEN**,
  “cannot be resolved with a finite computation”. Zero comments, zero
  claimed proofs.
- Erdős 1957, Problem 15 (fetched the Michigan Math. J. scan): if
  $(a_k)$ is the increasing sequence of sums of two squares, Bambah–
  Chowla give $a_{k+1}-a_k=O(a_k^{1/4})$; “it has not yet been shown
  that the $O$ can be replaced by $o$”. Lower bound
  $a_{k+1}-a_k>c(\log a_k)/\log\log a_k$ infinitely often.
- Bambah–Chowla, *Proc. Nat. Inst. Sci. India* 13 (1947): if
  $\alpha>2\sqrt{2}$ then for all large $n$ there are $u,v$ with
  $n\le u^2+v^2<n+\alpha n^{1/4}$. Arithmetic form (Shiu 2013/2019):
  $u=\lfloor\sqrt n\rfloor$, $v=\lceil\sqrt{n-u^2}\rceil$ gives
  $n\le u^2+v^2<n+2\sqrt{2}\,n^{1/4}+1$ for every $n\ge 1$.
- Uchiyama 1964: the $+1$ may be replaced by $-1$.
- Jameson, Math. Gazette 103 (2019): replaced by $-2$.
- Shiu, Integers 19 (2019), #A48: even $a=3$ (i.e.
  $n\le u^2+v^2<n+2\sqrt{2}\,n^{1/4}-3$) is open, and he produces an
  infinite family of $n$ on which both the Bambah–Chowla point and
  $(u+1)^2$ fail $a=3$. Under a fractional-part hypothesis on
  $\sqrt{2up+v^2-p^2}$ he would get *every* $\alpha>0$.
- Richards 1982: $\limsup(s_{n+1}-s_n)/\log s_n\ge 1/4$.
- Dietmann–Elsholtz–Kalmynin–Konyagin–Maynard, IMRN 2023 (arXiv:1810.03203):
  the log-scale constant is at least $195/449\approx 0.434$ in the
  arXiv v2 writeup; Bloom #222 quotes the published improvement
  $0.868\cdots$. **Logarithmic gaps do not move the $X^{1/4}$
  coefficient.** Isolated gap tables are residue unless they force a
  new infinite-family bound at the $X^{1/4}$ scale.
- Guo–Ilyin, J. Number Theory 2024: empty annuli of width
  $\lambda^s$ for $s<1/4$; at $s=1/4$ the Bambah–Chowla scale
  already forces a lattice point. No new coefficient.
- Iyer, arXiv:2503.15789 (2025): generalises Bambah–Chowla to
  $x^\theta+y^\theta$; for $\theta=2$ restates $2\sqrt{2}\,x^{1/4}+1$.
  No smaller constant.

Published record I must beat, after the fetch:

| quantity | published |
| --- | --- |
| multiplicative $C$ in $G(n)<C n^{1/4}$ for all large $n$ | $C>2\sqrt{2}\approx 2.828427$ (Bambah–Chowla 1947) |
| explicit for every $n\ge 1$ | $G(n)<2\sqrt{2}\,n^{1/4}+1$ |
| best additive saving | $G(n)<2\sqrt{2}\,n^{1/4}-2$ (Jameson 2019) |
| Green / Littlewood target | $C=1/10$, unknown |
| limsup $G(s_k)/\log s_k$ | $\ge 0.868\cdots$ (DEKKM 2023) |

Here $G(n)=\min\{s-n:s\ge n,\ s=a^2+b^2\}$. Backward gaps
$n-s$ are the same sequence of consecutive differences, so Green’s
interval $[X-\tfrac1{10}X^{1/4},X]$ is the same constant.

Do not claim the Landau–Ramanujan density. Average-gap heuristics
are not a bound.

## 2026-08-17 — tonight’s handle

Three live handles, in order of what would count as a dent:

1. **Beat the published multiplicative constant.** A proof that
   $G(n)<\alpha n^{1/4}$ for some explicit $\alpha<2\sqrt{2}$ and
   all large $n$. Shiu calls this open for seventy-plus years.
2. **Beat Jameson’s additive $-2$.** Prove $a=3$:
   $G(n)<2\sqrt{2}\,n^{1/4}-3$ for all large $n$. Shiu isolates
   the obstruction as an infinite 1-parameter family
   $n=u^2+m^2+1$ with $m$ even and $2u+1=(m+1)^2$. On that
   family both the BC-point and $(u+1)^2$ sit at $n+2m$, while
   $2m+2<\Phi_n<2m+3$, so $a=3$ is exactly the statement that
   $(u^2+m^2,\,u^2+(m+1)^2)$ contains another two-square.
3. **Infinite-family lower bound at the $X^{1/4}$ scale.** If that
   same interval is empty for infinitely many even $m$, then
   $\limsup G(n)/n^{1/4}=2\sqrt{2}$ and Bambah–Chowla is sharp;
   in particular Green’s $1/10$ fails for infinitely many $X$.
   Isolated empty intervals are residue unless the emptiness is
   infinite.

Starting with (2) and (3) on the Shiu family, then a certified
replay of the elementary $2\sqrt{2}$ bound, then a gap census.

## 2026-08-17 — numbering correction, recorded

Erdős 1957 Problem 15 = Bloom #222, not #143. Green #66 is the
explicit-constant form of the same question. Work continues under
the house folder `two-squares-gap`.

## 2026-08-17 — elementary replay

`verify_bc.py --N 100000`: Bambah–Chowla leftover never meets
$\Phi+1$. Two-point $a=2$ never fails. Two-point $a=3$ fails
on 172 values; the sample is ladder tops
$1,3,6,21,30,59,\dots,161$ (Shiu shape).

## 2026-08-17 — Shiu family is occupied

Even $m\le 8000$, family $2u+1=(m+1)^2$, $n=u^2+m^2+1$:
the open interval $(u^2+m^2,u^2+(m+1)^2)$ is empty only for
$m=2$ ($n=21$). Occupied thereafter. Least $p=u-u'$ that
saves the interval has maximum $40$, at Shiu’s example $m=2862$.
No infinite-family sharpness of $2\sqrt{2}$ from this curve.

## 2026-08-17 — third-point hunt

`hunt_a3.py` on $n\le 2\cdot 10^5$: 239 two-point $a=3$ failures,
235 saved, **4 unsaved: 3, 6, 21, 91**. Ladder enumerator through
$u=20000$ ($n\le 4\cdot 10^8$): still those four. Every saved
failure has rung $t=0$.

## 2026-08-17 — integer classification

Two-point $a=3$ fails $\Leftrightarrow(\min(h,h_2)+3)^4\ge 64n$.
Expansions: rungs $t\ge 1$ never fail; $k\le 2m-3$ and
$k\ge 3m+3$ never fail. Obstruction = ladder tops with
$k\in[2m-2,3m+2]$. And $m\le\sqrt{2}\,n^{1/4}$.

## 2026-08-17 — danger-zone search

`certify_a3.py`:

| $M$ | tops | unsaved | $n\le(M/\sqrt{2})^4$ |
| ---: | ---: | ---: | ---: |
| 250 | 15 993 | 0 | $9.8\cdot 10^8$ |
| 2000 | 1 002 993 | 0 | $4\cdot 10^{12}$ |
| 4000 | 4 005 993 | 0 | $6.4\cdot 10^{13}$ |
| 8000 | 16 011 993 | 0 | $1.024\cdot 10^{15}$ |

Stored witnesses for $M=250$ and $M=2000$ pass
`verify_a3_cert.py` (rebuilds $n$ from $(m,k)$, checks
$a^2+b^2=s$ and $(s-n+3)^4<64n$).

## 2026-08-17 — exhaustive table

`verify_exhaustive.py --N 5000000`: generate every two-square,
set $G(n)=$ next one minus $n$. Failures of $a=3$:
exactly $\{1,3,6,21,91\}$. Failures of $a=2$: none.

## 2026-08-17 — gap census (residue, not a bound)

Through $N=2\cdot 10^7$, max $(s_{k+1}-s_k)/s^{1/4}$ is
$2.407$ at $1493\to 1508$. Green’s $1/10$ is still crossed
at $X=2\cdot 10^7$. Not a large-$X$ counterexample scheme;
Richards gaps are the wrong scale. Plot: `figures/gap_ratios.png`.

## 2026-08-17 — what we will claim

A certified improvement of Jameson’s published additive $-2$ to
$-3$, for all $2\le n\le 1.024\cdot 10^{15}$ except
$\{3,6,21,91\}$. Not Green’s $1/10$. Not a multiplicative
$\alpha<2\sqrt{2}$. Not $a=3$ for every large $n$.
Do not claim Landau–Ramanujan.
