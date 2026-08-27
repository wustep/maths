# Lift — $n=34$ at aspect 10

Same Newton $Q=I/D$ and mass-opt cut $Q>10/11$ as q8. The q8
bottleneck was the compact $P_{\max}$ tax at $n=33$. SLSQP
$\varphi$ at $n=34$ sits at $0.911456$.

Raising the bin count to $34$, target $0.9113$:

- Faces certify copositivity ($17{,}179{,}869{,}183$ faces,
  $4618$ residual skips, $\min m^\top Mm>5\cdot 10^{-4}$).
- $\gamma=0.907716$, $1/\gamma=1.101667<1.1017$.
- Cut $10/11\approx 0.90909>\gamma$.

Same §7 chain. Printed

$$
N_c<1.1017Z+3.936\,Z^{1/3}\qquad(Z\ge 4).
$$

$R\le 9$ with the mass-opt cut cannot beat $1.1020$. The
withdrawn $1.1168$ stays withdrawn. Finite $Z$ and $N_0(Z)-Z$
stay residue. $n=35$ remains a predicted printed $1.1013$.

Replay: `../run_all.sh`.
