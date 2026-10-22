#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

keys_file=/root/.ssh/authorized_keys
key_line="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEJlbmNoQXR0YWNrZXJLZXlOb3RSZWFsMDAwMDAwMDA bench-$marker"
filtered_copy="/tmp/bench-authorized-keys-$marker"

if [ -f "$work/keys.created" ]; then
    rm -f "$keys_file"
elif [ -f "$keys_file" ] && grep -qxF "$key_line" "$keys_file"; then
    grep -v -x -F "$key_line" "$keys_file" > "$filtered_copy"
    cat "$filtered_copy" > "$keys_file"
fi
rm -f "$filtered_copy"
rm -rf "$work"
exit 0
