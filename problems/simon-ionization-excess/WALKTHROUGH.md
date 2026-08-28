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

## Later the same day — more bins at aspect 10

0. What was actually missing — after q4 the compact $\gamma$ at $R=10$, $n=26$ sat $0.0047$ below the cut $10/11$. The leftover was the $P_{\max}$ tax, which shrinks as $q=R^{1/n}\to 1$. A smaller split $R$ cannot help while the large-aspect bound stays $R/(R+1)$: at $R=9$ that cut is $0.9$, so the leading is at least $1.1111$.

1. Named false starts — $R\le 9$ with the existing cut; quoting the aspect-$\le 4$ class-only $1.1087$; a moment-only sharper cut; $s>3$ and finite-$Z$ integers; recycling the withdrawn $1.1168$.

2. The useful failure — $R=9.5$, $n=26$ predicts $1.1053$, but $\gamma$ sits $4\cdot 10^{-5}$ below the cut $9.5/10.5$. That row is too tight to be the first certificate. The jump is more bins at the same split, not a fractional $R$.

3. The click — SLSQP $\varphi$ at $R=10$, $n=30$ is $0.91046$. Target $0.9103$ minus the $P$ error $0.00406$ gives $\gamma=0.906238$, and $10/11>\gamma$. Then $1/\gamma=1.103463<1.1035<1.1057$.

4. The argument — Theorem 4.2, radial $Q$. Compact cert on aspect $\le 10$ with $30$ bins. Mass-opt dichotomy on aspect $\ge 10$: $Q>10/11$. Weak $Q$-continuity on compact radial support. Truncation of a finite-$D$ measure. Same §7 chain with $\beta_3\ge\gamma_{10}$, Lieb $9/4$ on $Z\ge 4$, extras recomputed.

5. Computer search — stored $R=10$, $n=30$ faces ($1{,}073{,}741{,}823$, copositive, $420$ skips, $\min m^\top Mm>5\cdot 10^{-4}$); intermediate $n=28$ row at printed $1.1046$; stdlib rebuild of $A$ to $10^{-15}$; C and Rust on the $10/11$ grid; mass-opt scan, min $Q=0.9249>10/11$; interval §7 in `tighten_leading.py`.

6. Proven vs still open — printed leading $1.1057$ moves to $1.1035$. Remainders $2.953$, $3.892$, $3.9781$ stay. $R\le 9$ with the mass-opt cut is residue. $1.1168$ stays withdrawn. Finite-$Z$ integers unchanged (Lieb). $N_0(Z)-Z$ bounded open.

## Later the same day — more bins past $n=30$

0. What was actually missing — after q5 the compact $\gamma$ at $R=10$, $n=30$ sat $0.00285$ below the cut $10/11$. The leftover was still the $P_{\max}$ tax. $R\le 9$ with $Q>R/(R+1)$ cannot beat $1.1035$: the cut is $0.9$, so the leading is at least $1.1111$.

1. Named false starts — $R\le 9$ with the existing cut; a fractional split $R=9.8$ as the first certificate; $s>3$ and finite-$Z$ integers; recycling the withdrawn $1.1168$.

2. The useful failure — $R=9.8$, $n=32$ predicts $1.10238$, but $\gamma$ sits $2.8\cdot 10^{-4}$ below the cut $9.8/10.8$. That is more slack than q5's rejected $R=9.5$ row and still tighter than $R=10$. The jump is more bins at the same split.

3. The click — SLSQP $\varphi$ at $R=10$, $n=32$ is $0.91098$. Target $0.9108$ minus the $P$ error $0.00381$ gives $\gamma=0.906992$, and $10/11>\gamma$. Then $1/\gamma=1.102546<1.1026<1.1035$.

4. The argument — Theorem 4.2, radial $Q$. Compact cert on aspect $\le 10$ with $32$ bins. Mass-opt dichotomy on aspect $\ge 10$: $Q>10/11$. Weak $Q$-continuity on compact radial support. Truncation of a finite-$D$ measure. Same §7 chain with $\beta_3\ge\gamma_{10}$, Lieb $9/4$ on $Z\ge 4$, extras recomputed.

5. Computer search — stored $R=10$, $n=32$ faces ($4{,}294{,}967{,}295$, copositive, $1157$ skips, $\min m^\top Mm>6\cdot 10^{-4}$); stdlib rebuild of $A$ to $10^{-15}$; C and Rust on the $10/11$ grid; mass-opt scan, min $Q=0.9249>10/11$; interval §7 in `tighten_leading.py`.

6. Proven vs still open — printed leading $1.1035$ moves to $1.1026$. Remainders $2.953$, $3.892$, $3.9781$ stay. $R\le 9$ with the mass-opt cut is residue. $1.1168$ stays withdrawn. Finite-$Z$ integers unchanged (Lieb). $N_0(Z)-Z$ bounded open.

## Later the same day — past $n=32$

0. What was actually missing — after q6 the compact $\gamma$ at $R=10$, $n=32$ sat $0.00210$ below the cut $10/11$. The leftover was still the $P_{\max}$ tax. $R\le 9$ with $Q>R/(R+1)$ cannot beat $1.1026$: the cut is $0.9$, so the leading is at least $1.1111$.

1. Named false starts — $R\le 9$ with the existing cut; treating $R=9.8$ $n=33$ as the first certificate (predicted $\gamma$ sits $3\cdot 10^{-5}$ above $9.8/10.8$); a PSD+NN shortcut on $M$ (two negative eigenvalues; zeroing off-diagonals does not restore PSD); $s>3$ and finite-$Z$ integers; recycling the withdrawn $1.1168$.

2. The useful failure — $R=9.8$, $n=32$ still predicts $1.10238$ with $\gamma$ $2.8\cdot 10^{-4}$ below the cut. Raising $n$ at that split pushes $\gamma$ *over* the cut, so the unrestricted number would bind at $1.10204$ and inherit a hairline slack. The safer jump is more bins at the proven split $R=10$.

3. The click — SLSQP $\varphi$ at $R=10$, $n=33$ is $0.91122$. Target $0.9111$ minus the $P$ error $0.00369$ gives $\gamma=0.907407$, and $10/11>\gamma$. Then $1/\gamma=1.102041<1.1021<1.1026$.

4. The argument — Theorem 4.2, radial $Q$. Compact cert on aspect $\le 10$ with $33$ bins. Mass-opt dichotomy on aspect $\ge 10$: $Q>10/11$. Weak $Q$-continuity on compact radial support. Truncation of a finite-$D$ measure. Same §7 chain with $\beta_3\ge\gamma_{10}$, Lieb $9/4$ on $Z\ge 4$, extras recomputed.

5. Computer search — stored $R=10$, $n=33$ faces ($8{,}589{,}934{,}591$, copositive, $2518$ skips, $\min m^\top Mm>4\cdot 10^{-4}$); stdlib rebuild of $A$ to $10^{-15}$; C and Rust on the $10/11$ grid; mass-opt scan, min $Q=0.9249>10/11$; interval §7 in `tighten_leading.py`.

6. Proven vs still open — printed leading $1.1026$ moves to $1.1021$. Remainders $2.953$, $3.892$, $3.9781$ stay. $R\le 9$ with the mass-opt cut is residue. $1.1168$ stays withdrawn. Finite-$Z$ integers unchanged (Lieb). $N_0(Z)-Z$ bounded open.

## Later the same day — past $n=33$

0. What was actually missing — after q7 the compact $\gamma$ at $R=10$, $n=33$ sat $0.00168$ below the cut $10/11$. The leftover was still the $P_{\max}$ tax, plus unused $\varphi$: SLSQP and the stored face $\min\varphi$ sit at $0.91122$ while the certified target is $0.9111$. $R\le 9$ with $Q>R/(R+1)$ cannot beat $1.1021$: the cut is $0.9$, so the leading is at least $1.1111$.

1. Named false starts — $R\le 9$ with the existing cut; a Chebyshev $D\cdot M_{-1}\ge 1$ sharpening of that cut (the $R\le 9$ slab still dies below $0.90736$); quoting $1.102041$ as a printed dent (the notebook ceilings to $1.1021$); $s>3$ and finite-$Z$ integers; recycling the withdrawn $1.1168$.

2. The useful failure — $R=9.8$ with the cut binding prints $1.10204$, which is again $1.1021$. Chebyshev does not reopen $R\le 9$. The jump is either a higher target on the stored $n=33$ matrix or more bins at the same split.

3. The click — SLSQP $\varphi$ at $R=10$, $n=33$ is $0.911221$. q7 certified target $0.9111$. Raising the target to $0.9112$ on the same matrix subtracts the same $P$ error $0.00369$ and gives $\gamma=0.907507$, and $10/11>\gamma$. Then $1/\gamma=1.101920<1.1020<1.1021$.

4. The argument — Theorem 4.2, radial $Q$. Compact cert on aspect $\le 10$ with $33$ bins at the higher target. Mass-opt dichotomy on aspect $\ge 10$: $Q>10/11$. Weak $Q$-continuity on compact radial support. Truncation of a finite-$D$ measure. Same §7 chain with $\beta_3\ge\gamma_{10}$, Lieb $9/4$ on $Z\ge 4$, extras recomputed.

5. Computer search — stored $R=10$, $n=33$ faces at target $0.9112$ ($8{,}589{,}934{,}591$, copositive, $2455$ skips, $\min m^\top Mm>7\cdot 10^{-5}$, $\min\varphi=0.911221$); stdlib rebuild of $A$ to $10^{-15}$; C and Rust on the $10/11$ grid; mass-opt scan, min $Q=0.9249>10/11$; interval §7 in `tighten_leading.py`.

6. Proven vs still open — printed leading $1.1021$ moves to $1.1020$. Remainders $2.953$, $3.892$, $3.9781$ stay. $R\le 9$ with the mass-opt cut is residue. $1.1168$ stays withdrawn. Finite-$Z$ integers unchanged (Lieb). $N_0(Z)-Z$ bounded open. $n=34$ at the same split is still a predicted $1.1017$ if faces certify.

## Later the same day — past $n=33$ to $n=34$

0. What was actually missing — after q8 the compact $\gamma$ at $R=10$, $n=33$ sat $0.00158$ below the cut $10/11$. The leftover was still the $P_{\max}$ tax. Unused $\varphi$ at $n=33$ is spent (target $0.9112$, SLSQP $0.911221$). $R\le 9$ with $Q>R/(R+1)$ cannot beat $1.1020$: the cut is $0.9$, so the leading is at least $1.1111$.

1. Named false starts — $R\le 9$ with the existing cut; a Chebyshev $D\cdot M_{-1}\ge 1$ sharpening of that cut (the $R\le 9$ slab still dies below $0.90744$); $s>3$ and finite-$Z$ integers; recycling the withdrawn $1.1168$.

2. The useful failure — $R=9.8$ with the cut binding prints $1.10204$, which is $1.1021$. Chebyshev does not reopen $R\le 9$. The jump is more bins at the proven split.

3. The click — SLSQP $\varphi$ at $R=10$, $n=34$ is $0.911452$. Target $0.9113$ minus the $P$ error $0.00358$ gives $\gamma=0.907716$, and $10/11>\gamma$. Then $1/\gamma=1.101667<1.1017<1.1020$.

4. The argument — Theorem 4.2, radial $Q$. Compact cert on aspect $\le 10$ with $34$ bins. Mass-opt dichotomy on aspect $\ge 10$: $Q>10/11$. Weak $Q$-continuity on compact radial support. Truncation of a finite-$D$ measure. Same §7 chain with $\beta_3\ge\gamma_{10}$, Lieb $9/4$ on $Z\ge 4$, extras recomputed.

5. Computer search — stored $R=10$, $n=34$ faces at target $0.9113$ ($17{,}179{,}869{,}183$, copositive, $4618$ skips, $\min m^\top Mm>5\cdot 10^{-4}$, $\min\varphi=0.911456$); stdlib rebuild of $A$ to $10^{-15}$; C and Rust on the $10/11$ grid; mass-opt scan, min $Q=0.9249>10/11$; interval §7 in `tighten_leading.py`.

6. Proven vs still open — printed leading $1.1020$ moves to $1.1017$. Remainders $2.953$, $3.892$, $3.9781$ stay. $R\le 9$ with the mass-opt cut is residue. $1.1168$ stays withdrawn. Finite-$Z$ integers unchanged (Lieb). $N_0(Z)-Z$ bounded open. $n=35$ at the same split is still a predicted $1.1013$ if faces certify. Target $0.9114$ on this matrix is still a predicted $1.1016$.

## Later the same day — leftover past $n=34$

0. What was actually missing — after q9 the compact $\gamma$ at $R=10$, $n=34$ sat $0.00138$ below the cut $10/11$. The leftover is still the $P_{\max}$ tax. Unused $\varphi$ at $n=34$ is a hair (target $0.9113$, SLSQP $0.91145$, stored $\min\varphi=0.911456$). $R\le 9$ with $Q>R/(R+1)$ cannot beat $1.1017$: the cut is $0.9$, so the leading is at least $1.1111$.

1. Named false starts — $R\le 9$ with the existing cut; a Chebyshev $D\cdot M_{-1}\ge 1$ sharpening of that cut (the $R\le 9$ slab still dies below $0.90769$); treating a target-$0.9114$ probe on the $n=34$ matrix as an $n=35$ dent; $s>3$ and finite-$Z$ integers; recycling the withdrawn $1.1168$.

2. The useful failure — $R=9.8$ with the cut binding prints $1.10204$, which is $1.1021$. Chebyshev does not reopen $R\le 9$. The jump is more bins at the proven split, or a higher target on the stored $n=34$ matrix (full re-enum, not an $n=35$ dent).

3. The click — SLSQP $\varphi$ at $R=10$, $n=35$ is $0.911672$. Target $0.9115$ minus the $P$ error $0.003482$ gives $\gamma=0.908018$, and $10/11>\gamma$. Then $1/\gamma=1.101300<1.1013<1.1017$.

4. The argument — Theorem 4.2, radial $Q$. Compact cert on aspect $\le 10$ with $35$ bins. Mass-opt dichotomy on aspect $\ge 10$: $Q>10/11$. Weak $Q$-continuity on compact radial support. Truncation of a finite-$D$ measure. Same §7 chain with $\beta_3\ge\gamma_{10}$, Lieb $9/4$ on $Z\ge 4$, extras recomputed.

5. Computer search — stored $R=10$, $n=35$ faces at target $0.9115$ ($34{,}359{,}738{,}367$, copositive, $8362$ skips, $\min m^\top Mm>5\cdot 10^{-4}$, $\min\varphi=0.911674$); stdlib rebuild of $A$ to $10^{-15}$; C and Rust on the $10/11$ grid; mass-opt scan, min $Q=0.9249>10/11$; interval §7 in `tighten_leading.py`.

6. Proven vs still open — printed leading $1.1017$ moves to $1.1013$. Remainders $2.953$, $3.892$, $3.9781$ stay. $R\le 9$ with the mass-opt cut is residue. $1.1168$ stays withdrawn. Finite-$Z$ integers unchanged (Lieb). $N_0(Z)-Z$ bounded open. Target $0.9114$ on the $n=34$ matrix was not run and is not this dent.

## Later — leftover past $n=35$

0. What was actually missing — after q10 the compact $\gamma$ at $R=10$, $n=35$ sat $0.00107$ below the cut $10/11$. The leftover is still the $P_{\max}$ tax. $R\le 9$ with $Q>R/(R+1)$ cannot beat $1.1013$: the cut is $0.9$, so the leading is at least $1.1111$.

1. Named false starts — $R\le 9$ with the existing cut; a Chebyshev $D\cdot M_{-1}\ge 1$ sharpening of that cut (the $R\le 9$ slab still dies below $0.908018$); treating a higher-target probe on the $n=34$ or $n=35$ matrix as an $n=36$ dent; $s>3$ and finite-$Z$ integers; recycling the withdrawn $1.1168$.

2. The useful failure — $R=9.8$ with the cut binding prints $1.10204$, which is $1.1021$. Chebyshev does not reopen $R\le 9$. The jump is more bins at the proven split, or a higher target on a stored matrix (full re-enum, not an $n=36$ dent).

3. The click — predicted only until faces run. $n=36$ mid-radius bins at aspect $10$. Compact $\gamma$ must sit below $10/11$, and printed $1/\gamma$ must beat $1.1013$. Face enumeration is the certificate.

4. The argument — Theorem 4.2, radial $Q$. Compact cert on aspect $\le 10$ with $36$ bins if faces certify. Mass-opt dichotomy on aspect $\ge 10$: $Q>10/11$. Same §7 chain.

5. Computer search — leftover. $2^{36}-1=68{,}719{,}476{,}735$ faces. SLSQP prediction in `compute/q11/certs/scan_compact.json`. No new leading until the dump is copositive.

6. Proven vs still open — printed leading stays $1.1013$ until faces certify. Remainders $2.953$, $3.892$, $3.9781$ stay. $R\le 9$ with the mass-opt cut is residue. $1.1168$ stays withdrawn. Finite-$Z$ integers unchanged (Lieb). $N_0(Z)-Z$ bounded open.
