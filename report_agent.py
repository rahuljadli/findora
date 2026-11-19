import os
from dotenv import load_dotenv
from ddgs import DDGS
from agents import Agent, ModelSettings, Runner, function_tool, OpenAIChatCompletionsModel
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

instruction ="You are a report generator agent,You are given a querry and some reasearch around it" \
"You are to generate a report based on the reasearch and the querry." \
"You need to generate a report that is at least 500 words long and is in a professional tone." \
"You need to generate a report in a markdown format and include a title and a table of contents." \
"You need to generate a report that is well structured and has a clear introduction, body and conclusion." \
"You need to generate a report that is well researched and includes references to the sources used."

class ReportData(BaseModel):
    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")
    markdown_report: str = Field(description="The final report")
    follow_up_questions: list[str] = Field(description="Suggested topics to research further")


report_agent = Agent(
    name="ReportAgent",
    model=gemini_model,
    instructions=instruction,
    output_type=ReportData,
)