# 🚀 OSINT Phone Intelligence Platform – Schnellstart

```text
╔════════════════════════════════════════════════════╗
║   1) chmod +x start_osint.sh                      ║
║   2) ./start_osint.sh                             ║
║   3) Browser: http://localhost:15000              ║
╚════════════════════════════════════════════════════╝
```

## Was wurde bei der Installation korrigiert?

- Beide Vorlagen sind vorhanden: `osint-platform-backend/.env.example` und `app/.env.example`.
- Installer erstellt automatisch **2 aktive Env-Dateien**: `osint-platform-backend/.env` und `app/.env.local`.
- Frontend wird gebaut und in `osint-platform-backend/static/` bereitgestellt.
- Health-Check prüft zuverlässig, ob der Server wirklich läuft.

## Manueller Start (Fallback)

### Backend
```bash
cd osint-platform-backend
cp .env.example .env
# SECRET_KEY setzen (Pflicht):
sed -i.bak "s/^SECRET_KEY=.*/SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')/" .env && rm -f .env.bak
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

> **Hinweis:** Die `.env`-Datei setzt `PORT=15000`. Ohne diese Datei startet Flask auf dem Default-Port 5000.

### Frontend (nur Dev-Modus)
```bash
cd app
npm install
npm run dev
```

Dann im Browser öffnen:
- Backend-UI: `http://localhost:15000`
- Frontend-Dev: `http://localhost:5173`
