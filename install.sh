#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if command -v python3 >/dev/null 2>&1; then
  exec python3 "$SCRIPT_DIR/scripts/install_adapter.py" "$@"
fi
if command -v python >/dev/null 2>&1 && python -c 'import sys; raise SystemExit(0 if sys.version_info[0] >= 3 else 1)' >/dev/null 2>&1; then
  exec python "$SCRIPT_DIR/scripts/install_adapter.py" "$@"
fi
echo "Python 3 is required to run the Tilly installer." >&2
exit 1
