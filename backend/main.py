import os
import time
import json
import asyncio
from typing import Dict, Tuple
import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv
from agents import run_captain_pipeline

load_dotenv()

app = FastAPI(title="AI CricTracker — Captain Cool Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL = "gemini-2.5-flash"

def get_client() -> genai.Client:
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set.")
    return genai.Client(api_key=GEMINI_API_KEY)

class URLRequest(BaseModel):
    url: str

class CaptainRequest(BaseModel):
    url: str  # Cricbuzz match URL

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

# ── Memory Cache (10s TTL for live endpoint) ──────────────────────────────────
CACHE_TTL = 10
live_cache: Dict[str, Tuple[float, dict]] = {}


# ── Internal Scraper (used by agents as tool + by HTTP endpoints) ─────────────
async def _fetch_html(url: str) -> str:
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url, headers=HEADERS, timeout=15.0)
            r.raise_for_status()
            return r.text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e}")


async def _extract_static(html: str) -> dict:
    """Extract static match info using Gemini."""
    soup = BeautifulSoup(html, 'html.parser')
    h1 = soup.find('h1')
    info = soup.find(class_='cb-match-info')
    text = (h1.get_text(' ', strip=True) if h1 else "") + " " + \
           (info.get_text(' ', strip=True) if info else soup.text[:2000])

    client = get_client()
    prompt = f"""
    Extract static match information from this text.
    Return ONLY valid JSON matching this schema:
    {{"matchTitle":"","venue":"","toss":"","format":""}}
    
    Text: {text[:3000]}
    """
    r = await asyncio.to_thread(
        client.models.generate_content,
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.1)
    )
    raw = r.text.strip().strip("```json").strip("```").strip()
    return json.loads(raw)


async def _extract_live(html: str) -> dict:
    """Extract live score data using Gemini."""
    soup = BeautifulSoup(html, 'html.parser')
    container = soup.find(class_='cb-col-100 cb-col')
    commentary = soup.find(class_='cb-com-ln')

    text = ""
    if container:
        text += container.get_text(' ', strip=True)
    if commentary:
        text += " " + commentary.parent.get_text(' ', strip=True)
    if not text:
        text = soup.body.get_text(' ', strip=True)[:5000]
    text = text[:5000]

    client = get_client()
    schema = json.dumps({
        "matchStatus": "",
        "score": "",
        "runRate": "",
        "batsmen": [{"name": "", "runs": "", "balls": ""}],
        "bowlers": [{"name": "", "overs": "", "runs": "", "wickets": ""}],
        "recentBalls": [""]
    })
    prompt = f"""
    Extract live cricket match data from the text below.
    Return ONLY valid JSON matching this schema (no markdown):
    {schema}
    
    Text: {text}
    """
    r = await asyncio.to_thread(
        client.models.generate_content,
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.1)
    )
    raw = r.text.strip().strip("```json").strip("```").strip()
    return json.loads(raw)


# ── API Endpoints ─────────────────────────────────────────────────────────────

@app.post("/api/scrape/static")
async def scrape_static(req: URLRequest):
    html = await _fetch_html(req.url)
    return await _extract_static(html)


@app.post("/api/scrape/live")
async def scrape_live(req: URLRequest):
    # Cache check
    now = time.time()
    if req.url in live_cache:
        ts, data = live_cache[req.url]
        if now - ts < CACHE_TTL:
            return data

    html = await _fetch_html(req.url)
    result = await _extract_live(html)
    live_cache[req.url] = (now, result)
    return result


@app.post("/api/scrape/history")
async def scrape_history(req: URLRequest):
    """For AI agents: deep historical commentary analysis."""
    html = await _fetch_html(req.url)
    soup = BeautifulSoup(html, 'html.parser')
    container = soup.find(id='matchCenter') or soup.body
    text = container.get_text(' | ', strip=True)[:15000]

    client = get_client()
    schema = json.dumps({
        "matchSummary": "",
        "keyEvents": [""],
        "turningPoint": ""
    })
    prompt = f"""
    Analyze this historical cricket commentary and extract key insights.
    Return ONLY valid JSON matching this schema:
    {schema}
    
    Data: {text}
    """
    r = await asyncio.to_thread(
        client.models.generate_content,
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.3)
    )
    raw = r.text.strip().strip("```json").strip("```").strip()
    return json.loads(raw)


@app.post("/api/captain")
async def get_captain_decision(req: CaptainRequest):
    """
    Main agentic endpoint. Runs the 4-agent Captain Cool pipeline:
    StatsAnalyst (with live tool call) → Strategist → Devil's Advocate → Commentator
    """
    # Pre-fetch live data from our scraper (this IS the real tool call)
    now = time.time()
    if req.url in live_cache and now - live_cache[req.url][0] < CACHE_TTL:
        live_data = live_cache[req.url][1]
    else:
        html = await _fetch_html(req.url)
        live_data = await _extract_live(html)
        live_cache[req.url] = (now, live_data)

    # Run the full multi-agent pipeline
    result = await run_captain_pipeline(url=req.url, raw_live_data=live_data)
    return result


# ── Serve Static Frontend (Production Docker) ─────────────────────────────────
frontend_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
