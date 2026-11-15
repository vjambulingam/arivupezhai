#!/usr/bin/env bash
#
# generate-book-formats.sh
# Wrapper script to run generate-book-formats.py
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"

exec "$PYTHON" "$SCRIPT_DIR/generate-book-formats.py" "$@"
