import os
import warnings
import logging
import asyncio
from typing import Dict, Any
from datetime import datetime, timedelta

# Third-Party Libraries
from dotenv import load_dotenv, find_dotenv

# Google ADK and GenAI Libraries
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, Agent, LoopAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool, ToolContext, google_search, agent_tool, AgentTool, preload_memory
from google.adk.apps.app import App, ResumabilityConfig
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.genai import types

# --- Configuration and Setup ---
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO) 
if not os.environ.get("GOOGLE_API_KEY"):
    print("⚠️ WARNING: GOOGLE_API_KEY not found. Ensure it is in your .env file.")

retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)

def check_appeal_eligibility(date_of_denial: str) -> dict:
    """Checks if the claim is within the typical 180-day timely filing limit."""
    try:
        denial_dt = datetime.strptime(date_of_denial, "%Y-%m-%d")
        deadline = denial_dt + timedelta(days=180) 
        
        # Check eligibility based on current system time
        if datetime.now() > deadline:
            return {"status": "ineligible", "message": f"Deadline passed on {deadline.strftime('%Y-%m-%d')}."}
        return {"status": "eligible", "message": "Eligible. Proceed with data collection."}
        
    except ValueError:
        return {"status": "warning", "message": "Date format error. Please check the date and proceed with caution."}


# Mid-level agent combining tools
researcher_agent = LlmAgent(
    name="ResearchAssistant",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    description="Finds and summarizes information on the denial reason from the insurance mention by user",
    output_key="evidence",
    tools=[google_search]
)

# High-level agent delegating research
appeal_writting_agent = LlmAgent(
    name="LetterWriter",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction="""
    Write a letter to appeal the denial. Use {evidence}. 
    Your final output MUST be the include the Appeal Letter you have written.
    """,
    output_key="appealletter",
)






# This is the function that the RefinerAgent will call to exit the loop.
def exit_loop():
    """Call this function ONLY when the review_result is 'APPROVED', indicating the appeal letter is well written"""
    return {"status": "APPROVED", "message": "Appeal letter well written"}


reviewer = LlmAgent(
    name="reviewer", 
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
     instruction=""" You are a letter reviewer. Review the {evidence} and {appealletter}, 
     You must compare these two and make sure the  the appeal letter incorporate the evidence. 
     After verifying the facts, you must refine the grammar and adjust the tone to be professional and persuasive. 
     If the letter matches all these, you MUST respond with the exact phrase: "APPROVED".
     Else, provide the review comment.""",
    output_key="review_result")


# This agent refines the story based on critique OR calls the exit_loop function.
refiner_agent = Agent(
    name="RefinerAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction="""YYou are an appeal letter refiner. You have a {review_result} and {appealletter}.
    
    Your task is to analyze the review.
    - IF the review is EXACTLY "APPROVED", you MUST call the `exit_loop` function and nothing else.
    - OTHERWISE, rewrite the appeal letter to fully incorporate the feedback from the critique.""",
    output_key="appealletter",  
    tools=[FunctionTool(exit_loop)] )


final_output_agent = LlmAgent(
    name="FinalOutputPresenter",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    # Instruction to retrieve the final result from the appealletter key
    instruction="""
    The appeal letter refinement process is complete. 
    Output the full text of the final approved letter stored in {appealletter}. 
    Present only the letter text, and nothing else.
    """,
    output_key="final_appeal_letter" 
)

# The LoopAgent contains the agents that will run repeatedly: Reviewer -> Refiner.
story_refinement_loop = LoopAgent(
    name="LetterRefinementLoop",
    sub_agents=[reviewer, refiner_agent],
    max_iterations=3
)

review_pipeline = SequentialAgent(
    name="ReviewPipeline",
    sub_agents=[
        researcher_agent,      
        appeal_writting_agent, 
        story_refinement_loop, final_output_agent 
    ]
)


root_agent = LlmAgent(
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    name='claim_ally_agent',
    instruction="""
You are a helpful claim denial appeal agent that provides and writes appeal letters based on user information.

1.  **Initial Step:** If the user wishes to appeal a denied claim, ask them for the exact date of denial (e.g., '2025-10-20').
2.  **Tool Check (Eligibility):** Once the user provides the date of denial, activate the 'check_appeal_eligibility' tool immediately using this date.
3.  **If Eligible:** If the 'check_appeal_eligibility' tool returns an 'eligible' status, ask the user for the **policy ID** and the **reason for denial**. 
3.  After receiving this information, **combine the date of denial, the policy ID, and the reason for denial into a single, comprehensive request** and activate the 'review_pipeline' tool to write the appeal letter and present the final letter to the user.
4.  **If Error:** If the 'check_appeal_eligibility' tool returns an 'error' status, inform the user that the date must be in **YYYY-MM-DD** format and ask them to re-enter the date of denial and start initial step.
5.  **If Ineligible:** If the 'check_appeal_eligibility' tool returns an 'ineligible' status, let the user know that the time frame for appeal has passed.
""",
    tools=[AgentTool(agent=review_pipeline), check_appeal_eligibility])
