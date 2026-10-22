#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

[ -f "/tmp/bench-$marker/seeded" ] || exit 1
[ -z "$(ls -A "/tmp/bench-destruction-$marker/documents" 2>/dev/null)" ] || exit 1
exit 0
