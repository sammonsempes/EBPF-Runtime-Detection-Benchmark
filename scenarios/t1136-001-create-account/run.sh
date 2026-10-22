#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

account="bench$(printf '%s' "$marker" | tr 'A-Z' 'a-z' | tr -cd 'a-z0-9' | cut -c1-20)"

sh "$(dirname "$0")/cleanup.sh"

echo "BENCH_ACTION $(date +%s.%N)"
useradd -m -s /bin/bash -c "bench $marker" "$account" || exit 1
printf '%s:%s\n' "$account" "bench-$marker" | chpasswd
id "$account"
