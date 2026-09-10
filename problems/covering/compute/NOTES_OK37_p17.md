# OK37 partition residue — Alexander’s ask

**Ask.** Partition the Östergård–Kaikkonen $[37,25]_2$ radius-3 seed
$H=[I_{12}\mid M]$ (DM 178 Table 2; $M$ hex `B16`, not `BI6`) into $p\le 17$
blocks with a $(3,\ell)$ property so Construction QM$_4^3$ at $m=4$ could give
$\ell_2(24,3)\le 607$ versus the table’s 618.

**Floor.** Cadical SAT shows the minimum $(3,0)$-partition size is **$p=18$**.
Every $p\le 17$ is UNSAT. Explicit 18-block labels:
[`partition_H_OK37_p18_ell0.txt`](partition_H_OK37_p18_ell0.txt)
(block sizes: 15 singletons + $7+7+8$).

**Why $\ell\ge 1$ is impossible.** The seed has **no dependent triples**, so
syndrome $0$ has no weight-1/2/3 representation; every $(3,\ell)$ cover with
$\ell\ge 1$ fails at the trivial partition already.

**Why 607 fails.** QM$_4^3$ at $m=4$ needs $p\le 17$ on this seed. The
certified minimum is $p=18$, so the $n=607$ lift **does not apply**. No dent.

**Replay.**

```bash
cd problems/covering/compute
python3 -c "
from ok37_seed import ok37_columns, is_partition_3ell
labels=[int(x) for line in open('partition_H_OK37_p18_ell0.txt')
        if not line.startswith('#') for x in line.split()]
print(is_partition_3ell(ok37_columns(), labels, ell=0), len(set(labels)))
"
# → True 18
```

Campaign code and SAT residue: [`q12/`](q12/). Summary JSON:
[`ok37_p_le17_results.json`](ok37_p_le17_results.json).
