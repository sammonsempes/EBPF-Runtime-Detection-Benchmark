#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

key_line="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEJlbmNoQXR0YWNrZXJLZXlOb3RSZWFsMDAwMDAwMDA bench-$marker"

grep -qxF "$key_line" /root/.ssh/authorized_keys 2>/dev/null || exit 1
exit 0
