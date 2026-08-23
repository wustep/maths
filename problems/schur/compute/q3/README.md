# q3: source recovery and 1697 search

Rowley's official arXiv source archive for `2107.03560` contains the
ancillary workbook `anc/Specimens_S_7____TFTs-4,5,6.xls`. Its SHA-256 is

```
c50cf981c1c437557b261cb8a66e193ee2cf77a8a50b0ae70c986b1c1cbb6fbb
```

The workbook's `S(7) >= 1696` sheet was extracted with
`extract_rowley_xls.py`; the zero-based result is `rowley_1696.txt`.
Verification and the seven direct-extension checks need only Python's
standard library:

```bash
python3 ../verify_coloring.py rowley_1696.txt --expect-length 1696
python3 analyze_rowley_extension.py rowley_1696.txt \
  --output rowley_extension_audit.json
```

The base is valid and fully symmetric about 1697. Appending 1697 creates
between 74 and 249 vertex-disjoint boundary conflicts, depending on its
color. Consequently any repair that keeps the appended color must change at
least 74 entries of Rowley's coloring. This is an exact wall for a direct or
very-small-edit extension, not an obstruction to an unrestricted coloring.

To replay provenance as well, fetch the workbook from the official source
archive, install `xlrd==2.0.2`, and run:

```bash
python3 extract_rowley_xls.py Specimens_S_7____TFTs-4,5,6.xls extracted.txt
cmp extracted.txt rowley_1696.txt
```

## Search result

`search_unrestricted.c` represents every one of the 719,952 Schur edges on
`[1697]`; it imposes no reflection. A 180-second run from the Rowley phase
with random seed 22 reconstructed and preserved a two-violation coloring:

```bash
gcc -O3 -march=native -std=c11 -Wall -Wextra \
  -o search_unrestricted search_unrestricted.c
./search_unrestricted rowley_1696.txt candidate.txt 190 22 400000
python3 audit_near.py candidate.txt
```

The exact remaining triples are

```
537 + 537 = 1074
537 + 640 = 1177
```

all four entries having color 6. The committed vector is
`near_1697_two_violations.txt`; it is residue, not a coloring and not a lower
bound. Four further 180-second runs from that vector (seeds 101, 202, 303,
404) did not improve it.

Two exact repair encodings use `python-sat`:

```bash
python3 repair_cegar.py near_1697_two_violations.txt \
  --output coloring_1697.txt --near-output repaired_near.txt \
  --log repair.json --solver glucose42 --seconds 60
python3 repair_full_sat.py near_1697_two_violations.txt \
  --output coloring_1697.txt --log full.json \
  --solver glucose42 --seconds 120
```

The lazy repair learned 216,924 edges and released 1,051 phase pins before
timing out. The full 5,076,998-clause encoding released 1,498 pins, leaving
199 fixed, and timed out in its seventeenth solve. Neither returned a model.

`search_twisted_reflection.py` tests the different symmetry
`c(1698-x)=pi(c(x))`, where `pi=(0 1)(2 3)(4 5)(6)`. This avoids the ordinary
reflection obstruction at `566+566=1132`, but its exact 5,045,600-clause run
also timed out after 120 seconds. It did not prove the symmetric family
impossible.

The short replay checks the published base, the exact residue, the Lean
obstruction, and compilation of the C search:

```bash
./run_all.sh
```

No 1,697 coloring was found. See `q3_search_summary.json` for the precise
terminal states; no timeout here is an upper bound for `S(7)`.
