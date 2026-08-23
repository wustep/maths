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
