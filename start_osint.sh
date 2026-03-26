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
BACKEND_PORT_DEFAULT="15000"
BACKEND_PORT="${BACKEND_PORT_DEFAULT}"
if [[ -f "${BACKEND_DIR}/.env" ]]; then
  # Read PORT from the backend .env (the env var actually used by the backend)
  PORT_FROM_ENV="$(grep -E '^PORT=' "${BACKEND_DIR}/.env" | tail -n1 | cut -d'=' -f2- | tr -d '\"' || true)"
  if [[ -n "${PORT_FROM_ENV}" ]]; then
    BACKEND_PORT="${PORT_FROM_ENV}"
  fi
fi
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

echo -e "${BLUE}[1/8] Prüfe Voraussetzungen${NC}"
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

echo -e "${BLUE}[2/8] Richte Python-Umgebung ein${NC}"
cd "${BACKEND_DIR}"
if [[ ! -d "${VENV_DIR}" ]]; then
  python3 -m venv venv
fi
# shellcheck source=/dev/null
source "${VENV_DIR}/bin/activate"
python -m pip install --upgrade pip >/dev/null
pip install -r requirements.txt

echo -e "${BLUE}[3/8] Prüfe Backend-.env Vorlage${NC}"
if [[ ! -f .env.example ]]; then
  echo -e "${RED}ERROR:${NC} osint-platform-backend/.env.example fehlt"
  exit 1
fi

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo -e "${GREEN}✓ Backend .env aus .env.example erstellt${NC}"
else
  echo -e "${YELLOW}ℹ Backend .env existiert bereits – wird nicht überschrieben${NC}"
fi

if grep -q '^SECRET_KEY=change-me$' .env; then
  SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
  python - <<PYTHON
from pathlib import Path
env_path = Path(".env")
content = env_path.read_text()
content = content.replace("SECRET_KEY=change-me", "SECRET_KEY=${SECRET_KEY}")
env_path.write_text(content)
PYTHON
  sed "s|^SECRET_KEY=change-me$|SECRET_KEY=${SECRET_KEY}|" .env > "${tmp_env_file}" && mv "${tmp_env_file}" .env
  echo -e "${GREEN}✓ SECRET_KEY wurde sicher generiert${NC}"
fi

echo -e "${BLUE}[4/8] Installiere Frontend-Dependencies${NC}"
cd "${FRONTEND_DIR}"
if [[ -f package-lock.json ]]; then
  npm ci
else
  npm install
fi

echo -e "${BLUE}[5/8] Erzeuge Frontend-.env.local${NC}"
if [[ ! -f .env.example ]]; then
  echo -e "${RED}ERROR:${NC} app/.env.example fehlt"
  exit 1
fi

if [[ ! -f .env.local ]]; then
  cp .env.example .env.local
  echo -e "${GREEN}✓ Frontend .env.local aus .env.example erstellt${NC}"
else
  echo -e "${YELLOW}ℹ Frontend .env.local existiert bereits – wird nicht überschrieben${NC}"
fi

echo -e "${BLUE}[6/8] Erzeuge Frontend-Build${NC}"
npm run build

mkdir -p "${BACKEND_DIR}/static"
rm -rf "${BACKEND_DIR}/static"/*

if [[ ! -d dist ]]; then
  echo -e "${RED}ERROR:${NC} Frontend-Build-Verzeichnis 'dist/' wurde nicht gefunden. Bitte prüfen, ob 'npm run build' erfolgreich war."
  exit 1
  PIDS="$(lsof -ti:"${BACKEND_PORT}" 2>/dev/null || true)"
  if [[ -n "${PIDS}" ]]; then
    # Versuche zuerst einen sauberen Shutdown mit SIGTERM
    kill ${PIDS} 2>/dev/null || true
    sleep 2
    # Erzwinge ggf. das Beenden verbleibender Prozesse mit SIGKILL
    kill -9 ${PIDS} 2>/dev/null || true
  fi

if ! compgen -G "dist/*" > /dev/null; then
  echo -e "${RED}ERROR:${NC} Frontend-Build-Verzeichnis 'dist/' ist leer. Bitte prüfen, ob 'npm run build' erfolgreich war."
  exit 1
fi
cp -r dist/* "${BACKEND_DIR}/static/"

echo -e "${BLUE}[7/8] Starte Backend${NC}"
cd "${BACKEND_DIR}"
if command -v lsof >/dev/null 2>&1; then
  PIDS="$(lsof -ti":${BACKEND_PORT}" -sTCP:LISTEN 2>/dev/null || true)"
  if [[ -n "${PIDS}" ]]; then
    kill -- ${PIDS} 2>/dev/null || true
    sleep 2
    kill -9 -- ${PIDS} 2>/dev/null || true
  fi
fi

python app.py &
BACKEND_PID="$!"

echo -e "${BLUE}[8/8] Warte auf Health-Check${NC}"
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

if [[ ! -f "${BACKEND_DIR}/.env" ]] || [[ ! -f "${FRONTEND_DIR}/.env.local" ]]; then
  echo -e "${RED}ERROR:${NC} Eine der zwei erwarteten .env-Dateien fehlt."
  exit 1
fi

# Determine local IP address in a cross-platform way
if command -v uname >/dev/null 2>&1; then
  case "$(uname)" in
    Darwin)
      # macOS: try common interfaces, fall back to localhost
      IP_ADDRESS="$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || printf '127.0.0.1')"
      ;;
    *)
      # Linux/other: try hostname -I, fall back to localhost if it fails or is empty
      if command -v hostname >/dev/null 2>&1; then
        IP_ADDRESS="$(hostname -I 2>/dev/null | awk '{print $1}')"
      fi
      : "${IP_ADDRESS:=127.0.0.1}"
      ;;
  esac
else
  # Fallback if uname is unavailable
  IP_ADDRESS="127.0.0.1"
fi

echo -e "${GREEN}"
cat <<SUCCESS
┌──────────────────────────────────────────────────────────────┐
│  ✅ INSTALLATION FERTIG                                      │
│  🌐 Öffne: http://localhost:${BACKEND_PORT}                  │
│  🔍 API:   http://localhost:${BACKEND_PORT}/api/health       │
│  🛑 Stop:  Ctrl + C                                          │
└──────────────────────────────────────────────────────────────┘
SUCCESS

echo -e "${NC}${BLUE}LAN URL:${NC} http://${IP_ADDRESS}:${BACKEND_PORT}"

wait "${BACKEND_PID}"
