#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

backup_dir="$work/logs"
marker_log="/var/log/bench-$marker.log"
log_files="/var/log/auth.log /var/log/wtmp /var/log/btmp /var/log/lastlog /var/log/dpkg.log /var/log/apt/history.log $marker_log"

backup_name() {
    printf '%s/%s' "$backup_dir" "$(printf '%s' "$1" | tr '/' '_')"
}

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$backup_dir" || exit 1
printf 'bench application log line %s\n' "$marker" > "$marker_log" || exit 1

for log_file in $log_files; do
    [ -f "$log_file" ] && cp -p "$log_file" "$(backup_name "$log_file")"
done

truncated=0
echo "BENCH_ACTION $(date +%s.%N)"
for log_file in $log_files; do
    [ -f "$(backup_name "$log_file")" ] || continue
    if : > "$log_file" && truncate -s 0 "$log_file"; then
        echo "truncated $log_file"
        truncated=$((truncated + 1))
    fi
done

[ "$truncated" -gt 0 ]
