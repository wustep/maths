# Walkthrough — simon-ionization-excess

Discovery notes, not a cleaned proof. Beats: `refs/walkthrough-style.md`.

0. What was actually missing — a replayable certificate for the 2025 HPS numbers, and any finite handle that moves a printed inequality. The bounded-excess conjecture itself is the missing theorem. The leftover degree of freedom in HPS §7 is the interval on which they maximise $a_1(N/Z)$: they wrote $[ \beta_3^{-1},5/2]$ and then evaluated only the left endpoint.

1. Named false starts — beating $1.1185$ by taking $s>3$ (not proved); replacing the LT factor $1.456$ by an unreplayed 2024 claim; improving Nam’s $\beta$ lower bound far enough to matter (the ionization upper bound uses $1/\beta$, so an *upper* bound on $\beta$ is the wrong direction).

2. The useful failure — replaying $a_1(x)$ on HPS’s stated interval $[b(3),5/2]$ shows the maximum is at $x=5/2$, value $3.89949\ldots$, not at the left. Their $3.893$ is only the left-endpoint number. The printed $3.90$ still covers $5/2$, so Prop. 2.5 is safe. The failure teaches that the interval, not the algebra of $b(3)$, is the handle.

3. The click — Prop. 2.5 is for $Z\ge4$. Lieb already gives $N<2Z+1$, hence $N/Z<2+1/Z\le9/4$. On $[b(3),9/4]$ the maximum of $a_1$ *is* at the left, and $a_1<3.892$. The extras are unchanged. At $Z=4$ the collected $Z^{1/3}$ remainder is $<3.9781$, which beats the printed $4$.

4. The argument — same HPS chain: weight $|x|^3$, Lemma 6.4 with $\kappa$ from FHJN $1.456$, $\lambda=(5/12)^{1/3}$, contradiction assumption $N\ge\beta_3^{-1}Z+a_1 Z^{1/3}+\cdots$. The only change is the Lieb interval used to bound $a_1(N/Z)$, plus exact $b(3)$ in place of $1.1185$ inside that estimate. No new $\beta_3$.

5. Computer search — `replay_hps.py` / `tighten_hps.py` (mpmath intervals), `verify_remainder.py` (stdlib math, no shared code), `verify_b3.c` and `verify_b3.rs` (closed form vs ternary max of $(1+t^{s-1})/(1+t^s)$). Hylleraas exact rationals for $H^-$. Lean cubic witnesses for the printed $b(3)$ enclosure. UHF table is heuristic.

6. Proven vs still open — printed HPS remainders $2.96$, $3.90$, $4$ move to $2.953$, $3.892$, $3.9781$. Leading $1.1185$ does not move. $N_0(Z)-Z$ bounded is open. $N_0(1)=2$ is a replay. He$^-$ binding is residue. 1984 10(a) is open.

## Later the same day — try to move 1.1185

0. What was actually missing — Proposition 4.5 pulls $\min f$ out of a weighted average of $f(t)$. Figure 2 already says that minimum is not sharp. The leftover degree of freedom is a *global* lower bound on that average, or a proof that Lemma 4.3 survives past $s=3$, or an integer bound at a concrete $Z>1$. A remainder shave is not the handle.

1. Named false starts — $s>3$ by the same IMS/Hardy chain (the improved Hardy constant is $9/4$, so $c_H-s^2/4\ge0$ only for $s\le3$); using Nam’s $\beta$ upper end (wrong direction); excluding $N=4$ at $Z=2$ by pair geometry or a new Lieb weight; treating hydrogen uniqueness as new; a tail polynomial that claimed $1.1168$.

2. The useful failure — $I_s(\nu)$ on two-shell dipoles goes negative the moment $s>3$ (exact $-1025/2048$ at $s=4$). So $b(4)\approx1.083$ cannot be fed into Theorem 2.2. Separately, $h(0,1)\approx0.991$ on the proposed tail lift sits *above* the HPS power-law trial $0.921$. The lift was claiming a lower bound larger than an explicit measure. That kills $1.1168$ and teaches that a compact-window bound is not a global bound unless the tail estimate is actually a lower bound.

3. The click — after Newton, $I/D$ is an average of $f(t)$ and cannot put all pair-weight at $t=t_0$ (self-pairs and non-adjacent ratios). On measures whose $D$-mass has aspect $\le4$, a mid-radius Rayleigh plus a total-variation reweighting error *does* certify $Q\ge0.901924$. The numerical minimizer has aspect $\sim3.50$, so it lives in that class. The jump $1.1185\to1.1087$ is real *inside the class* and empty for Theorem 2.2.

4. The argument that did not close — to replace $1.1185$ one still needs $Q\ge\gamma>1/b(3)$ for every radial probability, or a proof that a minimizer has aspect $\le4$. First variation for a probability is $V(r)=(Q/2)(r^2+D)$ on the support. Geometric $t_0$-chains stay above $0.937$; a two-window split with cross terms at $\min f$ returns $\min f$. Neither is a lift. Finite $Z$: the tetrahedron gives $\alpha_{4,2}\cdot3<2$ ($54<64$), so $s=2$ pair geometry cannot beat Lieb at helium.

5. Computer search — `verify_beta3.c` exhaustive faces ($n=18$, $262143$ faces, $0$ singular, $\min m^TMm>0.0128$); independent Rust $n=16$ rebuild; `s_gt_3.py` interval + rational $s=4$; `verify_tetra.c` / `.py`; `aspect_try.py` chains and random atomics; q1 remainder scripts left untouched.

6. Proven vs still open — compact $Q\ge0.901924$ on aspect $\le4$ is certified and is not a published-record dent. $s>3$ is closed along HPS Lemma 4.3. Finite-$Z$ integer bounds unchanged (Lieb). Leading $1.1185$ unchanged. $N_0(Z)-Z$ bounded open. $1.1168$ withdrawn.
