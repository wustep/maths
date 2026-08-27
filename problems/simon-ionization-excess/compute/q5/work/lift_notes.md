# Lift — more bins at aspect 10

Same Newton $Q=I/D$ and mass-opt cut $Q>10/11$ as q4. The q4
bottleneck was the compact $\gamma$ at $R=10$, $n=26$
($\varphi=0.9091$, $P$ error $\approx 0.00469$), not the cut.

Raising $n$ on the mid-radius Rayleigh:

- $R=10$, $n=28$, $\varphi=0.9097$ gives $\gamma=0.905348$,
  $1/\gamma=1.104547<1.1046$.
- $R=10$, $n=30$, $\varphi=0.9103$ gives $\gamma=0.906238$,
  $1/\gamma=1.103463<1.1035$.
- Cut $10/11\approx 0.90909>\gamma$ on both rows.

$1{,}073{,}741{,}823$ faces at the winning row, copositive,
$420$ residual skips, $\min m^\top Mm>5\cdot 10^{-4}$.
Stdlib rebuild of $A$ matches the stored matrix to $10^{-15}$.

Same §7 chain. Printed

$$
N_c<1.1035Z+3.941\,Z^{1/3}\qquad(Z\ge 4).
$$

$R\le 9$ with the mass-opt cut cannot beat $1.1057$. The
withdrawn $1.1168$ stays withdrawn. Finite $Z$ and $N_0(Z)-Z$
stay residue.

Replay: `../run_all.sh`.
