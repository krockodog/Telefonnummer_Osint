# OSINT Phone Intelligence Platform

A professional, production-ready platform for phone number OSINT (Open Source Intelligence) investigations.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Node](https://img.shields.io/badge/node-18+-green.svg)

## Overview

The OSINT Phone Intelligence Platform enables users to investigate phone numbers, discover associated social media profiles, and analyze risk factors through a modern web interface. All investigations are conducted ethically and in compliance with data protection regulations.

## Features

### Core Functionality
- **Phone Number Analysis**: Validate numbers, extract carrier info, location, and timezone
- **Social Media Search**: Find profiles on Facebook, Instagram, Twitter/X, LinkedIn, TikTok, Telegram, WhatsApp
- **Web Search**: Search for numbers across multiple sources
- **Risk Assessment**: Comprehensive risk scoring based on multiple factors
- **Lookup Sources**: Direct links to external phone lookup databases
- **AI-Powered Analysis**: Enhanced insights from Kimi, Perplexity, and Gemini

### Security & Compliance
- **Rate Limiting**: Prevents API abuse
- **Input Validation**: Sanitizes all user inputs
- **GDPR/BDSG Compliant**: No persistent data storage
- **Legal Disclaimer**: Clear terms of use

### Technical Features
- **Modern Frontend**: React 18 + TypeScript + Tailwind CSS
- **Robust Backend**: Python Flask with security best practices
- **Responsive Design**: Works on all devices
- **Dark Theme**: Professional OSINT-optimized interface

## Quick Start

### One-Command Installer (recommended)

```bash
chmod +x start_osint.sh
./start_osint.sh
```

```text
╔══════════════════════════════════════════════════════════════╗
║  Installer erledigt automatisch:                            ║
║  • Python venv + pip install                                ║
║  • npm install + Frontend Build                             ║
║  • erzeugt 2 aktive Env-Dateien aus .env.example          ║
║  • Start + Health-Check auf Port 15000                      ║
╚══════════════════════════════════════════════════════════════╝
```

Öffne danach: `http://localhost:15000`

Der Installer legt diese Dateien an: `osint-platform-backend/.env` und `app/.env.local`.

### Manual Setup

#### Prerequisites
- Python 3.9+
- Node.js 18+
- npm

#### Backend Setup

```bash
cd osint-platform-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

#### Frontend Setup (development)

```bash
cd app
npm install
npm run dev
```

Frontend dev server: `http://localhost:5173`

## Project Structure

```
.
├── app/                          # React Frontend
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── services/            # API services
│   │   ├── types/               # TypeScript types
│   │   ├── App.tsx              # Main app
│   │   └── main.tsx             # Entry point
│   ├── package.json
│   └── README.md
│
├── osint-platform-backend/      # Python Backend
│   ├── src/                     # Source modules
│   │   ├── phone_analyzer.py
│   │   ├── social_media_search.py
│   │   ├── web_search.py
│   │   └── risk_analyzer.py
│   ├── app.py                   # Flask app
│   ├── config.py                # Configuration
│   ├── requirements.txt
│   └── README.md
│
└── README.md                    # This file
```

## API Documentation

### Endpoints

| Endpoint | Method | Description | Rate Limit |
|----------|--------|-------------|------------|
| `/api/health` | GET | Health check | - |
| `/api/analyze/phone` | POST | Analyze phone number | 30/hour |
| `/api/search/social` | POST | Search social media | 20/hour |
| `/api/search/web` | POST | Web search | 20/hour |
| `/api/lookup/sources` | POST | Get lookup sources | 30/hour |
| `/api/investigate` | POST | Full investigation | 10/hour |
| `/api/platforms` | GET | List platforms | - |

### Example Request

```bash
curl -X POST http://localhost:5000/api/investigate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "+49 170 1234567",
    "type": "phone",
    "include_social": true,
    "include_web": true
  }'
```

## Configuration

### Backend (.env)

```env
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-secret-key
HOST=0.0.0.0
PORT=5000
RATE_LIMIT=100 per hour
DATABASE_URL=sqlite:///osint.db
LOG_LEVEL=INFO
```

### Frontend (.env.local)

```env
VITE_API_URL=http://localhost:5000/api
```

## Deployment

### Production Build

1. Build frontend:
```bash
cd app
npm run build
```

2. Copy build to backend:
```bash
cp -r app/dist/* osint-platform-backend/static/
```

3. Run backend:
```bash
cd osint-platform-backend
python app.py
```

### Docker (Optional)

```dockerfile
# Dockerfile for backend
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## Security Considerations

- Change default `SECRET_KEY` in production (used for API key encryption)
- Use HTTPS in production
- Configure proper CORS origins
- Monitor rate limiting
- Keep dependencies updated
- **Encrypt API keys** using the provided crypto utility:
  ```bash
  python src/crypto_utils.py "sk-your-api-key"
  ```
- Review logs regularly
- Review logs regularly

## Legal & Compliance

### Permitted Use
- Personal security verification
- Fraud investigation
- Law enforcement research
- Journalistic investigations
- Business due diligence

### Prohibited Use
- Stalking or harassment
- Unauthorized surveillance
- Identity theft
- Any illegal activities

### Data Privacy
- No persistent storage of search data
- All processing in memory only
- No personal information collected
- GDPR/BDSG compliant

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for legal OSINT investigations only. Users are responsible for complying with all applicable laws and regulations. The authors assume no liability for misuse of this software.

## Support

For issues, questions, or feature requests, please use the GitHub issue tracker.

## Acknowledgments

- [phonenumbers](https://github.com/daviddrysdale/python-phonenumbers) - Phone number parsing
- [DuckDuckGo Search](https://github.com/deedy5/duckduckgo_search) - Web search
- [shadcn/ui](https://ui.shadcn.com/) - UI components
- [Tailwind CSS](https://tailwindcss.com/) - Styling

---

**Note**: This is a professional tool for legitimate OSINT purposes. Always ensure you have proper authorization and legal basis for your investigations.
