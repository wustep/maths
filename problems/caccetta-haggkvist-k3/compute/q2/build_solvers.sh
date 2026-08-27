#!/bin/sh
# Local kissat 4.0.4 + drat-trim.  Binaries stay in bin/ (gitignored).
set -eu
here=$(dirname "$0")
mkdir -p "$here/bin" /tmp/solvers
if [ ! -x /tmp/solvers/kissat/build/kissat ]; then
  cd /tmp/solvers
  curl -sL https://github.com/arminbiere/kissat/archive/refs/tags/rel-4.0.4.tar.gz -o kissat.tgz
  tar xf kissat.tgz
  rm -rf kissat
  mv kissat-rel-4.0.4 kissat
  cd kissat
  ./configure --quiet
  make -j"$(nproc)"
fi
if [ ! -x /tmp/solvers/drat-trim ]; then
  curl -sL https://raw.githubusercontent.com/marijnheule/drat-trim/master/drat-trim.c \
    -o /tmp/solvers/drat-trim.c
  gcc -O2 -o /tmp/solvers/drat-trim /tmp/solvers/drat-trim.c
fi
cp /tmp/solvers/kissat/build/kissat "$here/bin/kissat"
cp /tmp/solvers/drat-trim "$here/bin/drat-trim"
"$here/bin/kissat" --version
ls -l "$here/bin"
