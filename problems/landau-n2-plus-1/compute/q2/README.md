# Landau 4 census through n = 10^7

Replay from this directory:

```bash
./run_all.sh
```

That rebuilds the C residue sieve, writes `prime_n.txt` and `p2_omega2.txt`,
checks that they extend the committed N=10^6 lists, then verifies the lists
twice: a C trial-plus-Pollard pass (different algorithm from the residue
sieve) and `../verify.py` (Miller–Rabin rescan, multiply-back, and an
independent Python factorization). `gcc -O3` and Python 3 are enough; this
machine has no `make`.

The sieve refuses a run whose leftover arrays would exceed about 1.8 GiB.
At N=10^7 the resident set is about 56 MB.

`../sieve_n2p1.py --dir . --n-max 10000000` is the same residue algorithm
in Python and is slower. Keep it as the readable reference.

This is a finite classification, not a proof that there are infinitely many
primes n^2+1.
