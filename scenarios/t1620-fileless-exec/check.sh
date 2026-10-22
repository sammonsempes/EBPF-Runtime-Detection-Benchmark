#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

grep -qF "/memfd:bench-memfd-$marker" "/tmp/bench-$marker/fileless.proof" 2>/dev/null || exit 1
exit 0
