#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

[ -f "/tmp/bench-$marker/sshd.ran" ] || exit 1
exit 0
