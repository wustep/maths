# Lift — unused $\varphi$ or more bins at aspect 10

Same Newton $Q=I/D$ and mass-opt cut $Q>10/11$ as q7. The q7
bottleneck was the compact $\gamma$ at $R=10$, $n=33$
($\varphi=0.9111$, $P$ error $\approx 0.00369$), not the cut.

Two predicted rows that print below $1.1021$ if faces certify:

- $R=10$, $n=33$, target $0.9112$ on the same matrix as q7.
  SLSQP $\varphi\approx 0.91122$. Predicted $\gamma\approx 0.907507$,
  $1/\gamma\approx 1.10192$, printed $1.1020$. Cut $10/11>\gamma$.
- $R=10$, $n=34$, $\varphi=0.9113$. Predicted $\gamma\approx 0.907716$,
  $1/\gamma\approx 1.10167$, printed $1.1017$. Cut $10/11>\gamma$.

$R\le 9$ with the mass-opt cut cannot beat $1.1021$. The
withdrawn $1.1168$ stays withdrawn. Finite $Z$ and $N_0(Z)-Z$
stay residue.

Replay: `../run_all.sh`.
