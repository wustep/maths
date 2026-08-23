# The p=59 exact boundary

OEIS A398173 ends at $m(53)=14$, so $p=59$ is the first unpublished prime.
The saved certificate `p59_upper.json` proves only

$$
m(59)\le 15.
$$

It does not determine $m(59)$.

## Checked upper bound

CaDiCaL 1.9.5 found

$$
A=\{0,1,25,28,32,36,43,46,47,49,52,53,55,57,58\}
$$

in 48.766 seconds. The direct verifier recomputes all 225 ordered sums and
finds no multiplicity in $\{1,2\}$:

```bash
python3 problems/unique-sum/compute/q3/verify_upper.py
```

## Incomplete lower search

The independent Rust program searches for any admissible set of size at most
14. With a deterministic 100-million-node cap it reports

```text
p=59 limit=14 status=UNKNOWN nodes=100000000 memo_hits=27672395 memo=72327605
```

The recorded run took 523.030 seconds; timing is machine-dependent, while the
node and memo counts are deterministic for this implementation.

Compile and replay that finite prefix with:

```bash
rustc -D warnings -O problems/unique-sum/compute/q3/verify_exact.rs -o /tmp/verify-unique-sum
/tmp/verify-unique-sum 59 14 100000000
```

`UNKNOWN` exits with status 3. It is not a lower bound. In particular, this
run does not show that size 14, or any smaller size, is impossible.

The full cardinality-SAT encoding was also run at exact size 14 with
CaDiCaL 1.9.5, Kissat 4.0.4, CaDiCaL 3.0.0, and MapleChrono. None decided the
instance in these runs. CaDiCaL 1.9.5 was stopped after 37:01 wall time
(34:49 CPU); each of the other three was stopped after about 30 minutes of
wall time. These timeouts are leads about cost, not certificates.

## Near miss

Local search found the normalized 14-set

$$
\{0,1,3,4,5,9,13,15,16,21,29,33,45,58\},
$$

which has exactly one uniquely represented sum. All 49,168,350 normalized
14-sets within four swaps of it were checked and none worked. That is only a
finite neighborhood statement; it does not exclude a solution elsewhere.
