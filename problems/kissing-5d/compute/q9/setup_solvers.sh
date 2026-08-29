#!/bin/sh
# Native CaDiCaL 3.0.1 (binary DRAT), Heule drat-trim, Kissat 4.0.1.
# Same pair as q5 T5 / q7 / q8.
set -eu
HERE=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
cd "$HERE"
mkdir -p bin /tmp/solvers
if [ ! -x bin/cadical ]; then
  if [ -x ../q8/bin/cadical ]; then
    cp ../q8/bin/cadical bin/cadical
  else
    if [ ! -d /tmp/solvers/cadical ]; then
      git clone --depth 1 --branch rel-3.0.1 https://github.com/arminbiere/cadical.git /tmp/solvers/cadical
    fi
    (cd /tmp/solvers/cadical && ./configure && make -j"$(nproc)")
    cp /tmp/solvers/cadical/build/cadical bin/cadical
  fi
fi
if [ ! -x bin/drat-trim ]; then
  if [ -x ../q8/bin/drat-trim ]; then
    cp ../q8/bin/drat-trim bin/drat-trim
  else
    if [ ! -d /tmp/solvers/drat-trim ]; then
      git clone --depth 1 https://github.com/marijnheule/drat-trim.git /tmp/solvers/drat-trim
    fi
    (cd /tmp/solvers/drat-trim && make -j"$(nproc)")
    cp /tmp/solvers/drat-trim/drat-trim bin/drat-trim
  fi
fi
if [ ! -x bin/kissat ]; then
  if [ -x ../q8/bin/kissat ]; then
    cp ../q8/bin/kissat bin/kissat
  else
    if [ ! -d /tmp/solvers/kissat ]; then
      git clone --depth 1 --branch rel-4.0.1 https://github.com/arminbiere/kissat.git /tmp/solvers/kissat
    fi
    (cd /tmp/solvers/kissat && ./configure && make -j"$(nproc)")
    cp /tmp/solvers/kissat/build/kissat bin/kissat
  fi
fi
./bin/cadical --version
./bin/kissat --version
echo "solvers ready"
