#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

rm -f "/tmp/bench-suid-$marker"
rm -rf "/tmp/bench-$marker"
exit 0
