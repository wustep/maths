#!/bin/sh
# minimal q with UNSAT, by linear scan upward over a candidate list
K=$1; shift
for q in "$@"; do
  r=$(./cells --k $K --q $q --nodecap 3000000000 2>/dev/null | grep -o 'RESULT [A-Z]*')
  echo "k=$K q=$q -> $r"
  case "$r" in *UNSAT*) break;; esac
done
