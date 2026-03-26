#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALLER_SCRIPT="${SCRIPT_DIR}/start_osint.sh"

cat <<'BANNER'
╔════════════════════════════════════════════════════╗
║  OSINT Unified Launcher                            ║
║  start.sh -> start_osint.sh                        ║
╚════════════════════════════════════════════════════╝
BANNER

if [[ ! -f "${INSTALLER_SCRIPT}" ]]; then
  echo "Fehler: ${INSTALLER_SCRIPT} nicht gefunden."
  exit 1
fi

if [[ ! -x "${INSTALLER_SCRIPT}" ]]; then
  chmod +x "${INSTALLER_SCRIPT}"
fi

exec "${INSTALLER_SCRIPT}"
