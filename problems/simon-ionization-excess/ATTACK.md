# Attack log — simon-ionization-excess

Chronological attempts, newest last. A failed attack belongs here too.

## 2026-08-27 — mint and fetch

- Folder minted with `scripts/new-problem.sh simon-ionization-excess`. No sibling PR.
- Record fetched before any claim. Wikipedia / MathWorld used only as a map to Simon 2000 #9 and 1984 10(a).
- arXiv: Nam 1009.2367v3, Nam survey 1209.3642v2, Nam 2206.15393v1, HPS 2504.18487v1, Solovej HF math-ph/0012026v3, FHJN 1808.09017. Benguria–González-Brantes–Tubino 2207.08328v2 abs comment says the version has errors; not used as a record.
- Published non-asymptotic record to beat: Hundertmark–Pattakos–Schulz, $N_c<1.1185Z+4Z^{1/3}$ for $Z\ge4$, and Prop. 2.5 remainder $3.90$. Nam $1.22$ and Lieb $2Z+1$ remain the comparison for small $Z$.

## 2026-08-27 — false start: beat 1.1185 by a new $s$ or a better $\beta_3$

- $b(s)=\max_t(1+t^{s-1})/(1+t^s)$ decreases in $s$, but HPS only prove the theorem for $s\le3$. No $s>3$ argument was found.
- Nam $\beta\in[0.8218,0.8705)$ independently replayed. A second radial trial gives $\beta\le0.87022$, which tightens only the *upper* end of $\beta$ and cannot improve an ionization *upper* bound.
- FHJN 1.456 is the LT factor in $\kappa$. A later lead 1.44655 (arXiv:2403.04347) was not replayed and is not used.

## 2026-08-27 — useful failure: HPS $a_1$ endpoint

- HPS claim the supremum of $a_1(x)$ on $[\beta_3^{-1},5/2]$ is at the left. Independently it is a minimum in the middle and the max is at $x=5/2$, value $3.899495\ldots$. So their printed $3.893$ does not enclose that supremum. Printed $3.90$ still does.
- Prop. 2.5 is only stated for $Z\ge4$. Lieb gives $N/Z<2+1/Z\le9/4$ there, not $5/2$.

## 2026-08-27 — the click

- Restrict $a_1$ to $[b(3),9/4]$. Then the max *is* at the left, $a_1<3.892$.
- Same extras $0.0134$, $0.184$, $0.0196$. At $Z=4$ the $Z^{1/3}$ remainder coefficient is $3.978009\ldots<3.9781$, and it decreases in $Z$.
- Prop. 2.4: $a(5/2)=2.952038\ldots<2.953$, beating printed $2.96$.
- Leading $1.1185$ unchanged.

Certified (interval arithmetic in `tighten_hps.py`; second path `verify_remainder.py`; C and Rust on $b(2)$, $b(3)$):

$$
N_c<b(2)Z+2.953\,Z^{1/3}\qquad(Z\ge2),
$$

$$
N<b(3)Z+3.892\,Z^{1/3}+0.0134+0.184\,Z^{-1/3}+0.0196\,Z^{-2/3}\qquad(Z\ge4),
$$

$$
N_c<1.1185Z+3.9781\,Z^{1/3}\qquad(Z\ge4).
$$

## 2026-08-27 — small $Z$ and heuristics

- Hylleraas $\psi=e^{-\alpha(r_1+r_2)}(1+c r_{12})$, $\alpha=5/6$, $c=1/2$: $E=-815/1602$, $E+1/2=-7/801<0$. Combined with Lieb $N_c<3$, $N_0(1)=2$. Already in Lieb 1984. Replay, not a dent.
- Three-electron search for He$^-$ did not go below the He variational energy. Residue, not a lower bound.
- UHF / helium-like table for $Z=1\ldots10$: $\Delta E$ monotone on that table. Heuristic. Does not prove 1984 10(a).

## 2026-08-27 — Lean

- `lean/HPSCoefficient.lean`: $11184/10000<b(3)<11185/10000$ and the $b(2)$ enclosure.
- `lean/LiebPair.lean`: triangle $(\|x\|+\|y\|)/\|x-y\|\ge1$. Not the full Lieb bound.
- `lean/B3NatWitness.lean` checks with core Lean, no mathlib.

Replay: `problems/simon-ionization-excess/compute/q1/run_all.sh`.

## 2026-08-27 — q2 record replay (later papers)

- HPS 2504.18487 still **v1 only** (25 Apr 2025). Semantic Scholar
  citationCount 0; OpenAlex W4416381655 cited_by_count 0.
- Nam 1009.2367v3 and the 2206.15393 write-up of Lieb replayed
  again. Nam’s β interval cannot beat 1.1185
  (1/0.8705 ≈ 1.149).
- Benguria–González-Brantes 2511.07582v1 (10 Nov 2025), HTML
  Theorem 1.1 / (2): $N<1.4811Z+3.1516Z^{1/3}$ for $Z\ge12$,
  statistics-independent / bosonic. Improves Lieb for bosons at
  those $Z$. Does not beat 1.1185 for fermions. Replacement for
  2207.08328v2, whose abs comment says that version has errors
  (PDF/HTML 404).
- Corso–Ried 2403.04347v2 is an LT/CLR variational bound
  (1.44655 vs FHJN 1.456). It sits in the HPS remainder, not in
  $b(s)$. Not used.
- Lewin CR Physique (accepted 31 Mar 2025, PDF opened): even a
  huge $C$ for $N_{\max}\le Z+C$ is still unknown.

No later fermionic leading coefficient below 1.1185. No paper
proves a $Z$-independent bound on the excess. No unique $N_0(Z)$
for $Z>1$.

## 2026-08-27 — q2 false start: $s>3$

$b(4)\approx1.083$ would be a real jump if Lemma 4.3 extended.
Two-shell opposite dipoles make $I_s(\nu)$ negative for every
tested $s>3$. At $s=4$ the quadratic is the exact rational
$-1025/2048$. At $s=3$ the dipole form stays nonnegative (Hardy
threshold). Remark 2.3 stays a conjecture. Residue:
`compute/q2/certs/s_gt_3.json`.

## 2026-08-27 — q2 false start: finite $Z$

Published envelopes at $Z=2,3,4,5$: Lieb $N_c<2Z+1$ still
excludes the most integers. Nam and both HPS forms sit above
$2Z+1$ there. Regular tetrahedron: $\alpha_{4,2}\le\sqrt6/4$, so
$\alpha_{4,2}\cdot3<2$ because $54<64$. Pair geometry with the
kinetic term dropped cannot exclude $N=4$ at $Z=2$. Lieb-style
weights, Nam’s $\alpha_N$ remainder, and Temple/intermediate
Hamiltonians also failed. Unsettled $N$ at $Z=2$ is $\{2,3,4\}$.
Hydrogen uniqueness not claimed. Residue: `compute/q2/certs/smallz.json`.

## 2026-08-27 — q2 useful failure: withdrawn $1.1168$

A tail polynomial $h(D_L,D_R)$ was used to lift a middle-window
Rayleigh to every Borel probability, claiming
$\beta_3\ge0.895396$ and $\beta_3^{-1}\le1.11682<1.1185$. False:
$h(0,1)\approx0.991$ exceeds the HPS power-law $I/D\approx0.921$
on a measure supported in that tail. Also $I_{CC}\ge\beta D_C$
is false. `certs/beta3_rad.json` is withdrawn.

## 2026-08-27 — q2 compact class, no lift

The mid-radius face enumeration *is* correct on a compact
aspect. After the $P_{\max}=(q-1)/(q+1)$ reweighting error,

$$
Q\ge0.901924\qquad\text{on $D$-aspect }\le4,
$$

so $1/Q\le1.108741$ in that class (`certs/beta3_compact.json`,
C faces at $n=18$, $0$ singular; Rust $n=16$ rebuild). The
numerical power-law minimizer has aspect $\sim3.50$, so it sits
in the class. HPS $\beta_3$ is an inf over *all* radial
probabilities, so this does not replace $1.1185$ in Theorem 2.2.

Two-window lift with cross terms at $\min f$ has
$p_{12}\approx0.995$ and collapses to $\min f$. Geometric
$t_0$-chains stay at $Q\ge0.9379$ in a scan
(`certs/aspect_try.json`); that is not a lower bound. No
certificate that every minimizer has bounded aspect.

## 2026-08-27 — q2 status

Residue. Leading coefficient still $1.1185$
(Hundertmark–Pattakos–Schulz arXiv:2504.18487v1). Remainder
dent from q1 unchanged. $N_0(Z)-Z$ bounded still open.

Replay: `problems/simon-ionization-excess/compute/q2/run_all.sh`.
