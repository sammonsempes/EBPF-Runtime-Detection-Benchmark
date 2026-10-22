#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

[ -x "/root/workspace/bench-$marker/checksum" ] || exit 1
grep -qF "checksum(bench-$marker) = " "/tmp/bench-$marker/checksum.out" 2>/dev/null || exit 1
exit 0
