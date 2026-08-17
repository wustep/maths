#!/bin/sh
# Read deckrecon "hash" lines and report duplicate full/reduced SHA-256s.
# Lines: full_sha set_sha dmin dmax nred g6
set -eu
in=${1:--}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
if [ "$in" = "-" ]; then
    cat >"$tmp/all"
else
    cp "$in" "$tmp/all"
fi
# keep only SHA lines (deckrecon also prints a read= summary)
awk '/^[0-9a-f]{64} [0-9a-f]{64} /' "$tmp/all" >"$tmp/h"
mv "$tmp/h" "$tmp/all"
n=$(wc -l <"$tmp/all")
cut -d' ' -f1 "$tmp/all" | sort | uniq -c | awk '$1>1{print}' >"$tmp/full.dups"
cut -d' ' -f2 "$tmp/all" | sort | uniq -c | awk '$1>1{print}' >"$tmp/set.dups"
nf=$(wc -l <"$tmp/full.dups")
ns=$(wc -l <"$tmp/set.dups")
echo "lines=$n full_dup_keys=$nf set_dup_keys=$ns"
if [ "$nf" -gt 0 ]; then
    echo "FULL DECK DUPLICATE HASHES:"
    cat "$tmp/full.dups"
fi
if [ "$ns" -gt 0 ]; then
    echo "REDUCED DECK DUPLICATE HASHES:"
    cat "$tmp/set.dups"
fi
[ "$nf" -eq 0 ] && [ "$ns" -eq 0 ]
