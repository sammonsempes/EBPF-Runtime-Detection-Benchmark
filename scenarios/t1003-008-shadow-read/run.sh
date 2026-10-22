#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

staged_copy="/tmp/bench-shadow-$marker"

sh "$(dirname "$0")/cleanup.sh"

echo "BENCH_ACTION $(date +%s.%N)"
cat /etc/shadow > /dev/null || exit 1
dd if=/etc/shadow of="$staged_copy" status=none || exit 1
cut -d: -f1 "$staged_copy" | head -n 5
