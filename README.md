# Pulse Studio

Careem Challenge 2 — a Gemini-style studio that co-designs Careem screens (Rides, Food, Quik, Pay) with Design DNA, EN/AR, and iOS/Android.

**Repo:** [github.com/toobajatoi/Pulse-Studio](https://github.com/toobajatoi/Pulse-Studio)

## Live

**App:** [https://pulse-studio-ashen.vercel.app](https://pulse-studio-ashen.vercel.app)

Deploys from this GitHub repo on Vercel. These environment variables are already set on the project (never commit them):

- `GEMINI_API_KEY`
- `GROQ_API_KEY`
- `LLM_TIMEOUT` = `12`

## Run locally

```bash
pip install -r requirements.txt
python studio_server.py
```

Open [http://localhost:8787](http://localhost:8787). Put keys in `.streamlit/secrets.toml` (copy `.streamlit/secrets.toml.example`).

## What it does

1. Brief → three directions (you pick)
2. Canvas with a real phone preview
3. EN / AR and iOS / Android on the preview
4. Style Memory (DNA) that only learns when you keep a preference

Challenge 1 Streamlit companion:

```bash
pip install -r requirements-local.txt
streamlit run app.py
```
