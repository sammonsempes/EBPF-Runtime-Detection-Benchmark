#!/bin/sh
set -u

history_file=/root/.bash_history

[ -L "$history_file" ] || exit 1
[ "$(readlink "$history_file")" = /dev/null ] || exit 1
exit 0
