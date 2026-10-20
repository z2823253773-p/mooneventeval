#!/bin/sh
set -eu
repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
MOON_HOME="$repo_root/.tools/moonbit/0.10.14+7d59c7ec9"
export MOON_HOME
PATH="$MOON_HOME/bin:$PATH"
export PATH
for tool in moon moonc moonrun moonfmt; do
  if [ ! -x "$MOON_HOME/bin/$tool" ]; then
    echo "Locked toolchain incomplete: missing $tool; no global fallback" >&2
    exit 1
  fi
done
case "$("$MOON_HOME/bin/moonc" -v)" in
  'v0.10.14+7d59c7ec9 '*) ;;
  *) echo 'Locked compiler identity mismatch' >&2; exit 1 ;;
esac
case "${1-}" in
  moon|moonc|moonrun|moonfmt)
    locked_command="$MOON_HOME/bin/$1"
    shift
    exec "$locked_command" "$@"
    ;;
  *) exec "$@" ;;
esac
