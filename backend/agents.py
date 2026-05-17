"""
Multi-Agent System for "Captain Cool" — IPL Match Strategist.
Four distinct Gemini-powered agents collaborate to make tactical decisions.

Agent Pipeline:
  1. StatsAnalystAgent  → calls live scraper tool, interprets match state
  2. StrategistAgent    → proposes the next captain's decision
  3. DevilsAdvocateAgent → challenges the proposal
  4. MatchCommentatorAgent → produces fan-friendly final output
"""

import json
import asyncio
import os
from google import genai
from google.genai import types
from tools import SCRAPER_TOOL

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL = "gemini-2.5-flash"


def get_client() -> genai.Client:
    return genai.Client(api_key=GEMINI_API_KEY)


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 1: Stats Analyst — Uses Gemini Function Calling to invoke the scraper
# ══════════════════════════════════════════════════════════════════════════════
class StatsAnalystAgent:
    NAME = "Stats Analyst"
    ROLE = "Data Intelligence Officer"
    SYSTEM_PROMPT = """
    You are an elite cricket statistician and data analyst working for an IPL franchise.
    Your job is to use the get_live_match_data tool to fetch live data from a Cricbuzz URL,
    then extract and interpret the key statistics a captain needs:
    - Current match state (score, overs, run rate, required rate if 2nd innings)
    - Batter profiles (who is set, who is new, strike rates)
    - Bowler workloads (who has overs left, who is expensive, who is taking wickets)
    - Momentum (recent dot balls, boundaries, wickets)
    
    Always call the tool first. Then provide a clean, structured match state summary.
    Be precise and data-driven. Use cricket terminology.
    """

    async def analyze(self, url: str, raw_data: dict | None = None) -> str:
        """
        If raw_data is provided (from the existing scraper), use it directly.
        Otherwise, use Gemini function calling to fetch it via the tool.
        """
        client = get_client()

        if raw_data:
            # Direct path: data already fetched by our scraper
            prompt = f"""
            The live match data has been fetched. Here is the current state:
            {json.dumps(raw_data, indent=2)}
            
            Provide a comprehensive tactical analysis of this match state for the captain.
            Focus on: momentum, key player matchups, over-by-over context, and pressure points.
            """
            response = await asyncio.to_thread(
                client.models.generate_content,
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.SYSTEM_PROMPT,
                    temperature=0.2,
                )
            )
            return response.text

        # Function-calling path: let Gemini call the tool
        messages = [
            types.Content(
                role="user",
                parts=[types.Part(text=f"Fetch and analyze the live match at this URL: {url}")]
            )
        ]

        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL,
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=self.SYSTEM_PROMPT,
                tools=[SCRAPER_TOOL],
                temperature=0.2,
            )
        )

        # Check if Gemini wants to call our tool
        candidate = response.candidates[0]
        for part in candidate.content.parts:
            if part.function_call:
                fc = part.function_call
                # Return a signal so main.py can execute the actual scraper
                return json.dumps({
                    "__tool_call__": True,
                    "function": fc.name,
                    "args": dict(fc.args)
                })

        return response.text


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 2: Strategist — Proposes the next tactical decision
# ══════════════════════════════════════════════════════════════════════════════
class StrategistAgent:
    NAME = "The Strategist"
    ROLE = "Virtual Captain (Dhoni Mode)"
    SYSTEM_PROMPT = """
    You are a virtual version of MS Dhoni — calm, calculated, and always 3 steps ahead.
    You receive a match state analysis and must propose ONE specific, decisive tactical decision.
    
    Your decision must cover ONE of:
    - Who bowls the next over and why (consider matchups, dew, pitch)
    - A batting order change (pinch-hitter, promoting anchor, protecting tail)
    - Field placement strategy for the next over
    - Strategic timeout timing and intent
    - Impact Player substitution with specific player name
    
    RULES:
    - Be extremely specific. Name the bowler. Name the fielding position. Name the batter.
    - Give your reasoning in cricket language ("the leggie is wasted against a left-hander in dew")
    - Commit to one decision. Dhoni never hesitates.
    - End your response with: DECISION: [one line summary of the call]
    """

    async def propose(self, match_analysis: str) -> str:
        client = get_client()
        prompt = f"""
        The Stats Analyst has provided this match state:
        ---
        {match_analysis}
        ---
        
        As captain, what is your next tactical move? Explain your reasoning deeply.
        """
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=self.SYSTEM_PROMPT,
                temperature=0.7,
            )
        )
        return response.text


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 3: Devil's Advocate — Challenges the proposal aggressively
# ══════════════════════════════════════════════════════════════════════════════
class DevilsAdvocateAgent:
    NAME = "Devil's Advocate"
    ROLE = "Contrarian Cricket Analyst"
    SYSTEM_PROMPT = """
    You are a sharp, contrarian cricket analyst — think Harsha Bhogle meets Navjot Sidhu on a bad day.
    You have JUST heard the captain's tactical proposal.
    Your job is to CHALLENGE it. Find the flaw. Propose a better alternative.
    
    You must:
    1. Identify the single biggest risk in the captain's decision
    2. Propose a completely different tactical alternative
    3. Give at least one historical cricket precedent where similar decisions backfired
    4. State clearly why YOUR alternative is superior
    
    Be bold. Be specific. Use cricket statistics and analogies.
    End with: COUNTER-PROPOSAL: [one line alternative decision]
    """

    async def challenge(self, strategist_proposal: str, match_analysis: str) -> str:
        client = get_client()
        prompt = f"""
        Match Context:
        {match_analysis}
        
        The Captain's Decision:
        ---
        {strategist_proposal}
        ---
        
        Challenge this decision. What could go wrong? What would YOU do instead?
        """
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=self.SYSTEM_PROMPT,
                temperature=0.8,
            )
        )
        return response.text


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 4: Match Commentator — Fan-friendly final output
# ══════════════════════════════════════════════════════════════════════════════
class MatchCommentatorAgent:
    NAME = "Match Commentator"
    ROLE = "Voice of Cricket (Star Sports)"
    SYSTEM_PROMPT = """
    You are the lead commentator on Star Sports covering an IPL match.
    You have just witnessed a heated debate between the AI Captain and a Devil's Advocate analyst.
    
    Your job is to summarize this for the fans watching at home. You must:
    1. Briefly recap the match situation in exciting, emotional language
    2. Explain the Captain's decision as if it just happened on the field
    3. Acknowledge the Devil's Advocate's concern and explain why the Captain's call still makes sense
    4. Give the FINAL VERDICT — what decision should happen RIGHT NOW
    5. Add a "What to watch for" — what will tell us if this decision was right
    
    Write as if 40,000 fans are watching. Be dramatic. Use cricket emotion.
    No jargon that a casual fan wouldn't understand. Explain every term.
    
    Format your output as:
    🏟️ MATCH SITUATION: ...
    ⚡ THE CAPTAIN'S CALL: ...
    🤔 THE DEBATE: ...
    🏆 FINAL VERDICT: ...
    👀 WATCH FOR: ...
    """

    async def commentate(
        self,
        match_analysis: str,
        strategist_proposal: str,
        devils_challenge: str
    ) -> str:
        client = get_client()
        prompt = f"""
        Match State Summary:
        {match_analysis}
        
        Captain's Proposal:
        {strategist_proposal}
        
        Devil's Advocate Challenge:
        {devils_challenge}
        
        Now commentate on this debate for the fans. Give us the final verdict!
        """
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=self.SYSTEM_PROMPT,
                temperature=0.9,
            )
        )
        return response.text


# ══════════════════════════════════════════════════════════════════════════════
# Orchestrator — Runs the full 4-agent pipeline
# ══════════════════════════════════════════════════════════════════════════════
async def run_captain_pipeline(url: str, raw_live_data: dict | None = None) -> dict:
    """
    Orchestrates the multi-agent debate pipeline:
    StatsAnalyst → Strategist → Devil's Advocate → Commentator
    
    Returns a structured JSON with the full debate and final decision.
    """
    stats_agent = StatsAnalystAgent()
    strategist = StrategistAgent()
    devil = DevilsAdvocateAgent()
    commentator = MatchCommentatorAgent()

    debate_log = []

    # ── Step 1: Stats Analyst ─────────────────────────────────────────────────
    print("[Agent 1/4] StatsAnalystAgent analyzing match...")
    match_analysis = await stats_agent.analyze(url=url, raw_data=raw_live_data)
    debate_log.append({
        "agent": StatsAnalystAgent.NAME,
        "role": StatsAnalystAgent.ROLE,
        "output": match_analysis
    })

    # ── Step 2: Strategist proposes ───────────────────────────────────────────
    print("[Agent 2/4] StrategistAgent proposing decision...")
    strategist_proposal = await strategist.propose(match_analysis)
    debate_log.append({
        "agent": StrategistAgent.NAME,
        "role": StrategistAgent.ROLE,
        "output": strategist_proposal
    })

    # ── Step 3: Devil's Advocate challenges ───────────────────────────────────
    print("[Agent 3/4] DevilsAdvocateAgent challenging...")
    devils_challenge = await devil.challenge(strategist_proposal, match_analysis)
    debate_log.append({
        "agent": DevilsAdvocateAgent.NAME,
        "role": DevilsAdvocateAgent.ROLE,
        "output": devils_challenge
    })

    # ── Step 4: Commentator gives final verdict ───────────────────────────────
    print("[Agent 4/4] MatchCommentatorAgent delivering verdict...")
    final_commentary = await commentator.commentate(
        match_analysis, strategist_proposal, devils_challenge
    )
    debate_log.append({
        "agent": MatchCommentatorAgent.NAME,
        "role": MatchCommentatorAgent.ROLE,
        "output": final_commentary
    })

    # Extract decision lines
    decision_line = next(
        (line.replace("DECISION:", "").strip()
         for line in strategist_proposal.split("\n") if "DECISION:" in line),
        "See captain's full proposal above."
    )
    counter_line = next(
        (line.replace("COUNTER-PROPOSAL:", "").strip()
         for line in devils_challenge.split("\n") if "COUNTER-PROPOSAL:" in line),
        "See devil's advocate challenge above."
    )

    return {
        "agentDebate": debate_log,
        "finalDecision": {
            "decision": decision_line,
            "fullProposal": strategist_proposal,
            "dissentingView": counter_line,
            "commentatorVerdict": final_commentary
        }
    }
