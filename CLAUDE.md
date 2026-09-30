@CLAUDE_KBC.md

## Project: Kate Life Events (brief is known, plan is committed)
Kate detects life events from transactions and offers one-tap insurance/banking actions.
Moving is built end to end; baby/car/job are declared plug-ins. See README.md for
file ownership and module contracts; respect them. This supersedes the "brief not known"
status block and the problem shortlist in CLAUDE_KBC.md; its other rules still apply.

- `.venv` — activate with `.venv\Scripts\Activate.ps1`; deps in `requirements.txt`
- `streamlit run app.py` — demo; `python scripts/check.py` — run before every push
- `kate/data.py` (synthetic data), `kate/events.py` (signals → score → actions),
  `kate/persona.py` (Kate prompt + scripted fallbacks), `kate/impact.py` (the € number)
- `ui/phone.py` (customer screen), `ui/bank.py` (bank view), `services.py` (LLM + voice)
- The numbers in `kate/impact.py` are illustrative placeholders until someone sources them.
