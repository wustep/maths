# Lift — unused $\varphi$ at aspect 10

Same Newton $Q=I/D$ and mass-opt cut $Q>10/11$ as q7. The q7
bottleneck was the compact target $0.9111$ on the $n=33$
mid-radius matrix. SLSQP $\varphi$ and the face $\min\varphi$
both sit at $0.911221$.

Raising the target to $0.9112$:

- Faces certify copositivity ($8{,}589{,}934{,}591$ faces,
  $2455$ residual skips, $\min m^\top Mm>7\cdot 10^{-5}$).
- $\gamma=0.907507$, $1/\gamma=1.101920<1.1020$.
- Cut $10/11\approx 0.90909>\gamma$.

Same §7 chain. Printed

$$
N_c<1.1020Z+3.937\,Z^{1/3}\qquad(Z\ge 4).
$$

$R\le 9$ with the mass-opt cut cannot beat $1.1021$. The
withdrawn $1.1168$ stays withdrawn. Finite $Z$ and $N_0(Z)-Z$
stay residue. $n=34$ remains a predicted printed $1.1017$.

Replay: `../run_all.sh`.
