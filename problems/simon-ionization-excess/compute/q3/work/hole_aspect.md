# HOLE? NO_HOLE_FOUND

Adversarial check of the proposed q3 aspect lift. No dent. No Borel
probability with \(Q<0.8995\), and no mass-stationary \(k\)-atomic
with \(Q\le 0.921\) and aspect \(\ge 12\).

Opened this pass: [HPS HTML](https://arxiv.org/html/2504.18487v1)
(4.1), Thm 4.2, Prop. 4.5. Class is \(D_3=P\cap H^{-1}\cap L_2\), so
\(D<\infty\). Radial shells (1D \(k\)-atomic) sit in that class
(\(\widehat\mu\sim j_0\), \(\int|\widehat\mu|^2/(1+|k|^2)<\infty\)).

## Strongest objection

Existence of a \(k\)-atomic minimizer is a one-line sketch, not a
compactness proof. The lift applies compact \(\gamma\) only to a
minimizer (critical \(\Rightarrow\) aspect \(<Q/(1-Q)\)). If for large
\(k\) the inf were approached only by non-critical measures with
aspect \(>12\) and \(Q<\gamma\), the lift would fail. I could not
build that sequence: stretching the 6-atomic local min out to
\(R=12\ldots50\) and reoptimising masses sends \(Q\to 0.9253\) and
breaks criticality (rel err \(0.003\to 0.080\)); forced-aspect
\(Q\)-mins degenerate to a \((k-1)\)-atomic. So this is an unwritten
step, not a numerical break.

Step 6 as written is false: at large \(r\), \(V-(Q/2)(r^2+D)\sim
(1-Q)r^2/2>0\), not negative. \(F(r)=2V/(r^2+D)\to 1\), so equality
on an unbounded support forces \(Q=1\). Repairable.

The \(R=12\) row’s 5 “singular” faces are residual skips
(\(10^{-8}\)–\(6\cdot10^{-8}\)), mixed sign, \(\mathrm{slsqp}\,
\min m^\top Mm\ge 0.009\). Not a hole in compact \(\gamma\).
\(D\)-aspect \(=\) \(m\)-aspect on \((0,\infty)\). Mass at 0: \(V(0)=D/2\),
equality \(\Rightarrow Q=1\). Lagrange is one multiplier: integrating
\(2V-Qr^2=\lambda\) against \(m\) forces \(\lambda=QD\).

## Formulas (hold)

On \(\mathrm{supp}\subseteq[1,R]\):
\(V(1)=D/2+M_{-1}/2\), \(V(R)=R^2/2+M_3/(2R)\).
Max abs err \(1.1\cdot10^{-13}\) on 80 random atomics.
Criticality \(\Rightarrow M_{-1}=Q+(Q-1)D\),
\(M_3=(Q-1)R^3+QDR\). On the q2 6-atomic local min
(\(Q=0.923231\), aspect \(2.91\), eq rel \(2\cdot10^{-7}\)):
moment errors \(5\cdot10^{-8}\), \(2\cdot10^{-8}\).
Then \(M_{-1}>0\Rightarrow D<Q/(1-Q)\) and
\(M_3>0\Rightarrow D>((1-Q)/Q)R^2\), hence \(R<Q/(1-Q)\).
Algebra: any mass-stationary measure with aspect \(12\) has
\(Q>12/13\approx 0.92308>0.921\).

## Numbers (no killer)

| object | \(Q\) | aspect | notes |
|---|---|---|---|
| compact \(\gamma\) \(R=12\) | \(\ge 0.899526\) | \(\le 12\) | D-aspect class |
| \(f_{\min}\) | \(0.894107\) | — | HPS Prop. 4.5 |
| power \(\alpha=-2\), \(n=3.5\) | \(0.920655\) | \(3.50\) | HPS Fig. 2 trial |
| 64-atom of that trial | \(0.920678\) | \(3.43\) | cap \(Q/(1-Q)=11.607<12\) |
| 6-atomic local min | \(0.923231\) | \(2.91\) | cap \(12.026>12\); not a \(Q_{\mathrm{hi}}\) |
| 2-atomic critical at \(R=12\) | \(0.994576\) | \(12\) | eq rel \(10^{-16}\) |
| best critical found at \(R=12\) (k=5) | \(0.978410\) | \(12\) | still \(\gg 0.921\) |
| forced-aspect-12 \(Q\)-min (k=8) | \(0.922580\) | \(12\) | **not** critical (rel \(0.065\)) |
| random 500 atomics | \(\ge 0.9241\) | \(\le 200\) | none \(<0.8995\) |
| two-clump / near-0 / heavy tail | \(\ge 0.9224\) | up to \(10^3\) | none \(<0.8995\) |

A trial with \(Q<12/13\) is required for the \(11.7<12\) slot. The
6-atomic does not give it; the 64-atom / power-law does.

## Scripts

- `probe_hole_aspect.py` → `probe_hole_aspect.json`
- `probe_crit_largeR.py` → `probe_crit_largeR.json`
- `dump_R12_singular.c` → `R12_singular_masks.txt`

Replay: `python3 probe_hole_aspect.py && python3 probe_crit_largeR.py`
and `gcc -O3 -o dump_R12_singular dump_R12_singular.c -lm && ./dump_R12_singular ../../q2/certs/beta3_mid_R12_n22.txt`.
