"""
Interactive CLI for the Autonomous Research Agent.
"""
import os
import sys
import re
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from agent import ResearchAgent

# Load environment variables from .env
load_dotenv()
console = Console()


def slugify(text: str) -> str:
    """Sanitize topic string into a valid filename."""
    text = re.sub(r'[^\w\s-]', '', text.lower()).strip()
    return re.sub(r'[-\s]+', '-', text)[:40]


def main():
    console.rule("[bold cyan]Autonomous AI Research Agent (Gemini-Powered)[/bold cyan]")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        console.print("[bold red]Error: GEMINI_API_KEY not found in environment or .env file.[/bold red]")
        api_key = Prompt.ask("[yellow]Enter your Gemini API key (or press Ctrl+C to exit)[/yellow]", password=True)
        if not api_key:
            console.print("[red]API Key required. Exiting...[/red]")
            sys.exit(1)

    try:
        agent = ResearchAgent(api_key=api_key)
    except Exception as e:
        console.print(f"[bold red]Failed to initialize Research Agent: {e}[/bold red]")
        sys.exit(1)

    while True:
        console.print("\n[bold]Enter a topic or research question (or 'quit' to exit):[/bold]")
        topic = Prompt.ask("[Topic]")
        
        if topic.strip().lower() in ["quit", "exit", "q"]:
            console.print("[green]Goodbye![/green]")
            break

        if not topic.strip():
            continue

        with console.status("[bold green]Agent researching and browsing the web...[/bold green]", spinner="dots"):
            try:
                report = agent.research(topic)
            except Exception as err:
                console.print(f"[bold red]An error occurred during research: {err}[/bold red]")
                continue

        # Render report in terminal
        console.print("\n" + "=" * 80)
        console.print(Markdown(report))
        console.print("=" * 80)

        # Save report to markdown file
        os.makedirs("reports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/research_{slugify(topic)}_{timestamp}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)

        console.print(f"\n[bold green][SAVED] Report successfully saved to:[/bold green] [cyan]{filename}[/cyan]\n")


if __name__ == "__main__":
    main()
