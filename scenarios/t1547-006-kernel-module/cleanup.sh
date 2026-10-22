#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

rm -f "/tmp/bench-module-$marker.ko"
rm -rf "/tmp/bench-$marker"
exit 0
