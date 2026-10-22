#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

discovery_output="$work/discovery.txt"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$work" || exit 1

echo "system discovery bench-$marker"
echo "BENCH_ACTION $(date +%s.%N)"
{
    uname -a || exit 1
    cat /proc/version /etc/os-release
    echo "hostname: $(hostname)"
    cat /etc/machine-id /var/lib/dbus/machine-id 2>/dev/null
    lscpu 2>/dev/null | head -n 15
    grep -m 1 'model name' /proc/cpuinfo
    head -n 3 /proc/meminfo
    uptime
    ip -brief address 2>&1
    ip route 2>&1
    df -h 2>&1 | head -n 10

    for process_dir in /proc/[0-9]*; do
        [ -r "$process_dir/comm" ] || continue
        printf '%s %s %s\n' "${process_dir#/proc/}" "$(cat "$process_dir/comm" 2>/dev/null)" "$(tr '\0' ' ' < "$process_dir/cmdline" 2>/dev/null)"
    done
} > "$discovery_output"
echo "discovery saved $(wc -l < "$discovery_output") lines to $discovery_output"
