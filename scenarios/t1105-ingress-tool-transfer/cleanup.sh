#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

rm -f "/tmp/bench-payload-$marker.sh"
rm -rf "/tmp/bench-$marker"
exit 0
