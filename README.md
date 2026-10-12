# 🤖 Autonomous AI Research Agent

A lightweight, powerful Python-based autonomous research agent powered by the **Google GenAI SDK (Gemini API)**. The agent autonomously searches the web, extracts relevant articles, analyzes sources, and compiles comprehensive Markdown research dossiers with cited sources.

---

## 🚀 Features

- **Autonomous Tool-Use Loop**: Uses Gemini native function calling to formulate queries, browse DuckDuckGo, and selectively scrape deep webpage content.
- **Deep Web Scraping**: Cleans and strips HTML to feed dense, relevant knowledge into the LLM context.
- **Structured Synthesis**: Automatically formats findings with executive summaries, key trends, challenges, and cited sources.
- **Auto Report Export**: Automatically saves reports with timestamps and slugified filenames into the `reports/` folder.
- **Rich Terminal UI**: Pretty formatting and live progress spinners using `rich`.

---

## 📁 Project Structure

```text
research-agent/
├── .env.example       # Template for API keys
├── requirements.txt   # Dependencies
├── tools.py           # DuckDuckGo search & BeautifulSoup web scraper
├── agent.py           # Autonomous research loop & Gemini tool-calling engine
├── main.py            # Interactive CLI interface
└── reports/           # Generated Markdown dossiers (created on first run)
```

---

## 🛠️ Getting Started

### 1. Install Dependencies

In your terminal or command prompt:

```bash
pip install -r requirements.txt
```

### 2. Configure Your API Key

Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/).

Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

Open `.env` and set your key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

*(Note: If you run `python main.py` without a `.env` file, the CLI will interactively prompt you to enter the key.)*

### 3. Run the Agent

```bash
python main.py
```

Provide any topic or question (e.g. *"Recent breakthroughs in solid-state batteries in 2025-2026"* or *"State of open source multi-modal models"*), and the agent will autonomously perform the research and save a report.
