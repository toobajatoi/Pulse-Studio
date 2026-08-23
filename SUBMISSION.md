# Pulse Studio — Careem Challenge submission

**Challenge:** Generative design studio for Careem product screens  
**Time to try:** 30–60 minutes with free tools only  
**Confidential data:** None. All trip, food, and payment copy is dummy UAE content.

## Public prototype

**Live app:** [https://pulse-studio-ashen.vercel.app](https://pulse-studio-ashen.vercel.app)

Hard-refresh once, then: *Payment failed* → pick a direction → toggle EN/AR → open **DNA**.

**Code:** [https://github.com/toobajatoi/Pulse-Studio](https://github.com/toobajatoi/Pulse-Studio)

## Public dataset

Not required. Pulse Studio does not use Kaggle, data.gov, or Careem dumps. Screens use self-created dummy copy (AED, Dubai streets, fake card endings).

Optional Challenge 1 companion notes (also dummy, self-created): `data/usability_feedback.csv`

## How it works

1. Open the live app and type a brief, or tap a starter such as Payment failed or Food home.
2. Pulse returns three design directions. Pick one.
3. Canvas shows a phone preview plus the design system for that screen.
4. Toggle **EN / AR** and **iOS / Android**. Style Memory (the DNA drawer) steers spacing, corners, copy, and guidance.
5. Flow maps the journey and missing failure states (cancel, no-show, payment failed).

**Tools (all free):** Python + a small web UI, Gemini / Groq / OpenRouter, Vercel.

## 100-word summary

Pulse Studio is a generative design workspace for Careem screens. Type a brief or pick a starter. A free LLM returns three directions; one tap opens a phone with Careem tokens, EN/AR, and iOS or Android. Style Memory sliders steer spacing, copy, and guidance. Flow maps the journey and failure states. All copy is dummy UAE content—no confidential Careem data. Built with Python and free Gemini/Groq/OpenRouter models, deployed on Vercel so a reviewer can try it in 30–60 minutes. The next screen follows what you kept, not a one-off prompt.
