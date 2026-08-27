# Lift — more bins at aspect 10

Same Newton $Q=I/D$ and mass-opt cut $Q>10/11$ as q5. The q5
bottleneck was the compact $\gamma$ at $R=10$, $n=30$
($\varphi=0.9103$, $P$ error $\approx 0.00406$), not the cut.

Raising $n$ on the mid-radius Rayleigh:

- $R=10$, $n=32$, $\varphi=0.9108$ gives $\gamma=0.906992$,
  $1/\gamma=1.102546<1.1026$.
- Cut $10/11\approx 0.90909>\gamma$.

$4{,}294{,}967{,}295$ faces at the winning row, copositive,
$1157$ residual skips, $\min m^\top Mm>6\cdot 10^{-4}$.
Stdlib rebuild of $A$ matches the stored matrix to $10^{-15}$.

Same §7 chain. Printed

$$
N_c<1.1026Z+3.938\,Z^{1/3}\qquad(Z\ge 4).
$$

$R\le 9$ with the mass-opt cut cannot beat $1.1035$. The
withdrawn $1.1168$ stays withdrawn. Finite $Z$ and $N_0(Z)-Z$
stay residue.

Replay: `../run_all.sh`.
