"""
Core Autonomous Research Agent loop powered by the Google GenAI SDK.
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from rich.console import Console
from rich.panel import Panel

from tools import search_web, scrape_webpage

# Load .env file automatically
load_dotenv()

console = Console()

SYSTEM_PROMPT = """You are an Autonomous Research Specialist AI Agent.
Your goal is to conduct comprehensive, accurate, objective research on any topic requested by the user.

You have access to two tools:
1. `search_web(query: str, max_results: int)`: Search DuckDuckGo for topics, latest news, and URLs.
2. `scrape_webpage(url: str, max_chars: int)`: Read the detailed text content from a specific web page.

Workflow guidelines:
- Step 1: Formulate search queries based on the user's research topic.
- Step 2: Search for reliable sources and analyze the snippets returned.
- Step 3: Scrape the most promising URLs to gather in-depth details, data, facts, and perspectives.
- Step 4: If information is missing or conflicting, perform follow-up targeted searches.
- Step 5: Synthesize your findings into a comprehensive, well-structured Markdown research report.

Report Structure Requirements:
- Title & Executive Summary
- Key Findings / Analysis
- In-depth Breakdown of Key Themes
- Challenges, Controversies, or Future Outlook
- Cited Sources with hyperlinks

Never invent facts or URLs. Always ground your final report in the evidence gathered from search and scraping tools.
"""


class ResearchAgent:
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-3.5-flash-lite"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key is required. Set GEMINI_API_KEY environment variable or pass api_key."
            )

        self.client = genai.Client(api_key=self.api_key)
        self.model = model
        self.tool_map = {
            "search_web": search_web,
            "scrape_webpage": scrape_webpage
        }

    def research(self, topic: str, max_iterations: int = 8, on_step=None) -> str:
        """
        Runs the autonomous research loop on the provided topic.

        Args:
            topic: The topic/question to research.
            max_iterations: Maximum tool call loops.
            on_step: Optional callback fn(step_type: str, message: str, details: Any) for UI updates.
        """
        console.print(Panel(f"[bold cyan]Initiating Research Topic:[/bold cyan] {topic}", title="Research Agent"))
        if on_step:
            on_step("start", f"Initiating research on: {topic}", None)

        # Initialize chat session with tools attached
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.3,
            tools=[search_web, scrape_webpage]
        )

        chat = self.client.chats.create(model=self.model, config=config)

        # Initial prompt to the agent
        prompt = f"Please conduct comprehensive research on the following topic and produce a detailed report:\n\nTopic: {topic}"

        iteration = 0
        response = chat.send_message(prompt)

        while iteration < max_iterations:
            iteration += 1

            # Check if model made any function calls
            function_calls = response.function_calls

            if not function_calls:
                # No more tools called, agent has completed its synthesis
                console.print(f"[bold green][OK] Research completed after {iteration} step(s).[/bold green]")
                if on_step:
                    on_step("complete", f"Research synthesis finished in {iteration} steps.", None)
                return response.text

            # Execute tool calls
            for call in function_calls:
                func_name = call.name
                func_args = call.args

                console.print(f"[yellow]>> Calling tool:[/yellow] [bold]{func_name}[/bold] with {func_args}")
                if on_step:
                    on_step("tool_call", f"Calling tool: `{func_name}`", func_args)

                if func_name in self.tool_map:
                    try:
                        tool_result = self.tool_map[func_name](**func_args)
                    except Exception as err:
                        tool_result = {"error": str(err)}
                else:
                    tool_result = {"error": f"Tool '{func_name}' not recognized."}

                if on_step:
                    on_step("tool_result", f"Received data from `{func_name}`", tool_result)

                # Send function response back to the chat
                response = chat.send_message(
                    types.Part.from_function_response(
                        name=func_name,
                        response={"result": tool_result}
                    )
                )

        console.print("[bold yellow][!] Reached maximum agent loop iterations. Finalizing synthesis...[/bold yellow]")
        if on_step:
            on_step("finalize", "Finalizing comprehensive report...", None)
        final_summary = chat.send_message("Please finalize your research report now based on all information gathered.")
        return final_summary.text
