# q15: two radius-3 continuations of the 817-column seed

See [CLAIM.md](CLAIM.md) for the exact certified inequalities. The inherited
34-block $(3,0)$-partition admits a safe merge of blocks 15 and 24, giving
33 blocks. QM$_4^3$ at $m=5$ then gives a 41 by 26175 matrix. Refining the
seed partition to 129 blocks and using $m=7$ gives a 47 by 104703 matrix.

Run `compute/q15/run_all.sh` from `problems/covering/`. It regenerates both
matrices in temporary storage, compares their hashes through the committed
manifests, checks the full $2^{26}$ seed syndrome space under each partition,
and checks every output column and rank in C. Peak syndrome bitmap is 8 MiB.
The output syndromes at redundancies 41 and 47 are certified by Theorem 6.1,
not enumerated. The matrices are retained as generators plus hashes to avoid
committing two large text files.
