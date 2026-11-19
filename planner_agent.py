import os
from dotenv import load_dotenv
from agents import Agent,   OpenAIChatCompletionsModel
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

load_dotenv(override=True)

# ---------------------------------------------------------------------------
# Model setup - using Gemini (free tier) via the OpenAI-compatible endpoint.
# Swap this out for `model="gpt-4o-mini"` etc. if you'd rather use OpenAI.
# ---------------------------------------------------------------------------
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
google_api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

gemini_client = AsyncOpenAI(
    base_url=GEMINI_BASE_URL,
    api_key=google_api_key,
    timeout=60.0,
    max_retries=5,
)

gemini_model = OpenAIChatCompletionsModel(
    model="gemini-3.5-flash-lite",
    openai_client=gemini_client,
)

class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search term to use for the web search.")

class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")


instructions = "You are a Planner Agent,You are given a querry and you return the 3 search options that the user can use to search the web for the querry."     

planner_agent = Agent(
    name="PlannerAgent",
    model=gemini_model,
    instructions=instructions,
    output_type=WebSearchPlan,)