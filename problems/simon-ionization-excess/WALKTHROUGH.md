# Walkthrough — simon-ionization-excess

Discovery notes, not a cleaned proof. Beats: `refs/walkthrough-style.md`.

0. What was actually missing — a replayable certificate for the 2025 HPS numbers, and any finite handle that moves a printed inequality. The bounded-excess conjecture itself is the missing theorem. The leftover degree of freedom in HPS §7 is the interval on which they maximise $a_1(N/Z)$: they wrote $[ \beta_3^{-1},5/2]$ and then evaluated only the left endpoint.

1. Named false starts — beating $1.1185$ by taking $s>3$ (not proved); replacing the LT factor $1.456$ by an unreplayed 2024 claim; improving Nam’s $\beta$ lower bound far enough to matter (the ionization upper bound uses $1/\beta$, so an *upper* bound on $\beta$ is the wrong direction).

2. The useful failure — replaying $a_1(x)$ on HPS’s stated interval $[b(3),5/2]$ shows the maximum is at $x=5/2$, value $3.89949\ldots$, not at the left. Their $3.893$ is only the left-endpoint number. The printed $3.90$ still covers $5/2$, so Prop. 2.5 is safe. The failure teaches that the interval, not the algebra of $b(3)$, is the handle.

3. The click — Prop. 2.5 is for $Z\ge4$. Lieb already gives $N<2Z+1$, hence $N/Z<2+1/Z\le9/4$. On $[b(3),9/4]$ the maximum of $a_1$ *is* at the left, and $a_1<3.892$. The extras are unchanged. At $Z=4$ the collected $Z^{1/3}$ remainder is $<3.9781$, which beats the printed $4$.

4. The argument — same HPS chain: weight $|x|^3$, Lemma 6.4 with $\kappa$ from FHJN $1.456$, $\lambda=(5/12)^{1/3}$, contradiction assumption $N\ge\beta_3^{-1}Z+a_1 Z^{1/3}+\cdots$. The only change is the Lieb interval used to bound $a_1(N/Z)$, plus exact $b(3)$ in place of $1.1185$ inside that estimate. No new $\beta_3$.

5. Computer search — `replay_hps.py` / `tighten_hps.py` (mpmath intervals), `verify_remainder.py` (stdlib math, no shared code), `verify_b3.c` and `verify_b3.rs` (closed form vs ternary max of $(1+t^{s-1})/(1+t^s)$). Hylleraas exact rationals for $H^-$. Lean cubic witnesses for the printed $b(3)$ enclosure. UHF table is heuristic.

6. Proven vs still open — printed HPS remainders $2.96$, $3.90$, $4$ move to $2.953$, $3.892$, $3.9781$. Leading $1.1185$ does not move. $N_0(Z)-Z$ bounded is open. $N_0(1)=2$ is a replay. He$^-$ binding is residue. 1984 10(a) is open.
