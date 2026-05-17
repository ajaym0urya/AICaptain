"""
Tool definitions for Gemini function calling.
The StatsAnalystAgent uses these to fetch live cricket data.
"""
from google.genai import types

# ── Gemini Function Declaration ────────────────────────────────────────────────
# This is the formal schema Gemini uses to decide when/how to call our scraper.
GET_LIVE_MATCH_DATA = types.FunctionDeclaration(
    name="get_live_match_data",
    description=(
        "Fetches real-time cricket match data from a Cricbuzz live match URL. "
        "Returns the current score, run rate, active batsmen, active bowlers, "
        "and the most recent ball-by-ball commentary."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "url": types.Schema(
                type=types.Type.STRING,
                description="The full Cricbuzz live match URL, e.g. https://www.cricbuzz.com/live-cricket-scores/..."
            )
        },
        required=["url"]
    )
)

SCRAPER_TOOL = types.Tool(function_declarations=[GET_LIVE_MATCH_DATA])
