#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

ssh_dir=/root/.ssh
keys_file="$ssh_dir/authorized_keys"
key_line="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEJlbmNoQXR0YWNrZXJLZXlOb3RSZWFsMDAwMDAwMDA bench-$marker"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$work" || exit 1
[ -f "$keys_file" ] || : > "$work/keys.created"

echo "BENCH_ACTION $(date +%s.%N)"
mkdir -p "$ssh_dir"
chmod 700 "$ssh_dir"
printf '%s\n' "$key_line" >> "$keys_file" || exit 1
chmod 600 "$keys_file"
grep -xF "$key_line" "$keys_file"
