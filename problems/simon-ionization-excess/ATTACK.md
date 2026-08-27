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

## 2026-08-27 — q3 record replay

- HPS 2504.18487 still **v1 only** (25 Apr 2025). OpenAlex
  W4416381655 `cited_by_count` 0. Semantic Scholar 429 this pass.
- Nam 1009.2367v3 and Benguria–González-Brantes 2511.07582v1
  unchanged: no fermionic leading coefficient below $1.1185$.
- q1 and q2 replayed (`compute/q1/run_all.sh`,
  `compute/q2/run_all.sh`), both exit 0.

## 2026-08-27 — q3 leftovers: finite $Z$ and $s>3$

Lieb still gives the best integers at $Z=2,\ldots,6$ ($N_c\le 2Z$).
Nam and HPS $s=2$ sit below $2Z+1$ as reals at $Z=6$ and still
above $12$. Five octahedron vertices block $N=5$ at $Z=3$ by pair
geometry ($128<169$), the same obstruction as the tetrahedron.
Two-shell dipoles still make $I_s$ negative for $s>3$
($-1025/2048$ at $s=4$). Infinite $t_0$-chains and log-radius
convolution recover only $\min f$ as a global floor. Residue:
`compute/q3/work/smallz.md`, `s_gt_3_toeplitz.md`.

## 2026-08-27 — q3 the click: mass-opt, not existence

The leftover from q2 was “a minimizer has bounded aspect.” An
adversarial probe found no $Q<0.8995$ and no mass-stationary
$k$-atomic with $Q\le 0.921$ and aspect $\ge 12$, but existence
of a global minimizer was still a sketch.

The lift does not need a minimizer. For *any* finite set of
radii, mass-optimisation on the simplex exists. The mass-critical
point is stationary for $Q$ and satisfies
$V(r_i)=(Q/2)(r_i^2+D)$ at every used atom. The endpoint
identities then force $Q>R/(R+1)$ if the used aspect is $R\ge 12$.
At $R=12$ that is $Q>12/13>0.899526$. If mass-opt drops an
endpoint, the used aspect shrinks into the compact class.

So every finitely atomic radial measure has $Q\ge\gamma_{12}$.
A compactly supported radial probability is a $Q$-limit of finite
spherical shells. A finite-$D$ measure is a $Q$-limit of compact
truncations ($r^2$ is UI for that one measure). Hence
$\beta_3\ge\gamma_{12}$ on HPS $D_3$.

The aspect-$\le 4$ number $1.1087$ is *not* used: the split
$\min(\gamma_R,R/(R+1))$ only beats $1.1185$ once $R\ge 9$.
The stored $R=12$ row is the first certified class that works.
$1.1168$ stays withdrawn.

## 2026-08-27 — q3 dent

Same HPS §7 chain with $\beta_3\ge 0.899526$:

$$
N<1.1118Z+3.880\,Z^{1/3}+0.0133+0.1833\,Z^{-1/3}+0.01956\,Z^{-2/3}
\qquad(Z\ge 4),
$$

$$
N_c<1.1118Z+3.966\,Z^{1/3}\qquad(Z\ge 4).
$$

Certified: `certs/lift.json`, interval §7 in `tighten_leading.py`,
stdlib `verify_lift.py`, C and Rust on the $12/13$ algebra,
mass-opt scan with no counterexample, stored $R=12$ faces
(copositive, $5$ residual skips). q1 remainders $2.953$, $3.892$,
$3.9781$ unchanged. $N_0(Z)-Z$ bounded still open.

Replay: `problems/simon-ionization-excess/compute/q3/run_all.sh`.

## 2026-08-27 — q4 record replay

- HPS 2504.18487 still **v1 only** (25 Apr 2025). OpenAlex
  W4416381655 `cited_by_count` 0.
- Nam 1009.2367v3 and Benguria–González-Brantes 2511.07582v1
  unchanged: no later fermionic leading coefficient.
- q1, q2, and q3 replayed (`compute/run_all.sh` through q3),
  exit 0.

## 2026-08-27 — q4 leftovers: finite $Z$, moments, $P_{\max}$

Lieb still gives the best integers at $Z=2,\ldots,6$. The q3
simplified $1.1118Z+3.966Z^{1/3}$ sits below printed HPS as a
real and still above $2Z+1$. Nam Lemma 1 at the Lieb edge and a
separated four-electron Hylleraas trial do not exclude a new
integer. $N_0(Z)-Z$ cannot move from a leading coefficient $>1$.

Endpoint identities plus Hölder/Chebyshev leave a nonempty
abstract $(Q,D)$ region below $\gamma_4$; a representing measure
on $[1,4]$ was not found in the scan, and no pen-and-paper $R=4$
lift was obtained. The TV amplitude $1-f_{\min}$ is sharp at
vertices ($F_{ii}=1$). A spread lemma is numerical only.
Residue: `compute/q4/work/smallz.md`, `moment_notes.md`,
`pmax_notes.md`. $1.1168$ stays withdrawn.

## 2026-08-27 — q4 the click: raise $\varphi$ and $n$, split at $R=10$

The q3 bottleneck was the compact $\gamma$ at $R=12$, not the
cut $12/13$. Certified $\varphi=0.9055$ sat $0.0014$ below SLSQP.
Larger $n$ shrinks $P=(q-1)/(q+1)$. The split
$\min(\gamma_R,R/(R+1))$ beats $1.1118$ as soon as $\gamma_R$
moves up and $R/(R+1)$ still exceeds it. $R=10$ is the first
row where a certified $\gamma$ and $10/11$ both sit above
$1/1.1118$.

## 2026-08-27 — q4 dent

Same HPS §7 chain with $\beta_3\ge 0.904414$ (aspect $10$,
$n=26$ faces, $\varphi=0.9091$):

$$
N<1.1057Z+3.860\,Z^{1/3}+0.0132+0.1830\,Z^{-1/3}+0.01952\,Z^{-2/3}
\qquad(Z\ge 4),
$$

$$
N_c<1.1057Z+3.946\,Z^{1/3}\qquad(Z\ge 4).
$$

Certified: `certs/lift.json`, interval §7 in `tighten_leading.py`,
stdlib `verify_lift.py` / `verify_rebuild.py`, C and Rust on the
$10/11$ algebra, mass-opt scan with no counterexample, stored
$R=10$ $n=26$ faces (C dump and independent Rust Cramer re-enum,
both copositive, $23$ residual skips). The unrestricted leading
sits below the aspect-$\le 4$ class-only $1.1087$. $1.1168$ stays
withdrawn. q1 remainders unchanged. $N_0(Z)-Z$ bounded still
open.

Replay: `problems/simon-ionization-excess/compute/q4/run_all.sh`.

## 2026-08-27 — q5 record replay

- HPS 2504.18487 still **v1 only** (25 Apr 2025). OpenAlex
  W4416381655 `cited_by_count` 0.
- Nam 1009.2367v3 and Benguria–González-Brantes 2511.07582v1
  unchanged: no later fermionic leading coefficient below the
  notebook $1.1057$.

## 2026-08-27 — q5 dead line: $R\le 9$ cut

The mass-opt identities still only give $Q>R/(R+1)$. At $R=9$
that is $0.9$, so $\min(\gamma_9,9/10)\le 0.9$ and the leading
is at least $1.1111>1.1057$. Same wall at $R=8$ ($1.125$).
Residue: `compute/q5/certs/r9_cut.json`. A sharper large-aspect
cut would reopen this line; none is certified.

## 2026-08-27 — q5 scan: more bins at $R=10$

SLSQP plus the $P_{\max}$ tax (`certs/scan_compact.json`):

- $R=10$, $n=26$ (q4 row): predicted $1.105688$.
- $R=10$, $n=27$: $1.105110$.
- $R=10$, $n=28$: $1.104547$.
- $R=10$, $n=30$: $1.103463$ ($2^{30}$ faces).
- $R=9.5$, $n=26$: $1.105316$, but $\gamma$ sits $4\cdot 10^{-5}$
  below the cut $9.5/10.5$ — too tight to trust as a first row.

The live line is $R=10$ with $n\ge 27$. Face enumeration is the
certificate, not the SLSQP prediction.

## 2026-08-27 — q5 dent

Same HPS §7 chain with $\beta_3\ge 0.906238$ (aspect $10$,
$n=30$ faces, $\varphi=0.9103$):

$$
N<1.1035Z+3.855\,Z^{1/3}+0.01320+0.1828\,Z^{-1/3}+0.019510\,Z^{-2/3}
\qquad(Z\ge 4),
$$

$$
N_c<1.1035Z+3.941\,Z^{1/3}\qquad(Z\ge 4).
$$

Certified: `certs/lift.json`, interval §7 in `tighten_leading.py`,
stdlib `verify_lift.py` / `verify_rebuild.py`, C and Rust on the
$10/11$ algebra, mass-opt scan with no counterexample, stored
$R=10$ $n=30$ faces ($1{,}073{,}741{,}823$, copositive, $420$
residual skips). Intermediate certified row $n=28$ gives printed
$1.1046$. $1.1168$ stays withdrawn. q1 remainders unchanged.
$N_0(Z)-Z$ bounded still open.

Replay: `problems/simon-ionization-excess/compute/q5/run_all.sh`.

## 2026-08-27 — q6 record replay

- HPS 2504.18487 still **v1 only** (25 Apr 2025). OpenAlex
  W4416381655 `cited_by_count` 0.
- Nam 1009.2367v3 and Benguria–González-Brantes 2511.07582v1
  unchanged: no later fermionic leading coefficient below the
  notebook $1.1035$.
- Independent replay of the q5 cert: `verify_lift.py` recon
  $\gamma=0.906238$, $1/\gamma=1.103463<1.1057$, cut $10/11>\gamma$.
  Hydrogen $N_0(1)=2$ replayed. q1 remainders $2.953$, $3.892$,
  $3.9781$ unchanged.

## 2026-08-27 — q6 dead line: $R\le 9$ cut

The mass-opt identities still only give $Q>R/(R+1)$. At $R=9$
that is $0.9$, so $\min(\gamma_9,9/10)\le 0.9$ and the leading
is at least $1.1111>1.1035$. Same wall at $R=8$ ($1.125$).
Residue: `compute/q6/certs/r9_cut.json`. A sharper large-aspect
cut would reopen this line; none is certified.

$s>3$ along Lemma 4.3 is still residue (two-shell $s=4$ rational
$-1025/2048$). Lieb still gives the best integers at $Z=2,\ldots,6$.

## 2026-08-27 — q6 scan: more bins at $R=10$

SLSQP plus the $P_{\max}$ tax (`certs/scan_compact.json` after
the scan is stored):

- $R=10$, $n=30$ (q5 row): predicted $1.103463$.
- $R=10$, $n=31$: $1.102938$.
- $R=10$, $n=32$: $1.102546$ ($2^{32}-1$ faces).
- $R=9.8$, $n=32$: $1.102384$, but $\gamma$ sits $2.8\cdot 10^{-4}$
  below the cut $9.8/10.8$ — tighter than the $R=10$ row.

The live line is $R=10$ with $n=32$. Face enumeration is the
certificate, not the SLSQP prediction.

## 2026-08-27 — q6 dent

Same HPS §7 chain with $\beta_3\ge 0.906992$ (aspect $10$,
$n=32$ faces, $\varphi=0.9108$):

$$
N<1.1026Z+3.853\,Z^{1/3}+0.01320+0.1828\,Z^{-1/3}+0.019500\,Z^{-2/3}
\qquad(Z\ge 4),
$$

$$
N_c<1.1026Z+3.938\,Z^{1/3}\qquad(Z\ge 4).
$$

Certified: `certs/lift.json`, interval §7 in `tighten_leading.py`,
stdlib `verify_lift.py` / `verify_rebuild.py`, C and Rust on the
$10/11$ algebra, mass-opt scan with no counterexample, stored
$R=10$ $n=32$ faces ($4{,}294{,}967{,}295$, copositive, $1157$
residual skips, $\min m^\top Mm>6\cdot 10^{-4}$). $1/\gamma=1.102546$
prints as $1.1026$. Cut $10/11>\gamma$. $1.1168$ stays withdrawn.
q1 remainders unchanged. $N_0(Z)-Z$ bounded still open.

Replay: `problems/simon-ionization-excess/compute/q6/run_all.sh`.

## 2026-08-27 — q7 record replay

- HPS 2504.18487 still **v1 only** (25 Apr 2025). OpenAlex
  W4416381655 `cited_by_count` 0. Submission history lists
  only `[v1]` Fri 25 Apr 2025.
- Nam 1009.2367v3 and Benguria–González-Brantes 2511.07582v1
  unchanged: no later fermionic leading coefficient below the
  notebook $1.1026$.
- Independent replay of the q6 cert: `verify_lift.py` recon
  $\gamma=0.9069918524731921$, $1/\gamma=1.1025457365170288<1.1035$,
  cut $10/11>\gamma$. Rebuild matches $A$ to $10^{-15}$.
  Hydrogen $N_0(1)=2$ replayed. q1 remainders $2.953$, $3.892$,
  $3.9781$ unchanged.

## 2026-08-27 — q7 dead line: $R\le 9$ cut

The mass-opt identities still only give $Q>R/(R+1)$. At $R=9$
that is $0.9$, so $\min(\gamma_9,9/10)\le 0.9$ and the leading
is at least $1.1111>1.1026$. Same wall at $R=8$ ($1.125$) and
at $R=9.5$ ($1.10526$). Residue: `compute/q7/certs/r9_cut.json`.
A sharper large-aspect cut would reopen $R\le 9$; none is
certified.

$s>3$ along Lemma 4.3 is still residue (two-shell $s=4$ rational
$-1025/2048$). Lieb still gives the best integers at $Z=2,\ldots,6$.

$M=A-\gamma\mathrm{Sym}(c,1)/2$ at the predicted $n=33$ target
has two negative eigenvalues. Zeroing negative off-diagonals
does not make it PSD, so the PSD+NN shortcut is not a
certificate. Large principal submatrices stay non-PD.

## 2026-08-27 — q7 scan: more bins at $R=10$

SLSQP plus the $P_{\max}$ tax (`certs/scan_compact.json`):

- $R=10$, $n=32$ (q6 row): predicted $1.102546$.
- $R=10$, $n=33$: $1.102041$ ($2^{33}-1$ faces). Cut
  $10/11>\gamma$.
- $R=10$, $n=34$: $1.101667$.
- $R=10$, $n=35$: $1.101300$ ($2^{35}-1$ faces).
- $R=9.8$, $n=32$: $1.102384$, $\gamma$ still
  $2.8\cdot 10^{-4}$ below $9.8/10.8$.
- $R=9.8$, $n=33$: predicted $\gamma$ sits
  $3\cdot 10^{-5}$ *above* the cut, so the split would bind
  at $10.8/9.8\approx 1.10204$.

The live line is $R=10$ with $n=33$. Face enumeration is the
certificate, not the SLSQP prediction.

## 2026-08-27 — q7 dent

Same HPS §7 chain with $\beta_3\ge 0.907407$ (aspect $10$,
$n=33$ faces, $\varphi=0.9111$):

$$
N<1.1021Z+3.851\,Z^{1/3}+0.01320+0.1828\,Z^{-1/3}+0.019500\,Z^{-2/3}
\qquad(Z\ge 4),
$$

$$
N_c<1.1021Z+3.937\,Z^{1/3}\qquad(Z\ge 4).
$$

Certified: `certs/lift.json`, interval §7 in `tighten_leading.py`,
stdlib `verify_lift.py` / `verify_rebuild.py`, C and Rust on the
$10/11$ algebra, mass-opt scan with no counterexample, stored
$R=10$ $n=33$ faces ($8{,}589{,}934{,}591$, copositive, $2518$
residual skips, $\min m^\top Mm>4\cdot 10^{-4}$). $1/\gamma=1.102041$
prints as $1.1021$. Cut $10/11>\gamma$. $1.1168$ stays withdrawn.
q1 remainders unchanged. $N_0(Z)-Z$ bounded still open.

Replay: `problems/simon-ionization-excess/compute/q7/run_all.sh`.
