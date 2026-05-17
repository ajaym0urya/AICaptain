import os
import time
from typing import Dict, Tuple
import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI CricTracker Backend")

# Allow requests from Next.js frontend (useful for local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq Client
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY)

class URLRequest(BaseModel):
    url: str

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- SIMPLE MEMORY CACHE ---
# Structure: { "url": (timestamp, data_dict) }
CACHE_TTL = 10 # seconds
live_cache: Dict[str, Tuple[float, dict]] = {}

async def fetch_html(url: str) -> str:
    async with httpx.AsyncClient() as http_client:
        try:
            response = await http_client.get(url, headers=HEADERS, timeout=15.0)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")

def ask_groq(prompt: str, data: str, json_schema: str) -> str:
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is not set.")
    
    full_prompt = f"""
    {prompt}
    
    Return ONLY a valid JSON object matching this schema. No markdown, no intro.
    {json_schema}
    
    Data:
    {data}
    """
    
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": full_prompt}],
        model="llama-3.1-8b-instant",
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content


@app.post("/api/scrape/static")
async def scrape_static(req: URLRequest):
    html = await fetch_html(req.url)
    soup = BeautifulSoup(html, 'html.parser')
    
    match_header = soup.find('h1')
    match_info_div = soup.find(class_='cb-match-info')
    
    text_data = (match_header.get_text(separator=' ', strip=True) if match_header else "") + " " + \
                (match_info_div.get_text(separator=' ', strip=True) if match_info_div else soup.text[:2000])

    prompt = "Extract static match information like venue, series, and toss details."
    schema = """
    {
      "matchTitle": "e.g., India vs Australia, 1st Test",
      "venue": "e.g., WACA Ground, Perth",
      "toss": "e.g., India won the toss and opt to bat",
      "format": "e.g., Test, ODI, or T20"
    }
    """
    
    import json
    result = ask_groq(prompt, text_data, schema)
    return json.loads(result)


@app.post("/api/scrape/live")
async def scrape_live(req: URLRequest):
    # Check cache first
    now = time.time()
    if req.url in live_cache:
        cached_time, cached_data = live_cache[req.url]
        if now - cached_time < CACHE_TTL:
            return cached_data

    # Not in cache or expired, fetch new data
    html = await fetch_html(req.url)
    soup = BeautifulSoup(html, 'html.parser')
    
    live_container = soup.find(class_='cb-col-100 cb-col') 
    commentary = soup.find(class_='cb-com-ln')
    
    raw_text = ""
    if live_container:
        raw_text += live_container.get_text(separator=' ', strip=True)
    if commentary:
        raw_text += " " + commentary.parent.get_text(separator=' ', strip=True)
        
    if not raw_text:
        raw_text = soup.body.get_text(separator=' ', strip=True)[:5000]
    
    raw_text = raw_text[:5000]

    prompt = "Extract the current live score, run rate, batsmen, bowlers, and recent balls."
    schema = """
    {
      "matchStatus": "e.g., India won by 10 wickets / Day 2: Stumps",
      "score": "e.g., IND 250/3 (45.2 Ovs)",
      "runRate": "e.g., CRR: 5.52 RRR: 7.10",
      "batsmen": [
        { "name": "Player 1", "runs": "45", "balls": "30" }
      ],
      "bowlers": [
        { "name": "Bowler 1", "overs": "4.2", "runs": "20", "wickets": "1" }
      ],
      "recentBalls": [
        "45.2: Bowler to Batsman, FOUR",
        "45.1: Bowler to Batsman, no run"
      ]
    }
    """
    
    import json
    try:
        result = ask_groq(prompt, raw_text, schema)
        parsed_result = json.loads(result)
        
        # Save to cache
        live_cache[req.url] = (now, parsed_result)
        return parsed_result
    except Exception as e:
        return {"error": str(e), "data": raw_text[:200]}


@app.post("/api/scrape/history")
async def scrape_history(req: URLRequest):
    """Dedicated endpoint for AI Agents to fetch deep historical data"""
    html = await fetch_html(req.url)
    soup = BeautifulSoup(html, 'html.parser')
    
    # Grab the entire commentary section (much larger than live)
    commentary_container = soup.find(id='matchCenter') or soup.body
    raw_text = commentary_container.get_text(separator=' | ', strip=True)
    
    # Allow a larger context window for the agent history (e.g. 15,000 chars)
    raw_text = raw_text[:15000]

    prompt = "Analyze the historical commentary provided. Summarize the key events, major partnerships, wickets, and the overall momentum shift of the match based on these past overs."
    schema = """
    {
      "matchSummary": "A 3-4 sentence detailed summary of the match so far.",
      "keyEvents": ["Event 1 e.g. Kohli hits 3 fours in an over", "Event 2 e.g. Bumrah takes back to back wickets"],
      "turningPoint": "What was the biggest turning point so far?"
    }
    """
    
    import json
    result = ask_groq(prompt, raw_text, schema)
    return json.loads(result)


# --- SERVE STATIC FRONTEND (For Docker / Production) ---
frontend_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
