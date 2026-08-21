# Scripts

Research half of the same loop as `scripts/new-problem.sh` and
`.claude/skills/` (`new-problem`, `literature`). Stdlib
Python 3 only; `arxiv_fetch.py` needs `pdftotext` for PDF fallback.

```
python3 scripts/arxiv_fetch.py 2211.09055                                      # title, abstract, bound-looking sentences
python3 scripts/arxiv_fetch.py 2509.05260v3 --keep-pdf problems/chowla-cosine/compute/refs/bedert-2509.05260.pdf
python3 scripts/arxiv_fetch.py 2211.11731 --research problems/union-closed/RESEARCH.md   # append citation stub
python3 scripts/oeis_lookup.py A000045
python3 scripts/oeis_lookup.py 1,2,4,8,16,32,64
```

The "bound-looking sentences" list is a grep-grade heuristic to find where the claims live — it is not a citation. Read the paper, then replace the stub's TODO with the verified claim.
