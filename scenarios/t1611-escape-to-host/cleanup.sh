#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

mount_point="/tmp/bench-hostfs-$marker"

if mountpoint -q "$mount_point" 2>/dev/null; then
    umount "$mount_point" 2>/dev/null || umount -l "$mount_point" 2>/dev/null
fi
if ! mountpoint -q "$mount_point" 2>/dev/null; then
    rmdir "$mount_point" 2>/dev/null
fi
rm -f "/tmp/bench-hostdev-$marker"
rm -rf "/tmp/bench-$marker"
exit 0
