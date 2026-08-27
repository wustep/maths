# q9 — past the leading coefficient 1.1020

q8 lifted the aspect-10 compact bound and replaced printed $1.1021$
by $1.1020$ at $n=33$ bins, target $0.9112$. The leftover slack
is more bins at the same split: SLSQP at $n=34$ sits at
$\varphi\approx 0.91145$. $R\le 9$ with the mass-opt cut cannot
beat $1.1020$.

This folder keeps the split at aspect $10$ and raises the
mid-radius bin count to $34$. Predicted printed leading $1.1017$
if faces certify $Q\ge\varphi-P_{\max}(1-f_{\min})$ at target
$0.9113$ and the cut $10/11$ still exceeds that $\gamma$.

The withdrawn $1.1168$ stays withdrawn. Finite $Z$ and $N_0(Z)-Z$
stay residue. $s>3$ along Lemma 4.3 stays residue.

```bash
./run_all.sh
```

Exit 0 with a stored `raise_*.json` is a leading-coefficient lift.
Without that row it is a recorded residue. Leftover probes in `work/`.
