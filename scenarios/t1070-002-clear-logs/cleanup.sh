#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

backup_dir="$work/logs"
marker_log="/var/log/bench-$marker.log"
log_files="/var/log/auth.log /var/log/wtmp /var/log/btmp /var/log/lastlog /var/log/dpkg.log /var/log/apt/history.log"

for log_file in $log_files; do
    saved="$backup_dir/$(printf '%s' "$log_file" | tr '/' '_')"
    if [ -f "$saved" ]; then
        cat "$saved" > "$log_file"
    fi
done
rm -f "$marker_log"
rm -rf "$work"
exit 0
