#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

rm -rf "/root/workspace/bench-$marker" "/tmp/bench-$marker"
exit 0
