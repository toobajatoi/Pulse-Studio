# Pulse · Design Companion

Challenge 1 only. A Streamlit prototype that summarizes usability feedback, writes UI copy, and brainstorms layouts.

Uses **self-created dummy data** and a **free LLM**. Paste a free Groq key for Llama 3.1. If the public endpoint is busy, Pulse falls back to a local model so the demo still runs.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## What it does

1. **Summarize feedback** — themes, quoted evidence, five UI fixes
2. **Generate UI copy** — headline, helper, CTA, empty, error (EN / AR)
3. **Brainstorm layouts** — three directions, each with a test and a tradeoff

## Data

`data/usability_feedback.csv` — 48 dummy ride-hailing notes. No confidential information.

## LLM

- Default: [Pollinations](https://text.pollinations.ai) `openai-fast` — no API key
- Optional: free [Groq](https://console.groq.com) key → `openai/gpt-oss-20b`
