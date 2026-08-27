# Simon's problems (2000 list, with a 1984 pointer)

Barry Simon, *Schrödinger operators in the twenty-first century*, in
A. Fokas, A. Grigoryan, T. Kibble, B. Zegarlinski (eds.),
*Mathematical Physics 2000*, Imperial College Press, 2000, pp. 283–288.
Caltech reprint (opened and OCR'd this session):
[r40.pdf](http://www.math.caltech.edu/papers/bsimon/r40.pdf).

Fifteen Schrödinger-operator questions. Simon groups 1–8 as quantum
transport and anomalous spectra, 9–13 as Coulomb energies, and 14–15
as two leftovers. The statements below follow that reprint, not the
Wikipedia table (the wiki list is a map; its wording of #6 disagrees
with the reprint).

Status cutoff 2026-08-27. "Solved" means a paper that claims, and is
read as, a complete answer to the printed ask. The other eleven are
open.

| # | Short name | Statement (one sentence) | Status |
| ---: | --- | --- | --- |
| 1 | Extended states | For the Anderson model in dimension at least 3 and weak disorder, prove purely absolutely continuous spectrum in some energy interval. | Open. Simon's reprint is still the ask; no paper opened this session proves any interval of AC spectrum. |
| 2 | Localization in two dimensions | Prove that the two-dimensional Anderson model has dense pure point spectrum at every disorder. | Open. Same reprint; physicists expect localization, but there is no theorem for all couplings. |
| 3 | Quantum diffusion | Where that AC spectrum exists in dimension at least 3, prove that the second moment of the wave packet grows linearly in time (diffusive, not ballistic). | Open. Conditional on #1, and open even as a conditional statement. |
| 4 | Ten Martini | For every nonzero coupling and every irrational frequency, the almost Mathieu spectrum is a Cantor set (nowhere dense). | Solved. Avila–Jitomirskaya, [arXiv:math/0503363](https://arxiv.org/abs/math/0503363), *Ann. of Math.* 170 (2009). Earlier: Puig, [arXiv:math-ph/0309004](https://arxiv.org/abs/math-ph/0309004), for Diophantine frequency and non-critical coupling. |
| 5 | Critical measure zero | For every irrational frequency, the almost Mathieu spectrum at coupling 2 has Lebesgue measure zero. | Solved. Avila–Krikorian, [arXiv:math/0306382](https://arxiv.org/abs/math/0306382), *Ann. of Math.* 164 (2006), completing the Aubry–André measure conjecture. Simon already recorded Last, *Comm. Math. Phys.* 164 (1994), for unbounded partial quotients. |
| 6 | Subcritical AC spectrum | For every irrational frequency and coupling strictly less than 2, the almost Mathieu spectrum is purely absolutely continuous. | Solved. Avila, [arXiv:0810.2965](https://arxiv.org/abs/0810.2965), proves AC spectrum if and only if the coupling is subcritical, and states that this settles Simon's #6. (The reprint asks only the subcritical half; Wikipedia's "AC at coupling 2" is not the reprint.) |
| 7 | Embedded singular continuous spectrum | Does there exist a potential on the half-line with pointwise decay faster than \|x\|^{-1/2-ε} whose Schrödinger operator has some singular continuous spectrum? | Solved. Kiselev, [arXiv:math/0111200](https://arxiv.org/abs/math/0111200), *J. Amer. Math. Soc.* 18 (2005), constructs examples with decay just slower than Coulomb and states that this solves the Simon problem. Denisov, *J. Differential Equations* 191 (2003), 90–104, had the L²-decay case (not pointwise). |
| 8 | AC spectrum for decaying potentials | If the potential on R^ν, ν≥2, satisfies the weighted L² condition printed in the reprint, prove that −Δ+V has AC spectrum of infinite multiplicity on [0,∞). | Open. Simon records the one-dimensional theorem of Deift–Killip and the spherical reduction; the higher-dimensional ask is not closed in any paper opened this session. |
| 9 | Bounded ionization excess | Prove that N₀(Z)−Z stays bounded as Z→∞, where N₀(Z) is the largest number of electrons a nucleus of charge Z can bind. | Open. Record and the neighbouring 1984 monotonicity question live in `problems/simon-ionization-excess/`. |
| 10 | Ionization-energy asymptotics | What is the large-Z behaviour of the first ionization energy E(Z,Z−1)−E(Z,Z)? | Open. The three-term total-binding expansion is a different object (Simon recalls it as known); the single-electron ionization energy is not settled. |
| 11 | Shell model | Make mathematical sense of the nuclear / atomic shell model as a statement about the exact Schrödinger atom. | Open. Simon already called this vague. |
| 12 | Molecular configurations | Justify, from the many-body Schrödinger equation, the techniques used to predict configurations of large molecules. | Open. Likewise vague; a programme, not a yes/no. |
| 13 | Existence of crystals | Prove that the ground state of some neutral system of nuclei and electrons approaches a periodic configuration as the number of nuclei goes to infinity. | Open. Lewin, [C. R. Physique 26 (2025), 369–380](https://doi.org/10.5802/crphys.249), still lists macroscopic Coulomb crystallization as unproved. Short-range classical crystallization (Theil and later work) is a different theorem. |
| 14 | Continuity of the IDS | Prove that the integrated density of states k(E) is continuous in the energy. | Open. Simon records continuity in one dimension and in the discrete case; the higher-dimensional continuum ask is the one that was open in 2000, and no paper opened this session closes it in that generality. |
| 15 | Lieb–Thirring constants | Prove the Lieb–Thirring conjecture on the constants L(γ,1) for 1/2<γ<3/2. | Open. Record lives in `problems/simon-lieb-thirring/`. |

Folders in this notebook: [`problems/simon-lieb-thirring/`](../../problems/simon-lieb-thirring/)
(Simon 2000 #15) and
[`problems/simon-ionization-excess/`](../../problems/simon-ionization-excess/)
(Simon 2000 #9 and 1984 10(a)).

## The 1984 list

A different fifteen. Simon, *Fifteen problems in mathematical physics*,
in W. Jäger, J. Moser, R. Remmert (eds.), *Perspectives in Mathematics:
Anniversary of Oberwolfach 1984*, Birkhäuser, 1984, pp. 423–454.
Caltech reprint (opened this session):
[R27.pdf](http://www.math.caltech.edu/SimonPapers/R27.pdf).

Thirteen of those items are Schrödinger problems. In the 2000 reprint
Simon says that, depending on how one counts multiple parts, five of
the 1984 questions had been solved. This note does not recatalog 1984.

The ionization pair from 1984 sits next to 2000 #9. Problem 10(a) asks
for monotonicity of the ionization energy
(ΔE)(N−1,Z) ≥ (ΔE)(N,Z)
(convexity of the ground-state energy in the electron number).
Problem 10(c) asked for a small excess charge; the 2000 form is the
bounded-excess statement #9. Lewin, *C. R. Physique* 26 (2025), 369–380,
still lists both as open for Coulomb atoms with integer nuclear charge.
Coley, [arXiv:1710.02105](https://arxiv.org/abs/1710.02105), reprints
several 1984 statements as illustrations of what counts as a problem
in mathematical physics.

Wikipedia's page
[Simon problems](https://en.wikipedia.org/wiki/Simon_problems)
and Weisstein,
[Simon's Problems](https://mathworld.wolfram.com/SimonsProblems.html),
were used only as a map to the reprints and the arXiv ids.
