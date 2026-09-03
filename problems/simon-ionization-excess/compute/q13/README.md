# q13 — Gray-code faces at the proven aspect-10 split

Same HPS §7 / [arXiv:2504.18487v1](https://arxiv.org/abs/2504.18487)
chain as q1–q12. The published record is still v1 only. q11
(`#136` / `9d99070`) certified printed leading 1.1010 at
aspect 10, \(n=36\), target \(\varphi=0.9117\). That cert stays
frozen. q12 started \(n=37\) with the naive mask dump and
stopped incomplete. Those four shards stay leftover, not a bound.

This folder copies the q12 stack and replaces the dump with a
single-thread Gray-code enumerator (`verify_gray.c`). Each step
adds or removes one bin, so the inverse of \(M_S\) is a rank-1
update instead of Gauss-Jordan from scratch. RAM is \(O(n^2)\)
(about 2 MB RSS on this box). SLSQP at target \(\varphi=0.9119\)
predicts printed \(1.1006\) if faces certify. Face copositivity
is the certificate, not the prediction.

\(R\le 9\) with \(Q>R/(R+1)\) cannot beat \(1.1010\). Finite-\(Z\)
integers (Lieb), \(N_0(Z)-Z\) bounded, and \(s>3\) along
Lemma 4.3 stay leftover. The withdrawn \(1.1168\) stays withdrawn.

## Replay

```bash
problems/simon-ionization-excess/compute/q13/run_all.sh
```

Exit 0 with `certs/lift.json` is a lift of q11's 1.1010.
Exit 0 without `certs/lift.json` is residue.

```bash
gcc -O3 -march=native -o verify_gray verify_gray.c -lm
./verify_gray certs/beta3_mid_R10_n37_t0p9119.txt \
    certs/beta3_mid_faces_R10_n37_t0p9119.txt
```

A complete dump has `gray_i` equal to \(2^{37}-1\) and
`copositive 1`. Then `python3 raise_phi.py --R 10 --n 37 --target 0.9119`
reuses that dump.
