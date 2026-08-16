# How a Fifth-Power Record Did Not Move

## 0. What was actually missing

The capacity number \(\Theta(C_7)\) already moved in July 2026, but only through gadgets living in the 10th and 200th strong powers. The fifth-power independence number is a different finite object: a subset of \((\mathbb Z/7\mathbb Z)^5\) in which every pair has circular distance \(>1\) in some coordinate. The published maximum is still 367. The missing degree of freedom is one extra vertex, or a certificate that none exists.

A 368-set is already a dent. Its fifth root is about 3.2596, which would also beat the Lean-verified 3.258805, but that comparison is not required to count the finite set.

## 1. Named false starts

Not yet a cleaned list. The first obstruction is historical: Polak–Schrijver already tried other shifts and division factors on the \(n=382\) orbit and a 3-out/4-in neighbourhood of their 367-set. Linear codes stop at 343. Direct products \(3\times 108\) and \(10\times 33\) are 324 and 330.

## 2. The useful failure

Empty until a search returns a number.

## 3. The click

Empty. Hypothesis only: either some other \((n,q)\) has \(n/k\le 7/2\) and \(n\ge 368\), or the 367-set has a \(k\)-swap that the original 3-out search missed.

## 4. The argument, in the order it was found

Seed first. The Itty–Rosin–Carstensen–Reichman ancillary `R367.txt` is the Polak–Schrijver appendix, one word per line. A pairwise verifier checks circular distance \(>1\) in some coordinate. Reconstruction from the circular orbit is an independent check of the pipeline, not a new set.

## 5. Computer residue

- `compute/R367.txt` — published 367-set
- `compute/verify_set.py` — pairwise checker
- search logs to be written under `compute/`

## 6. What is proved vs still open

The 367-set is independent if the verifier says so. \(\alpha(C_7^{\boxtimes 5})\ge 367\) is old. Whether 368 exists is still open. \(\Theta(C_7)\) is not claimed from this folder.
