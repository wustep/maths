# Dead line — R=9 with the mass-opt cut

The mass-stationary identities force $Q>R/(R+1)$ on a used
support of aspect $\ge R$. At $R=9$ that cut is $9/10=0.9$, so

$$
\min(\gamma_9,9/10)\le 0.9,\qquad 1/0.9=1.1111>1.1026.
$$

No compact $\gamma_9$ can beat the q6 printed leading $1.1026$
while the large-aspect bound stays $R/(R+1)$. The same wall
holds at $R=8$ ($8/9$, leading $1.125$). q6 already recorded
this wall against $1.1035$; it is stricter against $1.1026$.

A sharper large-aspect cut ($Q>c>0.90699$ on aspect $\ge 9$)
would reopen this line. Two-atom mass-crit still sits near
$0.92$, but that is a search, not a cut.

$R=9.8$ with the cut binding would print $10.8/9.8\approx 1.10204$,
which beats $1.1026$, but only after a compact $\gamma$ that
actually clears $9.8/10.8$. q6's $n=32$ prediction sat
$2.8\cdot 10^{-4}$ below that cut.

Replay: `python3 r9_cut.py`.
