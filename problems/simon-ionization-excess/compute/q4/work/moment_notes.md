# q4 moment region — covering frozen

Light theory for lifting the aspect-≤4 compact bound
$\gamma_4=0.901924$ ($1/\gamma_4=1.1087$) via endpoint algebra and
moment inequalities alone. Not a dent.

## Setup

Newton kernel $g(r,u)=(r^3+u^3)/(2\max(r,u))$, $Q=I/D$, $D=\int r^2\,dm$.
Mass-stationarity at both ends of $\mathrm{supp}\subseteq[1,R]$ gives

$$
M_{-1}=Q+(Q-1)D,\qquad M_3=(Q-1)R^3+QDR.
$$

Positivity $M_{-1}>0$, $M_3>0$ $\Leftrightarrow$ $D\in\bigl(\frac{1-Q}{Q}R^2,\,
\frac{Q}{1-Q}\bigr)$, nonempty iff $Q>R/(R+1)$.

Extra linear constraints from $\mathrm{supp}\subseteq[1,R]$: Markov
$M_{-1}\in[1/R,1]$, $M_3\in[1,R^3]$, $D\in[1,R^2]$; Hölder
$\exists M_1\in[1,R]$ with $M_1M_{-1}\ge1$ and $D\ge M_1^2$; Chebyshev
from $(r-1)^2\ge0$.

Hausdorff step: $(M_{-1},1,D,M_3)$ must be a moment sequence of a
probability on $[1,R]$ (checked by $2/3$-atom reconstruction in
`moment_region.py`).

## Answers

### 1. $R=4$, target $\gamma_4=0.901924$, cut $4/5=0.8$

| layer | $Q<\gamma_4$? | witness |
|---|---|---|
| positivity + endpoint identities only | **nonempty** | scan finds pairs with $Q\approx0.80$, $D\approx4$ in the positivity slab |
| + Hölder / Chebyshev / Markov | **nonempty** | best scan: $Q\approx0.894$, $D\approx2.69$ |
| + Hausdorff / measure on $[1,4]$ | **empty** (scan) | sample above fails $3$-atom reconstruction; no endpoint-consistent $2$-atom has $Q<\gamma_4$ |

So endpoint identities plus the listed moment inequalities **do not**
alone force $Q\ge\gamma_4$: the abstract $(Q,D)$ slab still has points
below $\gamma_4$ until representability is imposed.

Actual mass-stationary measures with used aspect $\ge4$ sit far above
$\gamma_4$: forced-endpoint mass-opt $Q\approx0.923$ (`large_aspect.py`);
$3$-point stationarity min $Q\approx0.941$; $2$-atom mass-critical
$Q=0.97$ (`two_atom_crit.py`). None of these is a counterexample to a
lift — they confirm the numerical floor is above $\gamma_4$.

**Rigorous $R=4$ lift from moments alone:** **no**. The cut
$4/5<\gamma_4$ does not lift; the linear moment package without
Hausdorff still leaves a nonempty sub-$ \gamma_4$ region; Hausdorff
closes that region in scan but is not a short pen-and-paper bound.

### 2. $R=8$ and $R=9$

| $R$ | $\gamma_R$ | cut $R/(R+1)$ | cut $>\gamma$? | support-only $Q<\gamma_R$ | full moment $Q<\gamma_R$ |
|---|---|---|---|---|---|
| 8 | $0.900500$ | $8/9\approx0.8889$ | no | **empty** (scan) | **empty** |
| 9 | $0.900257$ (interp.) | $0.9$ | no | **empty** | **empty** |

At $R=8$ the positivity slab below $\gamma_8$ is narrow ($\approx0.012$
wide); Chebyshev/Hölder already kill every scanned pair. At $R=9$ the
gap cut–$\gamma$ is $\approx2.6\times10^{-4}$; again empty after linear
checks.

Improving the large-aspect cut $Q>R/(R+1)$ cannot beat q3’s
$1.1118$ here: at $R=4$ the cut is $0.8\ll\gamma_4$; at $R=8,9$ the cut
is below $\gamma_R$ and linear moments add nothing below $\gamma_R$.

### 3. One extra interior stationarity radius

Mass-stationarity at $\{1,t,R\}$ **does not** close the abstract
$(Q,D)$ hole at $R=4$ (support-feasible pairs below $\gamma_4$ still
exist without a representing measure). For **actual** $3$-atomic
stationary measures the minimum $Q$ rises to $\approx0.941$ at $R=4$,
well above $\gamma_4$. Interior stationarity is stronger than needed for
the lift question and does not produce a simple closed form.

### 4. Replay

```bash
python3 moment_region.py
```

Writes `moment_region.json`.
