<div align="center">

# 🏏 Captain Cool AI

### Multi-Agent IPL Match Strategist powered by Google Gemini 2.5 Flash

[![Deploy to Cloud Run](https://github.com/ajaym0urya/AICaptain/actions/workflows/deploy.yml/badge.svg)](https://github.com/ajaym0urya/AICaptain/actions/workflows/deploy.yml)
![Gemini 2.5 Flash](https://img.shields.io/badge/Gemini-2.5%20Flash-blue?logo=google&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js&logoColor=white)
![Google Cloud Run](https://img.shields.io/badge/Cloud%20Run-deployed-4285F4?logo=google-cloud&logoColor=white)

*Built for the [Agentic Premier League (APL)](https://gdg.community.dev/events/details/google-gdg-cloud-pune-presents-build-with-ai-hackathon-live/) by GDG Cloud Pune using Google Antigravity*

</div>

---

## ✨ What is Captain Cool AI?

Paste any **live Cricbuzz match URL** and get:

1. **Real-time scores** — live score, run rate, batsmen, bowlers, ball-by-ball commentary, updated every 10 seconds without reloading
2. **6-Agent Gemini Debate** — five specialized AI agents debate the next tactical decision in a genuine multi-turn loop
3. **Win Probability + Counterfactual** — "If Bumrah bowls now, MI win prob rises 21%. If Hardik bowls instead, it drops 9%"
4. **🎙️ Voice Output** — click Listen and the Commentator reads the verdict aloud like Star Sports

---

## 🤖 The 6-Agent Pipeline

```
StatsAnalyst ──► Strategist ──► Devil's Advocate ──► Strategist (Rebuttal) ──► Match Predictor ──► Commentator
 [TOOL CALL]     [PROPOSES]       [CHALLENGES]       [DEFENDS / REVISES]      [WIN PROBABILITY]   [VERDICT]
```

| # | Agent | Role | Model |
|---|---|---|---|
| 1 | **Stats Analyst** | Calls the live scraper tool, interprets match data | Gemini 2.5 Flash |
| 2 | **The Strategist** | Proposes one precise tactical decision (Dhoni Mode) | Gemini 2.5 Flash |
| 3 | **Devil's Advocate** | Challenges the proposal with precedent + alternative | Gemini 2.5 Flash |
| 4 | **The Strategist (Rebuttal)** | Hears the challenge — defends or revises the call | Gemini 2.5 Flash |
| 5 | **Match Predictor** | Win probability + counterfactual analysis | Gemini 2.5 Flash |
| 6 | **Match Commentator** | Fan-friendly Star Sports verdict + voice output | Gemini 2.5 Flash |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│              Next.js 15 Frontend                 │
│  Live Score Board  │  Captain's Corner UI        │
│  • 10s auto-poll   │  • Agent debate timeline    │
│  • Static once     │  • Win probability card     │
│                    │  • 🎙️ Voice output          │
│                    │  • 🔧 Tool call badge        │
└────────────────────┬─────────────────────────────┘
                     │
            ┌────────▼────────┐
            │  FastAPI Backend │
            │  port 8080       │
            │  10s cache       │
            └────────┬────────┘
                     │
            ┌────────▼──────────┐
            │  BeautifulSoup    │
            │  (HTML stripping) │
            └────────┬──────────┘
                     │
            ┌────────▼──────────┐
            │   Cricbuzz.com    │
            │  (live match page)│
            └────────┬──────────┘
                     │
            ┌────────▼──────────┐
            │  Gemini 2.5 Flash │
            │  (google-genai)   │
            └───────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **AI Model** | Google Gemini 2.5 Flash |
| **Agent SDK** | `google-genai` Python SDK with function calling |
| **Backend** | FastAPI + Uvicorn (async Python) |
| **Scraper** | `httpx` + `BeautifulSoup4` |
| **Frontend** | Next.js 15 (App Router, Static Export) |
| **Styling** | Tailwind CSS v4 + Framer Motion |
| **Voice** | Web Speech API (`SpeechSynthesisUtterance`) |
| **Container** | Docker multi-stage (Node 20 → Python 3.11) |
| **CI/CD** | GitHub Actions → Google Cloud Run |
| **IDE** | Google Antigravity |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- A **Gemini API Key** from [aistudio.google.com](https://aistudio.google.com/app/apikey) (free)

### 1. Clone the repo
```bash
git clone https://github.com/ajaym0urya/AICaptain
cd AICaptain
```

### 2. Start the Backend
```bash
cd backend

# Create environment file
cp .env.example .env
# Edit .env and add: GEMINI_API_KEY=your_key_here

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
python -m uvicorn main:app --reload
# Server runs at http://localhost:8000
```

> **Windows users**: If `pip` or `python` isn't recognized, use the full path:
> `& "C:\Users\<you>\AppData\Local\Programs\Python\Python314\python.exe" -m pip install -r requirements.txt`

### 3. Start the Frontend
```bash
cd frontend

# Install dependencies
npm install          # or: npm.cmd install (Windows)

# Start dev server
npm run dev          # or: npm.cmd run dev (Windows)
# Opens at http://localhost:3000
```

### 4. Use the App
1. Open `http://localhost:3000`
2. Paste any **live Cricbuzz match URL** (e.g. `https://www.cricbuzz.com/live-cricket-scores/...`)
3. Click **Start Tracking** — live scores appear and auto-refresh
4. Click **⚡ Ask AI Captain** — watch the 6-agent debate unfold
5. Click **🎙️ Listen** — hear the commentator verdict

---

## 📁 Project Structure

```
AICaptain/
├── backend/
│   ├── main.py          # FastAPI app — all API endpoints + static file serving
│   ├── agents.py        # 6 Gemini agent classes + orchestration pipeline
│   ├── tools.py         # Gemini function calling declaration (scraper tool)
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx      # Main page
│   │   │   └── layout.tsx
│   │   └── components/
│   │       ├── CricbuzzLive.tsx   # Live score dashboard + polling
│   │       └── CaptainCorner.tsx  # Agent debate UI + voice
│   ├── next.config.ts    # Static export config
│   └── package.json
│
├── .github/
│   └── workflows/
│       └── deploy.yml    # GitHub Actions → Cloud Run CD pipeline
│
├── Dockerfile            # Multi-stage: Node 20 build → Python 3.11 serve
└── .gitignore
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/scrape/static` | Venue, toss, match title — fetched once |
| `POST` | `/api/scrape/live` | Live score, batsmen, bowlers — 10s cached |
| `POST` | `/api/scrape/history` | Deep historical commentary for AI agents |
| `POST` | `/api/captain` | Full 6-agent debate pipeline |

All endpoints accept: `{ "url": "https://www.cricbuzz.com/..." }`

---

## ☁️ Deployment (Google Cloud Run)

Push to `main` → GitHub Actions auto-builds → deploys to Cloud Run.

### Required GitHub Secrets

| Secret | Description |
|---|---|
| `GCP_PROJECT_ID` | Your Google Cloud project ID |
| `GCP_SA_KEY` | Service account JSON key (Artifact Registry + Cloud Run roles) |
| `GEMINI_API_KEY` | Your Gemini API key |
| `GEMINI_API_KEY` | Reserved for future agent expansion |

### Manual Deploy
```bash
docker build -t captain-cool .
docker run -p 8080:8080 -e GEMINI_API_KEY=your_key captain-cool
```

---

## 🏆 Hackathon — APL by GDG Cloud Pune

This project was built for the **Agentic Premier League** hackathon.

**Mandatory Stack Used:**
- ✅ Gemini API (`gemini-2.5-flash` via `google-genai`)
- ✅ Google Antigravity (AI coding assistant — full session trace in commit history)
- ✅ Gemini Function Calling (real tool call from `StatsAnalystAgent`)
- ✅ Google Cloud Run (deployment target)
- ✅ GitHub Actions (CI/CD)

**Hard Requirements Met:**
- ✅ 5+ distinct named Gemini agents with separate system prompts
- ✅ Real tool call (`get_live_match_data` via Gemini function calling)
- ✅ Multi-turn reasoning loop (Strategist → Devil's Advocate → **Strategist Rebuttal**)
- ✅ Fan-friendly explainability (Commentator agent in plain English + voice)

**Stretch Goals Implemented:**
- ✅ Real-time mode — live Cricbuzz URL scraping
- ✅ Win probability + counterfactual analysis
- ✅ Voice output via Web Speech API
- ✅ Memory / caching across polling cycles

---

## 📝 License

MIT — feel free to use, fork, and build on top of this.

---

<div align="center">

Built with ❤️ using **Google Antigravity** | **Gemini 2.5 Flash** | lots of chai ☕

</div>
