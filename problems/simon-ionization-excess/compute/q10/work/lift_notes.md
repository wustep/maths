# Lift — $n=35$ at aspect 10

Same Newton $Q=I/D$ and mass-opt cut $Q>10/11$ as q9. The q9
bottleneck was the compact $P_{\max}$ tax at $n=34$. SLSQP
$\varphi$ at $n=35$ sits at $0.911672$.

Raising the bin count to $35$, target $0.9115$:

- Faces certify copositivity ($34{,}359{,}738{,}367$ faces,
  $8362$ residual skips, $\min m^\top Mm>5\cdot 10^{-4}$,
  $\min\varphi=0.911674$).
- $\gamma=0.908018$, $1/\gamma=1.101300<1.1013$.
- Cut $10/11\approx 0.90909>\gamma$.

Same §7 chain. Printed

$$
N_c<1.1013Z+3.935\,Z^{1/3}\qquad(Z\ge 4).
$$

$R\le 9$ with the mass-opt cut cannot beat $1.1017$. The
withdrawn $1.1168$ stays withdrawn. Finite $Z$ and $N_0(Z)-Z$
stay leftover. The $n=34$ target-$0.9114$ probe was not run
and is not this dent.

Replay: `../run_all.sh`.
