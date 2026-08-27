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
