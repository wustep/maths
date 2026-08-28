# Lift — $n=36$ at aspect 10

Same Newton $Q=I/D$ and mass-opt cut $Q>10/11$ as q10. The q10
bottleneck was the compact $P_{\max}$ tax at $n=35$. SLSQP
$\varphi$ at $n=36$ is predicted in `../certs/scan_compact.json`.

Raising the bin count to $36$, predicted target $0.9117$:
SLSQP $\varphi=0.911881$, $P$ error $0.00339$,
$\gamma=0.908315$, $1/\gamma=1.100940$, printed $1.1010$
if faces certify. Cut $10/11>\gamma$. Face enumeration is
the certificate. Until the faces dump is copositive, the
printed leading stays $1.1013$.

$R\le 9$ with the mass-opt cut cannot beat $1.1013$. The
withdrawn $1.1168$ stays withdrawn. Finite $Z$ and $N_0(Z)-Z$
stay leftover. A higher-target probe on the $n=34$ or $n=35$
matrix is not an $n=36$ dent.

Replay: `../run_all.sh`.
