#!/bin/sh
# Compile kissat without GNU make.
set -eu
SRC=/tmp/kissat
cd "$SRC"
./configure --quiet --no-proofs >/tmp/kissat-configure.log 2>&1 || ./configure --no-proofs
# configure writes makefile in a build dir
BUILD=$(ls -d "$SRC"/build 2>/dev/null || true)
if [ -z "$BUILD" ]; then
  # some versions use current dir
  BUILD="$SRC"
fi
# generate build.h
if [ -x "$SRC/scripts/generate-build-header.sh" ]; then
  mkdir -p "$SRC/build"
  (cd "$SRC/build" && ../scripts/generate-build-header.sh > build.h) || true
fi
mkdir -p "$SRC/obj"
CFLAGS="-O3 -DNDEBUG -DCOMPACT -DQUIET -std=c11 -I$SRC/src -I$SRC/build"
# list library sources
for f in "$SRC"/src/*.c; do
  b=$(basename "$f")
  case "$b" in
    main.c|application.c|handle.c|parse.c|witness.c) continue ;;
  esac
  echo "cc $b"
  gcc $CFLAGS -c "$f" -o "$SRC/obj/${b%.c}.o"
done
# build.h may be required by build.c — already compiled if present
ar rc "$SRC/obj/libkissat.a" "$SRC"/obj/*.o
gcc $CFLAGS -c "$SRC/src/main.c" -o "$SRC/obj/main.o"
for b in application handle parse witness; do
  gcc $CFLAGS -c "$SRC/src/$b.c" -o "$SRC/obj/$b.o"
done
gcc -O3 -o /workspace/maths/problems/ramsey-r55/compute/kissat \
  "$SRC/obj/main.o" "$SRC/obj/application.o" "$SRC/obj/handle.o" \
  "$SRC/obj/parse.o" "$SRC/obj/witness.o" "$SRC/obj/libkissat.a" -lm
echo "built $(/workspace/maths/problems/ramsey-r55/compute/kissat --version || true)"
ls -l /workspace/maths/problems/ramsey-r55/compute/kissat
