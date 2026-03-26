#!/usr/bin/env bash
set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/osint-platform-backend"
FRONTEND_DIR="${SCRIPT_DIR}/app"
VENV_DIR="${BACKEND_DIR}/venv"
BACKEND_PORT="15000"
BACKEND_PID=""

banner() {
  echo -e "${BLUE}"
  cat <<'BANNER'
╔══════════════════════════════════════════════════════════════╗
║   ____   _____ ___ _   _ _____    ____   ____ ___ _   _ _____║
║  / __ \ / ____|_ _| \ | |_   _|  |  _ \ / ___|_ _| \ | |_   _||
║ | |  | | (___  | ||  \| | | |    | |_) | |    | ||  \| | | |  ║
║ | |  | |\___ \ | || |\  | | |    |  __/| |___ | || |\  | | |  ║
║  \____/ ____) || || | \ | | |    |_|    \____|___|_| \_| |_|  ║
║       |_____/|___|_|  \_| |_|         INSTALLER v2            ║
╚══════════════════════════════════════════════════════════════╝
BANNER
  echo -e "${NC}"
}

require_cmd() {
  local cmd="$1"
  local hint="$2"

  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo -e "${RED}ERROR:${NC} '${cmd}' nicht gefunden. ${hint}"
    exit 1
  fi
}

cleanup() {
  if [[ -n "${BACKEND_PID}" ]]; then
    echo -e "\n${YELLOW}Stoppe Backend-Prozess (${BACKEND_PID}) ...${NC}"
    kill "${BACKEND_PID}" 2>/dev/null || true
    wait "${BACKEND_PID}" 2>/dev/null || true
  fi
}

trap cleanup INT TERM EXIT

banner

echo -e "${BLUE}[1/7] Prüfe Voraussetzungen${NC}"
require_cmd python3 "Bitte Python 3.9+ installieren."
require_cmd node "Bitte Node.js 18+ installieren."
require_cmd npm "Bitte npm installieren."
require_cmd curl "Bitte curl installieren."

if [[ ! -d "${BACKEND_DIR}" ]]; then
  echo -e "${RED}ERROR:${NC} Backend-Ordner fehlt: ${BACKEND_DIR}"
  exit 1
fi

if [[ ! -d "${FRONTEND_DIR}" ]]; then
  echo -e "${RED}ERROR:${NC} Frontend-Ordner fehlt: ${FRONTEND_DIR}"
  exit 1
fi

echo -e "${GREEN}✓ Python: $(python3 --version)${NC}"
echo -e "${GREEN}✓ Node:   $(node --version)${NC}"

echo -e "${BLUE}[2/7] Richte Python-Umgebung ein${NC}"
cd "${BACKEND_DIR}"
if [[ ! -d "${VENV_DIR}" ]]; then
  python3 -m venv venv
fi
# shellcheck source=/dev/null
source "${VENV_DIR}/bin/activate"
python -m pip install --upgrade pip >/dev/null
pip install -r requirements.txt

echo -e "${BLUE}[3/7] Erstelle .env (falls nicht vorhanden)${NC}"
if [[ ! -f .env ]]; then
  SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
  cat > .env <<ENV
FLASK_ENV=production
DEBUG=False
SECRET_KEY=${SECRET_KEY}
HOST=0.0.0.0
PORT=${BACKEND_PORT}
RATE_LIMIT=1000 per hour
DATABASE_URL=sqlite:///osint.db
CACHE_TYPE=simple
CACHE_TIMEOUT=3600
DATA_RETENTION_DAYS=7
LOG_LEVEL=INFO

# Optional AI API Keys
# KIMI_API_KEY=
# PERPLEXITY_API_KEY=
# GEMINI_API_KEY=
ENV
  echo -e "${GREEN}✓ .env wurde erstellt${NC}"
else
  echo -e "${YELLOW}ℹ .env existiert bereits – wird nicht überschrieben${NC}"
fi

echo -e "${BLUE}[4/7] Installiere Frontend-Dependencies${NC}"
cd "${FRONTEND_DIR}"
npm install

echo -e "${BLUE}[5/7] Erzeuge Frontend-Build${NC}"
echo "VITE_API_URL=/api" > .env.local
npm run build

mkdir -p "${BACKEND_DIR}/static"
rm -rf "${BACKEND_DIR}/static"/*
cp -r dist/* "${BACKEND_DIR}/static/"

echo -e "${BLUE}[6/7] Starte Backend${NC}"
cd "${BACKEND_DIR}"
if command -v lsof >/dev/null 2>&1; then
  lsof -ti:"${BACKEND_PORT}" | xargs -r kill -9 || true
fi

python app.py &
BACKEND_PID="$!"

echo -e "${BLUE}[7/7] Warte auf Health-Check${NC}"
for _ in {1..30}; do
  if curl -fsS "http://localhost:${BACKEND_PORT}/api/health" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! curl -fsS "http://localhost:${BACKEND_PORT}/api/health" >/dev/null 2>&1; then
  echo -e "${RED}ERROR:${NC} Backend konnte nicht gestartet werden."
  exit 1
fi

IP_ADDRESS="$(hostname -I | awk '{print $1}')"

echo -e "${GREEN}"
cat <<'SUCCESS'
┌──────────────────────────────────────────────────────────────┐
│  ✅ INSTALLATION FERTIG                                      │
│  🌐 Öffne: http://localhost:15000                           │
│  🔍 API:   http://localhost:15000/api/health                │
│  🛑 Stop:  Ctrl + C                                          │
└──────────────────────────────────────────────────────────────┘
SUCCESS

echo -e "${NC}${BLUE}LAN URL:${NC} http://${IP_ADDRESS}:${BACKEND_PORT}"

wait "${BACKEND_PID}"
