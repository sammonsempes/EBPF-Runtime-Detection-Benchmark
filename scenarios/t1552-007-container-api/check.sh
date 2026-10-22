#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

[ -s "/tmp/bench-$marker/token" ] || exit 1
exit 0
