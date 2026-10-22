#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

account="bench$(printf '%s' "$marker" | tr 'A-Z' 'a-z' | tr -cd 'a-z0-9' | cut -c1-20)"

if getent passwd "$account" > /dev/null; then
    userdel -r "$account" > /dev/null 2>&1 || userdel "$account" > /dev/null 2>&1
fi
if getent group "$account" > /dev/null; then
    groupdel "$account" > /dev/null 2>&1
fi
rm -rf "/home/$account" "/var/mail/$account"
exit 0
