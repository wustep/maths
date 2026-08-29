# Leftover — $n=37$ at aspect 10

Same Newton $Q=I/D$ and mass-opt cut $Q>10/11$ as q11. The q11
bottleneck was the compact $P_{\max}$ tax at $n=36$.

The stored q11 cert stays frozen: aspect $10$, $n=36$,
target $\varphi=0.9117$, $\gamma=0.908315$, $1/\gamma=1.100940$,
printed $1.1010$. Those faces were not re-enumerated.

SLSQP at $n=37$, target $0.9119$: $\varphi=0.912082$, $P$ error
$0.003294$, predicted $\gamma=0.908606$, $1/\gamma=1.100587$,
printed $1.1006$ if faces certify. The dump of $2^{37}-1$ faces
was stopped with the slowest shard at about $29.6\%$. Scanned
faces stay copositive, $\min\varphi=0.912085>0.9119$. Incomplete
search is not a bound. Printed leading stays $1.1010$.

$R\le 9$ with the mass-opt cut cannot beat $1.1010$. The
withdrawn $1.1168$ stays withdrawn. Finite $Z$ and $N_0(Z)-Z$
stay leftover.

Replay: `../run_all.sh`.
Checkpoint: `../certs/leftover_n37.json`.
