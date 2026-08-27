# Simon 2000 #9: bounded excess charge

- Slug: `simon-ionization-excess`
- List: Simon 2000 #9 (Coulomb energies); 1984 10(a) if useful
- Solver: Cursor Grok 4.6 xhigh
- Status: dent of the printed leading 1.1185. Same HPS chain with $\beta_3\ge 0.899526$ gives $N_c<1.1118Z+3.966\,Z^{1/3}$ for $Z\ge 4$. q1 remainder dent unchanged. Ionization conjecture open.
- Area: Mathematical physics / many-body Schrödinger
- Sources: Simon 2000 #9; Simon 1984 10(a),(d); Lewin, charged quantum particles
- Started: 2026-08-27

## In general

A nucleus of charge $Z$ and $N$ electrons has Hamiltonian

$$
H(N,Z)=\sum_{i=1}^{N}\Bigl(-\tfrac12\Delta_i-\frac{Z}{|x_i|}\Bigr)+\sum_{i<j}\frac1{|x_i-x_j|}
$$

on the fermionic space. Write $E(N,Z)$ for the bottom of the spectrum. Binding means $E(N,Z)<E(N-1,Z)$. Let $N_0(Z)$ (Simon) or $N_c(Z)$ (Nam, HPS) be the largest such $N$. Zhislin proved binding whenever $N<Z+1$. Lieb proved $N_c<2Z+1$. The ionization conjecture, Simon 2000 problem 9, asks for a $Z$-independent bound on the excess $N_0(Z)-Z$.

Wikipedia is only a map. The published record is on arXiv.

## Precise statement

Prove that $N_0(Z)-Z$ stays bounded as $Z\to\infty$, or give a verified finite improvement of a published non-asymptotic upper bound on $N_c(Z)$.

The 1984 companion 10(a) asks for monotonicity of the ionization energy $\Delta E(N,Z)=E(N-1,Z)-E(N,Z)$ in $N$. A certified range where that inequality holds is useful; it is not a substitute for a bound on the excess.

## Published record (fetched 2026-08-27)

- Lieb, Phys. Rev. A 29 (1984): $N_c<2Z+1$ for all $Z>0$ (fermions or bosons).
- Nam, arXiv:1009.2367v3: $N_c<1.22Z+3Z^{1/3}$ for fermions; equivalently $\beta^{-1}Z+\cdots$ with $\beta\in[0.8218,0.8705)$.
- Hundertmark–Pattakos–Schulz, arXiv:2504.18487v1: $N_c<1.1185Z+4Z^{1/3}$ for all $Z\ge4$, and the sharper

  $$
  N<b(3)Z+3.90\,Z^{1/3}+0.0134+0.184\,Z^{-1/3}+0.0196\,Z^{-2/3},
  $$

  with $1.1184<b(3)<1.1185$. Also $N_c<\frac12(\sqrt2+1)Z+2.96Z^{1/3}$ for $Z\ge2$.
- Lieb–Sigal–Simon–Thirring: $N_c(Z)/Z\to1$. Fefferman–Seco and Seco–Sigal–Solovej: $N_c\le Z+O(Z^{5/7})$.
- Solovej, arXiv:math-ph/0012026: the ionization conjecture holds in Hartree–Fock.
- Bosonic atoms: $N_c/Z\to t_c\approx1.21$ (Benguria–Lieb, Solovej, Baumgartner).

## After 2026-08-27

The same HPS Section 7 chain, with Lieb’s $N/Z<2+1/Z\le9/4$ on the Prop. 2.5 range $Z\ge4$ and the exact $b(3)$ in $a_1$, gives

$$
N<b(3)Z+3.892\,Z^{1/3}+0.0134+0.184\,Z^{-1/3}+0.0196\,Z^{-2/3}\qquad(Z\ge4)
$$

and the simplified

$$
N_c<1.1185Z+3.9781\,Z^{1/3}\qquad(Z\ge4).
$$

Also $N_c<b(2)Z+2.953Z^{1/3}$ for $Z\ge2$. This beats the printed remainders 3.90, 4, and 2.96. It does not beat the leading 1.1185. Replay: `problems/simon-ionization-excess/compute/q1/run_all.sh`.

$N_0(1)=2$ is replayed (Hylleraas $E=-815/1602<-1/2$, plus Lieb). That uniqueness is already in Lieb 1984.

A later search (same day) replayed HPS v1, Nam, Lieb, and
Benguria–González-Brantes arXiv:2511.07582v1
($N<1.4811Z+3.1516Z^{1/3}$ for $Z\ge12$, bosonic / statistics-
independent). That paper does not beat $1.1185$ for fermions.
Two-shell dipoles make the HPS radialization form negative for
every tested $s>3$, so $b(4)$ cannot be used. Lieb remains the
best integer envelope at $Z=2,3,4,5$. A compact-aspect lower
bound $Q\ge0.901924$ (aspect $\le4$) is certified and does not
replace Theorem 2.2. A claimed $1.1168$ lift was withdrawn. Replay:
`problems/simon-ionization-excess/compute/q2/run_all.sh`.

A third search the same day lifts the aspect-$12$ compact bound
$Q\ge 0.899526$ to every radial probability in HPS (4.1):
mass-stationarity on a used support of aspect $\ge 12$ forces
$Q>12/13$, and every atomic measure reduces to one of those two
classes. Truncation plus spherical-shell approximation extends
the bound. The same Section 7 chain with this $\beta_3$ gives

$$
N<1.1118Z+3.880\,Z^{1/3}+0.0133+0.1833\,Z^{-1/3}+0.01956\,Z^{-2/3}
\qquad(Z\ge 4)
$$

and

$$
N_c<1.1118Z+3.966\,Z^{1/3}\qquad(Z\ge 4).
$$

This beats the printed leading $1.1185$. It does not use the
aspect-$\le 4$ number $1.1087$ as an unrestricted bound, and it
does not restore the withdrawn $1.1168$. Finite-$Z$ integers and
$s>3$ stay residue. Replay:
`problems/simon-ionization-excess/compute/q3/run_all.sh`.

## What would count as a new bound

A verified inequality that strictly improves a published record, with a replayable certificate. Examples: a leading coefficient below $1.1185$ for all large $Z$; a remainder strictly below the printed $3.90$ or $4$ on the HPS range; $N_c\le Z+C$ for a universal $C$; a unique exact $N_0(Z)$ for some $Z>1$ that the published inequalities do not already settle.

## What does not count

An incomplete variational or DFT search is not a lower bound. Restating HPS Proposition 2.5 is not a new bound. Hartree–Fock or DFT tables are heuristics. Simon 2000 #9 remains open unless the excess is shown bounded.
