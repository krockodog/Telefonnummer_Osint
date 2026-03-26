# 🚀 OSINT Phone Intelligence Platform – Schnellstart

```text
╔════════════════════════════════════════════════════╗
║   1) chmod +x start_osint.sh                      ║
║   2) ./start_osint.sh                             ║
║   3) Browser: http://localhost:15000              ║
╚════════════════════════════════════════════════════╝
```

## Was wurde bei der Installation korrigiert?

- Kein fehlerhaftes `cp .env.example .env` mehr (es gab keine `.env.example`).
- `.env` wird jetzt automatisch und sicher mit zufälligem `SECRET_KEY` erstellt.
- Frontend wird gebaut und in `osint-platform-backend/static/` deployt.
- Health-Check prüft zuverlässig, ob der Server wirklich läuft.

## Manueller Start (Fallback)

### Backend
```bash
cd osint-platform-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Frontend (nur Dev-Modus)
```bash
cd app
npm install
npm run dev
```

Dann im Browser öffnen:
- Backend-UI: `http://localhost:15000`
- Frontend-Dev: `http://localhost:5173`
