#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

unit_name="bench-$marker.service"
unit_file="/etc/systemd/system/$unit_name"
wants_dir=/etc/systemd/system/multi-user.target.wants
wants_link="$wants_dir/$unit_name"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$wants_dir"
echo "BENCH_ACTION $(date +%s.%N)"
cat > "$unit_file" <<EOF || exit 1
[Unit]
Description=bench persistence $marker

[Service]
ExecStart=/bin/sh -c 'while true; do sleep 3600; done'
Restart=always

[Install]
WantedBy=multi-user.target
EOF
ln -sf "$unit_file" "$wants_link" || exit 1
ls -l "$unit_file" "$wants_link"
