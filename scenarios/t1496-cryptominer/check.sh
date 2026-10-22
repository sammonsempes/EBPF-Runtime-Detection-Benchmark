#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

grep -qE '^xmrig simulation computed [0-9]+ hashes$' "/tmp/bench-$marker/miner.out" 2>/dev/null || exit 1
exit 0
