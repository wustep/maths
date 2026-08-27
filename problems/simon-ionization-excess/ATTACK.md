# Attack log — simon-ionization-excess

Chronological attempts, newest last. A failed attack belongs here too.

## 2026-08-27 — mint and fetch

- Folder minted with `scripts/new-problem.sh simon-ionization-excess`. No sibling PR.
- Record fetched before any claim. Wikipedia / MathWorld used only as a map to Simon 2000 #9 and 1984 10(a).
- arXiv: Nam 1009.2367v3, Nam survey 1209.3642v2, HPS 2504.18487v1, Solovej HF math-ph/0012026v3. Further ids in `RESEARCH.md`.
- Published non-asymptotic record to beat: Hundertmark–Pattakos–Schulz, $N_c<1.1185Z+4Z^{1/3}$ for $Z\ge4$, and Prop. 2.5 remainder $3.90$. Nam $1.22$ and Lieb $2Z+1$ remain the comparison for small $Z$.
- Campaign in `compute/q1/`: replay HPS/Nam constants; try to tighten the HPS remainder; Hylleraas certificate that $N_0(1)=2$; Lean for $b(3)$ and the Lieb triangle; HF/DFT heuristics and a $\Delta E$ table (residue unless a proof).

## 2026-08-27 — second-language $b(s)$ and published envelope table

- `compute/q1/verify_b3.c` (long double closed form) and `verify_b3.rs` (ternary/grid max of $(1+t^{s-1})/(1+t^s)$). Same interval assertions as HPS: $1.1184<b(3)<1.1185$ and $1.2071<b(2)<1.2072$. Replay via `./run_all.sh`.
- `compare_bounds.py` writes the piecewise published envelope for integer $Z=1..200$. Not a dent: table only. C and Rust agree on $b(3)$ to $10^{-12}$. Smallest integer $Z$ where the Prop. 2.5 RHS is below Nam is $28$; below Lieb $\lfloor 2Z\rfloor$ is $10$; below HPS $s=2$ is $36$ (paper Remark 2.6 had $35.8$). See `certs/best_published.json`.
