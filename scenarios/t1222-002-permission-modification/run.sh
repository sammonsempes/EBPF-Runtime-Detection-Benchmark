#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

sensitive_file=/etc/shadow
mode_file="$work/shadow.mode"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$work" || exit 1
stat -c %a "$sensitive_file" > "$mode_file" || exit 1

echo "BENCH_ACTION $(date +%s.%N)"
chmod 777 "$sensitive_file" || exit 1
stat -c '%a %n' "$sensitive_file"
