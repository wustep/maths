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

## Later the same day — lift the aspect-12 class

0. What was actually missing — a *global* lower bound on $Q$ strictly above $\min f$, or a proof that a minimizer of $\beta_3$ has bounded aspect. The compact $\gamma$ at $R=12$ was already $0.899526$, so $1/\gamma=1.11170<1.1185$ *inside that class*. The degree of freedom was the large-aspect measures.

1. Named false starts — treating existence of a continuum minimizer as the only lift (the first-variation identity at large $r$ is $\psi(r)\sim(1-Q)r^2/2>0$, which bounds support of a *critical* point but does not, by itself, bound $Q$ for a non-critical tail); using the aspect-$\le 4$ number $1.1087$ unrestricted; two-window $p_{12}$ (still collapses); $s>3$ and finite-$Z$ integers (still residue); a signed Toeplitz symbol that dips *below* $\min f$.

2. The useful failure — a forced-aspect-$12$ search can sit at $Q\approx 0.9226<12/13$ if it is *not* mass-stationary (relative first-variation error $0.065$). The algebra $Q>12/13$ is only for mass-critical points that use both ends. Incomplete optimisation is not a counterexample. The $R=12$ “singular” faces are mixed-sign residual skips, not a hole in copositivity.

3. The click — mass-optimisation on a *fixed* finite set of radii always exists, and *that* point is mass-stationary. If the used aspect stays $\ge 12$, the moment identities force $Q>12/13>\gamma_{12}$. If an endpoint is dropped, the used aspect falls into the compact class. Every atomic measure is at least as large as its mass-opt, hence $Q\ge\gamma_{12}$. No global existence theorem is required.

4. The argument — Theorem 4.2, radial $Q$. Compact cert on aspect $\le 12$. Mass-opt dichotomy on aspect $\ge 12$. Weak $Q$-continuity on compact radial support (finite spherical shells). Truncation of a finite-$D$ measure ($r^2$ is UI for that one measure). Same §7 chain with $\beta_3\ge\gamma_{12}$, Lieb $9/4$ on $Z\ge 4$, extras recomputed. Printed leading $1.1118$ is a round-up of $1.111696\ldots$.

5. Computer search — stored $R=12$, $n=22$ faces (copositive, $5$ skips); stdlib reconstruction of $\gamma=\phi-P_{\max}(1-f_{\min})$; C and Rust on the $12/13$ grid and the $V(1)$, $V(R)$ identities; mass-opt scan, min $Q=0.923274>12/13$; $64$-atom trial $Q<12/13$ (upper bound on $\beta_3$ only); interval §7 in `tighten_leading.py`.

6. Proven vs still open — printed leading $1.1185$ moves to $1.1118$. Remainders $2.953$, $3.892$, $3.9781$ stay. Aspect-$\le 4$ $1.1087$ is not unrestricted. $1.1168$ stays withdrawn. $s>3$ closed along Lemma 4.3. Finite-$Z$ integers unchanged (Lieb). $N_0(Z)-Z$ bounded open.

## Later the same day — raise the compact $\gamma$

0. What was actually missing — after the mass-opt lift, the leading coefficient is $1/\gamma_R$ for the smallest compact class whose cut $R/(R+1)$ still exceeds $\gamma_R$. At $R=12$ that $\gamma$ was $0.899526$ because the face target sat at $0.9055$ and the $P_{\max}$ tax was $0.006$. The degree of freedom was the target and the number of bins, not a new tail polynomial.

1. Named false starts — quoting $1.1087$ unrestricted (the $R=4$ cut is $4/5$); a moment-only $R=4$ lift (Hölder leaves a nonempty abstract $(Q,D)$ hole); replacing $P(1-f_{\min})$ by a spread (vertices have $\lambda=1$); $s>3$ and finite-$Z$ integers (still residue); recycling the withdrawn $1.1168$.

2. The useful failure — two-atomic mass-critical $Q(R)$ sits far above $R/(R+1)$ (at $R=4$, $Q\approx 0.970$), so the positivity cut is loose on $2$-atoms and still the only closed large-aspect bound. Forced-endpoint $k$-atomic mass-opt stays above $0.92$. That teaches that the jump is in the compact certificate, not in a sharper cut.

3. The click — SLSQP $\varphi$ at $R=12$, $n=22$ is $0.90692$, already above the certified $0.9055$. Raising the target is a re-run of the same faces. Dropping the split from $12$ to $10$ and taking $n=26$ shrinks $P$ enough that $\gamma=0.904414$ and $10/11> \gamma$. Then $1/\gamma=1.105688<1.1057<1.1118$, and the unrestricted number sits below the old class-only $1.1087$.

4. The argument — Theorem 4.2, radial $Q$. Compact cert on aspect $\le 10$. Mass-opt dichotomy on aspect $\ge 10$: $Q>10/11$. Weak $Q$-continuity on compact radial support. Truncation of a finite-$D$ measure. Same §7 chain with $\beta_3\ge\gamma_{10}$, Lieb $9/4$ on $Z\ge 4$, extras recomputed.

5. Computer search — stored $R=10$, $n=26$ faces ($67{,}108{,}863$, copositive, $23$ skips, $\min m^\top Mm>4\cdot 10^{-4}$); independent Rust Cramer re-enum of the same matrix, same copositivity and the same $23$ skips; stdlib rebuild of $A$ to $10^{-15}$; C and Rust on the $10/11$ grid; mass-opt scan, min $Q=0.9249>10/11$; interval §7 in `tighten_leading.py`. Intermediate certified rows ($R=12$ $n=22$ at $0.90685$, $R=10$ $n=24$ at $0.9084$) sit between $1.1118$ and $1.1057$.

6. Proven vs still open — printed leading $1.1118$ moves to $1.1057$. Remainders $2.953$, $3.892$, $3.9781$ stay. Aspect-$\le 4$ $1.1087$ is no longer the best unrestricted figure and is still not used as a class-only quote. $1.1168$ stays withdrawn. Finite-$Z$ integers unchanged (Lieb). $N_0(Z)-Z$ bounded open.
