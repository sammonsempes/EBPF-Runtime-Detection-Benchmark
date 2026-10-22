#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

grep -qx 'echo bench-reverse-shell-done' "/tmp/bench-$marker/revshell.history" 2>/dev/null || exit 1
exit 0
