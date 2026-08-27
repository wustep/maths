# Small-Z replay — q4

Nothing here is a dent. Best published integer bound at
$Z=2,\ldots,6$ is still Lieb $N_c\le 2Z$.

The q3 leading dent $N_c<1.1118Z+3.966\,Z^{1/3}$ ($Z\ge 4$) tightens
the printed HPS simplified envelope as reals but excludes no extra
integer $N$ beyond Lieb, Nam, and the HPS printed lines.

Hydrogen uniqueness $N_0(1)=2$ is Lieb 1984 and is not claimed.

Replay:

```
python3 problems/simon-ionization-excess/compute/q4/work/smallz_replay.py
```

Certificate: `compute/q4/certs/smallz.json`.

## Published envelopes at $Z=2,\ldots,6$

Same arithmetic as q3 `work/smallz_replay.py`, now with the q3 simplified
column. Integer exclusion: $N_c<U$ means at most the largest integer
strictly below $U$.

| $Z$ | Lieb | Nam | HPS $s=2$ printed / q1 | HPS $s=3$ printed / q1 | HPS simp. printed / q1 | q3 simp. | best integer | unsettled |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2 | 5 | 6.219763 | 6.143580 / 6.134760 | n/a | n/a | n/a | $N_c\le 4$ | $2,3,4$ |
| 3 | 7 | 7.986749 | 7.890379 / 7.880283 | n/a | n/a | n/a | $N_c\le 6$ | $3,\ldots,6$ |
| 4 | 9 | 9.642203 | 9.527134 / 9.516022 | 10.801690 / 10.788991 | 10.823604 / 10.788840 | 10.742833 | $N_c\le 8$ | $4,\ldots,8$ |
| 5 | 11 | 11.229928 | 11.097063 / 11.085093 | 12.388782 / 12.375102 | 12.432404 / 12.394955 | 12.340765 | $N_c\le 10$ | $5,\ldots,10$ |
| 6 | 13 | 12.771362 | 12.621318 / 12.608598 | 13.917968 / 13.903431 | 13.979482 / 13.939687 | 13.877500 | $N_c\le 12$ | $6,\ldots,12$ |

At every $Z\ge 4$, the q3 simplified $U$ sits below the printed HPS
simplified $U$ and above $2Z+1$, so its integer cap matches Lieb
($N_c\le 2Z$). **No extra integer is excluded** by the q3 dent beyond
what Lieb, Nam, and the HPS printed envelopes already leave open.

Nam states that $1.22Z+3Z^{1/3}<2Z+1$ when $Z\ge 6$. HPS states that
Prop. 2.4 improves Lieb for $Z>5.3$. Both hold as real comparisons at
$Z=6$, and both still have $U>12$.

Zhislin gives $N_0(Z)\ge Z$.

## One finite-$Z$ try

**Nam Lemma 1 at the Lieb edge.** Plug $N=2Z$ (the largest integer
still allowed by Lieb at each $Z$) into Nam Lemma 1,
$\alpha_N(N-1)<Z(1+0.68\,N^{-2/3})$, using published lowers
$\max\{1/2,\mathrm{Prop.\,1},\sqrt5/4\}$ on $\alpha_N$. At
$Z=2,\ldots,6$ the lower side stays below the Lemma-1 right-hand side;
same at the unsettled candidates $N=3,4$ for $Z=2$. No contradiction.

**Four-electron Hylleraas-style comparison for $Z=2$, $N=4$.** The
separated trial He (exact Hylleraas $-54353/18800$) plus two hydrogen
$1s$ electrons at infinity gives a legal variational upper bound
$E(4,2)\le -54353/18800-1\approx -3.891$. The q1 hydrogenic
$1s^22s$ three-electron upper is about $-7.289$. The separated
four-electron upper sits above that three-electron upper, but comparing
two variational uppers does not prove $E(4,2)\ge E(3,2)$ and therefore
does not prove non-binding at $N=4$. A compact Hylleraas$\times$outer
product omitting core–outer repulsion is invalid (energy too negative).

Pair geometry and Temple/tetrahedron routes are not repeated here (q2–q3).

## $N_0(Z)-Z$

Cannot move this session. No verified integer envelope beats Lieb at a
concrete $Z>1$. The q3 leading dent is asymptotic ($Z\ge 4$) and does
not tighten integer caps. A leading coefficient $>1$ cannot prove a
$Z$-independent excess bound on $N_0(Z)-Z$.

## Status

Residue. No verifier-plus-certificate beats a published integer
envelope at a concrete $Z>1$.

$$
N_c(2)\le 4,\quad N_c(3)\le 6,\quad N_c(4)\le 8,\quad N_c(5)\le 10,\quad N_c(6)\le 12.
$$
