# Small-Z certificates — Simon ionization

Compute notes for the two- and three-electron trials in this folder.
This is a replay of published facts about hydrogen, not a new bound.

## Result

The Hylleraas trial

$$\psi=\exp\bigl(-\tfrac56(r_1+r_2)\bigr)\bigl(1+\tfrac12 r_{12}\bigr)$$

has exact variational energy $-815/1602$ on $H(2,1)$. That is strictly
below the hydrogen threshold $-1/2$, with gap $7/801$. Binding of the
second electron follows, so the maximal binding number at $Z=1$ is at
least 2.

Lieb's published theorem is $N_c<2Z+1$.
At unit nuclear charge that is strictly less than 3, hence at most
2 electrons. Combined:

$$
N_0(1)=2.
$$

Lieb, Phys. Rev. A 29, 3018 (1984), already concludes that hydrogen
binds exactly two electrons and that $\mathrm{H}^{--}$ is not stable. Nam,
arXiv:2206.15393, restates that this settles the ionization
conjecture for the hydrogen atom. The certificate is a replay with
an explicit rational energy. It is not a new bound.

A stronger Chandrasekhar trial with $a=26/25$, $b=7/25$ gives
exact energy $-1076189452297/2096620401250\approx -0.513297$,
gap $13939625836/1048310200625\approx 0.013297$ below $-1/2$.
Same conclusion.

Helium at nuclear charge 2 with two electrons has a Hylleraas energy
$-54353/18800\approx -2.891117$, about $0.0126$ above the published
non-relativistic value $-2.9037243770341195$ (Nakashima–Nakatsuji
2007). That is a variational object, not a uniqueness theorem for
helium.

He$^-$ does not bind in the trials below. That search is residue,
not a lower bound. We do not claim a unique maximal $N$ for any
nuclear charge larger than 1.

## Hamiltonian and threshold

Infinite nuclear mass, Hartree atomic units:

$$
H=-\tfrac12\Delta_1-\tfrac12\Delta_2-\frac{Z}{r_1}-\frac{Z}{r_2}+\frac1{r_{12}}.
$$

Hydrogen is exact: $E(1,1)=-1/2$. Binding of H$^-$ is
$E(2,1)<-1/2$.

The uncorrelated product $\exp(-\alpha(r_1+r_2))$ has energy
$\alpha^2-2(Z-5/16)\alpha$, minimum $-(Z-5/16)^2$. At $Z=1$ this
is $-121/256>-1/2$, so a product of 1s orbitals does not bind.

The correlation factor $(1+c r_{12})$, or Chandrasekhar's
split-exponent symmetrised product, is the classical repair
(Hylleraas 1929; Bethe 1929; Chandrasekhar 1944). Closed forms
are written out in `hylleraas.py`. Høgaasen–Richard–Sorba,
arXiv:0907.2614, record the Chandrasekhar algebra we re-derived
from hydrogenic factorisation plus the Coulomb integral

$$
\int\!\!\int\frac{e^{-\lambda r_1-\mu r_2}}{r_{12}}\,d^3r_1\,d^3r_2
=\frac{32\pi^2(\lambda^2+3\lambda\mu+\mu^2)}{\lambda^2\mu^2(\lambda+\mu)^3}.
$$

Lieb's triangle $N_c<2Z+1$ is invoked, not re-proved.

## Files and replay

From `problems/simon-ionization-excess/compute/q1/`:

```bash
python3 hylleraas.py
python3 hylleraas.py --write-certs
python3 he_hylleraas.py
python3 three_electron_try.py
```

| file | role |
| --- | --- |
| `hylleraas.py` | exact Hylleraas $(α,c)$ and Chandrasekhar $(a,b)$ at general $Z$ |
| `he_hylleraas.py` | helium $Z=2$ replay vs Nakashima–Nakatsuji |
| `three_electron_try.py` | three-electron Slater search; residue for He$^-$ |
| `certs/hminus.json` | parameters, exact energy, enclosure, gap, script SHA |
| `certs/n0_z1.json` | uniqueness at hydrogen, both legs |

The primary energy comparison is integer arithmetic on a rational.
The decimal enclosure in the cert is floor/ceil of that rational
times $10^{40}$, not a floating-point evaluation of the Hamiltonian.

## Helium object

Uncorrelated $α=27/16$ gives the textbook $-729/256=-2.84765625$.
Hylleraas $α=37/20$, $c=37/100$ gives $-54353/18800$. Chandrasekhar
$a=109/50$, $b=119/100$ gives about $-2.875658$, matching the
Chandrasekhar column in arXiv:0907.2614 Table 1. Zhislin already
binds two electrons at helium. We do not extract a unique $N$ from
this.

## Three-electron search (residue)

Hydrogenic $J$ and $K$ used in the $N=3$ Slater energies were
replayed from the same Coulomb generating function:
$J(1s,2s)=17ζ/81$, $K(1s,2s)=16ζ/729$, and the $1s$–$2p$ and
$2s$–$2p$ values listed in `three_electron_try.py`.

A single-charge hydrogenic $1s^2 2s$ or $1s2s2p\,{}^4P$ trial, and a
screened Slater $1s^2 2s$ with a nodeless $2s$ orthogonalised against
$1s$, were minimised at $Z=2$ and $Z=3$.

He$^-$ ($Z=2$, $N=3$). Best screened $1s^2 2s$ in the scan is about
$-2.8465$, above the published helium energy $-2.9037$ and above our
own helium Hylleraas $-2.8911$. The hydrogenic ${}^4P$ is worse
(about $-2.01$). No trial here has $E_{\mathrm{var}}(3,2)$ below a
lower bound on $E(2,2)$. He$^-$ is not shown to bind. Residue, not a
lower bound.

Lithium ($Z=3$, $N=3$). Screened $1s^2 2s$ reaches about $-7.418$,
and an optimised hydrogenic $1s^2 2s$ reaches
$-6642153923171/911250000000\approx-7.28906$. Both sit below the
published Li$^+$ energy $\approx-7.27991$ (Nakashima–Nakatsuji,
$Z=3$). That comparison is not a certificate: we do not own a lower
bound on $E(2,3)$. Our own Li$^+$ Hylleraas/Chandrasekhar numbers
are upper bounds and cannot be used as a threshold. Zhislin already
binds the neutral lithium atom. We do not claim a unique $N$ at
lithium.

A three-electron Hylleraas–CI fragment was not built. The Slater
search is the attempt.

## What this is not

- Not a new bound on the maximal electron number, or on the excess
  charge as $Z\to\infty$.
- Not a proof that He$^-$ binds.
- Not a uniqueness theorem for any $Z>1$.
- Lieb's functional-analytic proof is cited, not reproduced.
