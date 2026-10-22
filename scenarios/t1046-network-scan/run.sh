#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
attacker="${BENCH_ATTACKER:-attacker}"
work="/tmp/bench-$marker"

scan_log="$work/scan.log"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$work" || exit 1

open_port_found=no
echo "BENCH_ACTION $(date +%s.%N)"
for port_range in 1-1024 3300-3400 8000-8100; do
    if timeout 15 nc -z -v -w 1 "$attacker" "$port_range" >> "$scan_log" 2>&1; then
        open_port_found=yes
    fi
done

grep -E 'succeeded|open' "$scan_log"
echo "scan of $attacker produced $(wc -l < "$scan_log") results"
[ "$open_port_found" = yes ]
