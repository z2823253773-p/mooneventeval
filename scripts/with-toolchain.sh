#!/bin/sh
set -eu
repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
MOON_HOME="$repo_root/.tools/moonbit/0.10.14+7d59c7ec9"
export MOON_HOME
PATH="$MOON_HOME/bin:$PATH"
export PATH
if [ ! -x "$MOON_HOME/bin/moonc" ]; then
  echo 'Locked toolchain missing; run python3 scripts/install_toolchain.py' >&2
  exit 1
fi
case "$("$MOON_HOME/bin/moonc" -v)" in
  'v0.10.14+7d59c7ec9 '*) ;;
  *) echo 'Locked compiler identity mismatch' >&2; exit 1 ;;
esac
exec "$@"
