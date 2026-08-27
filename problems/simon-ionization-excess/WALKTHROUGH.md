# Walkthrough — simon-ionization-excess

Discovery notes, not a cleaned proof. Beats: `refs/walkthrough-style.md`.
Empty beats mean the search is not done.

0. What was actually missing — A published linear upper bound on
   Nc(Z), with an explicit leading coefficient, not the folklore
   "about Z+1". Simon's #9 is the O(1) excess. The finite object
   that can move is that leading coefficient, currently b(3) < 1.1185.

1. Named false starts — Treat Lieb's 2Z+1 as the current record.
   Nam 2012 already beats it for Z ≥ 6; Hundertmark–Pattakos–Schulz
   2025 beats Nam. Treat Fefferman–Seco / Seco–Sigal–Solovej
   Z + O(Z^{5/7}) as a bounded excess. That is o(Z), not O(1), and
   the implied constant is not competitive at realistic Z.

2. The useful failure — Simon's reprint writes N0(Z) < 2Z; every
   later paper writes Nc < 2Z+1. Quote the paper you are beating.
   The 1984 10(a) monotonicity question is next door and is not
   implied by a better linear coefficient.

3. The click — Hundertmark–Pattakos–Schulz Proposition 2.5 is the
   number to beat. The leading coefficient is a closed form in
   √2, so it can be replayed without trusting a decimal.

4. The argument — None toward bounded excess. The compute is a
   comparison of already published functions of Z.

5. Computer search — `compute/ionization_bounds.py` rebuilds b(3),
   checks the two decimal windows printed in 2504.18487, and writes
   the Z-table. See `compute/record.json`.

6. Proven vs still open — Replayed the published record. Did not
   produce a coefficient below 1.1184, nor an O(1) excess, nor
   1984 10(a). Simon #9 remains open.
