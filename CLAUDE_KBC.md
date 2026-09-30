# Tectonic Hackathon: KBC track (preselection, 30 Sep 2026, 18:00–23:00)

## STATUS: BRIEF NOT KNOWN YET
Do NOT propose solutions, write code, or pick a direction until I paste the KBC brief.
When I paste it: run the grill-me skill first, then commit to ONE plan within 15 minutes.

## Setup
- Team of 3–4, 5 hours total (plan for ~4h30 of build; submissions close ~22:30–23:00).
- Top 16 teams per track advance to the final in Ghent on 20 Oct (€10k prize).
- Judges are KBC business people, not ML reviewers. Event language: English.
- Sponsors/tech partners: Google Cloud (Gemini), ElevenLabs (voice), Cursor, Aikido.
  Using their tech where it's cheap earns goodwill.
- Event theme: "Building on moving ground, the end of SaaS as we know it" → agentic/AI-native angle.

## What wins (optimize for this, not rigor)
- The flashiest WORKING demo with obvious business value beats a technically better model.
  A polished web UI + AI-generated visuals/text beats a better AUC in a notebook.
- The demo must show:
  1. a named user (relationship manager, credit analyst, SME owner, retail client),
  2. a clear before → after,
  3. one hard number on screen (€ saved, hours saved, defaults avoided, % automated).
- A live LLM feature is mandatory: generated memo, chat, or ElevenLabs voice.
- Always keep a recorded backup video of the demo in case the live one breaks.

## Hard rules for Claude
- Model work is capped at ~45 min: TabPFN (or XGBoost if data is too large) + SHAP is enough.
  No hyperparameter tuning, no model zoo, no deep learning.
- If data is synthetic or messy, don't spend >20 min cleaning; fake-but-plausible is fine for the demo.
- Push back hard if I start polishing the model instead of the UI/demo.
- Prefer boring, reliable stack choices; no new frameworks tonight.
- Keep every answer short and actionable; we are on a clock.

## Timeline (relative to brief release)
- 0:00–0:20 grill + scope, pick ONE user and ONE workflow
- 0:20–1:30 data + baseline model + explanations
- 1:30–3:45 UI + AI feature (memo/chat/voice) + the € number
- 3:45–4:30 rehearse the demo (under 3 min, no pitch) + record the backup video
- 4:30–5:00 buffer, submit

## Stack (pre-scaffolded)
- Python env: pandas, tabpfn, xgboost, shap
- UI: Streamlit (fastest) or Next.js skeleton, KBC-blue theme (#003665 / #00AEEF)
- LLM: Gemini / Claude API; voice: ElevenLabs. Keys in .env (never commit it).

## Background research (for context only; don't anchor on it)
- KBC already has mature credit/PD models and risk monitoring. A bare default-prediction
  model looks like table stakes; it must be wrapped in a workflow tool to impress.
- KBC Innovation Banking (Commercial Banking) lends to startups/scale-ups and scores
  "potential based on parameters", with 200+ companies in the portfolio. Tectonic's site links to it,
  so it's a strong hint the case is SME/startup credit.
- Kate (KBC's assistant) runs on GPT-4.1 since Oct 2025; agentic AI is still "being explored".
- Competitor ING is ahead on agentic back-office: agentic mortgage assistant (pilot Mar 2026, scaling),
  agentic KYC, a "hidden affluent client" detection model, >80% of chats resolved without humans.
  → The "ING gap": ING already does this kind of agentic work; this is KBC's version.

## Shortlist of likely problems (quick solution sketches)
1. Startup/SME credit scoring (Innovation Banking): TabPFN + SHAP → analyst cockpit with
   traffic light, top 3 reasons, LLM-written one-page credit memo.
2. Early warning for business clients: transaction features → distress score →
   RM dashboard "call these 10 clients this week" + drafted outreach.
3. Agentic credit application: upload payslips/balance sheets → LLM extraction + rule checks →
   pre-filled credit file + missing-docs list + time-saved counter.
4. Kate for Business cash-flow copilot: 90-day cash forecast from transactions;
   "can I afford to hire in March?" answered by chat/voice.
5. Late invoice prediction (KBC works with Billit/Go Solid): predict late payers →
   suggest reminder or invoice financing before the cash gap.
6. Scam/phishing shield: classify SMS/email/call transcript, explain in NL/FR/EN;
   demo with an ElevenLabs fake "KBC employee" call caught live.
7. KYC/AML review copilot: registry + UBO + adverse media → sourced risk memo, approve/escalate.
8. Next-best-action / hidden affluent: segment clients → next product → personalized
   Kate-style nudge → projected € uplift.

## Demo script (under 3 min, demo only, no slides or pitch)
The pain and the € number are spoken over the demo, never as separate slides.
Three stories, one idea: Kate reads your payments and keeps your cover and budget in step with your life.
1. Moving, Lotte (0:00–1:10): clock on 20 Aug, nothing happens → drag to 30 Sep, Kate card appears
   → Talk to Kate → "Yes, I'm moving" → checklist with the tenant fire insurance she was missing
   → approve → done screen. Glance right: bank view confidence + € per 10k customers.
2. Trip cover, Sofie (1:10–2:00): tap the mic (or the 🎤 question button): "We're going to
   Normandy... are we covered?" Kate answers out loud: liability and home covered, medical abroad,
   cancellation and car breakdown not → "Fix it" in one tap. Kate found the trip from the booking.
3. Financial Care, Arne (2:00–2:50): clock on 31 Aug, Kate quiet (healthy). Drag to 30 Sep: tuition
   + kot rent → strain → Kate offers 3 modes. Tap Mode 3: rent first, round-ups, gym to Basic, each
   explained with Undo. Say that Mode 1 turns Kate silent and Mode 2 only suggests.
Cut if over time: the bank-view glance in story 1. Janssens, Marc and the Plug-ins tab are for Q&A.
Hit "Restart demo" in the sidebar before every run.
