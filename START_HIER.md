# 🚀 OSINT Phone Intelligence Platform - Schnellstart

## Ein-Klick-Start

```bash
./start_osint.sh
```

Dann öffne deinen Browser:
- **http://localhost:15000**

## Was das Skript macht

1. ✅ Prüft Python & Node.js
2. ✅ Installiert Abhängigkeiten (falls nötig)
3. ✅ Erstellt Konfigurationsdateien
4. ✅ Baut das Frontend
5. ✅ Startet Backend + Frontend

## Testen der Suche

Sobald die Seite geladen ist:

1. Gib eine **Telefonnummer** ein z.B. `+49 170 1234567`
2. Oder einen **Username** z.B. `@johndoe`
3. Oder einen **Namen** z.B. `Max Mustermann`
4. Klicke auf **"Search"**

## Ergebnisse

Die Ergebnisse werden in Tabs angezeigt:
- **Overview** - Telefonanalyse (Carrier, Ort, Format)
- **Social** - Social Media Profile
- **Web** - Web-Suchergebnisse
- **Risk** - Risiko-Bewertung
- **Sources** - Externe Datenbank-Links
- **AI** - KI-Analyse (Kimi, Perplexity)

## Fehlerbehebung

### "Port already in use"
```bash
lsof -ti:15000 | xargs kill -9
```

### "Module not found"
```bash
cd osint-platform-backend
pip3 install flask flask-cors flask-limiter flask-talisman phonenumbers duckduckgo-search requests python-dotenv
```

### Frontend bauen
```bash
cd app
npm install
npm run build
```

## Manueller Start (falls das Skript nicht funktioniert)

**Terminal 1 - Backend:**
```bash
cd osint-platform-backend
python3 app.py
```

**Terminal 2 - Frontend:**
```bash
cd app
npm run dev
```

Dann öffne: http://localhost:5173

---

**Hinweis:** Die KI-API-Keys (Kimi & Perplexity) sind bereits verschlüsselt in der `.env` Datei eingetragen.
