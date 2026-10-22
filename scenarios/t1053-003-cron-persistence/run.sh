#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

cron_file="/etc/cron.d/bench-$marker"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p /etc/cron.d
echo "BENCH_ACTION $(date +%s.%N)"
printf '%s\n' "* * * * * root /bin/sh -c 'echo bench-cron-$marker' >/dev/null 2>&1" > "$cron_file" || exit 1
chmod 644 "$cron_file"
cat "$cron_file"
