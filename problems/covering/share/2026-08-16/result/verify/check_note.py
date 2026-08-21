#!/usr/bin/env python3
"""Check that NOTE.md quotes numbers the pipeline actually produced.

Every quantitative claim in NOTE.md is supposed to come out of verify.py /
verify.rs / build_propagation.py rather than out of somebody's head.  This
script closes the loop: it reads the fact dumps produced by this run, renders
each headline number in the exact textual form NOTE.md is expected to use, and
requires that string to appear in NOTE.md.

What this guarantees: if a computed value changes, NOTE.md stops matching and
run_all.sh fails, so the prose cannot silently drift away from the artifact.

What this does NOT guarantee: that every sentence in NOTE.md is true, or that
no *additional* number was invented somewhere in the file.  It is a ratchet
against drift, not a proof reader.
"""

import argparse
import json
import os
import sys


def load_flat(path):
    facts = {}
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.rstrip("\n")
            if not line:
                continue
            key, _, value = line.partition("\t")
            facts[key] = value
    return facts


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--facts", required=True, help="directory of *.py.tsv dumps")
    ap.add_argument("--family", required=True, help="family_table.json")
    ap.add_argument("--note", required=True, help="NOTE.md")
    args = ap.parse_args(argv)

    f10 = load_flat(os.path.join(args.facts, "H_r10_n50.py.tsv"))
    fkr = load_flat(os.path.join(args.facts, "kr_r10_n51.py.tsv"))
    f18 = load_flat(os.path.join(args.facts, "H_r18_n815.py.tsv"))
    f20 = load_flat(os.path.join(args.facts, "H_r20_n1631.py.tsv"))
    build = load_flat(os.path.join(args.facts, "build.tsv"))
    with open(args.family, "r", encoding="utf-8") as handle:
        family = json.load(handle)
    with open(args.note, "r", encoding="utf-8") as handle:
        note = handle.read()

    def frac(facts):
        return "%s/%s" % (facts["density_num"], facts["density_den"])

    def cover(facts):
        return "%s/%s" % (facts["syndromes_covered"], facts["syndromes_total"])

    required = [
        ("r=10 length", f10["n"]),
        ("r=10 codimension", "[%s,%s]" % (f10["n"], int(f10["n"]) - int(f10["r"]))),
        ("r=10 coverage", cover(f10)),
        ("r=10 density fraction", frac(f10)),
        ("r=10 density decimal", f10["density_decimal"]),
        ("r=10 multiplicity histogram", f10["mult_hist"].replace(",", ", ")),
        ("r=10 syndromes needing a pair", f10["pair_needed"]),
        ("r=10 pair-only histogram", f10["pair_hist"].replace(",", ", ")),
        ("r=10 forced-split count", f10["forced_split"]),
        ("r=10 dependent triples", f10["dependent_triples"]),
        ("r=10 best single deletion", f10["min_uncovered_on_deletion"]),
        ("r=10 partition size", "p(H) = %s" % f10["partition_blocks"]),
        ("r=10 block sizes", f10["partition_sizes"].replace(",", ", ")),
        ("dependent triple across blocks", "(491, 734, 821)"),
        ("KR length", fkr["n"]),
        ("KR density fraction", frac(fkr)),
        ("KR coverage", cover(fkr)),
        ("r=18 length", f18["n"]),
        ("r=18 coverage", cover(f18)),
        ("r=18 density fraction", frac(f18)),
        ("r=20 length", f20["n"]),
        ("r=20 coverage", cover(f20)),
        ("r=20 density fraction", frac(f20)),
        ("legal m values", build["legal_m"].replace(",", ", ")),
        ("family closed form", "51 \\cdot 2^{r/2-5} - 1"),
        ("asymptotic density fraction", "%s/%s" % (
            build["asymptotic_density_num"], build["asymptotic_density_den"])),
        ("paper asymptotic density fraction", "%s/%s" % (
            build["paper_asymptotic_density_num"],
            build["paper_asymptotic_density_den"])),
        ("reachable even r", build["family_reachable_r"].replace(",", ", ")),
        ("unreachable even r", build["family_unreachable_r"].replace(",", ", ")),
    ]

    # every reachable row's length must be quoted somewhere, at least for the
    # rows the note tabulates explicitly
    for row in family:
        if row["reachable"] and row["r"] in (10, 18, 20):
            required.append(("family n at r=%d" % row["r"], str(row["n"])))
            required.append(("family published n at r=%d" % row["r"],
                             str(row["published"])))

    missing = [(label, text) for label, text in required if text not in note]
    for label, text in missing:
        sys.stderr.write("check_note: NOTE.md does not contain %s: %r\n"
                         % (label, text))
    if missing:
        return 1
    sys.stdout.write("check_note: %d computed strings all present in NOTE.md\n"
                     % len(required))
    return 0


if __name__ == "__main__":
    sys.exit(main())
