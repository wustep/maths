# Small-Z residue — q2

Attempts at a certified finite-$Z$ bound on $N_0(Z)-Z$ for Simon
ionization excess. Nothing here is a dent. Hydrogen uniqueness
$N_0(1)=2$ is Lieb 1984 and is not claimed.

Replay: `problems/simon-ionization-excess/compute/q2/run_all.sh`.

Papers opened this session (record only):

- Hundertmark–Pattakos–Schulz, [arXiv:2504.18487v1 HTML](https://arxiv.org/html/2504.18487v1)
- Nam, [arXiv:1009.2367v3 HTML](https://arxiv.org/html/1009.2367v3)

## Published envelopes at $Z=2,3,4,5$

`envelopes.py` (mpmath) and `envelopes_check.py` (stdlib) replay the
printed inequalities and the q1 remainder tightening. Integer
exclusion is $N_c<U\Rightarrow N_c\le$ the largest integer strictly
below $U$.

At every one of these four charges the best published envelope is
Lieb $N_c<2Z+1$. Nam and both HPS forms (printed and q1) sit above
$2Z+1$, so they exclude no extra integer $N$.

| $Z$ | Lieb $U$ | Nam $U$ | HPS $s=2$ printed | HPS $s=2$ q1 | HPS $s=3$ printed / q1 | best integer | excludes | unsettled |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2 | 5 | 6.219763 | 6.143580 | 6.134760 | n/a ($Z<4$) | $N_c\le 4$ | $N\ge 5$ | $2,3,4$ |
| 3 | 7 | 7.986749 | 7.890379 | 7.880283 | n/a | $N_c\le 6$ | $N\ge 7$ | $3,4,5,6$ |
| 4 | 9 | 9.642203 | 9.527134 | 9.516022 | 10.801690 / 10.788991 | $N_c\le 8$ | $N\ge 9$ | $4,\ldots,8$ |
| 5 | 11 | 11.229928 | 11.097063 | 11.085093 | 12.388782 / 12.375102 | $N_c\le 10$ | $N\ge 11$ | $5,\ldots,10$ |

Zhislin binds for every $N<Z+1$, so $N_0(Z)\ge Z$. Combined with Lieb,
the only uniqueness in the published record at these charges is still
hydrogen. Precise decimals: `certs/envelopes.json`.

## Lieb-style weights

Nam's write-up of Lieb (HTML §2.1): multiply the eigenvalue equation
by $|x_N|\overline{\Psi}$, drop the non-negative $(H_{N-1}-E)$ and
weighted kinetic terms, then use the triangle
$(|x|+|y|)/|x-y|\ge 1$. That is $N<2Z+1$. The triangle is sharp along
opposite rays, so the pair geometry of $\varphi(x)=|x|$ cannot be
improved uniformly.

For a general weight $\varphi$, the same identity (kinetic dropped)
excludes $N$ at charge $Z$ if

$$
R_N(\varphi)=\inf\frac{\sum_{i<j}(\varphi(x_i)+\varphi(x_j))/|x_i-x_j|}{\sum_k\varphi(x_k)/|x_k|}>Z.
$$

For $\varphi(x)=|x|$ one has $R_N\ge(N-1)/2$, hence $R_4\ge 3/2<2$ and
$R_3\ge 1<2$. To exclude $N=4$ or $N=3$ at $Z=2$ one needs $R>2$.

`lieb_weights.py` minimises $R_3$ and $R_4$ for

- $\varphi=|x|^s$ ($s=1,1.25,1.5,2,3$),
- $\varphi=|x|/(1+\lambda|x|)$,
- $\varphi=1-e^{-\alpha|x|}$,
- $\varphi=|x|e^{-\mu|x|}$,
- $\varphi=\min(|x|,\rho)$,
- a $C^1$ compact cutoff $|x|\,\eta(|x|/\rho)$.

A search minimum is an *upper* bound on $\inf R$. The power family
reproduces the equilateral / tetrahedron values ($R_3=2/\sqrt{3}\approx 1.155$,
$R_4=3\sqrt{6}/4\approx 1.837$), both below $2$. The screened and compact
families degenerate: the optimiser pushes mass where $\varphi$ vanishes
and $R$ collapses toward $0$, which is still $R\le 2$. Those weights
therefore cannot exclude $N=3$ or $N=4$ at $Z=2$. Kinetic positivity is
proved in the literature only for $\varphi=|x|^b$, $b\in[0,1]$ (Lieb;
Chen–Siedentop); it was not used as a bound for the other families.

## Nam / HPS at small $N$

Nam Lemma 1: $\alpha_N(N-1)<Z(1+0.68\,N^{-2/3})$.
Nam Proposition 1: $\alpha_N\ge\frac{N}{N-1}\bigl[\beta-3(\beta/6)^{1/3}N^{-2/3}\bigr]$
with $\beta\ge 0.8218$. At $N=4$ the remainder already exceeds $\beta$,
so that lower bound is weaker than the triangle $1/2$.

Nam's $\sqrt5/4$ for $N\ge 3$ gives $\alpha_4\cdot 3\le 3\sqrt5/4\approx 1.677<2$.
Even with the kinetic term dropped this does not exclude $N=4$ at $Z=2$.
Excluding $N=3$ at $Z=2$ would need $\alpha_3>1$, which is impossible
because $\alpha_N\le\beta<0.8705$.

HPS (7.10) at $Z=2$, $N=4$: $N\beta_2\approx 3.31$ versus a right-hand
side $\approx 5$ (the $N^{1/3}$ remainder is $\sim 2.5$). No
contradiction. Same at $Z=3,4,5$ for $N$ still allowed by Lieb.
Dump: `certs/nam_smallz.json`.

The centred regular tetrahedron evaluates $\alpha_{4,2}$ exactly:
all $|x|=\sqrt{3}$, all $|x-y|=\sqrt{8}$, so $\alpha_{4,2}\le\sqrt{6}/4$.
Then $\alpha_{4,2}\cdot 3\le 3\sqrt{6}/4<2$ because $54<64$. Two
independent checks: `verify_tetra.py` and `verify_tetra.c`. This is a
certified *obstruction* to a dent by the $s=2$ pair geometry, not a
dent. The same for $N=3$: the centred equilateral triangle gives
$\alpha_{3,2}\le\sqrt{3}/3$, hence $\alpha_{3,2}\cdot 2=2/\sqrt{3}<2$.

`alpha_n.py` / `alpha_n_check.py` search $\alpha_{N,s}$. The search
minimum matches those closed forms at $s\ge 1.5$. A search min is an
upper bound on the infimum and is not used as a lower bound.

## Temple / intermediate Hamiltonian

Hylleraas at $Z=2$, $\alpha=37/20$, $c=37/100$ gives
$E(2,2)\le -54353/18800$ (q1, exact rational). That is a legal *upper*
on the helium threshold.

Hydrogenic $1s^2 2s$ and $1s2s2p\,{}^4P$ trials on $H(3,2)$ sit above
that upper bound by $0.204$ and $0.885$ (q1 `three_electron_try.py`,
replayed). Temple requires $\mu<E_1$. Taking $E_1$ as the HVZ threshold
$E(2,2)$ makes the hypothesis false. No Temple number is claimed.

Crude intermediate Hamiltonians:

- drop repulsion: $E(3,2)\ge 3E(1,2)=-6$, far below helium;
- replace $1/|x-y|$ by $1/(|x|+|y|)$: a product scan of that minorant
  reached about $-3.82$ at $\zeta=1.6$, still $0.93$ below
  $-54353/18800$.

Variational uppers on $E(3,2)$ were not used as non-binding evidence.
HF/DFT were not used.

## What would have been a dent

A certified $N_c(2)\le 3$ (i.e. $N_c(2)<4$) or $N_c(2)=2$, with an
independent second path, would beat Lieb's integer bound at helium.
Nothing in this folder certifies that.

## Status

Residue. Best published integer bounds at the requested charges:

$$
N_c(2)\le 4,\qquad N_c(3)\le 6,\qquad N_c(4)\le 8
$$

(Lieb $N_c<2Z+1$). $N_0(Z)\ge Z$ by Zhislin. No unique $N_0(Z)$ for
$Z>1$. Certificate of the residue: `certs/smallz.json`.
