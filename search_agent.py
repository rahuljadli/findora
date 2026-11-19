"""
Search Agent for Findora

Instead of the paid `WebSearchTool` (which uses OpenAI's hosted web search and
costs money per call), this module implements a FREE custom search tool backed
by DuckDuckGo (via the `ddgs` package - no API key required).

Usage:
    from search_agent import search_agent, search_web

    result = await Runner.run(search_agent, "What's the latest news on AI agents?")
    print(result.final_output)
"""

import os
from dotenv import load_dotenv
from ddgs import DDGS
from agents import Agent, ModelSettings, Runner, function_tool, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

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

search_model = OpenAIChatCompletionsModel(
    model="gemini-3.5-flash-lite",
    openai_client=gemini_client,
)

# ---------------------------------------------------------------------------
# Free custom search tool (DuckDuckGo) - replaces the paid WebSearchTool
# ---------------------------------------------------------------------------
@function_tool
def search_web(query: str, max_results: int = 3) -> str:
    """
    Search the web for a given query and return a summary of the top results.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default 3).
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
    except Exception as exc:
        return f"Search failed: {exc}"

    if not results:
        return f"No results found for query: {query!r}"

    formatted = []
    for i, r in enumerate(results, start=1):
        title = r.get("title", "No title")
        body = r.get("body", "")
        href = r.get("href", "")
        formatted.append(f"{i}. {title}\n   {body}\n   Source: {href}")

    return "\n\n".join(formatted)


# ---------------------------------------------------------------------------
# The Search Agent
# ---------------------------------------------------------------------------
INSTRUCTIONS = (
    "You are a research assistant. Given a search term, use the search_web tool "
    "to find up-to-date information, then produce a concise summary of the results. "
    "The summary must be 2-3 paragraphs and less than 300 words. Capture the main "
    "points, write succinctly, and no need for complete sentences or good grammar. "
    "This will be consumed by someone synthesizing a report, so it's vital you "
    "capture the essence and ignore any fluff. Do not include any additional "
    "commentary other than the summary itself."
)

search_agent = Agent(
    name="Search Agent",
    instructions=INSTRUCTIONS,
    tools=[search_web],
    model=search_model,
)

async def run_search_agent(query: str) -> str:
    """
    Run the search agent with the given query and return the final output.

    Args:
        query: The search query string.
    """
    result = await Runner.run(search_agent, query)
    return result.final_output


if __name__ == "__main__":
    import asyncio

    ans = asyncio.run(run_search_agent("What's the latest news on AI agents?"))
    print(ans)