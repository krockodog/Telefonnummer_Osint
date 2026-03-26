# OSINT Phone Intelligence Platform - Backend

A production-ready Python Flask backend for phone number OSINT (Open Source Intelligence) investigations.

## Features

- **Phone Number Analysis**: Validate and extract detailed information from phone numbers
- **Social Media Search**: Discover profiles across multiple platforms
- **Web Search Integration**: Search for phone numbers across the web
- **Risk Assessment**: Comprehensive risk analysis based on multiple factors
- **AI-Powered Analysis**: Integration with Kimi, Perplexity, and Gemini for enhanced insights
- **Security**: Rate limiting, input validation, and secure API design
- **Compliance**: GDPR/BDSG compliant data handling

## Tech Stack

- **Framework**: Flask 2.3+
- **Security**: Flask-Limiter, Flask-Talisman, Flask-CORS
- **Phone Processing**: phonenumbers library
- **Web Search**: DuckDuckGo Search
- **HTTP**: requests, aiohttp

## Installation

### Prerequisites

- Python 3.9 or higher
- pip
- virtualenv (recommended)

### Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` from template:
```bash
cp .env.example .env
```

4. Set a secure `SECRET_KEY` in `.env` (replace `change-me`).

5. Run the application:
```bash
python app.py
```

The API will be available at `http://localhost:15000`

## API Endpoints

### Health Check
```
GET /api/health
```

### Analyze Phone Number
```
POST /api/analyze/phone
Content-Type: application/json

{
  "phone_number": "+49 170 1234567"
}
```

### Search Social Media
```
POST /api/search/social
Content-Type: application/json

{
  "query": "+49 170 1234567",
  "type": "phone",
  "platforms": ["facebook", "instagram", "twitter"]
}
```

### Web Search
```
POST /api/search/web
Content-Type: application/json

{
  "query": "+49 170 1234567",
  "type": "phone"
}
```

### Get Lookup Sources
```
POST /api/lookup/sources
Content-Type: application/json

{
  "phone_number": "+49 170 1234567"
}
```

### Full Investigation
```
POST /api/investigate
Content-Type: application/json

{
  "query": "+49 170 1234567",
  "type": "phone",
  "include_social": true,
  "include_web": true
}
```

### Get Platforms
```
GET /api/platforms
```

### AI Services

#### Get AI Services Status
```
GET /api/ai/status
```

#### AI-Powered Analysis
```
POST /api/ai/analyze
Content-Type: application/json

{
  "query": "+49 170 1234567",
  "type": "phone",
  "providers": ["kimi", "perplexity", "gemini"]
}
```

#### Deep Research (Perplexity)
```
POST /api/ai/research
Content-Type: application/json

{
  "query": "phone number +49 170 1234567 spam reports"
}
```

#### Generate AI Report
```
POST /api/ai/report
Content-Type: application/json

{
  "investigation_data": {
    "query": "+49 170 1234567",
    "phone_analysis": { ... },
    "risk_analysis": { ... }
  }
}
```

#### AI Social Profile Analysis
```
POST /api/ai/social-profile
Content-Type: application/json

{
  "username": "johndoe",
  "platform": "instagram"
}
```

## AI Service Configuration

To enable AI-powered features, configure the following API keys in your `.env` file:

| Service | API Key Variable | Documentation |
|---------|------------------|---------------|
| **Kimi (Moonshot AI)** | `KIMI_API_KEY` | https://platform.moonshot.cn/ |
| **Perplexity AI** | `PERPLEXITY_API_KEY` | https://www.perplexity.ai/settings/api |
| **Google Gemini** | `GEMINI_API_KEY` | https://ai.google.dev/ |

### Secure API Key Storage

API keys can be stored in two ways:

1. **Plain text** (not recommended for production):
   ```env
   KIMI_API_KEY=sk-your-api-key
   ```

2. **Encrypted** (recommended):
   ```env
   KIMI_API_KEY=ENC:encrypted-string-here
   ```

To encrypt an API key:
```bash
python src/crypto_utils.py "sk-your-api-key"
```

The encrypted key will be printed. Copy it with the `ENC:` prefix to your `.env` file.

**Note:** Encrypted keys are tied to your `SECRET_KEY`. If you change `SECRET_KEY`, you must re-encrypt all API keys.

### AI Rate Limits

| Endpoint | Rate Limit |
|----------|------------|
| `/api/ai/analyze` | 15/hour |
| `/api/ai/research` | 10/hour |
| `/api/ai/report` | 5/hour |
| `/api/ai/social-profile` | 20/hour |

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/production) | `production` |
| `DEBUG` | Enable debug mode | `False` |
| `SECRET_KEY` | Flask secret key | Change in production |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `5000` |
| `RATE_LIMIT` | Rate limit string | `100 per hour` |
| `DATABASE_URL` | Database connection URL | `sqlite:///osint.db` |
| `CACHE_TYPE` | Cache backend | `simple` |
| `DATA_RETENTION_DAYS` | Data retention period | `7` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Rate Limiting

The API implements rate limiting to prevent abuse:
- Default: 100 requests per hour per IP
- Investigation endpoint: 10 per hour
- Search endpoints: 20-30 per hour

## Security Features

- **Rate Limiting**: Prevents API abuse
- **Input Validation**: Sanitizes all user inputs
- **CORS Protection**: Configurable CORS origins
- **Security Headers**: XSS protection, CSP, etc.
- **No Data Persistence**: Searches are not stored permanently

## Project Structure

```
osint-platform-backend/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── .env.example         # Example environment configuration
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── src/                 # Source modules
    ├── __init__.py
    ├── phone_analyzer.py      # Phone number analysis
    ├── social_media_search.py  # Social media search
    ├── web_search.py          # Web search functionality
    ├── risk_analyzer.py       # Risk assessment
    └── ai_services.py         # AI integrations (Kimi, Perplexity, Gemini)
```

## Development

### Running Tests

```bash
pytest
```

### Code Style

Follow PEP 8 guidelines:
```bash
flake8 app.py src/
```

## Legal Notice

This tool is intended for legal OSINT investigations only. Users must:
- Comply with GDPR, BDSG, and other applicable data protection laws
- Not use the tool for stalking, harassment, or illegal activities
- Have a legitimate purpose for investigations
- Respect privacy rights of individuals

## License

MIT License - See LICENSE file for details.

## Support

For issues and feature requests, please use the GitHub issue tracker.
