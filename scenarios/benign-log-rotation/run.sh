#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

log_dir="/var/log/benchapp-$marker"
config_dir="/tmp/bench-logrotate-$marker"
config_file="$config_dir/benchapp.conf"
state_file="$config_dir/state"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$log_dir" "$config_dir" || exit 1
chmod 755 "$log_dir"

timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
line_index=1
while [ "$line_index" -le 200 ]; do
    printf '%s INFO request %d served in %d ms\n' "$timestamp" "$line_index" "$((line_index % 37))" >> "$log_dir/app.log"
    printf '%s WARN slow query %d\n' "$timestamp" "$line_index" >> "$log_dir/worker.log"
    line_index=$((line_index + 1))
done

cat > "$config_file" <<EOF
$log_dir/*.log {
    rotate 3
    compress
    missingok
    notifempty
    create 0640 root root
}
EOF
chmod 644 "$config_file"

echo "BENCH_ACTION $(date +%s.%N)"
logrotate -f -s "$state_file" "$config_file" || exit 1
gzip -t "$log_dir/app.log.1.gz" "$log_dir/worker.log.1.gz" || exit 1
ls -l "$log_dir"
