#!/bin/sh
# Build the exact solver/checker pair used for q2 proof replay, without make.
set -eu
cd "$(dirname "$0")"

KISSAT_COMMIT=8af8e56f174b778aef3aa45af9f739b2a5f492c2
DRAT_COMMIT=2e3b2dc0ecf938addbd779d42877b6ed69d9a985
WORK_DIR=work
mkdir -p "$WORK_DIR"

if [ ! -d "$WORK_DIR/kissat/.git" ]; then
  git clone https://github.com/arminbiere/kissat.git "$WORK_DIR/kissat"
fi
git -C "$WORK_DIR/kissat" checkout --quiet "$KISSAT_COMMIT"

(
  cd "$WORK_DIR/kissat"
  ./configure --quiet
  mkdir -p obj build
  if [ -x scripts/generate-build-header.sh ]; then
    (cd build && ../scripts/generate-build-header.sh > build.h)
  fi
  CFLAGS="-O3 -DNDEBUG -DCOMPACT -DQUIET -std=c11 -Isrc -Ibuild"
  for file in src/*.c; do
    base=$(basename "$file")
    case "$base" in
      main.c|application.c|handle.c|parse.c|witness.c) continue ;;
    esac
    gcc $CFLAGS -c "$file" -o "obj/${base%.c}.o"
  done
  ar rc obj/libkissat.a obj/*.o
  gcc $CFLAGS -c src/main.c -o obj/main.o
  for base in application handle parse witness; do
    gcc $CFLAGS -c "src/$base.c" -o "obj/$base.o"
  done
  gcc -O3 -o ../kissat-bin obj/main.o obj/application.o obj/handle.o \
    obj/parse.o obj/witness.o obj/libkissat.a -lm
)

if [ ! -d "$WORK_DIR/drat-trim/.git" ]; then
  git clone https://github.com/marijnheule/drat-trim.git "$WORK_DIR/drat-trim"
fi
git -C "$WORK_DIR/drat-trim" checkout --quiet "$DRAT_COMMIT"
gcc -O3 -DNDEBUG "$WORK_DIR/drat-trim/drat-trim.c" -o "$WORK_DIR/drat-trim-bin"

echo "kissat $("$WORK_DIR/kissat-bin" --version) $KISSAT_COMMIT"
echo "drat-trim $DRAT_COMMIT"
