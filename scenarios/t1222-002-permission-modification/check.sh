#!/bin/sh
set -u

[ "$(stat -c %a /etc/shadow 2>/dev/null)" = 777 ] || exit 1
exit 0
