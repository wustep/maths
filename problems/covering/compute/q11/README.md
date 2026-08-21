# q11 — the fibered "graph plus kernel" family

New in quest q11 (2026-08-21).  Nothing here reruns q2/q4 (SA, guided, lifted,
k-swap, invariant orbit DFS), q9 (quotient-block replacement) or q10
(prescribed automorphisms).  `result/` is read only.

q9 replaced one quotient block of the certified 50-set at a time; q10 searched
sets invariant under a prescribed automorphism.  Both are anchored to a
*set*.  This quest is anchored to a *fibration*: it fixes a splitting of
$\mathbb F_2^r$ and prescribes how many columns sit over each point of the
quotient.  The extreme profile — one column over every nonzero quotient point,
everything else in the kernel — turns out to be a single family that contains
the documented records at $r=4,5,6,7,8,9$, and it is decidable by hand at
$r\le 8$.

## 1. The family

Split $\mathbb F_2^r = V \oplus W$ with $\dim V = F$ (the *fibre*),
$\dim W = M$ (the *base*), $r = F+M$.  Pick $A \subseteq V\setminus\{0\}$ and
$g : W\setminus\{0\} \to V$ and take the column set

$$S \;=\; \{(v,0) : v \in A\} \;\cup\; \{(g(u),u) : u \in W\setminus\{0\}\},
\qquad n = |A| + 2^M - 1 .$$

Every nonzero fibre carries exactly one column, so the length is pinned by $M$
and by $|A|$ alone.  Sorting the covering condition
$\{0\}\cup S\cup(S+S)=\mathbb F_2^r$ by fibre gives exactly two conditions:

* **fibre $0$:**  $\{0\}\cup A\cup(A+A) = V$, i.e. $A$ is 1-saturating in $V$
  (so $|A| \ge \ell_2(F,2)$);
* **fibre $u \ne 0$:**  $B + g(u) \subseteq D_u$, where
  $B := V \setminus (A\cup\{0\})$ and
  $D_u = \{\,g(w)+g(w+u) : w \notin \{0,u\}\,\}$.

Note $n = 2^F - 1 - |B| + 2^M - 1$: **the family's length is decreasing in
$|B|$**, so the whole question is how large $|B|$ can be made.

## 2. The line-colouring reformulation

The pair $\{w,w+u\}$ and the point $u$ span the same plane
$\{0,w,w+u,u\}$, i.e. the same **line** of $\mathrm{PG}(M-1,2)$, and

$$g(w)+g(w+u) \;=\; \tau(\ell) + g(u), \qquad
\tau(\ell) := g(a)+g(b)+g(a+b) \ \text{ for } \ \ell=\{a,b,a+b\}.$$

So $\tau$ is a colouring of the $\frac{(2^M-1)(2^{M-1}-1)}{3}$ lines of
$\mathrm{PG}(M-1,2)$ by $V$ ($\tau$ is the symmetric 2-cocycle of $g$; it is
constant on the three point-pairs of a line, which is why it is a function of
the line), and, writing $C_u = \{\tau(\ell) : \ell \ni u\}$, the fibre
condition becomes

> $$B \subseteq C_u \quad\text{for every point } u \text{ of } \mathrm{PG}(M-1,2).$$

Equivalently: **each colour class $L_b=\tau^{-1}(b)$, $b\in B$, is a set of
lines covering every point**, and the classes are disjoint.  A shear
$(v,u)\mapsto(v+K(u),u)$ with $K$ linear preserves the family, fixes $A$ and
changes $g$ by a linear map, so $g$ may be normalised to vanish on a basis of
$W$; $\tau$ is exactly the shear-invariant part of $g$.

[`lines.py`](lines.py) checks this reformulation against the flat $2^r$ sweep on
every solution below; the two agree in every case.

## 3. Two exact obstructions

**Lemma A (quadratic $g$, $M$ odd).**  *If $M$ is odd and $\tau$ is bilinear
(equivalently $g$ is quadratic), then $B=\varnothing$.*

*Proof.*  Write $T$ for the bilinear form, $L_u = T(\cdot,u)$.  Then
$D_u = g(u) + (\operatorname{Im}L_u\setminus\{0\})$, so
$B \subseteq \operatorname{Im}L_u$ for every $u\ne0$.  Let
$\lambda \in V^{*}$ be nonzero.  Then $\lambda\circ T$ is an alternating form
on $W$, and $\dim W = M$ is odd, so it is degenerate: some $u_0\ne0$ lies in
its radical, i.e. $\lambda(T(w,u_0))=0$ for all $w$, i.e.
$\operatorname{Im}L_{u_0}\subseteq\ker\lambda$.  Hence $B\subseteq\ker\lambda$
for **every** nonzero $\lambda$, and $\bigcap_{\lambda\ne0}\ker\lambda=\{0\}$,
so $B=\varnothing$. $\square$

$r=10$ has $M=5$: the quadratic members of the family are empty there, and the
same holds at $r=6$ and $r=9$.  Consistently, `lines.py` reports
`tau-bilinear=False` for every solution found with $M$ odd, and the one
bilinear solution in the table below is the $M=2$ one.

**Lemma B (line-cover counting).**  *Let $c(M)$ be the least number of lines
covering all points of $\mathrm{PG}(M-1,2)$ and $L(M)$ the number of lines.
Then $|B| \le \min\bigl(\lfloor L(M)/c(M)\rfloor,\ 2^{M-1}-1,\ 2^F-1\bigr)$.*

The classes $L_b$ are disjoint covers, so $\sum_{b\in B}|L_b| \le L(M)$ and
each $|L_b|\ge c(M) \ge \lceil (2^M-1)/3\rceil$; the second term is the number
of lines through a point.  For $M=5$: $L=155$, $c=11$, so $|B|\le 14$ and

> at $r=10$ the family cannot produce any $n \le 47$,

which is sharper than the per-fibre floor $n\ge47$ that the counting alone
gives.  ($c(5)=11$ is attained: a maximal partial line spread of
$\mathrm{PG}(4,2)$ has 9 lines and its 4 holes are covered by 2 more lines.)

## 4. What the family actually gives

`graph_search.c` is an exact DFS over $g$ for a prescribed $A$ (shear-normalised,
with the per-fibre slack $2^{M-1}-1-|B|$ used as a waste budget);
`gen_asets.c` emits a $GL(F,2)$-reduced complete list of $A$-masks;
`sa_graph.c` anneals directly on the line-colouring objective ("make $k$ colours
common to every point"), which is what settles the larger cases.

| $r$ | $(F,M)$ | family best $n$ | $|B|$ | status of shorter lengths | documented record |
| --- | --- | --- | --- | --- | --- |
| 4 | (2,2) | **5** | 1 | $n\le4$ needs $\|A\|\le1$, not 1-saturating | $\ell_2(4,2)\le5$ |
| 6 | (3,3) | **13** | 1 | $n=11,12$ **exhausted** (all $A$) | — |
| 7 | (3,4) | **19** | 3 | $n=18$ needs $\|A\|=3$, not 1-saturating | GDT $f(7)=19$ |
| 8 | (4,4) | **26** | 4 | $n=23,24$ **exhausted** (all 6435 / 5005 $A$); $n=25$ **exhausted** (24 reduced $A$) | $\ell_2(8,2)\le26$ (Table 5.1) |
| 9 | (4,5) | **39** | 7 | $n=38$: colour condition satisfiable, fibre 0 never was — residue, not decided | GDT $f(9)=39$ |
| 10 | (5,5) | **54** | 8 | $n\le47$ **impossible** (Lemma B); $48\le n\le53$ not found, not decided | $\ell_2(10,2)\le50$ (q1) |
| 11 | (5,6) | 86 (short runs only) | 8 | $n=83$ reached cost 5, $n=79$ not reached | GDT $f(11)=79$ |

So one family reproduces the documented lengths at $r=4,7,8,9$ (and the
Gabidulin–Davydov–Tombak odd-$r$ values $f(7)=19$, $f(9)=39$) from a two-line
definition, and **cannot beat any of them**.  Explicit matrices, each replayed
by the independent C sweep `verify_H.c`:

* [`H_r4_n5_fibered.txt`](H_r4_n5_fibered.txt) — 16/16
* [`H_r6_n13_fibered.txt`](H_r6_n13_fibered.txt) — 64/64
* [`H_r7_n19_fibered.txt`](H_r7_n19_fibered.txt) — 128/128
* [`H_r8_n26_fibered.txt`](H_r8_n26_fibered.txt) — 256/256
* [`H_r9_n39_fibered.txt`](H_r9_n39_fibered.txt) — 512/512
* [`H_r10_n54_fibered.txt`](H_r10_n54_fibered.txt) — 1024/1024
* [`H_r11_n86_fibered.txt`](H_r11_n86_fibered.txt) — 2048/2048

### Why $r=10$ is the bad case for this family

At $r=2m+1$ the useful split is $(F,M)=(m,m+1)$: the base is one dimension
bigger than the fibre, each nonzero fibre gets $2^{m}-1$ pairs to cover $2^{m}$
targets, and there is room to spare — that is the shape of the classical
odd-$r$ formula.  At $r=2m$ the split has to be $(m,m)$, each fibre gets only
$2^{m-1}-1$ pairs for $2^{m}$ targets, and the deficit has to be paid by the
kernel block $A$, whose own $\binom{|A|}{2}$ sums are then almost entirely
wasted (at $r=10$, $|A|=18$ supplies 171 covers for 31 targets).  On top of
that, $M=5$ is odd, so Lemma A removes the quadratic members outright.  The
$r=10$ record 50 is **not** in this family, and the family's own best is 54.

### The $r=9$, $n=38$ residue

$n=38$ needs $|B|=8$ with $|A|=7$.  The colour condition alone is reachable —
the annealer hits cost 0 at $k=8$ routinely — but the eight colours common to
all 31 points never had a 1-saturating complement.  Of the recorded blocking
sets ([`fullsets_r9_k8.txt`](fullsets_r9_k8.txt), classified by
[`fullsets.py`](fullsets.py)) **29 of 29, 13 of them distinct, are affine
hyperplanes of $\mathbb F_2^4$** — and for those
$A = V\setminus(B\cup\{0\}) = H\setminus\{0\}$ for a hyperplane $H$, so
$A+A\subseteq H$ and fibre 0 cannot be covered, whatever $g$ does.

That is an observation about the sample, not a theorem: whether some $g$ makes
eight common colours that are *not* an affine hyperplane is **open**.  This is
search residue, not an exclusion, and $\ell_2(9,2)\le39$ stands.

$r=11$ ($M=6$, 63 free values of $g$) was only probed with short annealing
schedules and is the least explored row: the family reached $n=86$, and $n=83$
came within cost 5, but the record $n=79$ needs $|B|=15$ and was not reached.
Lemma A does not apply there ($M=6$ is even), so the quadratic members are the
obvious unexplored direction at $r=11$.

**None of this is a lower bound** on any $\ell_2(r,2)$.  The exclusions above
are exclusions *inside one family*.

## 5. Replay

    cd problems/covering/compute/q11
    gcc -O3 -o /tmp/gs  graph_search.c
    gcc -O2 -o /tmp/gen gen_asets.c
    gcc -O3 -o /tmp/sa  sa_graph.c -lm
    gcc -O2 -o /tmp/vh  verify_H.c
    sh run_q11_checks.sh
