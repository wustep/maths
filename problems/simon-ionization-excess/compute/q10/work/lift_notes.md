# Lift leftover — $n=35$ at aspect 10

Same Newton $Q=I/D$ and mass-opt cut $Q>10/11$ as q9. The q9
bottleneck was the compact $P_{\max}$ tax at $n=34$. Predicted
SLSQP $\varphi$ at $n=35$ sits near $0.91167$.

Raising the bin count to $35$, target $0.9115$:

- Faces must certify copositivity ($34{,}359{,}738{,}367$ faces).
- Predicted $\gamma\approx 0.90802$, $1/\gamma\approx 1.10130$.
- Printed leading $1.1013$ if the faces dump is copositive and
  $10/11>\gamma$.

An optional cheaper probe retargets $\varphi=0.9114$ on the
existing $n=34$ matrix (predicted printed $1.1016$). That is
not an $n=35$ dent; it still needs a full re-enum of
$2^{34}-1$ faces because $M$ depends on the target.

$R\le 9$ with the mass-opt cut cannot beat $1.1017$. The
withdrawn $1.1168$ stays withdrawn. Finite $Z$ and $N_0(Z)-Z$
stay residue.

Replay: `../run_all.sh`.
