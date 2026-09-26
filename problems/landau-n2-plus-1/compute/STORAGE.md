# Storage

`prime_n.txt` and `p2_omega2.txt` under `q3/` are regenerable by
`q3/sieve_n2p1`. At $N=10^8$ the $P_2$ list is several hundred
megabytes, above GitHub's blob limit. They are gitignored. Counts,
Wolf rows, $\Omega$ histogram, and SHA-256 of both lists live in
`q3/n2p1.json`. Replay:

```
problems/landau-n2-plus-1/compute/q3/run_all.sh
```

The $N=10^6$ lists in `compute/` and the $N=10^7$ lists in `q2/` stay
committed.
