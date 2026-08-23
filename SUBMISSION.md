# Pulse — Design Companion

**Challenge:** 1 only · Design Companion

## 100-word summary

Pulse is a Streamlit Design Companion. It reads 48 self-created ride-hailing usability notes and sends the filtered set to a free LLM. The model returns three designer-ready outputs: a theme summary with quoted evidence, UI copy (headline, helper, CTA, empty, error) in English or Arabic, and three layout hypotheses each with a test and a tradeoff. Prompts forbid invented metrics and dark patterns. The default model is Pollinations openai-fast, which needs no API key. A free Groq key can be pasted for faster Llama 3.1 calls. No confidential Careem data is used.

## Dataset

Self-created dummy file: `data/usability_feedback.csv`

## Prototype

```bash
streamlit run app.py
```

## LLM

- Pollinations `openai-fast` — free, no key
- Optional Groq `llama-3.1-8b-instant` — free key from console.groq.com
