#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

[ -u "/tmp/bench-suid-$marker" ] || exit 1
grep -q 'euid=0(' "/tmp/bench-$marker/suid.out" 2>/dev/null || exit 1
exit 0
