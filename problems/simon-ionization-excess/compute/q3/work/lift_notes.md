# Lift — mass-opt dichotomy

HPS (4.1), $s=3$: $\beta_3=\inf I_3/D_3$ on $D_3=P\cap H^{-1}\cap L_2$.
Theorem 4.2: radial measures achieve the inf for $s\le 3$. After
Newton,

$$
Q=\frac{I}{D},\qquad
g(r,u)=\frac{r^3+u^3}{2\max(r,u)},\qquad
D=\int r^2\,dm.
$$

q2 compact (R=12, n=22 faces): $Q\ge\gamma=0.899526$ on $D$-aspect
$\le 12$. Five singular faces are residual skips; copositive, 
$\min m^\top Mm>0.004$.

Mass-stationarity on a finite support (one Lagrange multiplier)
gives $V(r_i)=(Q/2)(r_i^2+D)$ at every used atom. With
$\mathrm{inf\,supp}=1$ and $\mathrm{sup\,supp}=R$,

$$
M_{-1}=Q+(Q-1)D,\qquad M_3=(Q-1)R^3+QDR.
$$

Both positive $\Rightarrow R<Q/(1-Q)$ $\Rightarrow Q>R/(R+1)$.
At $R=12$, $Q>12/13>\gamma$.

Any finitely atomic $m$: mass-opt on the same radii exists (simplex
compact). Either the used aspect is $\le 12$ and $Q\ge\gamma$, or
it is $\ge 12$ and $Q>12/13$. So every atomic measure has $Q\ge\gamma$.

A compactly supported radial probability is a weak limit of finite
spherical shells, with $Q$ continuous ($g$ bounded on $[a,b]^2$,
$D\ge a^2$). A finite-$D$ measure is a $Q$-limit of compact
truncations ($r^2$ is UI for that one measure). Hence
$\beta_3\ge\gamma$ and $\beta_3^{-1}\le 1.11170<1.1118<1.1185$.

Not the aspect-$\le 4$ number $1.1087$. Not the withdrawn $1.1168$.

Replay: `../run_all.sh`.
