

import asyncio
from agents import Runner, trace, gen_trace_id
from openai import InternalServerError
from planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from search_agent import search_agent
from report_agent import report_agent, ReportData
from email_agent import email_agent

# Limit how many searches run at once, to reduce the chance of hitting
# Gemini's "high demand" 503s and free-tier rate limits.
SEARCH_CONCURRENCY_LIMIT = 3


async def run_agent_with_503_retry(agent, message, max_attempts: int = 3, base_delay: float = 3.0):
    """
    Run an agent, retrying a few times if Gemini returns a transient
    503 "high demand" error. Re-raises the error if all attempts fail.

    Args:
        agent: The Agent to run.
        message: The input message/prompt.
        max_attempts: Maximum number of attempts before giving up.
        base_delay: Delay in seconds, multiplied by the attempt number.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return await Runner.run(agent, message)
        except InternalServerError:
            if attempt == max_attempts:
                raise
            await asyncio.sleep(base_delay * attempt)


class ResearchManager:
    
    async def run(self, query: str) -> str:
        """
        Run the search agent with the given query and return the final output.

        Args:
            query: The search query string.
        """
        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id):
            yield "Starting research process..."
            search_keywords = await self.run_planner_agent(query)
            yield f"Searching results"
            perform_search_results = await self.perform_searches(search_keywords)
            yield "Searches complete, writing report..."
            report = await self.write_report(query, perform_search_results)
            yield "Report written, sending email..."
            await self.send_email(report)
            yield "Email sent, research complete"
            yield report.markdown_report
            
            
           
    async def send_email(self, report: ReportData) -> None:
        """
        Send the report via email.

        Args:
            report: The report data to send.
        """
        await run_agent_with_503_retry(email_agent, report.markdown_report)

    async def write_report(self, query: str, search_results: list[str]) -> ReportData:
        """
        Write the report for the query.

        Args:
            query: The search query string.
            search_results: The search results to include in the report.
        """
        input_message = f"Original query: {query}\nSummarized search results: {search_results}"
        result = await run_agent_with_503_retry(report_agent, input_message)
        return result.final_output
    
    async def perform_searches(self, search_keywords: WebSearchPlan) -> list[str]:
        """
        Perform the searches for the given search keywords and return the results.

        Searches are run concurrently using asyncio.gather for speed.
        Note: if you hit Gemini free-tier rate limits (429 errors), consider
        reverting to the sequential approach with a delay between calls.

        Args:
            search_keywords: The search keywords to use for the searches.
        """
        semaphore = asyncio.Semaphore(SEARCH_CONCURRENCY_LIMIT)

        async def bounded_search(item: WebSearchItem) -> str:
            async with semaphore:
                return await self.run_search_agent(item.query, item)

        tasks = [bounded_search(item) for item in search_keywords.searches]
        return await asyncio.gather(*tasks)
      
    async def run_search_agent(self, query: str, item: WebSearchItem) -> str:
        """
        Run the search agent with the given query and return the final output.

        Args:
            query: The search query string.
        """
        message = f"Search term: {query} reason for searching: {item.reason}"
        result = await run_agent_with_503_retry(search_agent, message)
        return result.final_output
    
    async def run_planner_agent(self, query: str) -> str:
        """
        Run the planner agent with the given query and return the final output.

        Args:
            query: The search query string.
        """
        web_searches = await run_agent_with_503_retry(planner_agent, query)
        return web_searches.final_output