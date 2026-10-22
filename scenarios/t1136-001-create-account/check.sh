#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

account="bench$(printf '%s' "$marker" | tr 'A-Z' 'a-z' | tr -cd 'a-z0-9' | cut -c1-20)"

getent passwd "$account" > /dev/null || exit 1
[ -d "/home/$account" ] || exit 1
exit 0
