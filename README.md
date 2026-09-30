# Kate Life Events

Kate detects life events from transaction data and turns them into ready-to-approve
insurance and banking actions. Moving house is built end to end; other events are plug-ins.

## Setup (once, ~10 min)

```powershell
git clone <repo-url>
cd <repo-folder>
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env      # then paste the keys from the team chat
```

macOS/Linux: `python3.11 -m venv .venv`, `.venv/bin/python -m pip install -r requirements.txt`, `cp .env.example .env`.

The app runs without any keys (Kate uses scripted messages). `GEMINI_API_KEY` makes Kate live;
`ELEVENLABS_API_KEY` adds the voice button.

## Run

Always run from `.venv`. Anaconda's or a global `streamlit` is too old and fails with
`unexpected keyword argument 'width'`.

```powershell
.venv\Scripts\python.exe -m streamlit run app.py    # the demo, works even without activating
.venv\Scripts\Activate.ps1
streamlit run app.py          # same thing once activated
python scripts/check.py       # run before every push, needs no keys
python -m kate.data           # regenerate data/ after editing kate/data.py
```

## Who owns what

One owner per file. Change someone else's file only after telling them.

| Area | Files | What to build next |
|---|---|---|
| Data | `kate/data.py`, `kate/avg_belgian.py`, `kate/avg_student.py`, `data/` | Keep the three datasets plausible |
| Detection | `kate/events.py` | Tune weights, "old rent stopped" signal, wire a second plug-in |
| Kate (LLM + voice) | `kate/persona.py`, `kate/coverage.py`, `kate/care.py`, `kate/prompts/`, `services.py` | Persona tone, voice in/out |
| Customer screens | `ui/phone.py` (story 1), `ui/trip.py` (story 2), `ui/care.py` (story 3), `ui/common.py`, `ui/theme.py` | Make it look like KBC Mobile |
| Bank screen + number | `ui/bank.py`, `kate/impact.py` | Source the assumptions, make the € number land |
| Wiring | `app.py` | Should rarely change |

## Contracts between modules

- `data.load_transactions()` returns columns `persona_id, date, counterparty, description, amount`.
- `data.load_personas()` returns dicts with `id, name, first_name, age, segment, address, tone, products`.
- `MOVING.detect(txs, today)` returns a `Detection` with `score`, `status`, `fired`, `facts`.
- `MOVING.actions(profile, detection)` returns a list of `Action`.
- `services.chat(messages, system)` returns Kate's reply as text and raises if no LLM is reachable.
- `impact.compute(assumptions)` returns the numbers shown in the bank view.

Keep these signatures stable. If you must change one, say so in the team chat first.

## Git, tonight

Everyone commits straight to `main`. Small commits, often.

```powershell
git pull --rebase
python scripts/check.py
git add -A
git commit -m "what changed"
git push
```

If `git pull --rebase` reports a conflict, fix the file, then `git add <file>` and `git rebase --continue`.
When the demo works end to end, tag it: `git tag demo-ok; git push --tags`.
Never commit `.env`.
