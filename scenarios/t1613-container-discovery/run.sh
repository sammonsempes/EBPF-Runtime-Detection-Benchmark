#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

discovery_output="$work/discovery.txt"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$work" || exit 1

echo "container discovery bench-$marker"
echo "BENCH_ACTION $(date +%s.%N)"
{
    ls -la /.dockerenv /run/.containerenv 2>&1
    cat /proc/1/cgroup /proc/self/cgroup || exit 1
    ls /sys/fs/cgroup 2>&1 | head -n 20
    cat /proc/self/mountinfo || exit 1
    grep -E '^(Cap|Seccomp|NoNewPrivs)' /proc/self/status
    effective_capabilities=$(awk '/^CapEff/ { print $2 }' /proc/self/status)
    capsh --decode="$effective_capabilities" 2>&1
    tr '\0' ' ' < /proc/1/cmdline
    echo
    env | grep -iE 'kube|docker|container' || true
} > "$discovery_output"
echo "discovery saved $(wc -l < "$discovery_output") lines to $discovery_output"
