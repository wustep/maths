# Bounded ionization excess (Simon 2000 #9)

- Slug: `simon-ionization-excess`
- List: Simon 2000 #9; Simon 1984 10(a) nearby
- Solver: Grok 4.6
- Status: open
- Area: Many-body Schrödinger / Coulomb systems
- Sources: Simon, *Mathematical Physics 2000*, pp. 283–288; Lieb, *Phys. Rev. A* 29 (1984); Nam arXiv:1009.2367; Hundertmark–Pattakos–Schulz arXiv:2504.18487; Lewin, *C. R. Physique* 26 (2025); Nam arXiv:2206.15393
- Started: 2026-08-27

## Statement

Let H(N,Z) be the non-relativistic Hamiltonian of N fermionic electrons
and one infinitely heavy nucleus of charge Z, with Coulomb attraction
and repulsion. Write E(N,Z) for the ground-state energy. Following
Simon (2000), N0(Z) is the smallest N such that E(N+j,Z) = E(N,Z) for
every positive integer j — the maximal number of electrons the nucleus
can bind. Zhislin gives N0(Z) ≥ Z. Ruskai and Sigal proved that some
finite N0(Z) exists. Simon's #9 asks:

Prove that N0(Z) − Z remains bounded as Z → ∞.

Simon already calls N0(Z) ∈ {Z, Z+1} a reasonable further guess.
The papers below write Nc(Z) for the same (or the closely related)
maximal binding number; we keep their notation when quoting them.

The 1984 neighbour, Simon's 10(a), asks for monotonicity of the
ionization energy: (ΔE)(N−1,Z) ≥ (ΔE)(N,Z). That is convexity of
N ↦ E(N,Z). It is a different statement from bounded excess. Both
are open for Coulomb atoms.

## Published record

Fetched and read this session (see RESEARCH.md).

- Lieb, *Phys. Rev. A* 29 (1984), 3018–3028: Nc(Z) < 2Z+1 for every
  Z ≥ 1. (Simon's reprint quotes the slightly weaker N0(Z) < 2Z.)
  The argument does not use Fermi statistics.

- Nam, arXiv:1009.2367, *Comm. Math. Phys.* 312 (2012):
  Nc(Z) < 1.22 Z + 3 Z^{1/3} for every Z ≥ 1 (and the only other
  possibility is N = 1). This beats Lieb once Z ≥ 6.

- Hundertmark–Pattakos–Schulz, arXiv:2504.18487 (25 April 2025),
  Proposition 2.5: for Z ≥ 4,

$$
N<b(3)\,Z+3.90\,Z^{1/3}+0.0134+0.184\,Z^{-1/3}+0.0196\,Z^{-2/3},
$$

  with the explicit leading coefficient

$$
1.1184<b(3)=\frac23\frac{(1+\sqrt{2})^{1/3}}{(1+\sqrt{2})^{2/3}-1}<1.1185.
$$

  The same paper's coarser line, and the abstract, is
  Nc(Z) < 1.1185 Z + 4 Z^{1/3} for Z ≥ 4. Proposition 2.4 is the
  s=2 bound Nc(Z) < ((√2+1)/2) Z + 2.96 Z^{1/3} for Z ≥ 2, which
  already improves Nam's 1.22 for every such Z.

- Asymptotic neutrality is older and weaker than a bounded excess:
  Lieb–Sigal–Simon–Thirring, then Fefferman–Seco and
  Seco–Sigal–Solovej, give Nc(Z) ≤ Z + O(Z^{5/7}). That is o(Z),
  not O(1). The implied constant is not a replacement for the
  linear bounds above at realistic Z.

- Lewin, *C. R. Physique* 26 (2025), 369–380, and Nam,
  arXiv:2206.15393, still state the ionization conjecture
  (Nc ≤ Z + C, ideally C = 1 or 2) as open, even with an enormous C.
  Lewin also keeps 1984 10(a) open for integer nuclear charges.

Independently recomputed (compute/): the closed form for b(3) does
lie in (1.1184, 1.1185); ((√2+1)/2) lies in (1.2071, 1.2072); Nam
first undercuts Lieb at Z = 6; the s=3 Hundertmark–Pattakos–Schulz
line undercuts their s=2 line once Z ≥ 36, matching their 35.8
remark. None of that is a new bound.

## What would count as a new bound

A verified finite improvement of a documented record. Success is one of:

**(A)** Nc(Z) < c Z + o(Z) (or + C Z^{1/3}) with a leading c strictly
below 1.1184, valid for all large Z, citing Hundertmark–Pattakos–Schulz
arXiv:2504.18487 as the beaten number.

**(B)** The Simon ask: N0(Z) − Z ≤ C for an explicit finite C and all
Z, or even N0(Z) ≤ Z + C for a stated C (Lieb's ionization conjecture).

**(C)** A strictly smaller explicit remainder than 4 Z^{1/3} (or than
the 3.90 Z^{1/3} + … expansion) at the same leading coefficient,
again with a citation of the beaten display.

**(D)** A proof of 1984 10(a) for atoms — monotonicity of the
ionization energy for integer Z — which is not implied by (A)–(C).

A comparison table of already published upper bounds is not a new
bound. Experimental NIST ionization curves are not a mathematical
record. Bosonic atoms are a different theorem (Benguria–Lieb /
Solovej, lim Nc/Z = tc ≈ 1.21) and do not move the fermionic ask.
An incomplete search over small Z is not a lower bound on the excess.
