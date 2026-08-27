# Small-Z residue — q3

Nothing here is a dent. Best published integer bound at
$Z=2,\ldots,6$ is still Lieb $N_c\le 2Z$.

Hydrogen uniqueness $N_0(1)=2$ is Lieb 1984 and is not claimed.

Replay:

```
python3 problems/simon-ionization-excess/compute/q3/work/smallz_replay.py
python3 problems/simon-ionization-excess/compute/q3/work/smallz_check.py
```

Opened this session: Nam
[1009.2367v3 HTML](https://arxiv.org/html/1009.2367v3),
HPS [2504.18487v1 HTML](https://arxiv.org/html/2504.18487v1)
Prop. 2.4–2.5 and (7.10),
BGB [2511.07582v1 HTML](https://arxiv.org/html/2511.07582v1)
(only for $Z\ge 12$).

## Published envelopes at $Z=2,\ldots,6$

Same arithmetic as q2 `envelopes.py`, now including $Z=6$.
Integer exclusion: $N_c<U$ means at most the largest integer
strictly below $U$.

| $Z$ | Lieb | Nam | HPS $s=2$ printed / q1 | HPS $s=3$ printed / q1 | best integer | unsettled |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 2 | 5 | 6.219763 | 6.143580 / 6.134760 | n/a | $N_c\le 4$ | $2,3,4$ |
| 3 | 7 | 7.986749 | 7.890379 / 7.880283 | n/a | $N_c\le 6$ | $3,\ldots,6$ |
| 4 | 9 | 9.642203 | 9.527134 / 9.516022 | 10.801690 / 10.788991 | $N_c\le 8$ | $4,\ldots,8$ |
| 5 | 11 | 11.229928 | 11.097063 / 11.085093 | 12.388782 / 12.375102 | $N_c\le 10$ | $5,\ldots,10$ |
| 6 | 13 | 12.771362 | 12.621318 / 12.608598 | 13.917968 / 13.903431 | $N_c\le 12$ | $6,\ldots,12$ |

Nam states that $1.22Z+3Z^{1/3}<2Z+1$ when $Z\ge 6$. HPS states
that Prop. 2.4 improves Lieb for $Z>5.3$. Both hold as real
comparisons at $Z=6$, and both still have $U>12$, so they exclude
no extra integer. BGB’s formula at $Z=6$ is about $14.61>13$ and
is not applicable.

Zhislin gives $N_0(Z)\ge Z$.

## One finite-$Z$ try

HPS Prop. 2.4 maximises the remainder $a(x)$ on $N/Z\le 5/2$.
At a fixed $Z$, Lieb is $N/Z<2+1/Z$. That $a(2+1/Z)$ is increasing
for $x>0.81$, so the max is the right endpoint. The $Z$-local
envelope $b(2)Z+a(2+1/Z)\,Z^{1/3}$ is $10.964878$ at $Z=5$ and
$12.466731$ at $Z=6$: below $2Z+1$ as reals, still above $2Z$.
Same integers as Lieb.

Direct HPS (7.10) and the $s=2$ form (7.6) at the Lieb edge
$N=2Z$, using q1’s $\lambda\approx 0.628336$ for $s=2$ (printed
$0.6284$ is weaker): no contradiction. Closest gap is $Z=6$,
$N=12$: $N\beta_2\approx 9.941<10.269$.

Nam Lemma 1 / Prop. 1 likewise: published $\alpha$ lowers sit
below the kinetic right-hand side (at $Z=6$, $N=12$ about
$6.321<6.778$).

Pair geometry, kinetic dropped. Tetrahedron still blocks $N=4$
at $Z=2$ ($54<64$). Five vertices of the regular octahedron give

$$\alpha_{5,2}\le(4\sqrt{2}+1)/10,\qquad \alpha_{5,2}\cdot 4<3$$

because $128<169$: the $s=2$ pair ratio cannot exclude $N=5$ at
$Z=3$.

The full octahedron has $5\alpha_{6,2}>3$ ($8>25/4$); a prism
scan stays above $0.6$. Not a dent.

## Status

Residue. No verifier-plus-certificate beats a published integer
envelope at a concrete $Z>1$.

$$
N_c(2)\le 4,\quad N_c(3)\le 6,\quad N_c(4)\le 8,\quad N_c(5)\le 10,\quad N_c(6)\le 12.
$$
