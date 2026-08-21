#!/usr/bin/env bash
#
# Reproduce and check every claim in this folder, from the committed matrix
# text alone.  Exits 0 only if all of it passes.
#
#   ./run_all.sh
#
# Requires python3 and rustc.  No network, no packages, no RNG.  Output is
# byte-identical across runs: no timestamps, no temp paths, no wall-clock, and
# LC_ALL=C so sorting is stable.
#
# What it does, in order:
#   1. compile verifier #2
#   2. rebuild the KR baseline and both propagated matrices from scratch and
#      byte-compare them against the committed copies (a stale committed
#      matrix is a hard failure, not a silent pass)
#   3. run BOTH verifiers over all four matrices and diff their fact dumps
#   4. byte-compare the fact dumps against the committed snapshots
#   5. assert every headline number individually, by name
#   6. check that NOTE.md quotes the computed numbers and not something else

set -euo pipefail
export LC_ALL=C
cd "$(dirname "$0")"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/data" "$WORK/facts"

pass=0

ok()  { printf 'ok    %s\n' "$1"; pass=$((pass + 1)); }
die() { printf 'FAIL  %s\n' "$1" >&2; exit 1; }

# read one key out of a key<TAB>value dump
kv() {
  awk -F'\t' -v key="$2" '$1 == key { print $2; found = 1 }
                          END { if (!found) exit 3 }' "$1"
}

# expect FILE KEY WANT LABEL
expect() {
  local got
  got="$(kv "$1" "$2")" || die "$4: key '$2' is missing from $(basename "$1")"
  [ "$got" = "$3" ] || die "$4: $2 = '$got', expected '$3'"
  ok "$4"
}

# expect_contains FILE KEY SUBSTRING LABEL
expect_contains() {
  local got
  got="$(kv "$1" "$2")" || die "$4: key '$2' is missing from $(basename "$1")"
  case "$got" in
    *"$3"*) ok "$4" ;;
    *) die "$4: $2 = '$got', which does not contain '$3'" ;;
  esac
}

# ---------------------------------------------------------------------------
# 0. toolchain
# ---------------------------------------------------------------------------

command -v python3 >/dev/null || die "python3 not found"
command -v rustc   >/dev/null || die "rustc not found (verifier #2 is Rust; \
two independent verifiers is the point, so this is not optional)"
ok "toolchain: python3 and rustc present"

# ---------------------------------------------------------------------------
# 1. compile verifier #2
# ---------------------------------------------------------------------------

rustc -O --edition 2018 -o "$WORK/verify_rs" verify/verify.rs 2>"$WORK/rustc.log" \
  || { cat "$WORK/rustc.log" >&2; die "verify.rs did not compile"; }
ok "verifier #2 compiled"

RS="$WORK/verify_rs"
PY="python3 verify/verify.py"

# ---------------------------------------------------------------------------
# 2. the seed matrix is the committed one, unchanged
# ---------------------------------------------------------------------------

cmp -s data/H_r10_n50.txt ../compute/H_r10_n50.txt \
  || die "data/H_r10_n50.txt differs from ../compute/H_r10_n50.txt"
ok "seed matrix is byte-identical to ../compute/H_r10_n50.txt"

# ---------------------------------------------------------------------------
# 3. rebuild everything generated, and compare
# ---------------------------------------------------------------------------

python3 verify/build_propagation.py \
  --seed data/H_r10_n50.txt \
  --partition data/partition_p10.json \
  --outdir "$WORK/data" \
  --t-max 32 \
  --emit-family "$WORK/data/family_table.json" \
  --emit-family-md "$WORK/data/family_table.md" \
  --emit-appendix "$WORK/appendix_matrix.tex" \
  --emit-flat "$WORK/facts/build.tsv" >/dev/null
ok "build_propagation.py ran (GF self-tests, (4.2) conditions, allocator)"

for f in kr_r10_n51.txt H_r18_n815.txt H_r20_n1631.txt family_table.json family_table.md; do
  cmp -s "$WORK/data/$f" "data/$f" \
    || die "regenerated data/$f differs from the committed copy"
done
cmp -s "$WORK/appendix_matrix.tex" appendix_matrix.tex \
  || die "regenerated appendix_matrix.tex differs from the committed copy"
ok "regenerated artifacts are byte-identical to the committed copies"

B="$WORK/facts/build.tsv"
expect "$B" legal_m "4,5" \
  "QM_2^2 condition n_0 >= 2^m >= p(H_0) permits exactly m = 4, 5"
expect "$B" kr_canary_h5_h27_h29 0 \
  "KR bit-order canary h_5 + h_27 + h_29 = 0 (Thm 5.2(ii))"
expect "$B" seed_p 10 "seed 2-partition has p(H_0) = 10"
expect "$B" qm2_m4_n 815 "QM_2^2 at m=4 gives n = 2^4*51 - 1 = 815"
expect "$B" qm2_m5_n 1631 "QM_2^2 at m=5 gives n = 2^5*51 - 1 = 1631"
expect "$B" qm2_m4_p_bound 33 "QM_2^2 at m=4 gives p(H_C) <= 2^5 + 1 = 33"
expect "$B" qm2_m5_p_bound 65 "QM_2^2 at m=5 gives p(H_C) <= 2^6 + 1 = 65"
expect "$B" family_closed_form "51*2^(r/2-5)-1" "family closed form"
expect "$B" asymptotic_density_num 2601 "asymptotic density numerator 51^2"
expect "$B" asymptotic_density_den 2048 "asymptotic density denominator 2^11"
expect "$B" paper_asymptotic_density_num 2704 \
  "paper's asymptotic density numerator 52^2 (= 26^2/2^9)"
expect "$B" family_reachable_r \
  "10,18,20,30,32,34,36,38,40,46,48,50,52,54,56,58,60,62,64" \
  "even r reachable by iterating QM_2^2 from this seed"
expect "$B" family_unreachable_r "12,14,16,22,24,26,28,42,44" \
  "even r NOT reachable by QM_2^2 from this seed"

# ---------------------------------------------------------------------------
# 4. both verifiers, all four matrices
# ---------------------------------------------------------------------------

run_pair() {
  # run_pair FILE NAME R N [extra flags...]
  local file="$1" name="$2" r="$3" n="$4"; shift 4
  $PY "data/$file" --name "$name" --expect-r "$r" --expect-n "$n" "$@" \
      --emit-flat "$WORK/facts/$name.py.tsv" >/dev/null \
    || die "$name: verifier #1 (python) failed"
  "$RS" "data/$file" --name "$name" --expect-r "$r" --expect-n "$n" "$@" \
      --emit-flat "$WORK/facts/$name.rs.tsv" >/dev/null \
    || die "$name: verifier #2 (rust) failed"
  diff -u "$WORK/facts/$name.py.tsv" "$WORK/facts/$name.rs.tsv" >"$WORK/facts/$name.diff" \
    || { cat "$WORK/facts/$name.diff" >&2; die "$name: the two verifiers disagree"; }
  ok "$name: verifier #1 and verifier #2 agree on every reported fact"
  cmp -s "$WORK/facts/$name.py.tsv" "data/facts/$name.tsv" \
    || die "$name: recomputed facts differ from the committed snapshot data/facts/$name.tsv"
  ok "$name: facts match the committed snapshot"
}

run_pair H_r10_n50.txt   H_r10_n50   10 50 \
  --minimality --triples --partition data/partition_p10.json
run_pair kr_r10_n51.txt  kr_r10_n51  10 51 --triples
run_pair H_r18_n815.txt  H_r18_n815  18 815
run_pair H_r20_n1631.txt H_r20_n1631 20 1631

F10="$WORK/facts/H_r10_n50.py.tsv"
FKR="$WORK/facts/kr_r10_n51.py.tsv"
F18="$WORK/facts/H_r18_n815.py.tsv"
F20="$WORK/facts/H_r20_n1631.py.tsv"

# ---------------------------------------------------------------------------
# 5. the headline assertions, one at a time
# ---------------------------------------------------------------------------

# --- r = 10, the result ----------------------------------------------------
expect "$F10" r 10                    "r=10: matrix has 10 rows"
expect "$F10" n 50                    "r=10: matrix has 50 columns"
expect "$F10" rank 10                 "r=10: F_2 rank is 10"
expect "$F10" columns_distinct 1      "r=10: 50 pairwise distinct columns"
expect "$F10" columns_nonzero 1       "r=10: no zero column"
expect "$F10" syndromes_covered 1024  "r=10: coverage 1024/1024"
expect "$F10" syndromes_total 1024    "r=10: syndrome space is 2^10 = 1024"
expect "$F10" radius_exactly_2 1      "r=10: covering radius is exactly 2"
expect "$F10" density_num 319         "r=10: density numerator 319"
expect "$F10" density_den 256         "r=10: density denominator 256"
expect "$F10" density_decimal 1.24609375 "r=10: density = 319/256 = 1.24609375"
expect "$F10" mult_hist "1:859,2:129,4:24,5:9,6:3" \
  "r=10: representation multiplicity histogram"
expect "$F10" pair_needed 973         "r=10: 973 syndromes need a pair"
expect "$F10" pair_hist "1:821,2:123,4:19,5:8,6:2" \
  "r=10: pair-only multiplicity histogram over those 973"
expect "$F10" forced_split 821        "r=10: 821 forced-split pairs"

# --- the (2,0)-partition ---------------------------------------------------
expect "$F10" partition_valid 1       "r=10: partition is a valid (2,0)-partition"
expect "$F10" partition_failures 0    "r=10: no syndrome lacks a cross-block pair"
expect "$F10" partition_blocks 10     "r=10: p(H) = 10 blocks (paper's p(H_KR) = 11)"
expect "$F10" partition_sizes "8,1,3,2,8,8,8,2,1,9" "r=10: block sizes"

# --- minimality ------------------------------------------------------------
expect "$F10" min_uncovered_on_deletion 9 \
  "r=10: MINIMALITY -- best single deletion still leaves 9 uncovered syndromes"

# --- dependent triples -----------------------------------------------------
expect "$F10" min_distance 3          "r=10: minimum distance d = 3"
expect "$F10" dependent_triples 10    "r=10: exactly 10 linearly dependent triples"
expect "$F10" triples_three_blocks 1  "r=10: exactly one triple spans three blocks"
expect_contains "$F10" triples_block_map "(491,734,821):6/4/9" \
  "r=10: the triple (491,734,821) sits in blocks 6, 4, 9 (Thm 5.2(ii) analogue)"

# --- Kaikkonen-Rosendahl baseline ------------------------------------------
expect "$FKR" n 51                    "KR: 51 columns"
expect "$FKR" columns_distinct 1      "KR: 51 distinct columns"
expect "$FKR" rank 10                 "KR: F_2 rank is 10"
expect "$FKR" syndromes_covered 1024  "KR: coverage 1024/1024"
expect "$FKR" density_num 1327        "KR: density numerator 1327"
expect "$FKR" density_den 1024        "KR: density = 1327/1024"
expect "$FKR" min_distance 3          "KR: minimum distance d = 3 (Thm 5.2(ii))"

# --- propagation -----------------------------------------------------------
expect "$F18" r 18                    "r=18: codimension 18"
expect "$F18" n 815                   "r=18: length 815"
expect "$F18" rank 18                 "r=18: F_2 rank is 18"
expect "$F18" syndromes_covered 262144 "r=18: coverage 262144/262144"
expect "$F18" syndromes_total 262144  "r=18: syndrome space is 2^18"
expect "$F18" radius_exactly_2 1      "r=18: covering radius is exactly 2"
expect "$F18" density_num 332521      "r=18: density numerator 332521"
expect "$F18" density_den 262144      "r=18: density = 332521/262144"

expect "$F20" r 20                    "r=20: codimension 20"
expect "$F20" n 1631                  "r=20: length 1631"
expect "$F20" rank 20                 "r=20: F_2 rank is 20"
expect "$F20" syndromes_covered 1048576 "r=20: coverage 1048576/1048576"
expect "$F20" syndromes_total 1048576 "r=20: syndrome space is 2^20"
expect "$F20" radius_exactly_2 1      "r=20: covering radius is exactly 2"
expect "$F20" density_num 1330897     "r=20: density numerator 1330897"
expect "$F20" density_den 1048576     "r=20: density = 1330897/1048576"

# ---------------------------------------------------------------------------
# 6. NOTE.md quotes the computed numbers
# ---------------------------------------------------------------------------

python3 verify/check_note.py \
  --facts "$WORK/facts" \
  --family data/family_table.json \
  --note NOTE.md \
  || die "NOTE.md quotes a number that the pipeline did not produce"
ok "NOTE.md is consistent with the computed facts"

printf '\n%d checks passed.\n' "$pass"
