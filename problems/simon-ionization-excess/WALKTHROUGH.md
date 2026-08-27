# Walkthrough — simon-ionization-excess

Discovery notes, not a cleaned proof. Beats: `refs/walkthrough-style.md`.
Empty beats mean the campaign is not done.

0. What was actually missing — a replayable certificate for the 2025 HPS numbers, and any finite handle (remainder, small-$Z$ uniqueness, coefficient) that moves a published inequality. The bounded-excess conjecture itself is the missing theorem. For hydrogen the missing *object* was an explicit trial with a strict, checkable gap below $-1/2$, not the uniqueness statement (Lieb already has that).

1. Named false starts — The uncorrelated product $\exp(-\alpha(r_1+r_2))$ is the textbook first try. Its energy is $-(Z-5/16)^2$. At $Z=1$ that is $-121/256>-1/2$, so H$^-$ does not bind in Hartree. A single-charge hydrogenic $1s2s2p$ quartet for He$^-$ lands near $-2.01$, far above helium.

2. The useful failure — The three-electron Slater scan is honest residue. Screened $1s^2 2s$ for He$^-$ bottoms out near the uncorrelated helium energy (about $-2.85$) once the extra $2s$ is made diffuse. That is the picture of an unbound electron at infinity, not a bound He$^-$. Lithium's screened $1s^2 2s$ does go below the published Li$^+$ energy, but without a lower bound on $E(2,3)$ that is not a certificate.

3. The click — Rational parameters make the Hylleraas and Chandrasekhar Rayleigh quotients exact fractions. The comparison $E+1/2<0$ is then integer arithmetic. The tiny pair $\alpha=5/6$, $c=1/2$ already gives $-815/1602$ and gap $7/801$. Chandrasekhar $a=26/25$, $b=7/25$ is closer to the classical minimum and gives a larger gap.

4. The argument — Variational lemma: a trial below the exact hydrogen threshold proves at least two bound electrons at $Z=1$. Lieb's published $2Z+1$ theorem cuts the other side. Combined uniqueness at hydrogen. The Lieb triangle is invoked, not re-proved. Helium is the same algebra at $Z=2$ and is only an energy object.

5. Computer search — `hylleraas.py` / `he_hylleraas.py` evaluate the closed forms. `three_electron_try.py` scans hydrogenic and screened $N=3$ Slater determinants and replays $J(1s,2s)=17ζ/81$, $K(1s,2s)=16ζ/729$ from the Coulomb generating function.

6. Proven vs still open — Simon 2000 #9 open. Uniqueness at hydrogen is already in Lieb plus the classical H$^-$ variational bound; we only replay it. He$^-$ is residue. No uniqueness claim for $Z>1$.
