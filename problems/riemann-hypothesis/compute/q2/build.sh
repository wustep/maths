#!/usr/bin/env bash
set -euo pipefail
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
out=${1:?usage: build.sh OUTPUT_DIRECTORY}
mkdir -p "$out"
includes=()
link=()
rustlink=()
if [[ -n ${FLINT_PREFIX:-} ]]; then
  includes=(-I"$FLINT_PREFIX/include" -I"$FLINT_PREFIX/include/x86_64-linux-gnu")
  lib="$FLINT_PREFIX/lib/x86_64-linux-gnu"
  if [[ ! -d "$lib" ]]; then lib="$FLINT_PREFIX/lib"; fi
  link=(-L"$lib" -Wl,-rpath,"$lib")
  rustlink=(-L "native=$lib" -C "link-arg=-Wl,-rpath,$lib")
fi
cc -O3 -std=c17 -Wall -Wextra -Werror -pedantic "${includes[@]}" \
  -DTRIANGLE_WEIGHT "$here/vendor/finite_original.c" \
  "${link[@]}" -lflint -lm -o "$out/original"
cc -O2 -std=c17 -Wall -Wextra -Werror "${includes[@]}" \
  -c "$here/arb_bridge.c" -o "$out/arb_bridge.o"
for name in direct interpolate; do
  rustc -O --edition=2021 -A dead_code -D warnings "$here/$name.rs" \
    -C "link-arg=$out/arb_bridge.o" "${rustlink[@]}" \
    -C link-arg=-lflint -o "$out/$name"
done
cc --version | head -1
rustc --version
sha256sum "$out/original" "$out/direct" "$out/interpolate"
