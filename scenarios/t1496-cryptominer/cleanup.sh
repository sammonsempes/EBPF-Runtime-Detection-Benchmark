#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

rm -rf "/tmp/bench-miner-$marker" "/tmp/bench-$marker"
exit 0
