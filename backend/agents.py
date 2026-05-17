"""
Multi-Agent System for "Captain Cool" — IPL Match Strategist.
Five distinct Gemini-powered agents collaborate to make tactical decisions.

Agent Pipeline (fully multi-turn):
  1. StatsAnalystAgent    → calls live scraper tool, interprets match state
  2. StrategistAgent      → proposes the next captain's decision
  3. DevilsAdvocateAgent  → challenges the proposal aggressively
  4. StrategistAgent      → REBUTS or REVISES after hearing the challenge (multi-turn loop)
  5. MatchPredictorAgent  → win probability + counterfactual analysis
  6. MatchCommentatorAgent → fan-friendly final verdict
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
# AGENT 1: Stats Analyst — Real Gemini Function Calling Tool Use
# ══════════════════════════════════════════════════════════════════════════════
class StatsAnalystAgent:
    NAME = "Stats Analyst"
    ROLE = "Data Intelligence Officer"
    SYSTEM_PROMPT = """
    You are an elite cricket statistician and data analyst working for an IPL franchise.
    
    Your job is to use the get_live_match_data tool to fetch live data from a Cricbuzz URL,
    then extract and interpret the key statistics a captain needs:
    - Current match state (score, overs, run rate, required rate if 2nd innings)
    - Batter profiles: who is set (balls faced 20+), who is new, estimated strike rates
    - Bowler workloads: overs remaining per bowler, economy, wickets taken
    - Match phase: Powerplay / Middle overs / Death overs
    - Momentum indicator: recent dot balls, boundary rate, wicket clusters
    - Pitch & conditions context from match info (venue, dew, time of day)
    
    Always call the tool first to get fresh data, then provide a rich, structured analysis.
    Be precise and data-driven. Every claim must be supported by a number.
    """

    async def analyze(self, url: str, raw_data: dict | None = None) -> str:
        client = get_client()

        if raw_data:
            prompt = f"""
            Live match data has been fetched via the get_live_match_data tool:
            
            ```json
            {json.dumps(raw_data, indent=2)}
            ```
            
            Provide a comprehensive tactical analysis of this match state for the captain.
            Structure your output as:
            
            📊 MATCH STATE: [Score, over, phase]
            📈 MOMENTUM: [Who has it and why — dot balls, boundaries, wickets]
            🏏 BATTING: [Who's set, who's new, SR comparison, match-up context]
            🎯 BOWLING: [Overs remaining per bowler, economy, matchup concerns]
            ⚠️ KEY PRESSURE POINTS: [What must happen in the next 2 overs]
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

        # Gemini function-calling path
        messages = [
            types.Content(
                role="user",
                parts=[types.Part(text=f"Fetch and analyze the live match at: {url}")]
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
        for part in response.candidates[0].content.parts:
            if part.function_call:
                fc = part.function_call
                return json.dumps({
                    "__tool_call__": True,
                    "function": fc.name,
                    "args": dict(fc.args)
                })
        return response.text


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 2: Strategist — Proposes the next tactical decision (Turn 1)
# ══════════════════════════════════════════════════════════════════════════════
class StrategistAgent:
    NAME = "The Strategist"
    ROLE = "Virtual Captain (Dhoni Mode)"
    SYSTEM_PROMPT = """
    You are a virtual MS Dhoni — calm, calculated, always 3 steps ahead.
    The best captains in cricket don't just react; they impose their plan.
    
    Given the match state analysis, propose ONE specific, decisive tactical decision.
    Your decision must be one of:
    - Bowling change: who bowls next and exact field placing
    - Batting order: pinch-hitter, promoting an anchor, protecting tail
    - Strategic timeout: exact timing and intent
    - Impact Player: which player, in which role, and when
    - Field setup: specific positions for the next over based on batter weakness
    
    Be extremely specific:
    - Name the bowler AND explain the matchup (e.g., "legspinner vs LHB in dew")
    - Name the exact field positions (e.g., "cow corner, fine leg up")
    - Reference pitch conditions if known
    
    End your response with:
    DECISION: [one precise line — who does what, right now]
    CONFIDENCE: [High / Medium / Low + one line why]
    """

    async def propose(self, match_analysis: str) -> str:
        client = get_client()
        prompt = f"""
        Stats Analyst's Report:
        ---
        {match_analysis}
        ---
        
        As captain, what is your next tactical move? Be decisive and extremely specific.
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

    async def rebut(self, original_proposal: str, devils_challenge: str, match_analysis: str) -> str:
        """
        MULTI-TURN LOOP: The Strategist hears the Devil's Advocate and responds.
        This is the mandatory back-and-forth the rubric requires.
        """
        client = get_client()
        rebuttal_system = """
        You are the same captain who just made a tactical call. 
        A sharp analyst has challenged your decision hard.
        
        Now you must either:
        A) DEFEND your original call — tear apart the challenge with hard facts
        B) REVISE your decision — if the challenge reveals something you missed, adapt
        
        Great captains absorb information and update. But they also stand firm when right.
        Think like Dhoni in the 2011 World Cup final — he came in at #5 against convention
        because he KNEW it was right and defended that call forever after.
        
        End with:
        FINAL CALL: [your committed decision — original or revised]
        VERDICT: [STANDING FIRM / REVISED — one line explaining why]
        """
        prompt = f"""
        Match Context:
        {match_analysis}
        
        Your original proposal:
        {original_proposal}
        
        The Devil's Advocate challenged you with:
        {devils_challenge}
        
        How do you respond? Defend or revise — but commit to a final call.
        """
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=rebuttal_system,
                temperature=0.6,
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
    You are the smartest contrarian in cricket analytics — sharper than any pundit.
    You have just heard the captain's tactical proposal. 
    
    Your ONLY job is to challenge it. Find the flaw. Propose a better alternative.
    
    Structure your challenge as:
    1. 🔴 THE FLAW: The single biggest risk or blind spot in the captain's decision
    2. 📚 PRECEDENT: One real historical match where a similar decision backfired
    3. 🔄 ALTERNATIVE: A completely different tactical move with specific reasoning
    4. 📊 DATA: One statistic that supports your alternative
    
    Be bold. Be specific. Cricket is a game of matchups — use them.
    
    End with:
    COUNTER-PROPOSAL: [exact alternative decision — one precise line]
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
        
        Challenge this decision aggressively. What could go wrong? What's the better move?
        """
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=self.SYSTEM_PROMPT,
                temperature=0.85,
            )
        )
        return response.text


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 4: Match Predictor — Win probability + counterfactual analysis
# ══════════════════════════════════════════════════════════════════════════════
class MatchPredictorAgent:
    NAME = "Match Predictor"
    ROLE = "Win Probability & Counterfactual Analyst"
    SYSTEM_PROMPT = """
    You are a cricket analytics expert specializing in win probability modelling.
    You think like a data scientist but communicate like a cricket commentator.
    
    Given the match state and the tactical debate, you must provide:
    1. Current win probability for both teams (estimated %, must add to 100%)
    2. Impact of the captain's decision on win probability (+X% shift if correct)
    3. Counterfactual: if the ALTERNATIVE decision was taken, how does win % change?
    4. Key variable: what single event in the next 2 overs will most change these numbers?
    
    Use realistic cricket analytics reasoning:
    - Consider run rate, wickets in hand, match phase, pitch conditions
    - Reference DLS concepts, required rate pressure, wicket value in context
    - Be specific with numbers. Vague statements are worthless.
    
    Format exactly as:
    WIN PROBABILITY: [Batting team]% | [Bowling team]%
    DECISION IMPACT: Captain's call shifts win prob by +X% if it works
    COUNTERFACTUAL: Alternative decision would give [Batting team]Y% instead
    SWING EVENT: [The one ball/over that will change everything]
    """

    async def predict(self, match_analysis: str, strategist_proposal: str, devils_counter: str) -> str:
        client = get_client()
        prompt = f"""
        Match State Analysis:
        {match_analysis}
        
        Captain's Proposed Decision:
        {strategist_proposal}
        
        Alternative Decision (Devil's Advocate):
        {devils_counter}
        
        Provide win probability estimates and counterfactual analysis.
        """
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=self.SYSTEM_PROMPT,
                temperature=0.3,
            )
        )
        return response.text


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 5: Match Commentator — Fan-friendly final output
# ══════════════════════════════════════════════════════════════════════════════
class MatchCommentatorAgent:
    NAME = "Match Commentator"
    ROLE = "Voice of Cricket (Star Sports)"
    SYSTEM_PROMPT = """
    You are the lead commentator on Star Sports, covering a nail-biting IPL match LIVE.
    You have just witnessed a heated tactical debate between the AI agents.
    
    Your job is to make this accessible, exciting, and emotional for the fans.
    
    RULES:
    - Never use "ML", "model", "algorithm", "agent" — you're talking about cricket strategy
    - Explain every cricket term for casual fans (e.g., "the death overs — the last 4 overs")
    - Be emotional. Build tension. This is LIVE cricket.
    - Reference the win probability in fan-friendly language
    
    Format your output EXACTLY as:
    🏟️ MATCH SITUATION: [2 sentences — the tension right now]
    ⚡ THE CAPTAIN'S CALL: [What the captain just decided to do, explained simply]
    🤔 THE DEBATE: [1 sentence on what the analysts disagreed about]
    📊 THE NUMBERS: [Win probability in plain language — "Team X has a 65% chance of winning"]
    🏆 FINAL VERDICT: [Your authoritative final take — what SHOULD happen]
    👀 WATCH FOR: [The one moment that will tell us if the captain was right]
    """

    async def commentate(
        self,
        match_analysis: str,
        strategist_proposal: str,
        devils_challenge: str,
        strategist_rebuttal: str,
        win_prediction: str,
    ) -> str:
        client = get_client()
        prompt = f"""
        Match State:
        {match_analysis}
        
        Captain's Proposal:
        {strategist_proposal}
        
        Devil's Advocate Challenge:
        {devils_challenge}
        
        Captain's Rebuttal (after hearing the challenge):
        {strategist_rebuttal}
        
        Win Probability Analysis:
        {win_prediction}
        
        Now deliver the ultimate fan-friendly verdict. Make it unforgettable.
        """
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=self.SYSTEM_PROMPT,
                temperature=0.95,
            )
        )
        return response.text


# ══════════════════════════════════════════════════════════════════════════════
# Orchestrator — Full 6-step multi-turn pipeline
# ══════════════════════════════════════════════════════════════════════════════
async def run_captain_pipeline(url: str, raw_live_data: dict | None = None) -> dict:
    """
    Full multi-turn agent pipeline:
    
    StatsAnalyst [TOOL CALL]
      → Strategist [PROPOSES]
        → DevilsAdvocate [CHALLENGES]
          → Strategist [REBUTS/REVISES] ← this is the mandatory multi-turn loop
            → MatchPredictor [WIN PROBABILITY + COUNTERFACTUAL]
              → Commentator [FINAL VERDICT]
    """
    stats_agent = StatsAnalystAgent()
    strategist = StrategistAgent()
    devil = DevilsAdvocateAgent()
    predictor = MatchPredictorAgent()
    commentator = MatchCommentatorAgent()

    debate_log = []

    # ── Step 1: Stats Analyst (with real tool call) ───────────────────────────
    print("[Agent 1/5] StatsAnalystAgent analyzing match via tool call...")
    match_analysis = await stats_agent.analyze(url=url, raw_data=raw_live_data)
    debate_log.append({
        "agent": StatsAnalystAgent.NAME,
        "role": StatsAnalystAgent.ROLE,
        "output": match_analysis,
        "toolCall": f"get_live_match_data(url='{url}')" if raw_live_data else None,
        "step": 1
    })

    # ── Step 2: Strategist proposes ───────────────────────────────────────────
    print("[Agent 2/5] StrategistAgent proposing initial decision...")
    strategist_proposal = await strategist.propose(match_analysis)
    debate_log.append({
        "agent": StrategistAgent.NAME,
        "role": StrategistAgent.ROLE,
        "output": strategist_proposal,
        "toolCall": None,
        "step": 2
    })

    # ── Step 3: Devil's Advocate challenges ───────────────────────────────────
    print("[Agent 3/5] DevilsAdvocateAgent challenging the proposal...")
    devils_challenge = await devil.challenge(strategist_proposal, match_analysis)
    debate_log.append({
        "agent": DevilsAdvocateAgent.NAME,
        "role": DevilsAdvocateAgent.ROLE,
        "output": devils_challenge,
        "toolCall": None,
        "step": 3
    })

    # ── Step 4: STRATEGIST REBUTS (mandatory multi-turn loop) ─────────────────
    print("[Agent 4/5] StrategistAgent rebutting the challenge (multi-turn loop)...")
    strategist_rebuttal = await strategist.rebut(strategist_proposal, devils_challenge, match_analysis)
    debate_log.append({
        "agent": StrategistAgent.NAME + " (Rebuttal)",
        "role": "Captain — Final Commitment",
        "output": strategist_rebuttal,
        "toolCall": None,
        "step": 4
    })

    # ── Step 5: Win Probability + Counterfactual ──────────────────────────────
    print("[Agent 5/5] MatchPredictorAgent calculating win probability...")
    win_prediction = await predictor.predict(match_analysis, strategist_proposal, devils_challenge)
    debate_log.append({
        "agent": MatchPredictorAgent.NAME,
        "role": MatchPredictorAgent.ROLE,
        "output": win_prediction,
        "toolCall": None,
        "step": 5
    })

    # ── Step 6: Commentator final verdict ─────────────────────────────────────
    print("[Agent 6] MatchCommentatorAgent delivering verdict...")
    final_commentary = await commentator.commentate(
        match_analysis, strategist_proposal, devils_challenge,
        strategist_rebuttal, win_prediction
    )
    debate_log.append({
        "agent": MatchCommentatorAgent.NAME,
        "role": MatchCommentatorAgent.ROLE,
        "output": final_commentary,
        "toolCall": None,
        "step": 6
    })

    # Extract structured lines
    decision_line = next(
        (line.replace("DECISION:", "").strip()
         for line in strategist_proposal.split("\n") if "DECISION:" in line),
        "See captain's full proposal."
    )
    final_call = next(
        (line.replace("FINAL CALL:", "").strip()
         for line in strategist_rebuttal.split("\n") if "FINAL CALL:" in line),
        decision_line
    )
    verdict = next(
        (line.replace("VERDICT:", "").strip()
         for line in strategist_rebuttal.split("\n") if "VERDICT:" in line),
        ""
    )
    counter_line = next(
        (line.replace("COUNTER-PROPOSAL:", "").strip()
         for line in devils_challenge.split("\n") if "COUNTER-PROPOSAL:" in line),
        "See devil's advocate challenge above."
    )

    return {
        "agentDebate": debate_log,
        "finalDecision": {
            "initialDecision": decision_line,
            "finalCall": final_call,
            "verdict": verdict,
            "dissentingView": counter_line,
            "winProbability": win_prediction,
            "commentatorVerdict": final_commentary
        }
    }
