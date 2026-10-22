#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

rm -rf "/tmp/.X11-$marker" "/tmp/bench-$marker"
exit 0
