# q1 bounds — HPS / Nam replay

Compute notes for `compute/q1/`. dent / residue as in AGENTS.md.

## How to run

```bash
python3 replay_hps.py
python3 tighten_hps.py
python3 replay_nam_beta.py
```

or `./run_all.sh` from this folder (invokes the three scripts if present).
Needs numpy, scipy, mpmath. Writes `certs/hps_replay.json`,
`certs/hps_tight.json`, `certs/nam_beta.json`.

## Record replayed

Opened 2026-08-27: [HPS 2504.18487v1](https://arxiv.org/abs/2504.18487)
HTML, [Nam 1009.2367v3](https://arxiv.org/abs/1009.2367) HTML,
[FHJN 1808.09017](https://arxiv.org/abs/1808.09017) HTML.

HPS §7 chain with 1.456 from FHJN Theorem 1 (not replaced).
A later LT claim 1.44655 (arXiv:2403.04347) was not replayed and is
not used.

| printed | independent enclosure | valid? |
| --- | --- | --- |
| $b(2)\in(1.2071,1.2072)$ | $1.20710678118\ldots$ | yes |
| $b(3)\in(1.1184,1.1185)$ | $1.11843379920\ldots$ | yes |
| $1.1185$ upper on $b(3)$ | yes | yes |
| $a\le 2.953$ then $2.96$ | $a(5/2)=2.95203835\ldots$ | both yes |
| $c<1.5855$ | $1.58543698\ldots$ | yes |
| $a_1<3.893$ on $[\beta_3^{-1},5/2]$ | $\sup=a_1(5/2)=3.89949515\ldots$ | **no** |
| $a_1<3.90$ on that interval | yes | yes |
| extras $0.0134$, $0.184$, $0.0196$ | $0.01331468$, $0.18361503$, $0.01959174$ | yes |
| Nam $\beta\ge 0.8218$ | $g(0.843)=0.82180392\ldots$ | yes |
| Nam $\beta<0.8705$ | $115/81-(1/2)\ln 3=0.87044694\ldots$ | yes |

Closed forms for $b(2)$, $b(3)$ match a numerical max of
$(1+t^{s-1})/(1+t^s)$ on $[0,1]$. $C_1^{-1}=2.34131154\ldots$ and
$C_2^{-1/2}=2.21537683\ldots$ match Lemma A.6 / (A.18), the displayed
closed forms, and the three Lieb integrals for $f_p$.

HPS said the supremum of $a_1(x)$ on $[\beta_3^{-1},5/2]$ is at the
left endpoint. Independently it is a minimum in the middle and the
max is at $x=5/2$. So $3.893$ is only an enclosure of the left-endpoint
formula, not of their stated supremum. $3.90$ still covers $x=5/2$.

Nam $g(\lambda)$ at the maximiser $\lambda\approx 0.8434764$ equals
$0.82180662586\ldots$. The AM-GM equality geometry sits in the
triangle, so $\inf W_\lambda/(|x|+|y|)=g(\lambda)$ there. A $(r,s,$
angle$)$ grid agrees to a few $10^{-7}$ and is not a lower bound.
$1/0.8218=1.21684108\ldots$, which Nam rounds to $1.22$.

## What tightened (dent)

Same HPS theorem, tighter arithmetic, interval enclosures.

1. Exact $b(3)$ in $a_1$, not $1.1185$.
2. Lieb $N/Z<2+1/Z$ for the Prop. 2.5 range $Z\ge 4$, so $N/Z<9/4$
   not $5/2$. Then $a_1(x)$ on $[b(3),9/4]$ *is* maximised at the
   left, and $a_1<3.892$.
3. Evaluating the actual $a_1(x)$ is what shows (2). At $x=b(3)$ the
   crude $Z<N\beta_3$ is equality.
4. Scanning $\lambda$ does not move $a_1$: HPS already minimises the
   left-endpoint coefficient.
5. Intervals on every claimed decimal.

Certified inequalities (see `certs/hps_tight.json`):

- $N_c<b(2)Z+2.953\,Z^{1/3}$ for $Z\ge 2$ (printed $2.96$).
- $N<b(3)Z+3.892\,Z^{1/3}+0.0134+0.184\,Z^{-1/3}+0.0196\,Z^{-2/3}$
  for $Z\ge 4$ (printed $3.90$; extras unchanged).
- $N_c<b(3)Z+3.9781\,Z^{1/3}$ and $N_c<1.1185Z+3.9781\,Z^{1/3}$
  for $Z\ge 4$ (printed $4$).

$r=\lambda(N\beta_3)^{-1/3}<0.5$ still holds on the contradiction set
$N\ge\beta_3^{-1}Z$, $Z\ge 4$.

## What did not

No new argument for $\beta_3$, so no dent of the leading $1.1185$.
A second Nam trial (64 atoms on $[1,10]$) gives $\beta\le 0.87021$
and sits next to Nam's own $0.8702$ remark; that tightens only the
upper end of $\beta$, which does not improve an ionization *upper*
bound. Optimising a single power $r^{-\alpha}1_{[1,L]}$ recovers
Nam's $(\alpha,L)=(3/2,9)$ and does not beat $115/81-(1/2)\ln 3$.
