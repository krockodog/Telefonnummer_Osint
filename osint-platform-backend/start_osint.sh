#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_SCRIPT="${SCRIPT_DIR}/../start_osint.sh"

cat <<'BANNER'
╔══════════════════════════════════════╗
║  OSINT Backend Launcher Redirector   ║
╚══════════════════════════════════════╝
BANNER

if [[ ! -f "${ROOT_SCRIPT}" ]]; then
  echo "Fehler: ${ROOT_SCRIPT} nicht gefunden."
  exit 1
fi

exec "${ROOT_SCRIPT}"
