# q7a: the open `ell_2(10,2) <= 49` search

The target is 49 distinct nonzero columns of rank 10 whose singletons and
unordered pair XORs cover all 1024 syndromes.  Equivalently, adjoining zero
gives a 50-point difference basis of `F_2^10`.

Nothing in this directory is a bound unless a 49-column candidate prints

```text
n=49 distinct=yes nonzero=yes rank=10 covered=1024/1024 holes=0
```

under the independent `verify_n49.c` verifier.  A nonzero residue is only
search data.

## Remaining invariant classes

`run_leftover_groups.sh` contains exactly the eleven classes left open after
q4 and q6a:

- three order-7 classes;
- two order-15 classes;
- one order-21 class;
- four order-3 classes; and
- one order-5 class.

It intentionally does not include any of the 79 q4 or 12 q6a exhaustions.
Set `CASE_TIMEOUT` to a large per-class wall-clock limit.  A timeout is not an
exclusion; only a complete `RESULT ... witnesses=0 ... exhausted` line is.

## SAT searches

`sat_n49.py` supports several independent slices of the full problem:

```sh
# Full existence search with the sound GL(10,2) frame normalization.
python3 compute/q7a/sat_n49.py --frame --output /tmp/n49.cols

# Geometric search through sets containing the APN Sidon graph
# {(u,u^3): u in GF(32)}.
python3 compute/q7a/sat_n49.py --apn --output /tmp/n49-apn.cols

# A stricter, much smaller APN search in which fixed-to-new cross-pairs
# must cover everything not already covered by the APN graph.
python3 compute/q7a/sat_n49.py --apn --cross-only

# Exact K-swap neighborhood of an existing 49-column configuration.
python3 compute/q7a/sat_n49.py --seed FILE --distance K \
  --output /tmp/n49-neighborhood.cols
```

The APN restriction is a construction search, not a WLOG reduction.  The
frame restriction is WLOG for the unrestricted existence question because
every covering has rank 10 and a linear change of coordinates maps a chosen
basis to the ten unit columns.

## Independent verification

```sh
gcc -O2 -std=c11 -Wall -Wextra compute/q7a/verify_n49.c \
  -o compute/q7a/verify_n49
compute/q7a/verify_n49 --columns /tmp/n49.cols
compute/q7a/verify_n49 --matrix compute/H_r10_n49.txt
```

The verifier reparses the input and performs a flat enumeration; it does not
reuse SAT auxiliaries or search coverage counters.
