"""Run before every push: python scripts/check.py  (no API keys needed)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

from streamlit.testing.v1 import AppTest  # noqa: E402

from kate import data, impact  # noqa: E402
from kate.events import MOVING  # noqa: E402

txs = data.load_transactions()
expected = {"lotte": "triggered", "janssens": "triggered", "marc": "quiet"}
ok = True

for profile in data.load_personas():
    d = MOVING.detect(txs[txs["persona_id"] == profile["id"]], data.END)
    good = d.status == expected[profile["id"]]
    ok &= good
    n_actions = len(MOVING.actions(profile, d)) if d.triggered else 0
    print(f"[{'OK' if good else 'FAIL'}]   {profile['id']:9} {d.score:.0%} {d.status:9} "
          f"{len(d.fired)} signals, {n_actions} actions, {d.facts.get('new_address')}")

premium = impact.compute(impact.DEFAULTS)["premium"]
print(f"[OK]   impact: € {premium:,.0f} per 10k customers / yr")

ROOT = Path(__file__).resolve().parent.parent


def click(app, label):
    next(b for b in app.button if b.label == label).click().run(timeout=60)


# Walk the whole customer flow; without LLM keys this exercises the scripted fallbacks.
app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=60)
try:
    click(app, "Talk to Kate")
    click(app, "Yes, I'm moving")
    click(app, next(b.label for b in app.button if b.label.startswith("Approve")))
    reached_done = any(b.label == "Back to overview" for b in app.button)
except StopIteration:
    reached_done = False
good = reached_done and not app.exception
ok &= good
print(f"[{'OK' if good else 'FAIL'}]   app flow home -> Kate -> checklist -> done"
      + "".join(f"\n       {e.value}" for e in app.exception))

sys.exit(0 if ok else 1)
