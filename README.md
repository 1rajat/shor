# Shor — Indian News Sentiment Intelligence

Real-time sentiment analysis platform for Indian news. Scrapes 60+ RSS sources, classifies articles using LLaMA-3 via Groq, and surfaces topic-level signals across politics, economy, cricket, business, and more.

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green) ![MongoDB](https://img.shields.io/badge/MongoDB-Motor-brightgreen) ![LLaMA](https://img.shields.io/badge/LLM-LLaMA--3.1--8b-orange)

## What It Does

- Scrapes 60+ Indian news sources every 5 minutes (NDTV, Times of India, The Hindu, Economic Times, Amar Ujala, Dainik Jagran, and more)
- Classifies each article using LLaMA-3.1-8b — sentiment (pos/neg/neu), score (-100 to +100), topic, region, entities
- Detects topic-level signals: groups related articles into **spike**, **trending**, or **sustained** signals
- Deduplicates syndicated stories across sources at both pipeline and UI level
- Serves results via REST API with real-time frontend

## Architecture

```
RSS Feeds (60+ sources)
        ↓
  news_rss.py          — parallel fetch, age filter, dedup
        ↓
  sentiment.py         — LLaMA-3.1-8b via Groq API (structured JSON extraction)
        ↓
  signal_detector.py   — topic grouping, signal type classification, scoring
        ↓
  fact_checker.py      — source credibility check
        ↓
  MongoDB              — signals collection, processed_articles cache
        ↓
  FastAPI              — REST API (/api/signals, /api/status, /api/refresh)
        ↓
  Vanilla JS frontend  — real-time overview, signal detail, source bar
```

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.9, FastAPI, Motor (async MongoDB) |
| LLM | LLaMA-3.1-8b-instant via Groq API |
| Scraping | feedparser, httpx, concurrent.futures |
| Database | MongoDB |
| Frontend | Vanilla JS, HTML/CSS (no framework) |

## Setup

### Prerequisites
- Python 3.9+
- MongoDB running locally (`mongod`)
- Groq API key — free at [console.groq.com](https://console.groq.com)

### Install

```bash
git clone https://github.com/YOUR_USERNAME/shor.git
cd shor/backend

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### Configure

```bash
cp .env.example .env
```

Edit `.env`:
```
GROQ_API_KEY=your_groq_api_key_here
MONGO_URI=mongodb://localhost:27017
MONGO_DB=shor
```

### Run

```bash
# Terminal 1 — backend
cd shor/backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend
cd shor/frontend
python -m http.server 3000
```

Open [http://localhost:3000](http://localhost:3000)

The backend auto-refreshes every 5 minutes. Hit **Refresh** in the UI to force an immediate fetch.

## API

| Endpoint | Description |
|----------|-------------|
| `GET /api/signals` | List all signals (filter by sentiment, region, type) |
| `GET /api/signals/{id}` | Signal detail with all articles |
| `POST /api/signals/refresh?force=true` | Trigger immediate refresh |
| `GET /api/status` | Pipeline status, last refresh time, signal count |
| `GET /health` | Health check |

### Query Parameters (`GET /api/signals`)
- `sentiment` — `pos`, `neg`, `neu`
- `region` — `Delhi`, `Mumbai`, `Bangalore`, `National`, etc.
- `signal_type` — `spike`, `trending`, `sustained`
- `limit` — default 50, max 200
- `skip` — for pagination

## Signal Types

| Type | Meaning |
|------|---------|
| `spike` | Sudden surge — 5+ articles in a short window |
| `trending` | Sustained coverage — 3+ articles over time |
| `sustained` | Long-running story with consistent coverage |

## News Sources

60+ sources across categories:

- **National** — NDTV, Times of India, The Hindu, Hindustan Times, India Today
- **Business** — Economic Times, Livemint, Moneycontrol, Business Standard
- **Hindi** — Amar Ujala, Dainik Jagran, Dainik Bhaskar, Navbharat Times
- **South** — Deccan Herald, Mathrubhumi, The News Minute, Deccan Chronicle
- **Digital** — The Wire, Scroll.in, The Print, The Quint, Newslaundry
- **Sports** — ESPNCricinfo, Sportskeeda, NDTV Sports
- **Entertainment** — Bollywood Hungama, Pinkvilla, Filmfare
- **Government** — PIB India

## License

MIT
