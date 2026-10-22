#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

rm -f "/tmp/bench-exfil-$marker.tar.gz"
rm -rf "/tmp/bench-$marker"
exit 0
