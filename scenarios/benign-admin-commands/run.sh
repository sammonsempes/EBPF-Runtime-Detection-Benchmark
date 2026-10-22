#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$work" || exit 1

echo "BENCH_ACTION $(date +%s.%N)"
id > "$work/id.out" || exit 1
ps aux > "$work/ps.out" || exit 1
ls -la / > "$work/ls.out" || exit 1
df -h > "$work/df.out" || exit 1
free -m > "$work/free.out"
cat /etc/os-release > "$work/os-release.out" || exit 1
uptime > "$work/uptime.out"
cat "$work/id.out" "$work/os-release.out"
