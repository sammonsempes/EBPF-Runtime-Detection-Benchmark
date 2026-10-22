#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

for output in id ps ls df os-release; do
    [ -s "$work/$output.out" ] || exit 1
done
exit 0
