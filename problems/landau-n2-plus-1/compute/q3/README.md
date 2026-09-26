# Landau 4 census through n = 10^8

Replay from this directory:

```bash
./run_all.sh
```

That rebuilds the C residue sieve in memory strips of five million even
n (about 50 MB leftover plus the prime list), writes `prime_n.txt` and
`p2_omega2.txt`, checks that they extend the certified N=10^7 lists in
`../q2/`, then verifies twice: a C trial-plus-Pollard pass (different
algorithm from the residue sieve) and a streaming Python multiply-back
plus Wolf/OEIS check. `gcc -O3` and Python 3 are enough.

The two lists are regenerable and gitignored (the P2 file is several
hundred megabytes). Counts, hashes, and Wolf rows sit in `n2p1.json`.

This is a finite classification, not a proof that there are infinitely
many primes n^2+1.
