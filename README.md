# Review Paper Agent

A Streamlit-based review paper writing assistant that guides you through a structured workflow — from **high-level overview → detailed structure → draft → final paper** — with user review at each stage.

## Features

- **5-Stage Workflow**: Topic → Overview → Structure → Draft → Finalize
- **3 Writing Modes**: Adjustable question depth and automation level based on user experience
- **LLM Integration (Optional)**: Enable AI assistance with an OpenAI or Anthropic API key
- **Manual Mode**: Write everything yourself without an API key
- **Interactive Chat**: Ask questions during the writing process
- **Export**: Download as Markdown (`.md`) or Word (`.docx`)

## Writing Modes

| Mode | Description | Best For |
|---|---|---|
| **Quick Start** | Enter a topic and the AI auto-generates the rest | Rapid prototyping / first drafts |
| **Standard** | User makes key decisions; AI handles detailed writing | General review paper writing |
| **Expert** | In-depth workshop-style questions at every stage | Publication-quality academic papers |

## Project Structure

```
ResearchRA/
├── app.py                         # Streamlit main app
├── requirements.txt               # Python dependencies
├── .streamlit/config.toml         # Streamlit theme config
├── src/
│   ├── llm_client.py              # OpenAI / Anthropic API client
│   ├── paper_state.py             # Paper state & mode management
│   └── prompts.py                 # Mode-specific LLM prompt templates
└── components/
    ├── sidebar.py                 # Sidebar (mode selection, progress, LLM settings)
    ├── export.py                  # Markdown / Word export
    ├── stage_topic.py             # Stage 1: Topic setup
    ├── stage_overview.py          # Stage 2: High-level overview
    ├── stage_structure.py         # Stage 3: Detailed structure design
    ├── stage_draft.py             # Stage 4: Draft writing
    └── stage_finalize.py          # Stage 5: Finalization
```

## Getting Started

```bash
pip install -r requirements.txt
streamlit run app.py
```

## LLM API Setup

After launching the app, open **LLM API Settings** in the left sidebar:

1. Select a provider (OpenAI or Anthropic)
2. Choose a model
3. Enter your API key
4. Adjust temperature
5. Click **Save Settings**

The app is fully functional without an API key — all content can be written manually.
