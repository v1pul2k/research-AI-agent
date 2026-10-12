"""
Streamlit Web UI for the Autonomous AI Research Agent.
"""
import os
import re
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st

from agent import ResearchAgent

# Page configuration
st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load existing environment
load_dotenv()


def slugify(text: str) -> str:
    """Sanitize topic string into a valid filename."""
    text = re.sub(r'[^\w\s-]', '', text.lower()).strip()
    return re.sub(r'[-\s]+', '-', text)[:40]


# --- Sidebar ---
st.sidebar.title("⚙️ Configuration")

# API Key management - Loaded securely from environment / .env
api_key = os.getenv("GEMINI_API_KEY", "")
if api_key:
    st.sidebar.success("🔒 API Key loaded securely from environment (.env)")
else:
    # Fallback only if no key is in .env
    api_key = st.sidebar.text_input(
        "Enter Gemini API Key",
        type="password",
        help="Add GEMINI_API_KEY to your .env file to avoid entering it here."
    )

# Model selection
model_choice = st.sidebar.selectbox(
    "Gemini Model",
    options=["gemini-3.5-flash-lite", "gemini-flash-latest", "gemini-2.5-pro"],
    index=0,
    help="gemini-3.5-flash-lite provides fast response times and solid tool execution."
)

max_iterations = st.sidebar.slider(
    "Max Research Loops",
    min_value=2,
    max_value=12,
    value=6,
    help="Maximum search and scrape iteration loops the agent is allowed to execute."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 Saved Reports")
reports_dir = "reports"
if os.path.exists(reports_dir):
    report_files = sorted(
        [f for f in os.listdir(reports_dir) if f.endswith(".md")],
        reverse=True
    )
    if report_files:
        selected_file = st.sidebar.selectbox("View previous reports", ["None"] + report_files)
        if selected_file != "None":
            with open(os.path.join(reports_dir, selected_file), "r", encoding="utf-8") as rf:
                past_content = rf.read()
            st.sidebar.download_button(
                label=f"📥 Download {selected_file}",
                data=past_content,
                file_name=selected_file,
                mime="text/markdown"
            )
    else:
        st.sidebar.info("No reports generated yet.")
else:
    st.sidebar.info("No reports directory yet.")


# --- Main Area ---
st.title("🔬 Autonomous AI Research Agent")
st.caption("Powered by Google Gemini API, DuckDuckGo Live Search & BeautifulSoup Scraper")

st.markdown(
    """
    Give the agent any research topic or question. It will autonomously:
    1. **Plan & search** DuckDuckGo for the most credible sources.
    2. **Read & scrape** full webpage articles.
    3. **Synthesize** a structured Markdown report with key takeaways and citations.
    """
)

# Topic input
topic_query = st.text_area(
    "What would you like the agent to research?",
    placeholder="e.g. Recent breakthroughs in Solid-State Batteries in 2026, or State of Open-Source Multimodal AI...",
    height=90
)

start_button = st.button("🚀 Start Autonomous Research", type="primary", use_container_width=True)

if start_button:
    if not api_key:
        st.error("Please enter a valid Gemini API Key in the sidebar or in your `.env` file.")
    elif not topic_query.strip():
        st.warning("Please provide a topic or question to research.")
    else:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("⚡ Agent Activity & Reasoning Log")
            step_container = st.container()

        steps_log = []

        def agent_callback(step_type, message, details):
            steps_log.append((step_type, message, details))
            with step_container:
                if step_type == "start":
                    st.info(f"🏁 **{message}**")
                elif step_type == "tool_call":
                    with st.expander(f"🛠️ {message}", expanded=True):
                        st.json(details)
                elif step_type == "tool_result":
                    with st.expander(f"📥 {message}", expanded=False):
                        if isinstance(details, list):
                            st.write(f"Found {len(details)} search results:")
                            for item in details[:3]:
                                st.markdown(f"- **[{item.get('title')}]({item.get('href')})**: {item.get('body')[:120]}...")
                        else:
                            st.text(str(details)[:600] + ("..." if len(str(details)) > 600 else ""))
                elif step_type == "complete":
                    st.success(f"✅ **{message}**")
                elif step_type == "finalize":
                    st.warning(f"📝 **{message}**")

        try:
            with st.spinner("Agent is actively searching the web and synthesizing findings..."):
                agent = ResearchAgent(api_key=api_key, model=model_choice)
                final_report = agent.research(
                    topic=topic_query.strip(),
                    max_iterations=max_iterations,
                    on_step=agent_callback
                )

            with col2:
                st.subheader("📄 Generated Research Dossier")
                st.markdown(final_report)

                # Save report
                os.makedirs("reports", exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"reports/research_{slugify(topic_query)}_{timestamp}.md"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(final_report)

                st.download_button(
                    label="📥 Download Research Report (.md)",
                    data=final_report,
                    file_name=f"research_{slugify(topic_query)}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
                st.success(f"Report saved locally to `{filename}`")

        except Exception as e:
            st.error(f"An error occurred during research: {str(e)}")
