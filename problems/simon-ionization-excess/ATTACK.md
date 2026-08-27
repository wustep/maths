# Attack log — simon-ionization-excess

Chronological attempts, newest last.

## 2026-08-27 — mint and record

Opened Simon's 2000 reprint (Caltech r40.pdf). Problem 9 is
"Prove that N0(Z) − Z is bounded as Z → ∞." The reprint already
quotes Lieb N0(Z) < 2Z and Lieb–Sigal–Simon–Thirring
N(Z)/Z → 1, and Zhislin N0(Z) ≥ Z.

Opened the 1984 reprint (Caltech R27.pdf) as the pointer for 10(a)
(monotonicity of ionization energy) and 10(c) (small excess charge).
Lewin, *C. R. Physique* 26 (2025), 369–380, still lists both as open
for Coulomb atoms.

Fetched the linear-bound record:

- Nam, arXiv:1009.2367: Nc < 1.22 Z + 3 Z^{1/3}, beats Lieb for
  Z ≥ 6.
- Hundertmark–Pattakos–Schulz, arXiv:2504.18487: leading coefficient
  b(3) ∈ (1.1184, 1.1185) with an explicit Z^{1/3} remainder for
  Z ≥ 4; coarser line 1.1185 Z + 4 Z^{1/3}. Their s=2 line already
  improves Nam for every Z ≥ 2.
- Nam, arXiv:2206.15393, and Lewin 2025: the O(1) excess is still
  open, even with a huge C.

Replayed the closed form for b(3) and the comparison table of the
three published upper bounds. Nam first undercuts Lieb at Z = 6.
The s=3 HPS line undercuts their s=2 line at Z = 36, matching their
"Z ≥ 35.8" remark. That is a replay, not a new bound.

No attempt to prove bounded excess or 1984 10(a).

Replay: `cd problems/simon-ionization-excess/compute && sh run_all.sh`
