# Lift — more bins at aspect 10

Same Newton $Q=I/D$ and mass-opt cut $Q>10/11$ as q6. The q6
bottleneck was the compact $\gamma$ at $R=10$, $n=32$
($\varphi=0.9108$, $P$ error $\approx 0.00381$), not the cut.

Raising $n$ on the mid-radius Rayleigh:

- $R=10$, $n=33$, $\varphi=0.9111$ gives $\gamma=0.907407$,
  $1/\gamma=1.102041<1.1021$.
- Cut $10/11\approx 0.90909>\gamma$.

$8{,}589{,}934{,}591$ faces at the winning row, copositive,
$2518$ residual skips, $\min m^\top Mm>4\cdot 10^{-4}$.
Stdlib rebuild of $A$ matches the stored matrix to $10^{-15}$.

Same §7 chain. Printed

$$
N_c<1.1021Z+3.937\,Z^{1/3}\qquad(Z\ge 4).
$$

$R\le 9$ with the mass-opt cut cannot beat $1.1026$. The
withdrawn $1.1168$ stays withdrawn. Finite $Z$ and $N_0(Z)-Z$
stay residue.

Replay: `../run_all.sh`.
