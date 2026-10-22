#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

[ -s "/tmp/bench-$marker/hostfs.ls" ] || exit 1
exit 0
