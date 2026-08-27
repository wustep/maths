# These numbers are not a bound

The files `certs/hf_table.json` and `certs/delta_e.json` are a
heuristic Hartree–Fock table for small $N$ and $Z$. They do not move
the ionization conjecture, and they do not improve a published
non-asymptotic bound on Nc. Status: residue.

Solovej already proved the ionization conjecture in Hartree–Fock
(arXiv:math-ph/0012026). A numerical HF table cannot touch that
theorem. The Schrödinger problem (Simon 2000 #9) is a different
object; HF energies are not energies of $H(N,Z)$.

## What was computed

Three series, all labeled HEURISTIC, in Hartree.

1. One-parameter Slater $1s$ Hartree–Fock for helium-like ions. For
   one electron the energy is the exact hydrogenic value
   $-Z^2/2$. For two electrons the restricted $1s^2$ ansatz with
   scale $\zeta=Z-5/16$ gives $E=-(Z-5/16)^2$.
2. Unrestricted HF in a small even-tempered Gaussian basis with 1s,
   2s and 2p scales (tight exponents ~ $Z^2$, valence ~ $(Z/2)^2$,
   plus a short diffuse tail). Integrals are analytic, same-centre
   Cartesian $s$ and $p$. Occupations follow Hund’s rule. Closed
   shells stay spin-restricted if the core-Hamiltonian guess is.
3. The same UHF loop on $s$-Gaussians only, for $N=0,1,2$. Extra
   electrons in a spherical $s$ basis are not a model of B–Ne.

Replay:

```bash
python3 rhf_atoms.py --self-test
python3 rhf_atoms.py
python3 delta_e_table.py
```

## Binding, and what would count

The table marks a pair as “binds” when the HF energy drops from
$N-1$ to $N$. That comparison is not a proof that the true
$E(N,Z)$ lies below $E(N-1,Z)$. Both numbers are variational
upper bounds. A worse $N$-electron trial can sit above a better
$(N-1)$-electron trial even if the $N$-electron atom is bound,
and the other way around.

A variational energy becomes a binding certificate — a genuine
lower bound on N0 — only if it lies strictly below a certified
value of $E(N-1,Z)$. The only exact thresholds used here are the
bare nucleus $E(0,Z)=0$ and the hydrogenic $E(1,Z)=-Z^2/2$.

For $Z\ge 2$ the Slater two-electron energy is below $-Z^2/2$, so
N0 is at least 2. That is already in Zhislin’s theorem ($N<Z+1$
binds) and is not a new bound. For $Z=1$ the same ansatz gives
$-(11/16)^2=-0.47265625$, which is above $-1/2$, so it does not
certify that H- is bound. The Hylleraas certificate that N0(1)
equals 2 is a different calculation.

Experimental ionization energies are leads, not certificates.

## The 1984 10(a) check

From the same energies the script writes

$$
\Delta E(N,Z)=E(N-1,Z)-E(N,Z)
$$

and tests $\Delta E(N-1,Z)\ge\Delta E(N,Z)$ on consecutive pairs
that both exist in the table. On this run the inequality held for
every such pair (10 helium-like, 63 UHF $s/p$, 10 s-only). That is
a property of these HF numbers, not a proof of monotonicity. A
failed pair would not be a counterexample to 10(a) either: the
inputs are HF numbers, not $E(N,Z)$.

Heuristic N0-hat in the UHF $s/p$ table is 1 for $Z=1$ and $Z$
for $Z=2$ through 10: no anion binds. H- is not below the exact
$-1/2$, so there is no new binding certificate. For $Z\ge 2$ the
two-electron energy is below $-Z^2/2$, which Zhislin already
gives. Two lithium-anion SCF runs ($Z=3$, $N=4$ and $5$) hit the
iteration cap; their energies still sit above Li.

## Thomas–Fermi

A Thomas–Fermi or spherical LDA toy was not needed for the
integrals and is not stored. Continuum TF energies do not decide
a finite N0.
